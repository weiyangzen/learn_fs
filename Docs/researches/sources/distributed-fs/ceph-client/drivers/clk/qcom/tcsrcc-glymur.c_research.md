# sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-glymur.c

## Purpose
This driver exposes Glymur TCSR reference-clock gates for eDP, multiple PCIe lanes/controllers, USB2/USB3, and USB4.

## Important APIs, types, and functions
- Thirteen `clk_branch` descriptors gate eDP, PCIe 1-4, USB2 1-4, USB3 0-1, and USB4 1-2 clkrefs.
- All gates use `BRANCH_HALT_DELAY`, `BIT(0)`, `clk_branch2_ops`, and `DT_BI_TCXO_PAD` as the parent.
- `tcsr_cc_glymur_clocks[]` maps binding IDs, and `tcsr_cc_glymur_desc` supplies regmap/clock metadata to qcom CC.
- `tcsr_cc_glymur_probe()` is a thin `qcom_cc_probe()` wrapper.

## Control flow
Registered via `subsys_initcall`, the platform driver matches `"qcom,glymur-tcsr"`, maps the TCSR register block with max register 0x94, and exposes the branch clocks. Consumers request reference clocks and the branch ops set/clear bit 0 at each offset.

## State and persistence behavior
The only persistent state is the enable bit in each TCSR register. The driver has no dynamic memory state after probe beyond framework registrations.

## Dependencies and integration points
It uses qcom common CC, CCF branch ops, regmap, device-tree binding `qcom,glymur-tcsr`, and TCXO parent indexing. It integrates with PCIe, USB, USB4, and display PHY nodes.

## Risks
The file includes several qcom clock headers not needed for the simple gates, but behavior is unaffected. Hardware risk centers on offset correctness and consumer binding references. Delayed halt checking may hide a stuck gate.

## Test signals
Expected signals are early successful probe, `clk_summary` entries for all clkrefs, PCIe/USB/eDP PHY initialization succeeding, and register-level confirmation that bit 0 toggles at offsets 0x44-0x88 as consumers enable clocks.
