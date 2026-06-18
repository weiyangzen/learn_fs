# sources/distributed-fs/ceph-client/lib/sg_pool.c

## Purpose
Implements small mempool-backed scatterlist chunk pools used by `sg_alloc_table_chained()` for callers that need atomic allocation of chained SG tables. It avoids direct potentially failing slab allocation in I/O paths by pre-creating per-size slab caches and mempools.

## APIs, Control Flow, and State
The exported APIs are `sg_alloc_table_chained()` and `sg_free_table_chained()`. Internal `struct sg_pool` records a chunk size, cache name, slab cache, and mempool. `sg_pool_index()` chooses the smallest configured pool for a requested number of entries, bounded by `SG_CHUNK_SIZE`. Allocation delegates to `__sg_alloc_table()` with `SG_CHUNK_SIZE`, an optional caller-provided first chunk, `GFP_ATOMIC`, and `sg_pool_alloc()`. Freeing calls `__sg_free_table()` with the same chunk size and `sg_pool_free()` unless all entries fit in the caller-owned first chunk. `sg_pool_init()` creates slab caches named `sgpool-*` and two-element mempools during `subsys_initcall`.

State is global and persistent after boot: the `sg_pools[]` array, each `kmem_cache`, and each `mempool_t`. Individual tables own only their chained SG entries and header counts.

## Dependencies, Integration, Risks, and Tests
Depends on `linux/scatterlist.h`, mempool, slab, and the generic scatterlist allocator/free implementation in `scatterlist.c`. It integrates with block and storage code that builds SG tables under atomic constraints. Risks include mismatched `nents_first_chunk` between allocation and free, `SG_CHUNK_SIZE` configuration outside expected bounds, leaking caller-owned first chunks, and expecting the pool to support more entries than its compile-time chunk size. Test signals include boot-time init failures, mempool exhaustion fault injection, chained allocation/free loops with different first-chunk sizes, and block-layer atomic allocation stress.
