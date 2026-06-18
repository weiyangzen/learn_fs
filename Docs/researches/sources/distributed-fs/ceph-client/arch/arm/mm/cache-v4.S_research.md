# sources/distributed-fs/ceph-client/arch/arm/mm/cache-v4.S

Purpose: provides baseline ARMv4 cache maintenance routines for simple or no-cache ARMv4 systems, with optional CP15 whole-cache flush support.

Important APIs/types/functions: exports `v4_flush_icache_all`, `v4_flush_user_cache_all` aliasing `v4_flush_kern_cache_all`, `v4_flush_kern_cache_all`, `v4_flush_user_cache_range`, `v4_coherent_kern_range`, `v4_coherent_user_range`, `v4_flush_kern_dcache_area`, `v4_dma_flush_range`, `v4_dma_unmap_area`, and `v4_dma_map_area`.

Control flow: many operations are no-ops unless `CONFIG_CPU_CP15` is enabled. CP15 paths use `mcr p15, 0, r0, c7, c7, 0` to flush ID cache. DMA unmap flushes for non-`DMA_TO_DEVICE`, while DMA map does nothing.

State and persistence: no software state. Hardware cache state is invalidated/flushed through CP15 when present.

Dependencies and integration points: selected by `CPU_CACHE_V4`, used by ARM7TDMI/ARM740T/ARM9TDMI and similar configurations through cache function tables.

Risks: this is intentionally coarse. Whole-cache operations may be overkill for range requests but safe for simple legacy caches. Selecting it for CPUs requiring line-level writeback or Harvard coherency would be incorrect.

Test signals: build no-CP15 and CP15 variants, run DMA map/unmap smoke tests, verify self-modifying code behavior on systems with I/D cache, and ensure no unsupported CP15 instructions execute on no-CP15 cores.
