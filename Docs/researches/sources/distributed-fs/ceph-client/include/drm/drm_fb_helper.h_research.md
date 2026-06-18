# sources/distributed-fs/ceph-client/include/drm/drm_fb_helper.h

Purpose: Defines the DRM fbdev emulation helper interface that maps KMS devices onto Linux fbdev/fbcon, including surface sizing, helper state, callback hooks, default fb_ops, mode restoration, damage flushing, hotplug handling, and suspend support.

Important APIs, types, and functions: Defines `struct drm_fb_helper_surface_size`, `struct drm_fb_helper_funcs`, `struct drm_fb_helper`, `drm_fb_helper_from_client()`, and `DRM_FB_HELPER_DEFAULT_OPS`. With `CONFIG_DRM_FBDEV_EMULATION`, declares prepare/init/fini/unprepare, fb_ops implementations, mode restore, unregister/fill info, damage range/area, deferred IO, suspend, cmap/ioctl, hotplug, initial config, and `drm_fb_helper_gem_is_fb()`. Without fbdev emulation, only a false `drm_fb_helper_gem_is_fb()` stub remains.

Control flow: Drivers prepare and initialize a helper, then probe fbdev through `drm_driver.fbdev_probe`. The helper chooses an initial KMS configuration, allocates or references a scanout framebuffer, fills `fb_info`, and services fbdev operations. Writes through fbdev accumulate damage and schedule work to flush. Hotplug may defer setup when no outputs exist or when another KMS master owns the device; mode restore reacquires fbdev control when appropriate. Suspend paths call driver-specific or generic fb suspend handling.

State and persistence: State is runtime: embedded DRM client, client buffer, framebuffer, `fb_info`, pseudo palette, damage clip/work, resume work, helper mutex, delayed hotplug/deferred setup flags, preferred bpp, and optional deferred IO state. It persists while fbdev emulation is registered and is torn down during driver unload or fbdev disable.

Dependencies and integration points: Depends on Linux fbdev, DRM client helpers, DRM framebuffers, fbcon, KMS mode setting, workqueues, deferred IO, GEM framebuffer detection, and driver `fbdev_probe`. It integrates with generic fbdev DMA/shmem/TTM wrappers and KMS hotplug/suspend paths.

Risks and test signals: Risks include console lock deadlocks on resume, damage coalescing races, stale fbdev modes after hotplug, deferred setup never retrying, mismatch between fbdev dimensions and scanout surface, incorrect pseudo-palette/cmap handling, and fbdev enabled when another master controls KMS. Test boot fbcon, no-monitor deferred setup, hotplug after boot, multi-display min/max sizing, fbdev writes and deferred IO, suspend/resume, KMS master handoff, cmap/ioctl paths, and teardown with fbcon active.
