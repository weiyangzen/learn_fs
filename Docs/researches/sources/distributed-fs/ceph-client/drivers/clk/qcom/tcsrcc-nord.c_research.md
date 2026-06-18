# sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-nord.c

## Purpose
This NORD TCSRCC driver exposes reference-clock gates for DisplayPort RX/TX lanes, PCIe, UFS, USB2/USB3 ports, and UX SGMII references.

## Important APIs, types, and functions
- Fifteen `clk_branch` descriptors use `BRANCH_HALT_DELAY`, bit 0, and `clk_branch2_ops`.
- Parent data uses `DT_BI_TCXO_PAD` for TCXO-derived clkrefs.
- `tcsr_cc_nord_clocks[]` maps NORD TCSR binding IDs to branches.
- `tcsr_cc_nord_desc` and `tcsr_cc_nord_probe()` register the clocks through `qcom_cc_probe()`.

## Control flow
At subsys init, the platform driver binds `"qcom,nord-tcsrcc"`, maps the TCSR block up to 0xf008, and registers branch gates. Peripheral drivers enable the relevant clkref, causing the branch ops to update bit 0 at DP/PCIe/UFS/USB/SGMII offsets.

## State and persistence behavior
The driver maintains no private runtime state. Hardware TCSR bits store reference-clock enable state and persist until consumer operations or reset alter them.

## Dependencies and integration points
It depends on qcom common CC, branch/regmap helpers, platform device matching, and `dt-bindings/clock/qcom,nord-tcsrcc.h`. It integrates with display, PCIe, UFS, USB, and network/SGMII consumers.

## Risks
The broad set of clkrefs makes binding index accuracy important. DP lane offsets are separated by 0x1000 regions; wrong offsets could break only a subset of display lanes. Because halt checks are delay-based, stuck or absent clkref feedback is not directly detected.

## Test signals
DisplayPort multi-lane, PCIe, UFS, USB2/USB3, and SGMII initialization should succeed with requested clock references. `clk_summary` should list all TCSRCC NORD gates, and register readback should show bit 0 changes at offsets such as 0xa008-0xf008 and USB/UFS offsets.
