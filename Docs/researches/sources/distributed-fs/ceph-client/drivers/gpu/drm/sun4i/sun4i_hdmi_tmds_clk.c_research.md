<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_hdmi_tmds_clk.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_hdmi_tmds_clk.c

## Purpose

`sun4i_hdmi_tmds_clk.c` registers the legacy HDMI TMDS clock as a common-clock provider backed by HDMI PLL and pad-control registers. It lets HDMI mode validation and enable paths request exact or nearest TMDS character rates.

## Important APIs, Types, And Functions

`struct sun4i_tmds` wraps `clk_hw`, `struct sun4i_hdmi *`, and a divider offset. Public creation is `sun4i_tmds_create()`. Clock ops are `sun4i_tmds_determine_rate()`, `sun4i_tmds_recalc_rate()`, `sun4i_tmds_set_rate()`, `sun4i_tmds_get_parent()`, and `sun4i_tmds_set_parent()`. `sun4i_tmds_calc_divider()` searches the HDMI divider and optional half-clock bit.

## Control Flow

Creation names two parents from `pll-0` and `pll-1`, allocates the clock wrapper, sets `CLK_SET_RATE_PARENT`, and stores the variant divider offset. Rate determination iterates all parents, half divisors 1/2, and divider values to find an exact parent rate or closest rounded parent. `set_rate()` recomputes the divider, toggles `SUN4I_HDMI_PAD_CTRL1_HALVE_CLK`, and writes `SUN4I_HDMI_PLL_CTRL_DIV()`. Parent ops read/write the parent select field in `PLL_DBG0`.

## State And Persistence Behavior

Software state is the devm-allocated `sun4i_tmds` and `hdmi->tmds_clk`. Hardware state persists in the HDMI pad half-clock bit, PLL divider field, and parent-select bits. The clock framework caches rates and parents around these register ops.

## Dependencies And Integration Points

It depends on common clock APIs, HDMI register definitions in `sun4i_hdmi.h`, and clocks acquired by `sun4i_hdmi_bind()`. `sun4i_hdmi_connector_clock_valid()` and `sun4i_hdmi_enable()` use the registered clock to validate and program HDMI modes.

## Risks And Test Signals

Risks include divider-offset differences on sun6i, using only two parents, closest-rate selection that can fail HDMI tolerance, and preserving unrelated pad/PLL bits. Test by checking `clk_round_rate()` near common HDMI pixel clocks, parent switching, half-rate cases, mode validation tolerance, and register values after enable on each variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_hdmi_tmds_clk.c -->
