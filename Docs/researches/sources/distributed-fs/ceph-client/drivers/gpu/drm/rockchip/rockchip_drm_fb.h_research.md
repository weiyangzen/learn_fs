# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_fb.h

## Purpose

`rockchip_drm_fb.h` is the minimal public header for Rockchip framebuffer mode configuration. It exposes only `rockchip_drm_mode_config_init`.

## Important APIs, Types, and Functions

- `rockchip_drm_mode_config_init(struct drm_device *dev)` initializes `drm_device->mode_config` with Rockchip framebuffer creation, atomic helpers, dimension limits, runtime-PM-aware commit tail, and normalized zpos.

## Control Flow

The header provides no control flow. The Rockchip DRM driver includes it during device setup and calls the exported initializer before registering or using mode objects.

## State and Persistence Behavior

State initialized by the declared function persists in `dev->mode_config`. The header itself owns no data.

## Dependencies and Integration Points

The header relies on consumers already having a visible `struct drm_device` declaration. It is consumed by Rockchip DRM setup code and by VOP code that includes the framebuffer interface.

## Risks and Edge Cases

Because this header does not include DRM type declarations itself, include ordering must provide `struct drm_device`. Any signature change must be synchronized with `rockchip_drm_fb.c`.

## Test Signals

Build coverage with all Rockchip DRM objects enabled is the main signal. Runtime validation is covered by framebuffer creation and atomic commit tests.
