<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_lvds.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_lvds.h

## Purpose

`sun4i_lvds.h` is the narrow declaration header for LVDS output initialization on sun4i TCON channel 0.

## Important APIs, Types, And Functions

It declares `sun4i_lvds_init(struct drm_device *drm, struct sun4i_tcon *tcon)`. The function creates the LVDS encoder/connector or bridge attachment for the given TCON.

## Control Flow

No code runs in the header. It allows `sun4i_tcon.c` to call the LVDS initializer when OF graph detection says the channel 0 output is an LVDS panel.

## State And Persistence Behavior

The header stores no state. State is owned by the LVDS implementation, DRM objects, and the TCON instance passed to the initializer.

## Dependencies And Integration Points

Consumers must have visible declarations for `struct drm_device` and `struct sun4i_tcon`. It forms the compile-time link from TCON bind logic to LVDS output creation.

## Risks And Test Signals

Risk is limited to prototype drift. Build coverage of `sun4i_tcon.c` and LVDS-enabled configurations, plus runtime LVDS probe, are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_lvds.h -->
