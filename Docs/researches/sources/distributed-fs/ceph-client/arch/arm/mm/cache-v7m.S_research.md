# sources/distributed-fs/ceph-client/arch/arm/mm/cache-v7m.S

Purpose: implements ARMv7-M cache maintenance through memory-mapped System Control Block registers instead of CP15 instructions, covering whole-cache, coherency, and DMA operations.

Important APIs/types/functions: defines macros `v7m_cache_read`, `v7m_cacheop`, `read_ccsidr`, `read_clidr`, `write_csselr`, `dcisw`, `dccisw`, `dccimvac`, `dcimvac`, `dccmvau`, `dccmvac`, `icimvau`, `invalidate_icache`, and `invalidate_bp`. Exports `v7m_invalidate_l1`, `v7m_flush_icache_all`, `v7m_flush_dcache_all`, `v7m_flush_kern_cache_all`, `v7m_flush_user_cache_all`, `v7m_flush_user_cache_range`, `v7m_coherent_kern_range`, `v7m_coherent_user_range`, `v7m_flush_kern_dcache_area`, `v7m_dma_flush_range`, `v7m_dma_map_area`, and `v7m_dma_unmap_area`; internal helpers are `v7m_dma_inv_range` and `v7m_dma_clean_range`.

Control flow: whole-cache routines read CLIDR/CCSIDR through SCB registers, select cache levels, and loop set/way maintenance via memory-mapped operation registers. Coherency cleans D lines to PoU, invalidates I lines to PoU, invalidates branch predictor, and barriers. DMA map/unmap mirrors v7 semantics using SCB clean/invalidate registers.

State and persistence: no software state. It writes memory-mapped cache operation registers under `BASEADDR_V7M_SCB`, changing cache state and selector state.

Dependencies and integration points: selected by `CPU_CACHE_V7M`, depends on `asm/v7m.h` SCB register offsets, `proc-macros.S`, and ARMv7-M architecture mode. It is often paired with `CPU_CACHE_NOP` for cases where some operations are stubs.

Risks: memory-mapped cache operations can corrupt temporary registers used in macro expansion; the code explicitly handles this in partial-line invalidation. Unlike CP15 `USER()` handling, v7-M open-coded ops must avoid placing fault fixups on the wrong instruction. Register offsets must match the SCB implementation.

Test signals: Cortex-M cache-enabled boot tests, SCB register access validation, DMA coherency with unaligned endpoints, self-modifying code tests, and no-MMU/MPU configurations selecting ARMv7-M.
