# sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-sm8650.c

## Purpose
This TCSRCC driver exposes SM8650 reference-clock gates for PCIe, UFS, UFS pad, USB2, and USB3, with special handling for Milos.

## Important APIs, types, and functions
- Six `clk_branch` descriptors use offsets in the 0x31100 range and `BRANCH_HALT_DELAY`.
- `tcsr_cc_sm8650_clocks[]` maps binding IDs to PCIe/UFS/USB clkrefs.
- `tcsr_cc_sm8650_probe()` checks `of_device_is_compatible(..., "qcom,milos-tcsr")`; for Milos it moves `tcsr_ufs_clkref_en` to offset 0x31118 and nulls USB2/USB3 clock entries.
- `qcom_cc_probe()` registers the resulting descriptor.

## Control flow
The platform driver binds either `"qcom,milos-tcsr"` or `"qcom,sm8650-tcsr"`. Probe mutates static descriptors for the Milos variant before common qcom CC registration. Clock consumers then enable branch gates by binding ID.

## State and persistence behavior
Hardware state is the bit-0 gate at each TCSR offset. The Milos compatibility path mutates static global descriptors and the clock array for the life of the module; because a single instance is expected, this is acceptable but not per-device isolated.

## Dependencies and integration points
The file integrates with qcom common CC, CCF, regmap, platform matching, `of_device_is_compatible()`, and `dt-bindings/clock/qcom,sm8650-tcsr.h`. Consumers are PCIe/UFS/USB PHY/controller drivers.

## Risks
Static mutation for Milos would be unsafe if both Milos and SM8650 instances could coexist. Nulling clock entries relies on qcom CC code accepting sparse arrays. Variant offset changes need hardware validation, especially because UFS moves to the same offset as the normal USB2 gate.

## Test signals
On SM8650, all six clocks should appear and toggle the 0x31100-0x31118 offsets. On Milos, USB2/USB3 clocks should be absent/unavailable and UFS should toggle 0x31118. Probe and peripheral bring-up logs should show no sparse-clock registration failures.
