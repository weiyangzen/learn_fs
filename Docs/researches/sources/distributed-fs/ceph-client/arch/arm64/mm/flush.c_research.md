# sources/distributed-fs/ceph-client/arch/arm64/mm/flush.c

Purpose: provides higher-level ARM64 cache flush integration for executable user mappings, ptrace page writes, D-cache dirty tracking, and persistent memory cache operations.

Important APIs/types/functions: `sync_icache_aliases`, `copy_to_user_page`, `__sync_icache_dcache`, `flush_dcache_folio`, `flush_dcache_page`, `caches_clean_inval_pou` export, `arch_wb_cache_pmem`, and `arch_invalidate_pmem`.

Control flow: executable writes call `sync_icache_aliases`, which either cleans D-cache and invalidates all I-cache on aliasing caches or uses PoU clean+invalidate for non-aliasing caches. `copy_to_user_page` memcpy's into the page then flushes if the VMA is executable. `__sync_icache_dcache` performs the folio-wide sync only once while `PG_dcache_clean` is clear, then marks it clean. Kernel writes clear that bit through `flush_dcache_folio/page`. PMEM writeback orders prior non-cacheable writes then cleans to PoP; invalidation uses PoC invalidation.

State and persistence: mutates folio `PG_dcache_clean` flag and issues cache maintenance. PMEM routines affect persistence visibility.

Dependencies/integration: core MM executable mapping setup, ptrace access, cache.S routines, folio/page flags, libnvdimm PMEM API, and architecture cache alias detection.

Risks: missing icache synchronization can execute stale instructions. Dirty flag races must remain benign across folio mappings. PMEM ordering depends on the outer-shareable barrier and DC CVAP/PoP support.

Test signals: ptrace writes to executable mappings, JIT/module text coherency, folio dirty-clean transitions, aliasing I-cache hardware, PMEM persistence tests, and DAX/libnvdimm cache API coverage.
