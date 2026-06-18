<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tcon.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tcon.h

## Purpose

`sun4i_tcon.h` defines the TCON register map, bitfield helpers, driver-private TCON structures, quirk callbacks, and exported functions used across the sun4i DRM pipeline.

## Important APIs, Types, And Definitions

The header provides many register offsets and bitfield macros for global control/interrupts, channel 0/1 control/timing/polarity/IO tristate, CPU trigger/DSI path, LVDS interface/analog controls, frame-rate-control dithering, mux control, and safe-period/ECC FIFO registers. `struct sun4i_tcon_quirks` describes SoC capabilities such as channel presence, LVDS support, alternate LVDS PLL, DE backend muxing, polarity register placement, eDP reset, minimum dclk divider, mux callback, and LVDS PHY setup callback. `struct sun4i_tcon` stores runtime TCON state. Exports include `sun4i_tcon_mode_set()`, `sun4i_tcon_set_status()`, `sun4i_tcon_enable_vblank()`, and `sun4i_tcon_of_table`.

## Control Flow

No standalone control flow runs here. Macros encode register values consumed by `sun4i_tcon.c` mode-setting, IRQ, bind, and PHY helpers, and by dot-clock code in `sun4i_tcon_dclk.c`.

## State And Persistence Behavior

The structures model persistent per-device state; register macros target persistent hardware state. `dclk_min_div` and `dclk_max_div` are mutable clock-search parameters shared between mode validation/programming and the dot-clock provider.

## Dependencies And Integration Points

It includes DRM modes, regmap, reset, and kernel list/clock declarations indirectly through consumers. It is included by TCON, RGB, LVDS, DSI, and dot-clock code and is part of the external match table used by the sun4i driver.

## Risks And Test Signals

Risks include incorrect bitfield widths, generation-specific register differences hidden behind shared names, and quirk mismatches with compatible strings. Test by compiling all sun4i variants and checking register programming on RGB, LVDS, DSI, HDMI, TV, and TCON TOP systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tcon.h -->
