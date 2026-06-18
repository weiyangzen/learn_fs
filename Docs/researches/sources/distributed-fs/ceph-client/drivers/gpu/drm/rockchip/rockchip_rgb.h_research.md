# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_rgb.h

## Purpose

`rockchip_rgb.h` exposes the optional internal RGB encoder helper. It provides real declarations when `CONFIG_ROCKCHIP_RGB` is enabled and NULL/no-op stubs otherwise.

## Important APIs, Types, and Functions

- `rockchip_rgb_init(struct device *dev, struct drm_crtc *crtc, struct drm_device *drm_dev, int video_port)` creates or discovers an internal RGB panel/bridge path for the given video port.
- `rockchip_rgb_fini(struct rockchip_rgb *rgb)` tears down the helper.
- Stub versions return NULL and do nothing when the feature is disabled.

## Control Flow

The header controls compile-time feature flow. VOP/VOP2 can call `rockchip_rgb_init` without local `#ifdef` blocks; disabled builds compile to no RGB output.

## State and Persistence Behavior

The header owns no state. Real runtime state is private to `rockchip_rgb.c`; disabled builds persist no object because init returns NULL.

## Dependencies and Integration Points

The signatures depend on `struct device`, `struct drm_crtc`, and `struct drm_device` declarations from includers. It is consumed by both legacy VOP and VOP2 drivers.

## Risks and Edge Cases

The disabled stub returning NULL is treated as "no RGB output"; callers must distinguish NULL from `ERR_PTR` in enabled builds. Include ordering must provide type declarations.

## Test Signals

Build with `CONFIG_ROCKCHIP_RGB=y` and disabled. Runtime tests should confirm VOP/VOP2 tolerate NULL stubs and properly bind/fini real RGB helpers when enabled.
