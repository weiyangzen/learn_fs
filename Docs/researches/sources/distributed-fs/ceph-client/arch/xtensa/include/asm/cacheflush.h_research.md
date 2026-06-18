<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cacheflush.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cacheflush.h

## Purpose
Declares and maps Xtensa cache flush APIs required by Linux MM, DMA, highmem, vmalloc, user-page copying, and instruction-cache coherency.

## Important APIs, Types, And Functions
Declares low-level functions like `__invalidate_*`, `__flush_*`, alias flush helpers, SMP/non-SMP `flush_cache_all`, `flush_cache_range`, `flush_icache_range`, `flush_cache_page`, `flush_dcache_folio`, `flush_dcache_page`, `copy_to_user_page`, and `copy_from_user_page`.

## Control Flow
Preprocessor feature checks choose real externs or inline no-ops depending on writeback caches, MMU, aliasing way size, and SMP. Generic cacheflush hooks are included after Xtensa-specific definitions.

## State And Persistence
No software state; functions mutate data and instruction caches and sometimes alias mappings.

## Dependencies And Integration Points
Depends on cache geometry, MMU state, page and folio types, SMP broadcast implementations, and generic cacheflush contracts.

## Risks And Edge Cases
VIPT aliasing when way size exceeds page size is the main hazard. Missing icache invalidation after user or module writes causes stale instruction execution. SMP requires cross-CPU coherency where local-only macros are insufficient.

## Test Signals
Run module loading, ftrace/kprobes, `mprotect` executable transitions, highmem user-page copy, page-cache writeback, and cache alias stress tests on SMP and UP variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cacheflush.h -->
