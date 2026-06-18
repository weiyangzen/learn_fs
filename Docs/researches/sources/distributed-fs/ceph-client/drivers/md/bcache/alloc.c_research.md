# sources/distributed-fs/ceph-client/drivers/md/bcache/alloc.c

## Purpose
`alloc.c` implements bcache bucket allocation, invalidation, priority/generation handling, and sector allocation within open data buckets.

## Important APIs, Types, and Functions
Important functions are `bch_inc_gen()`, `bch_rescale_priorities()`, `bch_can_invalidate_bucket()`, `__bch_invalidate_one_bucket()`, `invalidate_buckets_lru()`, `invalidate_buckets_fifo()`, `invalidate_buckets_random()`, `bch_allocator_thread()`, `bch_bucket_alloc()`, `__bch_bucket_free()`, `bch_bucket_free()`, `__bch_bucket_alloc_set()`, `bch_bucket_alloc_set()`, `bch_alloc_sectors()`, `bch_open_buckets_alloc()`, `bch_open_buckets_free()`, and `bch_cache_allocator_start()`. `struct open_bucket` tracks active write buckets.

## Control Flow, State, and Persistence
The allocator thread runs under `bucket_lock`, drains `free_inc` into reserve freelists once prio/gen metadata is safe, invalidates reclaimable buckets according to LRU/FIFO/random policy, and writes priorities/generations with `bch_prio_write()` when cache sync requires it. Allocating a bucket pops from reserve lists, pins it, marks GC state, assigns priority, and updates availability stats. Sector allocation chooses or allocates open buckets, fills a `bkey` with pointer and extent size, advances pointer offsets, and retains bucket pins while data is pending insertion. Persistent correctness depends on writing incremented bucket generations before reuse, preventing stale on-disk btree pointers from becoming valid after crash.

## Dependencies and Integration Points
The file depends on `bcache.h`, `btree.h`, FIFO/heap utilities, kthreads, random selection, tracepoints, GC wakeups, priority writes, and bkey pointer helpers. It is called by btree, request, writeback, and moving-GC paths.

## Risks and Test Signals
Risks include generation wraparound, deadlock between allocation and GC/prio writes, reserve starvation, incorrect pin accounting, open-bucket locality races, and IO disable shutdown behavior. Tests should stress random writes, writeback and moving GC reserves, crash recovery around prio writes, allocator thread stop, `CACHE_SET_IO_DISABLE`, low-space GC, and debug duplicate-bucket checks.
