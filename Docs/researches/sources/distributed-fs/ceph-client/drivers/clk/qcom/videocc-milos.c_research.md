# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-milos.c

## Purpose
This Milos VIDEOCC driver registers a compact video clock controller with one PLL, MVS0/MVS0C clocks, two GDSCs, and reset controls.

## Important APIs, types, and functions
- `video_cc_pll0` is a Lucid OLE alpha PLL configured around 604.8 MHz.
- Parent maps include XO and sleep sources with always-on parent variants.
- RCGs provide AHB, MVS0, sleep, and XO sources; dividers derive MVS0 and MVS0C divided paths.
- Branches expose MVS0/MVS0C core and shift clocks.
- `video_cc_milos_gdscs[]`, `video_cc_milos_resets[]`, `video_cc_milos_plls[]`, and critical CBCRs are collected in driver data/descriptor.
- `video_cc_milos_probe()` delegates to `qcom_cc_probe()`.

## Control flow
The platform driver matches `"qcom,milos-videocc"`. Common qcom probe maps registers, configures the listed PLL, keeps critical AHB/sleep/XO CBCRs enabled, and registers clocks, resets, and GDSCs. Video consumers then enable domains and clocks.

## State and persistence behavior
PLL, RCG, divider, branch, reset, and GDSC state lives in hardware registers. `.use_rpm = true` requests RPM-aware handling in the qcom CC layer. Software state remains static.

## Dependencies and integration points
It depends on qcom alpha PLL, branch, RCG, divider, GDSC, reset, regmap, platform matching, and `dt-bindings/clock/qcom,milos-videocc.h`. It serves video codec drivers and power-domain consumers.

## Risks
The Milos-specific PLL frequency and parent data must align with firmware/OPP expectations. Sparse or wrong reset mapping would break video block recovery. Critical clocks and RPM integration need power testing to avoid idle regressions.

## Test signals
Successful boot should register PLL0, MVS0/MVS0C clocks, and two GDSCs. Video encode/decode should power-cycle domains, change rates, and survive reset assertions. `clk_summary` should show critical CBCRs enabled.
