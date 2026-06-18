# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_fbdev.h

Purpose: this header conditionally exposes fbdev emulation support to the top-level Exynos DRM driver.

Important APIs: when `CONFIG_DRM_FBDEV_EMULATION` is enabled it declares `exynos_drm_fbdev_driver_fbdev_probe()` and defines `EXYNOS_DRM_FBDEV_DRIVER_OPS` as `.fbdev_probe = exynos_drm_fbdev_driver_fbdev_probe`. When disabled, the macro expands to `.fbdev_probe = NULL`.

Control flow and integration: `exynos_drm_drv.c` includes this macro in `struct drm_driver`, making fbdev support a compile-time feature without changing driver initialization logic.

State and persistence: none.

Dependencies: it forward-declares `struct drm_fb_helper` and `struct drm_fb_helper_surface_size` to avoid pulling fbdev headers into every user.

Risks: disabled builds must still compile all top-level driver code. Enabled builds depend on the C implementation and GEM/fb helpers being included.

Test signals: Kconfig builds with fbdev emulation enabled and disabled, plus runtime fbdev probe in enabled builds.
