# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sc7180.c

## Purpose
This SC7180 VIDEOCC driver registers a small Venus/vcodec clock controller with one Fabia PLL, Venus/vcodec branch clocks, and two GDSCs.

## Important APIs, types, and functions
- `video_pll0` is a Fabia alpha PLL whose configuration is built locally in probe.
- `video_cc_venus_clk_src` is the main Venus RCG with rates from 100 MHz to 434 MHz.
- Branches expose vcodec0 AXI/core and Venus AHB/CTL AXI/CTL core clocks.
- `venus_gdsc` and `vcodec0_gdsc` expose power domains.
- `video_cc_sc7180_probe()` maps registers, fills `alpha_pll_config`, configures PLL0 with `clk_fabia_pll_configure()`, forces `VIDEO_CC_XO_CLK` on via `regmap_update_bits(0x984)`, and calls `qcom_cc_really_probe()`.

## Control flow
The platform driver matches `"qcom,sc7180-videocc"`. Probe manually maps the register block, programs PLL0, enables the XO branch, and registers clocks and GDSCs. Consumers then use CCF/genpd to run Venus and vcodec hardware.

## State and persistence behavior
VIDEOCC hardware registers store PLL programming, RCG source/rate, branch enables, and GDSC power state. The probe-local PLL config is not retained after programming. No reset map is registered by this driver.

## Dependencies and integration points
It depends on qcom alpha PLL, branch, RCG, common CC, GDSC, regmap, platform bus, and `dt-bindings/clock/qcom,videocc-sc7180.h`. It integrates with SC7180 Venus/vcodec drivers.

## Risks
Manual PLL config in probe must match hardware; there is no named static config table. The forced XO bit at 0x984 is critical and easy to miss in refactors. Lack of reset controls means consumers cannot recover video blocks through this driver.

## Test signals
Boot should register SC7180 VIDEOCC and show PLL0 plus Venus/vcodec clocks. Video decode/encode should exercise Venus RCG rates and GDSC transitions. Register readback should confirm XO bit 0 at 0x984 remains enabled.
