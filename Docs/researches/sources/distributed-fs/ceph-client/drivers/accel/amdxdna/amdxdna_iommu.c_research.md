# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_iommu.c

Purpose: provides optional forced-IOVA mapping for AMD XDNA BOs and driver allocations when SVA/PASID is not used or when the `force_iova` module parameter is enabled.

Important APIs/functions: `amdxdna_iommu_init()` obtains the IOMMU group, and if `force_iova` is set, allocates a paging domain with PASID-capable flags, initializes the IOVA domain, and attaches the group. `amdxdna_iommu_map_bo()` maps shmem/dev-heap BO sg-tables into an allocated IOVA and records `mem.dma_addr`. `amdxdna_iommu_unmap_bo()` unmaps and frees the IOVA. `amdxdna_iommu_alloc()` and `amdxdna_iommu_free()` allocate page-backed coherent-ish driver memory and map/unmap it into the IOMMU domain.

Control flow: probe calls init before hardware startup; GEM open/free map and unmap BOs when IOVA mode is active; message-buffer allocation can use the alloc/free helpers.

State and persistence: `amdxdna_dev` stores `group`, `domain`, and `iovad`; each mapped BO stores its DMA/IOVA address. State is runtime only and released at remove.

Dependencies: Linux IOMMU, IOVA allocator, DRM shmem sg-tables, and AMD XDNA GEM types.

Risks: map failure after partial `iommu_map_sgtable()` must free the allocated IOVA. Only BO types `AMDXDNA_BO_DEV_HEAP` and `AMDXDNA_BO_SHMEM` are mapped here; type mismatches can leave unexpected physical addressing. `__get_free_pages()` allocation order can fail for large sizes.

Test signals: `force_iova=0/1`, domain allocation failure, sg-table absence, map partial failure, BO open/free mapping lifecycle, and message-buffer allocation/free under IOVA mode.
