# sources/distributed-fs/ceph-client/arch/arm/mm/cache-v6.S

Purpose: provides ARMv6 VIPT cache maintenance, I-cache invalidation, D-cache cleaning/invalidation, executable coherency, and DMA map/unmap routines.

Important APIs/types/functions: exports `v6_flush_icache_all`, `v6_flush_kern_cache_all`, `v6_flush_user_cache_all`, `v6_flush_user_cache_range`, `v6_coherent_kern_range`, `v6_coherent_user_range`, `v6_flush_kern_dcache_area`, `v6_dma_flush_range`, `v6_dma_map_area`, and `v6_dma_unmap_area`; internal labels include `v6_dma_inv_range` and `v6_dma_clean_range`.

Control flow: full kernel cache flush cleans/invalidates D-cache then invalidates I-cache. User cache all/range are no-ops because VIPT assumptions avoid per-address flush for normal user mappings. Coherency cleans D lines to PoU, drains, invalidates I lines, and returns `-EFAULT` if user line operations fault. DMA map selects invalidate for `DMA_FROM_DEVICE` and clean otherwise; unmap invalidates unless direction is `DMA_TO_DEVICE`.

State and persistence: no C-level state. It modifies cache and write-buffer state via CP15 and barriers.

Dependencies and integration points: selected by `CPU_CACHE_V6`, uses ARMv6 CP15 cache operations, `USER()` fixup tables, `asm/unwind`, and DMA direction constants.

Risks: VIPT assumptions and fixed 32-byte line size must match selected hardware. DMA invalidation must clean partial first/last lines. User coherency paths must return `-EFAULT` on unmapped addresses rather than faulting in kernel mode.

Test signals: ARMv6 executable mapping/JIT tests, DMA coherency with aligned and unaligned buffers, user address fault tests for `coherent_user_range`, and SMP/UP variants where selected by Kconfig.
