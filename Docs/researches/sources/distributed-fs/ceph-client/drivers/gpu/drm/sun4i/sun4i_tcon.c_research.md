<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tcon.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tcon.c

## Purpose

`sun4i_tcon.c` is the central Allwinner timing-controller driver. It binds a TCON to a display engine, creates the CRTC, programs channel 0/1 timings for RGB/LVDS/DSI/HDMI/TV, handles vblank IRQs/page-flip completion, creates channel 0 dot clock support, instantiates RGB or LVDS outputs, and provides SoC-specific output muxing quirks.

## Important APIs, Types, And Functions

Exported APIs are `sun4i_tcon_set_status()`, `sun4i_tcon_mode_set()`, `sun4i_tcon_enable_vblank()`, and `sun4i_tcon_of_table`. Major helpers include connector/pixel-depth lookup, LVDS PHY setup, channel enable/clock exclusivity, dithering setup, `sun4i_tcon0_mode_set_cpu/lvds/rgb()`, `sun4i_tcon1_mode_set()`, IRQ handler/page-flip finish, clock/regmap/IRQ init, engine matching through OF graph traversal or endpoint IDs, component bind/unbind, and platform mux callbacks for A10/A13/A31/R40/TCON TOP.

## Control Flow

Probe verifies panel/bridge dependencies for channel 0 and registers a component. Bind finds the matching `sunxi_engine`, allocates TCON state, resets hardware, handles optional eDP/LVDS resets and LVDS alternate clock availability, initializes clocks/regmap/IRQ, creates `dclk`, initializes the CRTC, creates LVDS or RGB output for channel 0, applies backend muxing quirks, and appends the TCON to the driver list. Atomic mode set dispatches by encoder type: DSI uses channel 0 CPU/8080-style trigger path, LVDS and RGB use channel 0 timing registers, HDMI/TV use channel 1 timing registers and output mux. Status enable toggles global enable, LVDS interface/PHY, channel gate, and clock exclusivity.

## State And Persistence Behavior

Persistent state is `struct sun4i_tcon`: DRM/device pointers, regmap, clocks, resets, CRTC pointer, ID, quirks, and list entry. Hardware state persists in timing, polarity, mux, LVDS, dithering, interrupt, and channel-control registers. Page-flip event state lives in `sun4i_crtc` and is completed under `dev->event_lock` from the IRQ handler.

## Dependencies And Integration Points

It depends on Linux component, regmap, clock/reset, IRQ, OF graph, DRM CRTC/encoder/connector/panel/bridge/vblank helpers, `sun4i_crtc`, `sunxi_engine`, RGB/LVDS/DSI helpers, TCON TOP, and `sun4i_tcon_dclk`. It is the timing bridge between display engines/mixers/backends and output encoders.

## Risks And Test Signals

Risks include fragile DT graph engine matching, legacy endpoint ID compatibility, LVDS property fallback disabling output, undocumented dithering/LVDS/mux bits, clock divider side effects, interlace vertical-total handling, IRQ ack semantics, and unbalanced clock exclusivity. Test on each compatible, RGB/LVDS/DSI/HDMI/TV modes, vblank/page flips, TCON TOP routing, old and corrected DT graphs, suspend/resume, and LVDS 18/24-bit panels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tcon.c -->
