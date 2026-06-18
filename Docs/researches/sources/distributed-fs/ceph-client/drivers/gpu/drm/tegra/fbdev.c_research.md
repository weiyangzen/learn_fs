# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/fbdev.c

Purpose: implements fbdev emulation probing and mmap support for Tegra DRM.

Important APIs/functions: `tegra_fb_mmap()` maps the first framebuffer plane through DRM GEM mmap and Tegra GEM mmap handling. `tegra_fbdev_fb_destroy()` tears down the helper, undoes the fbdev-specific `vmap()` for page-backed BOs, removes the framebuffer, and releases the DRM client. `tegra_fbdev_driver_fbdev_probe()` creates a dumb GEM BO sized from requested fbdev surface dimensions, allocates a Tegra framebuffer, fills fbdev info, maps backing pages if needed, and sets screen buffer/size/fixed memory information.

Control flow and state: the helper creates a single-plane framebuffer. For IOMMU/page-backed BOs it installs a kernel virtual mapping into `bo->vaddr` only for fbdev and later clears it during destroy. DMA-API BOs already have a persistent CPU mapping.

Dependencies/integration: relies on DRM fb helper infrastructure, Tegra `tegra_bo_create()`, `tegra_fb_alloc()`, and `__tegra_gem_mmap()`.

Risks: the special `bo->vaddr` assignment for page-backed fbdev objects must stay paired with destroy-time `vunmap()` or BO mapping semantics can be confused. Error handling after a failed `vmap()` removes the framebuffer but relies on DRM/GEM references to unwind the BO.

Test signals: boot console/fbdev handoff, fbdev mmap read/write, forced IOMMU and non-IOMMU configurations, and unload/reload leak checks are useful.
