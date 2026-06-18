# File Research: sources/block-storage/linux-dm/drivers/md/bcache/alloc.c

## Purpose
Implements bcache bucket allocation, invalidation, free-list management, priority rescaling, allocator kthread behavior, and sector allocation from open data buckets.

## Main Interfaces
- Bucket generation and priority: `bch_inc_gen()`, `bch_rescale_priorities()`.
- Invalidation checks/actions: `bch_can_invalidate_bucket()`, `__bch_invalidate_one_bucket()`.
- Bucket allocation/freeing: `bch_bucket_alloc()`, `__bch_bucket_alloc_set()`, `bch_bucket_alloc_set()`, `bch_bucket_free()`, `__bch_bucket_free()`.
- Data sector allocation: `bch_alloc_sectors()`.
- Open bucket lifecycle and allocator startup: `bch_open_buckets_alloc()`, `bch_open_buckets_free()`, `bch_cache_allocator_start()`.

## Control Flow
The allocator kthread drains `free_inc`, optionally discards those buckets, pushes them onto reserve freelists, then invalidates more buckets by LRU, FIFO, or random policy. For synchronous caches it writes updated priorities/generations before reuse. `bch_bucket_alloc()` consumes ready buckets from free lists or waits on `bucket_wait`. `bch_alloc_sectors()` chooses or creates an open data bucket, then hands out a sector range and advances pointer offsets.

## State And Synchronization
Bucket reuse is serialized under `cache_set.bucket_lock`; open data bucket selection uses `data_bucket_lock`. Bucket `pin`, `gc_mark`, `prio`, `gen`, and cache-set `avail_nbuckets`, `need_gc`, and `invalidate_needs_gc` control safe reuse. The allocator waits cooperatively and exits only after `kthread_stop()` when IO disable is set.

## Integration Points
Depends on btree GC marks from `btree.c`, prio persistence from journal/super code via `bch_prio_write()`, request/write paths via `bch_alloc_sectors()`, and bucket helpers from `bcache.h`.

## Notable Behaviors
- Generation increments are the core invalidation mechanism; generation wrap risk forces GC rather than reuse.
- `RESERVE_PRIO` is prioritized because priority/generation writes are required before normal allocation can progress.
- Open data buckets segregate flash-only and cached-device streams, sequential streams, and task-local write points to reduce cache pollution.
- Nonblocking allocation returns failure quickly and emits tracepoints.

## Risks And Review Focus
- Deadlock avoidance between allocation, prio writes, btree locks, and GC is central.
- Reusing buckets before generation persistence can corrupt crash recovery.
- `data_bucket_lock` is dropped around bucket allocation, so races with other writers are handled by retry and key refcount cleanup.
