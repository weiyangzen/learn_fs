# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_gem.c

Purpose: this file implements Exynos GEM buffer allocation, handle creation, mmap, dumb buffers, and PRIME import/export helpers.

Important APIs: `exynos_drm_gem_create()` validates flags and size, initializes a GEM object, adjusts noncontiguous requests when no IOMMU exists, and allocates DMA memory. `exynos_drm_gem_create_ioctl()`, `exynos_drm_gem_map_ioctl()`, and `exynos_drm_gem_get_ioctl()` are userspace IOCTL handlers. `exynos_drm_gem_get()` looks up a GEM handle and returns an Exynos GEM wrapper with a reference. `exynos_drm_gem_dumb_create()` backs DRM dumb buffers. PRIME helpers are `exynos_drm_gem_prime_import()`, `exynos_drm_gem_prime_get_sg_table()`, and `exynos_drm_gem_prime_import_sg_table()`.

Control flow: creation aligns the requested size to a page, initializes the DRM GEM object and mmap offset, then allocates DMA memory with attributes derived from Exynos BO flags. Contiguous allocations set `DMA_ATTR_FORCE_CONTIGUOUS`; write-combined or non-cacheable allocations set `DMA_ATTR_WRITE_COMBINE`; non-fbdev buffers skip kernel mapping. Handle creation gives userspace a handle and drops the allocation reference. Mmap routes imported dma-bufs to `dma_buf_mmap()` and local buffers to `dma_mmap_attrs()` after setting VM flags and page protection. Destruction frees exporter-owned imports through PRIME helpers or frees local DMA memory, releases GEM state, and kfrees the wrapper.

State and persistence: each GEM object stores flags, size, DMA cookie, optional kernel address, DMA address, DMA attrs, and optional imported sg table. No persistence beyond object lifetime exists.

Dependencies and integration points: depends on DMA-BUF namespace, DMA allocation/mmap APIs, DRM GEM/dumb/PRIME/VMA helpers, Exynos DMA device selection, and Exynos BO flag UAPI. Framebuffer, fbdev, IPP, and G2D code consume GEM DMA addresses and references.

Risks: no-IOMMU systems cannot honor noncontiguous allocations and silently drop that flag after warning. PRIME import requires a contiguous DMA mapping as checked by `drm_prime_get_contiguous_size()`. `to_dma_dev()` must be initialized by subdriver DMA registration before allocation. Cacheability flags must match userspace expectations to avoid coherency issues.

Test signals: GEM create/map/get IOCTLs, dumb create with and without IOMMU, fbdev kernel mapping, mmap protections for cacheable/WC/noncached buffers, PRIME import/export of contiguous and noncontiguous sg tables, destruction under handle/import references, and DMA allocation failures.
