<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_rgb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_rgb.c

## Purpose

`sun4i_rgb.c` creates the parallel RGB encoder and optional panel connector or bridge for TCON channel 0. It also validates RGB bridge modes against TCON register field limits and dot-clock tolerance.

## Important APIs, Types, And Functions

The exported initializer is `sun4i_rgb_init()`. `struct sun4i_rgb` holds connector, encoder, TCON, panel, and bridge pointers. Important callbacks are `sun4i_rgb_mode_valid()`, `sun4i_rgb_get_modes()`, `sun4i_rgb_encoder_enable()`, and `sun4i_rgb_encoder_disable()`.

## Control Flow

Init resolves a panel or bridge from the TCON OF graph. It creates a simple `DRM_MODE_ENCODER_NONE` encoder bound only to the TCON CRTC, creates a connector for direct panels, or attaches the bridge. Mode validation checks hsync/vsync widths, display/total field limits, and for bridge outputs rounds `tcon->dclk` with divider bounds 6..127 against a 0.5 percent tolerance. Panel outputs skip clock validation because panel timing tolerance may need future adjustment.

## State And Persistence Behavior

The RGB object is devm-allocated and persists with DRM registration. Panel power state is changed on enable/disable. `sun4i_rgb_mode_valid()` mutates `tcon->dclk_min_div` and `dclk_max_div` before clock rounding, so validation has side effects on the TCON clock search window.

## Dependencies And Integration Points

It depends on DRM panel/bridge helpers, TCON dot clock, `sun4i_tcon_mode_set()` for actual RGB timing programming, and OF graph port 1. Encoder type `DRM_MODE_ENCODER_NONE` selects TCON channel 0 RGB programming.

## Risks And Test Signals

Risks include clock validation side effects, skipping clock checks for panels, handling no panel/bridge as non-fatal disabled output, and bridge cleanup after partial init. Test with direct RGB panels, RGB-to-bridge outputs, invalid sync/size limits, dot-clock rounding near tolerance, bus flags for polarity in TCON mode set, and panel enable/disable sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_rgb.c -->
