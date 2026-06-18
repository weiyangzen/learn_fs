# sources/distributed-fs/ceph-client/arch/arm/mm/cache-v4wb.S

Purpose: implements ARMv4 write-back data-cache maintenance for StrongARM SA110/SA1100-style processors, including whole-cache cleaning via the `FLUSH_BASE` alias trick and DMA coherency routines.

Important APIs/types/functions: exports `v4wb_flush_icache_all`, `v4wb_flush_user_cache_all`, `v4wb_flush_kern_cache_all`, `v4wb_flush_user_cache_range`, `v4wb_flush_kern_dcache_area`, `v4wb_coherent_kern_range`, `v4wb_coherent_user_range`, `v4wb_dma_flush_range`, `v4wb_dma_map_area`, and `v4wb_dma_unmap_area`; internal labels include `flush_base`, `__flush_whole_cache`, `v4wb_dma_inv_range`, and `v4wb_dma_clean_range`.

Control flow: whole-cache flush toggles `flush_base`, reads through a cache-sized region to force dirty eviction, optionally handles mini-cache, then drains the write buffer. Range flushing cleans and invalidates line by line unless the range exceeds `CACHE_DLIMIT`. Coherency paths clean/invalidate D lines, invalidate I-cache, and drain write buffer. DMA map chooses clean/invalidate/flush by direction; unmap is a no-op.

State and persistence: `flush_base` is a small writable data word tracking the alias base used for whole-cache flushes. Hardware cache and write-buffer state are modified directly by CP15 operations.

Dependencies and integration points: selected by `CPU_CACHE_V4WB`, used by SA110/SA1100 and v4 write-back configurations. Depends on `FLUSH_BASE`, optional `FLUSH_BASE_MINICACHE`, CP15 line operations, and DMA direction constants.

Risks: cache size is compile-time selected for SA110 vs SA1100; wrong selection causes incomplete or wasteful flushes. Partial-line DMA invalidation must clean endpoints to avoid losing dirty unrelated data. The whole-cache alias method depends on correct platform mapping of `FLUSH_BASE`.

Test signals: SA110 and SA1100 build/boot tests, DMA direction tests with unaligned buffers, mini-cache configurations if present, executable mapping coherency tests, and stress around ranges just below/above `CACHE_DLIMIT`.
