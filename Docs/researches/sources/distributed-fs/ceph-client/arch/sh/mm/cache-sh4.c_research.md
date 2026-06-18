# sources/distributed-fs/ceph-client/arch/sh/mm/cache-sh4.c

Purpose: implements SH4/SH4A cache flushing hooks for I-cache, D-cache, folios, VMAs, pages, and whole-cache operations.

Important functions: `sh4_flush_icache_range`, `flush_cache_one`, `sh4_flush_dcache_folio`, `flush_icache_all`, `flush_dcache_all`, `sh4_flush_cache_all`, `sh4_flush_cache_mm`, `sh4_flush_cache_page`, `sh4_flush_cache_range`, `__flush_cache_one`, and `sh4_cache_init`.

Control flow: flush routines use SH4 cache instructions, MMU context/ASID checks, page/folio mapping state, and range iteration. Init binds SH4-specific functions to the generic cache hook pointers and low-level region flush routines.

State and persistence: mutates CPU caches and installs long-lived function hooks.

Dependencies and integration: called from generic cache APIs, page fault/writeback paths, highmem/page cache, and text modification paths.

Risks: SH4 aliasing and VIPT/PIPT behavior are subtle. Failing to flush executable mappings or shared aliases can produce stale instruction/data views.

Test signals: SH4 boot, module load/text patching, shared mmap alias tests, page cache writeback, and DMA coherency tests.
