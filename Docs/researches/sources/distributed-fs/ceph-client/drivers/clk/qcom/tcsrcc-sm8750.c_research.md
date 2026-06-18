# sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-sm8750.c

## Purpose
This driver registers SM8750 TCSR reference-clock gates for PCIe 0, UFS, USB2, and USB3.

## Important APIs, types, and functions
- Four `clk_branch` descriptors at offsets 0x0, 0x1000, 0x2000, and 0x3000.
- UFS/USB branches declare `DT_BI_TCXO_PAD` parent data; PCIe is a gate-only branch without explicit parent.
- `tcsr_cc_sm8750_clocks[]` maps binding IDs from `qcom,sm8750-tcsr.h`.
- `tcsr_cc_sm8750_probe()` calls `qcom_cc_probe()`.

## Control flow
The platform driver registers at subsys init and matches `"qcom,sm8750-tcsr"`. Probe maps the small TCSR region and registers branch clocks. Consumer enable requests set bit 0 at the corresponding region offset.

## State and persistence behavior
Only hardware TCSR enable bits store state. There is no runtime PM or software cache.

## Dependencies and integration points
It depends on qcom common CC, branch/regmap helpers, platform device matching, and the SM8750 TCSR dt-binding. It integrates with PCIe, UFS, and USB subsystems through clock phandles.

## Risks
The PCIe branch lacks explicit parent data while others point to TCXO. The simple four-offset layout is easy to audit, but any binding mismatch directly affects peripheral reference clocks. `BRANCH_HALT_DELAY` does not prove the hardware gate changed state.

## Test signals
Probe should expose four clocks. PCIe/UFS/USB PHY bring-up should request the expected clkrefs. Register readback should confirm bit 0 toggling at 0x0, 0x1000, 0x2000, and 0x3000.
