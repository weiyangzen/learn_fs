# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cacheflush.h

Purpose: defines PowerPC cache-maintenance interfaces for page dirty-to-icache tracking, vmalloc synchronization, dcache range clean/flush/invalidate, and instruction-cache flushing.

Important APIs/types/functions: defines `PG_dcache_clean`, `flush_cache_vmap()` for Book3S64 `ptesync`, `flush_dcache_folio()`, `flush_dcache_page()`, `flush_icache_range()`, `flush_icache_user_page()`, `flush_dcache_icache_folio()`, `flush_dcache_range()`, `clean_dcache_range()`, `invalidate_dcache_range()`, and `flush_instruction_cache()` with a 44x inline `iccci` implementation.

Control flow: `flush_dcache_folio()` skips work on coherent-icache CPUs and otherwise clears the per-folio clean bit. Range helpers align the start address down to the L1 dcache block size, iterate cache blocks with `dcbf`, `dcbst`, or `dcbi`, and issue `mb()` synchronization. Book3S64 vmalloc flush emits `ptesync` to avoid spurious kernel faults after PTE installation.

State and persistence: the `PG_dcache_clean` folio flag records whether a page needs icache cleaning before user execution. Cache operations affect CPU cache state, not durable memory state.

Dependencies and integration points: depends on cache geometry accessors, CPU feature checks, generic cacheflush, folio/page flags, vmalloc, JIT/text patching, and noncoherent DMA paths.

Risks: incorrect range alignment or missing barriers can leave stale dcache data. Failing to clear `PG_dcache_clean` after kernel writes can let user mappings execute stale instructions. `flush_cache_vmap()` placement is subtle but required for Book3S64 kernel mappings.

Test signals: module load/ftrace/BPF JIT text execution, dcache/icache coherency selftests, noncoherent DMA tests, vmalloc mapping access immediately after install, and 44x instruction-cache flush coverage.
