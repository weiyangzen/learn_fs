# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_fbdev.c

Purpose: this file provides fbdev emulation support for Exynos DRM by allocating a GEM-backed framebuffer and filling Linux `fb_info` fields for legacy framebuffer users.

Important APIs: `exynos_drm_fbdev_driver_fbdev_probe()` is the DRM fbdev driver callback. `exynos_drm_fb_mmap()` maps the fbdev framebuffer through GEM PRIME mmap. `exynos_drm_fb_destroy()` tears down the fb helper, removes the framebuffer, and releases the DRM client. `exynos_drm_fbdev_update()` fills fbdev metadata and points `screen_buffer` at the GEM kernel virtual address.

Control flow: when DRM fbdev setup asks for a surface, the probe computes pitch, pixel format, and allocation size from the requested surface size. It allocates a write-combined GEM with `kvmap=true`, creates a one-plane Exynos framebuffer around it, attaches helper funcs, and updates the `fb_info`. Errors unwind by cleaning the framebuffer or destroying the GEM.

State and persistence: fbdev state lives in `drm_fb_helper`, `fb_info`, the GEM object, and the DRM framebuffer. No persistent storage is used.

Dependencies and integration points: it depends on Linux fbdev APIs, DRM fb helper, GEM framebuffer helper, PRIME mmap, Exynos GEM, and Exynos framebuffer helpers. It is inserted into `struct drm_driver` through `EXYNOS_DRM_FBDEV_DRIVER_OPS`.

Risks: fbdev requires a kernel mapping, so GEM allocation must pass `kvmap=true`; failure would make `screen_buffer` invalid. `screen_size` is based on width, height, and cpp rather than pitch times virtual height, so unusual padding should be checked. Destroy order matters because fb helper, framebuffer, and DRM client references overlap.

Test signals: boot console/fbcon, mmap of `/dev/fb*`, fbdev teardown during driver unload, allocation failures, and legacy writes/draw ops on different bpp/depth combinations.
