# sources/distributed-fs/ceph-client/arch/sh/mm/cache-sh2a.c

Purpose: implements SH2A cache maintenance, including line-level operations and icache range flushing.

Important functions: `sh2a_flush_oc_line`, `sh2a_invalidate_line`, `sh2a__flush_wback_region`, `sh2a__flush_purge_region`, `sh2a__flush_invalidate_region`, `sh2a_flush_icache_range`, and `sh2a_cache_init`.

Control flow: range functions walk cache lines and issue SH2A-specific writeback/invalidate operations. Init wires these implementations into generic cache hooks.

State and persistence: mutates CPU cache state and runtime hook pointers.

Dependencies and integration: used by `cache.c` for `CPU_FAMILY_SH2A`, with raw I/O/cacheflush support.

Risks: distinguishing operand-cache and instruction-cache operations is essential for code modification and DMA consistency.

Test signals: SH2A boot, module/text patch icache tests, and DMA/cache coherency tests.
