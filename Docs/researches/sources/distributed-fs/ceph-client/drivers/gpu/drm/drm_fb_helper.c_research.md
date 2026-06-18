# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_fb_helper.c

## Purpose
`drm_fb_helper.c` implements the DRM fbdev emulation core. It bridges Linux fbdev operations to DRM client modesets, manages `fb_info` lifecycle, tracks dirty rectangles, handles suspend/resume and hotplug reprobe, and translates fbdev colormap, panning, blanking, and screeninfo requests into DRM behavior.

## Important APIs, Types, And Functions
Major exported entry points include `drm_fb_helper_prepare()`, `drm_fb_helper_init()`, `drm_fb_helper_initial_config()`, `drm_fb_helper_hotplug_event()`, `drm_fb_helper_fini()`, `drm_fb_helper_fill_info()`, `drm_fb_helper_blank()`, `drm_fb_helper_check_var()`, `drm_fb_helper_set_par()`, `drm_fb_helper_pan_display()`, `drm_fb_helper_setcmap()`, `drm_fb_helper_ioctl()`, `drm_fb_helper_damage_range()`, `drm_fb_helper_damage_area()`, `drm_fb_helper_deferred_io()`, suspend helpers, and `drm_fb_helper_gem_is_fb()`. Core state lives in `struct drm_fb_helper`, `struct drm_client_dev`, `struct fb_info`, `struct drm_mode_set`, `struct drm_clip_rect`, `struct fb_cmap`, and `struct drm_fb_helper_surface_size`.

## Control Flow
Initialization starts with `drm_fb_helper_prepare()`, which initializes locks, work items, damage state, callbacks, and preferred bpp. `drm_fb_helper_initial_config()` probes DRM client modesets, allocates `fb_info`, asks the driver `fbdev_probe` callback to allocate backing storage, attaches the framebuffer to modesets, fills fbdev metadata, registers the framebuffer, and records deferred setup if no CRTC sizing is available. Hotplug events either finish deferred setup or reprobe connectors and commit fbdev modes. fbdev write paths accumulate damage and schedule `damage_work`, which waits for vblank, snapshots the accumulated clip, calls the driver's `fb_dirty` hook, and restores damage on failure.

## State, Persistence, And Dependencies
Persistent in-kernel state includes `dev->fb_helper`, `fb_helper->info`, `fb_helper->fb`, `fb_helper->buffer`, modeset lists in the DRM client, work items, `damage_clip`, `deferred_setup`, `delayed_hotplug`, and `fbdefio`. Module parameters control fbdev emulation, over-allocation, and optional physical smem address leakage. The file depends on fbdev core, DRM client modeset helpers, atomic and legacy modeset paths, CRTC gamma APIs, DRM format metadata, DRM master arbitration, console locking, and workqueue execution.

## Integration Points
Memory-manager-specific helpers such as DMA, SHMEM, and TTM call into this file to fill `fb_info`, route deferred I/O damage, and use standard fb_ops callbacks. DRM drivers expose `drm_driver.fbdev_probe`, mode_config callbacks, primary-plane format lists, and CRTC/connector state. fbcon and legacy fbdev users interact through `fb_ops`, while KMS compositors interact indirectly when fbdev restore occurs after master release.

## Risks
The main risks are locking and lifecycle ordering: `register_framebuffer()` requires dropping helper locks, hotplug can arrive before initial config, and suspend/resume must coordinate console lock and damage work. Dirty handling intentionally avoids scheduling during oops paths. Colormap support must choose between pseudo-palette, legacy gamma, and atomic gamma LUT paths without leaking blobs or mishandling `-EDEADLK`. The helper rejects pixel-format changes, so fbdev users that expect mutable fb_var fields must be handled through compatibility workarounds only.

## Test Signals
High-value tests include initial config with no connectors then hotplug, fbdev over-allocation clamping, damage aggregation from writes and deferred mmap pages, suspend/resume with pending damage, `FBIO_WAITFORVSYNC`, panning on atomic and legacy devices, colormap updates for truecolor and indexed visuals, SDL-style zeroed pixel fields, big and small bpp formats including C1/C2/C4, and forced restore on KD_TEXT transitions.
