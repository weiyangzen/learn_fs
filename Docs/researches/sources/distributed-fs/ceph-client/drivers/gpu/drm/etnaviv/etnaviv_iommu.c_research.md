## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_iommu.c

### Purpose
`etnaviv_iommu.c` implements MMUv1 context allocation and page-table operations for older Vivante GPUs. MMUv1 uses a single shared GPU address context because the hardware cannot switch contexts without a stop-the-world operation.

### Important APIs, Types, And Functions
The private `struct etnaviv_iommuv1_context` embeds `struct etnaviv_iommu_context` and owns a 2 MiB write-combined page table. The exported ops table `etnaviv_iommuv1_ops` supplies `.free`, `.map`, `.unmap`, `.dump_size`, `.dump`, and `.restore`. `etnaviv_iommuv1_context_alloc()` creates or references the shared context.

### Control Flow
Allocation is serialized under `global->lock`. If a shared context already exists, it returns a new kref. Otherwise it allocates the context, allocates the page table, fills all entries with the global bad-page DMA address, initializes `drm_mm` from `GPU_MEM_START` over the 2 MiB page-table aperture, and stores the shared context. Map/unmap accept only 4 KiB pages and write physical or bad-page addresses into the indexed page-table slot. Restore programs memory-base and page-table registers for FE, TX, PE, PEZ, and RA.

### State, Persistence, And Dependencies
State persists in the shared context page table, `drm_mm`, mapping list, global bad page, and `global->v1.shared_context`. Dependencies include DMA write-combined allocation, DRM memory manager, generated HI/MC register definitions, and GPU MMIO helpers.

### Integration Points
Generic MMU code in `etnaviv_mmu.c` invokes these ops. GPU initialization selects MMUv1 unless identity advertises MMUv2. Submit and command-buffer mapping code see a normal `etnaviv_iommu_context` even though MMUv1 is shared.

### Risks
Shared context semantics mean isolation is weaker than MMUv2 and stale mappings affect all clients. Only 4 KiB operations are supported. Address indexing assumes IOVAs are inside the `GPU_MEM_START` aperture. Restore must program every relevant MC page-table register or a pipeline can see inconsistent memory.

### Test Signals
Signals include shared-context refcount reuse, map/unmap of single pages, dump size/content, bad-page fill after unmap, command buffer below MMUv1 limits, and context restore on hardware with FE/TX/PE/RA memory access.
