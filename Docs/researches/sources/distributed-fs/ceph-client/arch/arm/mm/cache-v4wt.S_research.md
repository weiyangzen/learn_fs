# sources/distributed-fs/ceph-client/arch/arm/mm/cache-v4wt.S

Purpose: implements ARMv4 write-through cache maintenance for CPUs such as ARM920T/922T/925T/1020-style configurations, assuming the write buffer is not enabled.

Important APIs/types/functions: exports `v4wt_flush_icache_all`, `v4wt_flush_user_cache_all`, `v4wt_flush_kern_cache_all`, `v4wt_flush_user_cache_range`, `v4wt_coherent_kern_range`, `v4wt_coherent_user_range`, `v4wt_flush_kern_dcache_area`, `v4wt_dma_flush_range`, `v4wt_dma_unmap_area`, and `v4wt_dma_map_area`; internal label `v4wt_dma_inv_range` performs line invalidation.

Control flow: whole-cache paths invalidate I-cache when executable and invalidate D-cache. Range paths either switch to whole-cache operation or iterate line by line invalidating D-cache and optionally I-cache. Coherency invalidates I-cache lines. DMA map is a no-op; unmap invalidates for non-`DMA_TO_DEVICE`; flush aliases to invalidate because data is write-through.

State and persistence: no software state. CP15 operations mutate cache state.

Dependencies and integration points: selected by `CPU_CACHE_V4WT`. Integrated through ARM cache function tables and DMA mapping code.

Risks: comments assume no write buffer, which is essential for treating flush as invalidate. If hardware has dirty buffered data, this implementation could lose coherency. Whole-cache threshold is marked as needing benchmarking.

Test signals: boot write-through v4 CPUs, DMA tests for all directions with unaligned buffers, executable mapping coherency tests, and validation that write-buffer assumptions hold for selected CPU configurations.
