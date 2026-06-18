# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_gem.h

Purpose: this header defines the Exynos GEM object wrapper and declares buffer-management APIs used across the driver.

Important types and APIs: `struct exynos_drm_gem` embeds `drm_gem_object` and stores Exynos BO flags, page-aligned size, DMA cookie, optional `kvaddr`, DMA address, DMA attributes, and imported `sg_table`. `to_exynos_gem()` converts from base GEM object. `IS_NONCONTIG_BUFFER()` checks the Exynos noncontiguous flag. The header declares creation/destruction, IOCTL handlers, handle lookup/put, dumb-create, and PRIME helper functions.

Control flow and integration: framebuffer creation, fbdev allocation, IPP buffer setup, and G2D command-list mapping all use this type to resolve userspace handles to DMA addresses. The top-level DRM driver points GEM and dumb-buffer hooks at the declared functions.

State and persistence: the header describes object state; the actual state persists for the lifetime of each GEM object and referenced dma-buf.

Dependencies: requires DRM GEM types and Linux mm types. It also assumes Exynos BO UAPI definitions are visible through including C files.

Risks: all consumers must call `exynos_drm_gem_put()` after successful `exynos_drm_gem_get()`. Imported buffers may not have local allocation cookies and must be destroyed through PRIME import handling.

Test signals: refcount balance in fb, IPP, and G2D paths; compile coverage; and PRIME/dumb/GEM IOCTL behavior.
