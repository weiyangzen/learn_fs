# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cache.h

Purpose: defines PowerPC cache-line geometry, instruction-fetch alignment, DMA alignment, and PPC64 cache information structures.

Important APIs/types/functions: macros include `L1_CACHE_SHIFT`, `L1_CACHE_BYTES`, `SMP_CACHE_BYTES`, `IFETCH_ALIGN_SHIFT`, `IFETCH_ALIGN_BYTES`, `MAX_COPY_PREFETCH`, and `ARCH_DMA_MINALIGN` for noncoherent caches. PPC64 types include `struct ppc_cache_info`, `struct ppc64_caches`, global `ppc64_caches`, and accessors such as `l1_dcache_shift()`, `l1_dcache_bytes()`, and `l1_icache_shift()`.

Control flow: compile-time CPU/config selection chooses cache-line sizes for 8xx, e500mc, PPC32, 47x, and PPC64. PPC64 runtime accessors read populated cache-info globals.

State and persistence: PPC64 cache descriptors persist in `ppc64_caches` after boot discovery. Other values are compile-time constants.

Dependencies and integration points: used by slab alignment, DMA mapping, copy routines, cache flush code, instruction patching, and performance-sensitive memory operations.

Risks: wrong cache-line size can cause false sharing, broken DMA alignment, or incomplete cache flushes. Runtime cache info must be initialized before accessors are used.

Test signals: boot CPU families covered by each branch, DMA tests on noncoherent systems, cache flush/instruction patching tests, and sanity checks against device-tree cache properties.
