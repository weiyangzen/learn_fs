# sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-eliza.c

## Purpose
This TCSR clock-controller driver exposes one-bit reference-clock enables for Eliza HDMI, PCIe, UFS, USB2, and USB3 PHY-related consumers.

## Important APIs, types, and functions
- Six `clk_branch` descriptors gate `tcsr_hdmi_clkref_en`, PCIe 0/1, UFS, USB2, and USB3 reference clocks.
- Each branch uses `BRANCH_HALT_DELAY`, `BIT(0)`, `clk_branch2_ops`, and mostly parent `DT_BI_TCXO_PAD`.
- `tcsr_cc_eliza_clocks[]` maps dt-binding IDs to branch clocks.
- `tcsr_cc_eliza_desc` and `tcsr_cc_eliza_probe()` register the controller with `qcom_cc_probe()`.

## Control flow
The driver registers at `subsys_initcall`, matches `"qcom,eliza-tcsr"`, maps the MMIO region using `tcsr_cc_eliza_regmap_config`, and registers branch clocks. Consumers then enable a branch to set bit 0 at that branch's TCSR offset.

## State and persistence behavior
State is the hardware latch at offsets 0x0 through 0x1c. There is no software cache or runtime PM. Branch enable state persists in TCSR registers until changed by the clock framework or reset.

## Dependencies and integration points
It depends on qcom common CC helpers, CCF branch ops, regmap, platform driver support, and `dt-bindings/clock/qcom,eliza-tcsr.h`. It integrates with PHY/controller drivers needing stable TCXO-derived reference clocks.

## Risks
All clocks are simple bit-0 gates, so the main risk is incorrect offset or binding ID. `BRANCH_HALT_DELAY` avoids strict halt polling; this is appropriate for reference gates but gives less direct hardware confirmation.

## Test signals
Probe should occur early and expose all six clock names. USB/PCIe/UFS/HDMI bring-up should succeed when their clkrefs are requested. Register tracing should show bit 0 toggles at the documented offsets.
