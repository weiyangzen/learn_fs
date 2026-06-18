# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_fb.c

Purpose: this file implements Exynos framebuffer creation, validation, DMA-address lookup, and DRM mode-config setup.

Important APIs: `exynos_drm_framebuffer_init()` builds a `drm_framebuffer` from Exynos GEM objects and a `drm_mode_fb_cmd2`. `exynos_user_fb_create()` is the mode-config `.fb_create` hook and validates userspace handles, plane sizes, and offsets. `exynos_drm_fb_dma_addr()` returns the DMA address for a framebuffer plane plus its offset. `exynos_drm_mode_config_init()` sets global Exynos mode-config limits and atomic callbacks.

Control flow: userspace `ADDFB2` reaches `exynos_user_fb_create()`, which looks up each GEM handle through `exynos_drm_gem_get()`, computes minimum required size from height, pitch, and offset, and then delegates to `exynos_drm_framebuffer_init()`. The initializer rejects non-contiguous GEM buffers when no IOMMU mapping exists, fills the DRM fb structure, and registers it with `drm_framebuffer_init()`. Plane update paths such as FIMD call `exynos_drm_fb_dma_addr()` to program scanout addresses.

State and persistence: no file-static mutable state. Framebuffer state is held by DRM's framebuffer object and its `fb->obj[]` references. The mode config stores min/max dimensions, callback pointers, and normalized z-position behavior.

Dependencies and integration points: it depends on DRM atomic helpers, GEM framebuffer helpers, Exynos GEM, CRTC, fbdev, and driver-private IOMMU helpers. FIMD and other display controllers consume the DMA-address helper.

Risks: size validation relies on integer arithmetic over pitch, offset, and height; unusual large values need DRM core bounds to prevent overflow. Without IOMMU, non-contiguous buffers are explicitly rejected for scanout. `exynos_drm_fb_dma_addr()` returns 0 on out-of-range index after a warning, which would be a bad hardware address if callers ignored invalid index logic.

Test signals: addfb with single and multiplanar formats, invalid handles, undersized GEMs, noncontiguous GEMs with and without IOMMU, framebuffer destruction, dumb-buffer scanout, and atomic commits using `drm_atomic_helper_commit_tail_rpm`.
