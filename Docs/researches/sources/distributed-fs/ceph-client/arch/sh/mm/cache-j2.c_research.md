# sources/distributed-fs/ceph-client/arch/sh/mm/cache-j2.c

Purpose: implements cache maintenance hooks for the J2 SuperH-compatible CPU.

Important functions: `j2_flush_icache`, `j2_flush_dcache`, `j2_flush_both`, and `j2_cache_init`.

Control flow: flush helpers operate over cache ranges/all-cache state using J2-specific control/register behavior. Init installs the J2 functions into the generic cache hook pointers.

State and persistence: mutates CPU cache state; hook assignments persist for runtime.

Dependencies and integration: called from `cpu_cache_init`, uses cacheflush, addrspace, processor, cpumask/MM helpers, and raw I/O accessors.

Risks: incomplete I/D-cache synchronization can break self-modifying/JIT/module code and DMA coherency assumptions.

Test signals: boot on J2, icache coherency tests, dcache flush tests, and executable page modification tests.
