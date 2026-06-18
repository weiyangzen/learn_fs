<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/framebuffer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/framebuffer.h

## Purpose

This header provides framebuffer/modeset integration declarations for GMA500.

## Important APIs, Types, And Functions

It includes `psb_drv.h` and declares `gma_connector_clones(struct drm_device *dev, int type_mask)`, used by output setup to compute encoder clone masks.

## Control Flow

No executable flow exists. `psb_setup_outputs()` calls the declared helper while iterating connectors.

## State And Persistence

The header stores no state. The declared function reads DRM connector/encoder state and output type masks to build persistent encoder clone capability fields.

## Dependencies And Integration Points

It ties `framebuffer.c` to shared PSB/GMA driver types and the connector clone helper implemented elsewhere in the driver.

## Risks And Test Signals

Risks are limited to declaration drift and broad inclusion of `psb_drv.h`. Test signals are compile/link success and clone-mask correctness for analog and HDMI connectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/framebuffer.h -->
