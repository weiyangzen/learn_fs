<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_rgb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_rgb.h

## Purpose

`sun4i_rgb.h` declares the parallel RGB output initializer used by the TCON component when channel 0 is connected to a non-LVDS panel or bridge.

## Important APIs, Types, And Functions

It exposes `sun4i_rgb_init(struct drm_device *drm, struct sun4i_tcon *tcon)`.

## Control Flow

There is no runtime flow in the header. It enables `sun4i_tcon.c` to instantiate RGB output support during TCON bind.

## State And Persistence Behavior

The header has no state. The implementation owns the DRM connector/encoder object and references the TCON passed by caller.

## Dependencies And Integration Points

Consumers need declarations for DRM device and TCON structures. It is part of the channel 0 output-selection split between RGB and LVDS support.

## Risks And Test Signals

Only prototype consistency is material. Build coverage with RGB support enabled and runtime probe of a panel or bridge connected to TCON port 1 validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_rgb.h -->
