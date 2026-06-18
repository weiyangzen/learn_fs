# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_framebuffer.h

## Purpose
`sun4i_framebuffer.h` declares the mode-config/framebuffer initialization entry point for the Allwinner DRM master driver.

## Important APIs, Types, and Functions
- `sun4i_framebuffer_init(struct drm_device *drm)`: installs framebuffer and atomic mode-config callbacks on a DRM device.

## Control Flow, State, and Persistence
The header has no state. The declared function mutates `drm->mode_config` when called from master bind, and those callbacks persist until DRM device teardown.

## Dependencies and Integration Points
It forward-relies on `struct drm_device` visibility in including files and is included by `sun4i_drv.c` and implemented by `sun4i_framebuffer.c`.

## Risks and Test Signals
The contract is small, so risks are signature drift and missing initialization before DRM registration. Build coverage and a probe test confirming `mode_config.funcs` and helper callbacks are installed are the main signals.
