## sources/distributed-fs/ceph-client/arch/arm64/include/asm/cache.h

Purpose: defines cache geometry, alignment, and cache-type helpers for arm64.

Important APIs/types/functions: exports L1 cache line constants, CLIDR extraction macros, DMA/kmalloc/slab alignment rules, `icache_is_aliasing`, `cache_type_cwg`, `cache_line_size_of_cpu`, `cache_line_size`, `dma_get_cache_alignment`, `arch_sync_dma_flush`, `arch_compact_of_hwid`, and `read_cpuid_effective_cachetype`.

Control flow: helpers read CPU ID registers, derive cache line sizes or aliasing flags, and compact MPIDR affinity into a topology key. KASAN/MTE configuration changes slab minimum alignment.

State and persistence: `__icache_flags` records global I-cache properties; other values are computed from CPU registers. No persistence beyond kernel data.

Dependencies and integration: depends on sysreg/cputype/MTE/KASAN headers. Used by DMA, slab, cache maintenance, CPU topology, and userspace cache-type reporting.

Risks: alignment mistakes can corrupt DMA buffers or KASAN tags; cache-type reporting affects self-modifying code and userspace. Test signals include DMA API tests, cacheflush tests, slab/KASAN boot tests, and heterogeneous CPU bring-up.
