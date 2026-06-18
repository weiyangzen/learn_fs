<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_hdmi_phy_clk.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_hdmi_phy_clk.c

## Purpose

`sun8i_hdmi_phy_clk.c` registers the optional HDMI PHY output clock used by H3/R40/A64-like PHY variants. It exposes PLL parent selection and predivider programming through common clock ops.

## Important APIs, Types, And Functions

`struct sun8i_phy_clk` wraps `clk_hw` and a PHY pointer. The public API is `sun8i_phy_clk_create()`. Clock ops are `sun8i_phy_clk_determine_rate()`, `sun8i_phy_clk_recalc_rate()`, `sun8i_phy_clk_set_rate()`, `sun8i_phy_clk_get_parent()`, and `sun8i_phy_clk_set_parent()`.

## Control Flow

Creation gets `pll-0` and optional `pll-1` parent names from the PHY, allocates the wrapper, registers `hdmi-phy-clk` with `CLK_SET_RATE_PARENT`, and stores it in `phy->clk_phy`. Rate determination scans all parents and dividers 1..16, choosing exact or closest parent/divider combination. Recalc reads the PLL CFG2 predivider field. Set-rate searches the best divider not above target and writes `SUN8I_HDMI_PHY_PLL_CFG2_PREDIV()`. Parent ops read/write the CKIN select field in PLL CFG1.

## State And Persistence Behavior

The registered clock persists after PHY init. Hardware state persists in PLL CFG1 parent select and CFG2 predivider fields. The PHY mode-setting code must preserve those fields when rewriting PLL configuration.

## Dependencies And Integration Points

It depends on the common clock framework, regmap, and `sun8i_dw_hdmi.h` register definitions. `sun8i_hdmi_phy_init()` creates this clock for variants with `has_phy_clk`, and `sun8i_h3_hdmi_phy_config()` sets its rate to the HDMI pixel clock.

## Risks And Test Signals

Risks include zero `best_m` if no divider satisfies a too-high target, optional second-parent setup, and race with PHY PLL writes that also touch CFG1/CFG2. Test rate rounding, parent switching, divider programming from 27 MHz through high TMDS clocks, and mode changes on H3/R40/A64 variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_hdmi_phy_clk.c -->
