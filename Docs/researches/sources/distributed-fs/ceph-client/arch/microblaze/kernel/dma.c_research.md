# sources/distributed-fs/ceph-client/arch/microblaze/kernel/dma.c

Purpose: supplies architecture DMA synchronization hooks for directly mapped non-coherent buses.

Important APIs and state: `arch_sync_dma_for_device()` and `arch_sync_dma_for_cpu()` call private `__dma_sync()`. For `DMA_TO_DEVICE` and `DMA_BIDIRECTIONAL`, it flushes dcache over the physical range; for `DMA_FROM_DEVICE`, it invalidates dcache; invalid directions BUG.

Control flow: both CPU and device sync paths share the same operation, assuming explicit cache maintenance is sufficient and physical addresses are accepted by the cacheflush implementation.

State and persistence: no persistent state. Effects are cache-hardware side effects over the requested DMA range.

Dependencies and integration: used by generic DMA mapping code. Depends on `flush_dcache_range()` and `invalidate_dcache_range()` being configured for the current cache policy.

Risks and test signals: wrong direction loses CPU or device writes. Empty or unaligned ranges depend on cache.c range alignment. Test streaming DMA in both directions and coherent versus non-coherent device paths.
