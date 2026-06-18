# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_gem.c

Purpose: Implements OMAPDRM GEM buffer objects, covering allocation, mmap fault handling, DMM/TILER remapping, PRIME export/import backing, page pinning, cache synchronization, debugfs description, and init/deinit of the user-GART used for tiled userspace mappings.

Important APIs/types/functions: `struct omap_gem_object` extends `drm_gem_object` with flags, dimensions, roll offset, lock, DMA address, pin count, sg table, TILER block, page array, DMA page addresses, and kernel vaddr. Internal user-GART types hold small page-aligned TILER blocks for faulting tiled buffers into CPU mappings. Public functions include `omap_gem_new`, `omap_gem_new_dmabuf`, `omap_gem_new_handle`, `omap_gem_dumb_create`, `omap_gem_dumb_map_offset`, `omap_gem_pin`, `omap_gem_unpin`, `omap_gem_get_sg`, `omap_gem_put_sg`, `omap_gem_mmap_offset`, `omap_gem_mmap_size`, `omap_gem_flags`, tiled address helpers, PM resume, and debugfs describe helpers.

Control flow: Object construction validates cache/tiled flags, chooses shmem, contiguous DMA, or imported dmabuf backing, aligns tiled dimensions, initializes GEM, optionally allocates DMA write-combined memory, and adds the object to `priv->obj_list`. Fault handling attaches shmem pages, then maps either direct PFNs for linear objects or pins a temporary user-GART entry for tiled objects. Pinning detects non-contiguous buffers and, for scanout with DMM, reserves and pins a TILER block to create a contiguous DMA aperture. SG export pins first, synchronizes dirty cached pages for DMA, then builds either one/tiled-row scatterlist entries from the aperture or page-sized entries from shmem pages.

State and persistence: State is in memory only: object lists, per-object mutex-protected page/DMA/pin/TILER state, and `priv->usergart`. Cached shmem coherence is tracked with `dma_addrs[i] == 0` meaning CPU-visible dirty page and nonzero meaning DMA-mapped. PM resume repins existing TILER blocks.

Dependencies and integration: Depends on DRM GEM, VMA manager, shmem, DMA mapping, PRIME, TILER/DMM helpers, `omap_drm_private`, and framebuffer/plane users that pin scanout buffers. `omap_gem_object_funcs` wires free/export/mmap/vm_ops into DRM core.

Risks: Pin error path sets `pin_cnt` before page/TILER failures and relies on later cleanup; tiled mmap uses a fixed two-entry user-GART and stack `pages[64]`; non-coherent cache management invalidates mappings and is sensitive to missed `omap_gem_dma_sync_buffer`; imported non-contiguous dmabufs require DMM; object destruction warns but cannot recover from leaked pins.

Test signals: Exercise dumb buffer create/map/mmap, PRIME export/import of contiguous and non-contiguous buffers, scanout with and without DMM, tiled mmap page faults, fbdev roll, suspend/resume with pinned TILER blocks, debugfs object listing, and error injection for DMA map/TILER reserve failures.
