# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-glymur.c

## Purpose
This driver registers Glymur VIDEOCC clocks, reset lines, and GDSCs for MVS0/MVS0C/MVS1 video hardware domains.

## Important APIs, types, and functions
- `video_cc_pll0` is a Taycan EKO T alpha PLL configured for 720 MHz.
- RCGs provide AHB, MVS0, sleep, and XO sources; dividers derive MVS0/MVS0C/MVS1 clocks.
- Branches expose MVS core, freerun, and shift clocks.
- `video_cc_mvs0_gdsc`, `video_cc_mvs0c_gdsc`, and `video_cc_mvs1_gdsc` define power domains.
- `video_cc_glymur_resets[]` maps interface/MVS block resets and freerun clock resets.
- `clk_glymur_regs_configure()` sets bit 0 at 0x9f24 before/while registering via driver data.
- `video_cc_glymur_desc` sets `.use_rpm = true` and includes PLLs, critical CBCRs, resets, and GDSCs.

## Control flow
The platform driver matches `"qcom,glymur-videocc"` and calls `qcom_cc_probe()`. Common qcom code maps the register block, configures alpha PLLs, keeps critical AHB/sleep/XO CBCRs enabled, runs the register configure hook, registers clocks, resets, and power domains, and honors RPM integration.

## State and persistence behavior
VIDEOCC registers hold PLL configuration, RCG selections, dividers, branch enables, reset bits, and GDSC states. The driver is descriptor-only after probe. Critical clocks are intentionally kept enabled.

## Dependencies and integration points
It depends on qcom alpha PLL, branch, RCG, divider, mux, GDSC, reset, regmap, and `dt-bindings/clock/qcom,glymur-videocc.h`. It integrates with video codec drivers through clocks, resets, and genpd domains.

## Risks
PLL frequency tables and divider topology must match video performance points. The 0x9f24 register tweak is hardware-specific and could regress if moved or omitted. GDSC ordering and reset IDs must match bindings. Critical CBCRs can keep hardware active and affect power measurements.

## Test signals
Video encode/decode should power domains on/off and switch clock rates successfully. `clk_summary` should show PLL0 and MVS clocks. Reset tests should hit interface/MVS reset lines. Power tests should confirm GDSC transitions and critical clocks remaining enabled.
