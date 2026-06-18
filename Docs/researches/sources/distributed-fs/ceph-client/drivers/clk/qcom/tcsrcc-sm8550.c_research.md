# sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-sm8550.c

## Purpose
This driver registers SM8550-family TCSR reference-clock gates, with a reduced descriptor for SAR2130P and a fuller descriptor for SM8550.

## Important APIs, types, and functions
- Six branch descriptors cover PCIe 0/1, UFS, UFS pad, USB2, and USB3 reference clocks.
- `tcsr_cc_sar2130p_clocks[]` omits UFS entries; `tcsr_cc_sm8550_clocks[]` includes all six.
- `of_device_id` entries attach `.data` pointers to either `tcsr_cc_sar2130p_desc` or `tcsr_cc_sm8550_desc`.
- `tcsr_cc_sm8550_probe()` maps the matched descriptor with `qcom_cc_map()` but then calls `qcom_cc_really_probe()` with `tcsr_cc_sm8550_desc`.

## Control flow
The subsys-init driver matches `"qcom,sar2130p-tcsr"` or `"qcom,sm8550-tcsr"`. Probe obtains match data for mapping, checks for mapping errors, and registers clocks. Consumers enable branch gates through CCF.

## State and persistence behavior
TCSR registers at 0x15100-0x15118 store the clock-reference enable state. No private mutable state is maintained.

## Dependencies and integration points
It uses qcom common CC, CCF branch ops, regmap, `of_device_get_match_data()`, and `dt-bindings/clock/qcom,sm8550-tcsr.h`. It integrates with PCIe, UFS, and USB PHY/controller device-tree nodes.

## Risks
The probe maps with match-specific data but always registers `tcsr_cc_sm8550_desc`; that appears inconsistent with the SAR2130P reduced descriptor and could expose clocks not meant for SAR2130P. Several branches use `BRANCH_HALT_SKIP`, so enable operations do not verify halt status. Binding arrays must match compatible-specific hardware.

## Test signals
On SM8550, all six clkrefs should register and enable. On SAR2130P, validation should specifically check whether UFS clocks appear unexpectedly and whether consumers bind correctly. Register readback and `clk_summary` should confirm branch states.
