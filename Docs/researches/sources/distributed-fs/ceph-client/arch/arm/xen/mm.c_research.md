## sources/distributed-fs/ceph-client/arch/arm/xen/mm.c

### Purpose
Handles ARM Xen DMA/cache coherency decisions, Xen SWIOTLB initialization, and grant-table cache flush hypercall support.

### Important APIs, Types, And Functions
Key functions are `xen_swiotlb_gfp`, `dma_cache_maint`, `xen_dma_sync_for_cpu`, `xen_dma_sync_for_device`, `xen_arch_need_swiotlb`, and `xen_mm_init`. State includes `hypercall_cflush`.

### Control Flow
Init detects Xen SWIOTLB need, allocates late SWIOTLB memory with DMA-capable GFP flags, probes `GNTTABOP_cache_flush`, and records availability. DMA sync functions translate DMA handles to physical addresses and issue cache flush hypercalls page by page. `xen_arch_need_swiotlb()` requests bounce buffering when cache-flush hypercalls are unavailable, memory is foreign, and the device is noncoherent.

### State, Persistence, And Dependencies
Persistent state is SWIOTLB allocation and the `hypercall_cflush` capability flag. Dependencies include DMA mapping APIs, memblock ranges, Xen grant-table hypercalls, `xen_swiotlb_detect`, and device coherency attributes.

### Integration Points
Used by generic Xen SWIOTLB and DMA paths so ARM guests can safely DMA to local or foreign memory.

### Risks
Cache maintenance on foreign/highmem pages is correctness-critical for noncoherent devices. Incorrect bounce-buffer decisions can cause data corruption. Page-boundary handling must match Xen page size.

### Test Signals
Run Xen guest network/block DMA under coherent and noncoherent device models, test foreign grant mappings, and verify cache flush hypercall fallback behavior.
