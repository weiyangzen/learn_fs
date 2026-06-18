<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_lvds.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_lvds.c

## Purpose

`sun4i_lvds.c` creates a DRM LVDS encoder and optional connector for TCON channel 0 when a panel-lvds or bridge is connected. It manages only DRM/panel lifecycle; TCON timing and LVDS PHY programming are handled by `sun4i_tcon.c`.

## Important APIs, Types, And Functions

The exported entry point is `sun4i_lvds_init()`. `struct sun4i_lvds` contains a connector, encoder, and panel pointer. Helpers include `sun4i_lvds_get_modes()`, connector destroy funcs, and encoder `enable`/`disable` callbacks that prepare/enable or disable/unprepare the panel.

## Control Flow

TCON bind calls `sun4i_lvds_init()` when OF graph port 1 resolves to an LVDS panel and LVDS prerequisites are available. Init finds a panel or bridge from the TCON node, initializes a simple LVDS encoder, restricts possible CRTCs to the owning TCON CRTC, creates and attaches an LVDS connector for panel outputs, or attaches a bridge when present. Enable/disable callbacks only sequence panel power.

## State And Persistence Behavior

The LVDS object is devm-allocated for the DRM device lifetime. Connector/encoder registration persists until driver cleanup. Hardware state is not directly programmed here; persistent display output state is in the panel, bridge, and TCON LVDS registers touched by other files.

## Dependencies And Integration Points

It depends on DRM panel/bridge/connector helpers, `drm_simple_encoder_init()`, OF graph lookup, and `struct sun4i_tcon`. `sun4i_tcon_mode_set()` and `sun4i_tcon_set_status()` use encoder type `DRM_MODE_ENCODER_LVDS` to choose channel 0 and LVDS PHY behavior.

## Risks And Test Signals

Risks include returning success when no panel/bridge exists, cleanup paths shared between panel and bridge cases, and panel power sequencing without error propagation. Test with LVDS panels and bridges, missing LVDS reset/clock properties in the TCON, mode enumeration from panel, encoder possible CRTC mask, and enable/disable cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_lvds.c -->
