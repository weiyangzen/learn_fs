# sources/distributed-fs/ceph-client/arch/mips/mm/c-r3k.c

Purpose: R2000/R3000 cache probing and cache operation implementation.

Important APIs/functions: `r3k_cache_init()` probes cache sizes/line sizes, assigns global cache flush and DMA function pointers, logs cache geometry, and builds clear/copy page routines. `r3k_cache_size()` and `r3k_cache_lsize()` use isolated cache space. Flush helpers cover I-cache, D-cache, page flush, and DMA writeback/invalidate.

Control flow: probing manipulates CP0 status isolate-cache bits and KSEG0 memory to infer sizes. Range flushes fall back to whole-cache flush if the range is too large or not KSEG0. Page flush checks ASID and PTE validity before flushing physical KSEG0 aliases.

State and persistence: static cache geometry variables and global function pointers persist for the booted kernel. No dynamic allocation.

Dependencies and integration: initialized from `cpu_cache_init()` for R3K CPUs; relies on CP0 status, KSEG0 addressing, MMU context, PTE helpers, and page routine generation.

Risks and test signals: cache probing writes through KSEG0 and is hardware-sensitive. Test boot on R3K/Tx39xx variants, DMA sync paths, executable page flushes, ASID-zero short-circuiting, and `BUG()` path for unsupported kernel vmap flush.
