# sources/distributed-fs/ceph-client/include/drm/drm_fbdev_ttm.h

Purpose: Provides the fbdev-emulation probe hook macro for drivers using TTM-managed backing storage.

Important APIs, types, and functions: With `CONFIG_DRM_FBDEV_EMULATION`, declares `drm_fbdev_ttm_driver_fbdev_probe()` and defines `DRM_FBDEV_TTM_DRIVER_OPS` to set `.fbdev_probe` accordingly. Without fbdev emulation, the macro sets `.fbdev_probe = NULL`.

Control flow: TTM-based drivers add this macro to the DRM driver ops. The fbdev helper invokes the probe callback to allocate a fbdev framebuffer through TTM-capable GEM/BO paths.

State and persistence: No header-owned state exists. Runtime state is in fb helper structures and TTM/GEM buffer objects.

Dependencies and integration points: Depends on fb helper surface sizing and TTM-backed framebuffer allocation. It integrates with `struct drm_driver.fbdev_probe`, Kconfig, and TTM GEM helpers.

Risks and test signals: Risks include missing fbdev support in Kconfig-off builds, BO placement/mapping failures during console setup, and eviction/pinning conflicts while fbdev is scanning out. Test fbcon boot, suspend/resume, memory pressure eviction behavior, hotplug resize, and fbdev teardown in TTM drivers.
