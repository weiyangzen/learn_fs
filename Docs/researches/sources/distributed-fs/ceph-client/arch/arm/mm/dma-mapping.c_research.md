## sources/distributed-fs/ceph-client/arch/arm/mm/dma-mapping.c

### Purpose
Provides ARM MMU DMA allocation, cache maintenance, contiguous/CMA remapping, atomic coherent pools, and optional IOMMU-backed DMA map ops.

### Important APIs, Types, And Functions
Important types are `arm_dma_alloc_args`, `arm_dma_free_args`, `arm_dma_allocator`, and `arm_dma_buffer`. Allocation paths include `__dma_alloc`, `__arm_dma_free`, `__alloc_simple_buffer`, `__alloc_from_contiguous`, `__alloc_remap_buffer`, `__alloc_from_pool`, and their free counterparts. Cache hooks are `arch_sync_dma_for_device` and `arch_sync_dma_for_cpu`. IOMMU support includes `arm_iommu_create_mapping`, `arm_iommu_attach_device`, `arm_iommu_detach_device`, `arm_iommu_alloc_attrs`, SG/page map/unmap/sync helpers, and `iommu_ops`. Setup hooks are `arch_setup_dma_ops`, `arch_teardown_dma_ops`, `arch_dma_alloc`, and `arch_dma_free`.

### Control Flow
Boot builds `atomic_pool` after CMA is ready and may remap reserved CMA lowmem as `MT_MEMORY_DMA_READY`. `__dma_alloc` chooses CMA, coherent simple, remapped noncoherent, or atomic pool allocation based on blocking context, device coherency, CMA availability, and `DMA_ATTR_NO_KERNEL_MAPPING`; it records the allocator in `arm_dma_bufs` so free can dispatch correctly. Streaming sync walks physical/highmem pages and runs inner plus outer cache maintenance. IOMMU paths allocate IOVA bitmap ranges, allocate pages, map contiguous PFN runs or SG chunks into an IOMMU domain, and unmap/free on release.

### State, Dependencies, And Integration
Persistent state includes `arm_dma_bufs`, `atomic_pool`, early CMA remap records, and per-device `dma_iommu_mapping` bitmaps/domains. Depends on genalloc, CMA, memblock, vmap, outer cache, cache-vector `dmac_*` calls, generic DMA/IOMMU APIs, Xen DMA setup, and `mmu.c` mapping types.

### Risks And Test Signals
Risks are allocator/free mismatches, atomic pool exhaustion, stale highmem cache lines, outer-cache ordering errors, wrong page attributes for coherent mappings, IOVA leaks/bitmap extension bugs, and SG merging mistakes. Test DMA API debug, noncoherent devices, highmem DMA, CMA/no-CMA boots, atomic GFP_ATOMIC allocations, IOMMU attach/detach, SG map/unmap under failures, and cache-coherency hardware tests.
