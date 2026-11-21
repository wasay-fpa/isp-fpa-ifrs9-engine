import pandas as pd


def classify_stage(days_past_due: int):
    if days_past_due < 0:
        return "Not Yet Due", 0.00
    elif days_past_due <= 15:
        return "Stage 1 (0-15d)", 0.015
    elif days_past_due <= 30:
        return "Stage 2 (16-30d)", 0.05
    return "Stage 3 (31+d)", 0.25


def run_reconciliation(csv_path: str = "sample_synthetic_subscribers.csv"):
    df = pd.read_csv(csv_path)
    open_ar = df[df["status"] == "UNPAID"].copy()

    stages = open_ar["days_past_due"].apply(classify_stage)
    open_ar["ifrs9_stage"] = [s[0] for s in stages]
    open_ar["ecl_rate"] = [s[1] for s in stages]
    open_ar["ecl_provision"] = (open_ar["monthly_fee_pkr"] * open_ar["ecl_rate"]).round(2)
    open_ar["net_carrying_value"] = (open_ar["monthly_fee_pkr"] - open_ar["ecl_provision"]).round(2)

    summary = open_ar.groupby("ifrs9_stage", as_index=False).agg(
        accounts=("subscriber_id", "count"),
        gross_ar=("monthly_fee_pkr", "sum"),
        ecl_provision=("ecl_provision", "sum"),
        net_carrying_value=("net_carrying_value", "sum"),
    )

    print("=== IFRS 9 ECL RECEIVABLES SUMMARY ===")
    print(summary.to_string(index=False))
    print(f"\nTotal Gross AR: PKR {summary['gross_ar'].sum():,.2f}")
    print(f"Total ECL Allowance: PKR {summary['ecl_provision'].sum():,.2f}")
    print(f"Net Carrying Value: PKR {summary['net_carrying_value'].sum():,.2f}")


if __name__ == "__main__":
    run_reconciliation()
