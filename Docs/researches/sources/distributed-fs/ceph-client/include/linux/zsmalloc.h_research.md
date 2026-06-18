# sources/distributed-fs/ceph-client/include/linux/zsmalloc.h

## Purpose
Declares the zsmalloc compressed-object allocator API. It provides pool lifecycle, handle-based allocation/free, compaction, size-class queries, statistics, and object read/write helpers for storing compressed pages or similar variable-sized objects in tightly packed memory.

## Important APIs, Types, and Functions
`struct zs_pool` is the opaque allocator pool. `struct zs_pool_stats` currently reports `pages_compacted`. Core lifecycle and allocation APIs are `zs_create_pool()`, `zs_destroy_pool()`, `zs_malloc()`, and `zs_free()`. Capacity and maintenance APIs include `zs_huge_class_size()`, `zs_get_total_pages()`, `zs_compact()`, `zs_lookup_class_index()`, and `zs_pool_stats()`. Object access uses `zs_obj_read_begin()`, `zs_obj_read_end()`, `zs_obj_read_sg_begin()`, `zs_obj_read_sg_end()`, and `zs_obj_write()`. `zsmalloc_mops` exposes movable-page operations.

## Control Flow
Callers create a pool, allocate objects by size and NUMA node, receive opaque unsigned-long handles, access object contents through read/write helpers that map or copy handle memory, and free handles back to the pool. Compaction can migrate objects to free pages and reports reclaimed page activity. Scatterlist read helpers support direct readout into SG-backed consumers.

## State and Persistence
Persistent allocator state lives in `struct zs_pool` and its internal size classes, pages, and object metadata. Object identity is represented by opaque handles, not stable virtual addresses. Pool statistics persist as counters populated by `zs_pool_stats()`.

## Dependencies and Integration Points
Depends on Linux types, GFP allocation flags, NUMA node IDs, scatterlists, and movable page operations. Integrates with zswap, zram, memory reclaim/compaction, compressed page storage, and migration infrastructure.

## Risks
Handles must not be treated as direct pointers or used after `zs_free()`. Object access begin/end pairs must be balanced, especially if the implementation maps temporary memory or pins migration. Compaction can move objects, so users must rely on handles and allocator APIs. Incorrect size-class assumptions can waste memory or corrupt object boundaries.

## Test Signals
Signals include zsmalloc selftests, zram/zswap stress, compaction and migration tests, NUMA allocation coverage, KASAN/KMSAN around object read/write lengths, scatterlist read tests, and leak checks on pool destroy.
