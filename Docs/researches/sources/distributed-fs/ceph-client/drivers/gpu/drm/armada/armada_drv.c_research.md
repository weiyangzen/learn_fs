# sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_drv.c

## Purpose

`armada_drv.c` is the Armada DRM master platform driver. It registers DRM ioctls, allocates the master DRM device, initializes mode-config and linear graphics-memory management, binds LCD CRTC components, initializes vblank/polling/debugfs/client setup, and registers both master and LCD platform drivers at module init.

## Important APIs, Types, And Functions

Key objects are `armada_ioctls`, `armada_drm_driver`, `armada_drm_mode_config_funcs`, `armada_master_ops`, `armada_drm_platform_driver`, and module init/exit functions. Important functions include `armada_drm_bind()`, `armada_drm_unbind()`, `armada_add_endpoints()`, `armada_drm_probe()`, `armada_drm_remove()`, and `armada_drm_shutdown()`.

## Control Flow

Module init first checks `drm_firmware_drivers_only()`, then registers the LCD platform driver and the master DRM platform driver. Master probe prefers `drm_of_component_probe()` and falls back to platform-data component matching plus endpoint matching. Bind scans platform memory resources, expecting resources above 64 KiB to be graphics memory and smaller resources to be invalid for the master, reserves the memory region, allocates `struct armada_private`, removes conflicting aperture devices, initializes mode-config limits, initializes the `drm_mm` linear allocator, binds components, initializes vblank, resets mode config, starts polling, registers the DRM device, initializes debugfs, and starts DRM client setup. Unbind reverses polling, unregister, atomic shutdown, component unbind, mode-config cleanup, allocator teardown, and drvdata clearing.

## State And Persistence Behavior

Persistent master state is `struct armada_private`, especially the DRM device, CRTC pointers, and linear allocator over the graphics memory resource. Userspace-visible ioctls include GEM create, mmap, and pwrite. The platform drivers remain registered until module exit.

## Dependencies And Integration Points

This file integrates Linux platform/component/OF graph infrastructure, aperture removal, DRM core/ioctls/PRIME helpers, Armada GEM/fb/CRTC/overlay code, and fbdev/debugfs optional paths. It binds child LCD components provided by `armada_crtc.c`.

## Risks And Edge Cases

Memory resource scanning treats any resource <=64 KiB as an error in the master path, so DT/platform resource ordering matters. Component matching has OF and legacy platform-data paths. Error unwinding must clean mode-config and `drm_mm` only after initialization. Debugfs init is called after `drm_dev_register()` using the primary minor. The driver exposes custom ioctls, so ABI compatibility matters.

## Test Signals

Tests include module load/unload, OF component probe and legacy platform-data probe, graphics-memory resource validation, aperture takeover, one/two LCD component binding, vblank init, DRM ioctl smoke tests, dumb-buffer creation, debugfs creation, fbdev client setup, shutdown behavior, and error injection for component bind/register failures.
