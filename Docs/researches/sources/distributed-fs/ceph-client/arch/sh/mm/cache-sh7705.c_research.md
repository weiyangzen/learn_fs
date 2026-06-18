# sources/distributed-fs/ceph-client/arch/sh/mm/cache-sh7705.c

Purpose: provides special cache operations for SH7705 32KB cache configurations.

Important functions: `cache_wback_all`, `sh7705_flush_icache_range`, `__flush_dcache_page`, `sh7705_flush_dcache_folio`, `sh7705_flush_cache_all`, `sh7705_flush_cache_page`, `sh7705_flush_icache_folio`, and `sh7705_cache_init`.

Control flow: handles SH7705-specific cache geometry and aliasing, including whole-cache writeback and page/folio flush cases. Init overrides generic SH3 hooks when CPU type and cache size match.

State and persistence: mutates CPU cache state and runtime cache hook pointers.

Dependencies and integration: selected from `cpu_cache_init` after SH3 init for the SH7705 512-set case.

Risks: this is a narrow CPU-specific override; applying it to the wrong cache geometry or missing it on affected hardware can break coherency.

Test signals: boot and cache coherency tests on SH7705 hardware/emulation with 32KB cache.
