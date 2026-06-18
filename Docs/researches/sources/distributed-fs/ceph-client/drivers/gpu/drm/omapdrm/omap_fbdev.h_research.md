# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_fbdev.h

Purpose: Declares and conditionally compiles the OMAP DRM fbdev emulation entry points.

Important APIs/functions: When `CONFIG_DRM_FBDEV_EMULATION` is enabled, it declares `omap_fbdev_driver_fbdev_probe()` and `omap_fbdev_setup()` and defines `OMAP_FBDEV_DRIVER_OPS` to populate `.fbdev_probe`. When disabled, the macro sets `.fbdev_probe = NULL` and `omap_fbdev_setup()` is an inline no-op.

Control flow: `omap_drv.c` includes this header to wire driver ops and to call fbdev setup after DRM registration.

State and persistence: No state is stored here; it gates fbdev state allocation in `omap_fbdev.c`.

Dependencies/integration: Forward-declares DRM device/fb helper/surface size types and integrates with DRM driver ops.

Risks and test signals: Conditional compilation must keep the main driver valid with fbdev enabled or disabled. Build both configurations and verify DRM registration succeeds without fbdev.
