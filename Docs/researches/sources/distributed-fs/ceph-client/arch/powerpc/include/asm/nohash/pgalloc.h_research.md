<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/pgalloc.h

## Purpose
This header provides common nohash page-table allocation and deferred-free helpers, then includes the 32-bit or 64-bit nohash allocation backend.

## Important APIs, Types, And Functions
It declares `tlb_remove_table()` and `tlb_flush_pgtable()`, defines `pgd_alloc()`, `pgd_free()`, `pgtable_free()`, `pgtable_free_tlb()`, `__tlb_remove_table()`, and `__pte_free_tlb()`. On 8xx, `pgd_alloc()` copies kernel PGD entries from `swapper_pg_dir` into new PGDs.

## Control Flow
PGD allocation pulls from `PGT_CACHE(PGD_INDEX_SIZE)`. Teardown encodes the page-table cache shift into the low bits of the pointer passed to `tlb_remove_table()`, then `__tlb_remove_table()` decodes and frees it later.

## State And Persistence Behavior
The header manages lifetime of allocated page-table pages and deferred TLB-gather free records. It does not maintain its own global state.

## Dependencies And Integration Points
It depends on generic MM, slab, `PGT_CACHE`, PTE fragment allocators, TLB gather, and architecture-specific 32/64 pgalloc headers.

## Risks And Edge Cases
The pointer low-bit shift encoding assumes alignment and `MAX_PGTABLE_INDEX_SIZE`. Forgetting `tlb_flush_pgtable()` before deferred PTE free can leave hardware walkers seeing freed tables. 8xx kernel PGD copying is required for kernel mappings.

## Test Signals
Run mmap/unmap stress, page-table debug, TLB gather teardown tests, 8xx process creation, and allocation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/pgalloc.h -->
