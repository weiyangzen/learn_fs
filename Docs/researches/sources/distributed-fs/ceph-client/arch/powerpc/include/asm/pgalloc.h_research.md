<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgalloc.h

## Purpose
This top-level page-table allocation header supplies shared PTE page allocation/free helpers, cache indexes, and selects Book3S or nohash allocation backends.

## Important APIs, Types, And Functions
It defines `pgtable_t`, `pte_alloc_one_kernel()`, `pte_alloc_one()`, `pte_free_kernel()`, `pte_free()`, optional `pte_free_defer()`, `MAX_PGTABLE_INDEX_SIZE`, `pgtable_cache[]`, `PGT_CACHE(shift)`, then includes either `asm/book3s/pgalloc.h` or `asm/nohash/pgalloc.h`.

## Control Flow
PTE pages are allocated through PTE fragment helpers. Free paths release fragments immediately or through deferred freeing when configured. Higher-level page-table frees are delegated to the selected backend.

## State And Persistence Behavior
Allocated PTE fragments become persistent page-table state until unmapped and freed. `pgtable_cache[]` stores slab caches for different table sizes.

## Dependencies And Integration Points
It depends on generic MM, PTE fragment allocation, and PowerPC MMU family selection. It integrates with all generic page-table allocation paths.

## Risks And Edge Cases
Backend selection must match Book3S/nohash page-table layout. Deferred PTE free is required for configurations that cannot immediately release tables. Cache index bounds are enforced by backends.

## Test Signals
Run page-table allocation stress, fork/exit, mmap/unmap, memory pressure, deferred-free configurations, and Book3S/nohash cross-builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgalloc.h -->
