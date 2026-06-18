# sources/distributed-fs/ceph-client/arch/arm/mm/cache-fa.S

Purpose: provides Faraday FA520/FA526/FA626 ARMv4-compatible cache maintenance routines for instruction/data cache flushing, coherency, and DMA cache handling.

Important APIs/types/functions: exports `fa_flush_icache_all`, `fa_flush_user_cache_all` aliasing `fa_flush_kern_cache_all`, `fa_flush_kern_cache_all`, `fa_flush_user_cache_range`, `fa_coherent_kern_range`, `fa_coherent_user_range`, `fa_flush_kern_dcache_area`, `fa_dma_flush_range`, `fa_dma_map_area`, and `fa_dma_unmap_area`; internal labels include `__flush_whole_cache`, `fa_dma_inv_range`, and `fa_dma_clean_range`. Constants define 16-byte cache lines, total D-cache size, and range threshold.

Control flow: whole-cache paths invalidate I-cache, clean/invalidate D-cache, invalidate BTB, drain write buffer, and flush prefetch. Range paths compare size against `CACHE_DLIMIT`, otherwise iterate by cache line. Coherency paths clean/invalidate D lines and invalidate I lines. DMA map chooses clean, invalidate, or flush based on DMA direction.

State and persistence: no global writable state. It directly changes CPU cache/BTB/write-buffer state through CP15 operations.

Dependencies and integration points: selected by `CPU_CACHE_FA`, used with FA526 processor support and `proc-macros.S` function pointer tables. Depends on CP15 cache op encodings and VM/DMA direction constants.

Risks: hard-coded cache size differs for Gemini vs other platforms; wrong value changes whole-cache threshold and coverage. DMA invalidation must clean partial lines to avoid discarding unrelated dirty data. Missing barriers or BTB invalidation can break self-modifying code and executable mappings.

Test signals: build FA526/Gemini and non-Gemini variants, run DMA map/unmap coherency tests for all directions, execute self-modifying/JIT code tests, and verify whole-cache threshold behavior for ranges around `CACHE_DLIMIT`.
