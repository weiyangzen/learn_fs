# sources/distributed-fs/ceph-client/arch/arm/mm/cache-nop.S

Purpose: provides no-op cache maintenance functions for CPUs or configurations where cache operations should be stubbed out, such as selected ARMv7-M/no-cache paths.

Important APIs/types/functions: exports typed stubs `nop_flush_icache_all`, `nop_flush_kern_cache_all`, `nop_flush_user_cache_all`, `nop_flush_user_cache_range`, `nop_coherent_kern_range`, `nop_coherent_user_range`, `nop_flush_kern_dcache_area`, `nop_dma_flush_range`, `nop_dma_map_area`, and `nop_dma_unmap_area`.

Control flow: every function immediately returns. `nop_coherent_user_range` returns zero in `r0` to match the success convention of user coherency routines.

State and persistence: no state and no hardware side effects.

Dependencies and integration points: selected by `CPU_CACHE_NOP` and used through processor/cache function tables generated with `proc-macros.S`.

Risks: only safe when hardware does not require cache maintenance or when another mechanism handles it. Accidentally selecting this for cached hardware would break DMA coherency, executable mapping coherency, and self-modifying code.

Test signals: verify selected configurations truly have no relevant cache, run DMA and instruction coherency smoke tests on no-cache systems, and inspect processor table wiring so no-op functions are not used by cached CPU models.
