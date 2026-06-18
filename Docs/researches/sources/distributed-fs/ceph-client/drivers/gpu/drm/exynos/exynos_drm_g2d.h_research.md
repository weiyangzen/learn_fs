# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_g2d.h

Purpose: this header exposes the G2D IOCTL handlers and per-file open/close hooks to the top-level Exynos DRM driver, with stubs for builds without G2D.

Important APIs: when `CONFIG_DRM_EXYNOS_G2D` is enabled it declares `exynos_g2d_get_ver_ioctl()`, `exynos_g2d_set_cmdlist_ioctl()`, `exynos_g2d_exec_ioctl()`, `g2d_open()`, and `g2d_close()`. When disabled, IOCTL handlers return `-ENODEV`, `g2d_open()` returns success, and `g2d_close()` is a no-op.

Control flow and integration: `exynos_drm_drv.c` includes the IOCTL declarations in its `exynos_ioctls[]` table and calls `g2d_open()` / `g2d_close()` during DRM file open/postclose. The stub design lets the top-level file lifecycle stay uniform across Kconfig variants.

State and persistence: none in the header. Enabled builds cause per-file G2D list state to be initialized in the C implementation.

Dependencies: only DRM device/file types are required from the including context.

Risks: disabled builds expose IOCTL numbers but return `-ENODEV`; userspace must handle that. Enabled builds require `file->driver_priv` to be initialized before `g2d_open()` is called.

Test signals: Kconfig enabled/disabled builds, G2D IOCTL unavailable behavior, and file open/close with G2D disabled.
