<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tcon_dclk.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tcon_dclk.c

## Purpose

`sun4i_tcon_dclk.c` registers TCON channel 0 dot clock as a common-clock provider backed by `SUN4I_TCON0_DCLK_REG` and output-polarity phase bits. It lets panels/bridges and TCON mode setting derive exact pixel clocks from the channel 0 source clock.

## Important APIs, Types, And Functions

`struct sun4i_dclk` wraps `clk_hw`, regmap, and TCON pointer. Public APIs are `sun4i_dclk_create()` and `sun4i_dclk_free()`. Clock ops include enable/disable/is_enabled, `sun4i_dclk_recalc_rate()`, `sun4i_dclk_determine_rate()`, `sun4i_dclk_set_rate()`, `sun4i_dclk_get_phase()`, and `sun4i_dclk_set_phase()`.

## Control Flow

Creation reads the output clock name from `clock-output-names`, uses `tcon->sclk0` as parent, registers a `CLK_SET_RATE_PARENT` clock, and stores it in `tcon->dclk`. Rate determination iterates from `tcon->dclk_min_div` through `dclk_max_div`, rounds the parent to `requested * divider`, and chooses exact or closest result while guarding `ULONG_MAX` overflow. Set-rate writes the divider field. Enable/disable toggles the gate bit, and phase maps 0/120/240 degree steps to bits 29:28 of the IO polarity register.

## State And Persistence Behavior

Software state persists in the registered clock and TCON pointer. Hardware state persists in the DCLK gate/divider and output phase bits. Divider search bounds are mutable TCON state set by RGB/LVDS/DSI mode paths.

## Dependencies And Integration Points

It depends on common clock provider APIs, regmap, TCON register definitions, and the TCON bind/unbind lifecycle. RGB mode validation and TCON channel 0 mode programming rely on this clock for pixel-clock feasibility and output timing.

## Risks And Test Signals

Risks include divider truncation in `parent_rate / rate`, shared phase bits with polarity programming, mutable divider bounds from callers, and manual `clk_register()`/`clk_unregister()` lifecycle. Test round-rate/set-rate for RGB/LVDS/DSI dividers, gate behavior during enable/disable, phase programming, overflow path, and TCON unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tcon_dclk.c -->
