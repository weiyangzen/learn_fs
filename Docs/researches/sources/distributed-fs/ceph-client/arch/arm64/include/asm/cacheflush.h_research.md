## sources/distributed-fs/ceph-client/arch/arm64/include/asm/cacheflush.h

Purpose: declares arm64 cache maintenance operations and defines instruction-cache flushing behavior.

Important APIs/types/functions: declares `caches_clean_inval_pou`, `icache_inval_pou`, D-cache clean/invalidate variants to PoC/PoP/PoU, `caches_clean_inval_user_pou`, `sync_icache_aliases`, `flush_icache_range`, `copy_to_user_page`, `flush_dcache_page`, `flush_dcache_folio`, and `icache_inval_all_pou`. Defines `PG_dcache_clean`.

Control flow: `flush_icache_range` cleans and invalidates to PoU, performs KGDB breakpoint cache sync when enabled, and syncs aliases. Page helpers delegate to implementation files.

State and persistence: uses page/folio `PG_dcache_clean` state to remember D-cache cleanliness. Cache hardware state is modified but not persisted.

Dependencies and integration: depends on MM, KGDB, cache assembly routines, module text patching, BPF/JIT, user page copying, and executable mapping paths.

Risks: missing clean/invalidate creates stale instructions, data corruption, or debugger breakpoints not taking effect. Test signals are module load/unload, BPF JIT tests, ftrace/kprobe patching, KGDB, self-modifying code, and DMA coherency tests.
