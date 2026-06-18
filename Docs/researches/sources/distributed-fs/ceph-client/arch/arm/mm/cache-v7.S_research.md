# sources/distributed-fs/ceph-client/arch/arm/mm/cache-v7.S

Purpose: implements ARMv7 cache maintenance using hierarchical cache discovery, set/way loops, point-of-unification operations, DMA maintenance, branch predictor invalidation, and erratum-aware barriers.

Important APIs/types/functions: exports `v7_invalidate_l1`, `v7_flush_icache_all`, `v7_flush_dcache_louis`, `v7_flush_dcache_all`, `v7_flush_kern_cache_all`, `v7_flush_kern_cache_louis`, `v7_flush_user_cache_all`, `v7_flush_user_cache_range`, `v7_coherent_kern_range`, `v7_coherent_user_range`, `v7_flush_kern_dcache_area`, `v7_dma_flush_range`, `v7_dma_map_area`, and `v7_dma_unmap_area`; internal DMA helpers are `v7_dma_inv_range` and `v7_dma_clean_range`. Optional `icache_size` supports `CONFIG_CPU_ICACHE_MISMATCH_WORKAROUND`.

Control flow: set/way routines read CLIDR/CSIDR, iterate cache levels, ways, and sets, and restore cache selector state. Kernel whole-cache flush cleans/invalidates D-cache then invalidates I-cache and BTB. Coherency cleans D lines to PoU, invalidates I lines, invalidates BTB, and returns `-EFAULT` if user line ops fault. DMA map/unmap dispatch based on DMA direction with endpoint cleaning for partial invalidation.

State and persistence: optional `icache_size` stores a workaround line size. Otherwise no software state. Hardware cache selector register and cache/BTB state are changed transiently; barriers ensure ordering.

Dependencies and integration points: selected by `CPU_CACHE_V7`, integrated with SMP alternatives (`ALT_SMP`/`ALT_UP`), preemption IRQ save around CSSR/CSIDR, errata configs `643719`, `764369`, `775420`, `814220`, and `proc-macros.S`.

Risks: set/way operations are sensitive to preemption because CSIDR describes the selected cache level. Errata barriers and LoUIS/LoUU handling are hardware-specific. User cache operations must not leave faults unhandled. Incorrect line-size detection breaks all range operations.

Test signals: ARMv7 SMP/UP boot tests, CPU hotplug, DMA coherency with unaligned buffers, self-modifying/JIT code, user fault injection in coherency paths, errata-specific builds, and systems with mismatched I-cache line sizes.
