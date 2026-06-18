# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/gem.c

Purpose: implements Tegra GEM buffer objects, host1x BO operations, mmap, IOMMU mapping, dumb buffer allocation, and PRIME dma-buf import/export.

Important APIs/functions: `tegra_bo_create()` and `tegra_bo_create_with_handle()` allocate GEM objects and backing memory. `tegra_bo_pin()/unpin()` bridge GEM BOs to host1x mappings for submit/display users, handling imported dma-bufs, page-backed IOMMU BOs, and DMA-API BOs. `tegra_bo_iommu_map()/unmap()` allocate DRM MM IOVA space and map sg tables into the Tegra domain. `tegra_bo_free_object()` removes cached host1x mappings, unmaps imports, releases backing memory, and drops dma-bufs. `tegra_drm_mmap()` and `__tegra_gem_mmap()` implement userspace mapping for page-backed and DMA coherent/write-combined objects. PRIME functions expose and import dma-bufs with CPU sync and vmap/mmap support.

Control flow and state: BO state distinguishes allocated-via-DMA (`vaddr/iova`), allocated-via-IOMMU (`pages/sgt/mm/iova/size`), imported-via-DMA (`dma_buf`), and imported-via-IOMMU (`gem.import_attach/sgt/mm`). Host1x mapping state is transient and reference-counted by host1x core.

Dependencies/integration: integrates DRM GEM, DMA API, dma-buf, IOMMU, DRM MM allocator, host1x BO APIs, and Tegra DRM global `tegra->domain/mm/mm_lock`.

Risks: cleanup paths are complex and must match allocation mode exactly. Imported IOMMU buffers are attached/mapped early, and errors must detach/unmap in the right order. Display users require contiguous mappings when no shared IOMMU group is present. CPU cache sync only runs for page-backed BOs.

Test signals: dumb buffer creation/mmap, PRIME self-import and foreign import/export, host1x pin/unpin with scatter-gather fragmentation, IOMMU exhaustion, module unload with stale mappings, and DMA-buf CPU access tests are key.
