# sources/distributed-fs/ceph-client/drivers/md/bcache/bcache.h

## Purpose
`bcache.h` is the main internal bcache header. It documents core design and declares the in-memory objects, flags, helpers, and cross-file APIs for cache sets, cache devices, backing devices, allocation, btrees, IO, writeback, and sysfs.

## Important APIs, Types, and Functions
Important types include `bucket`, `keybuf`, `bcache_device`, `cached_dev`, `cache`, `gc_stat`, `cache_set`, `bbio`, and `detached_dev_io_private`. It defines GC mark bitfields, allocation reserves, cache-set state flags, bucket/sector conversion helpers, pointer validity helpers, checksum macro `csum_set()`, error macros, lifecycle helpers, and prototypes for allocator, btree, superblock, writeback, journal, request, debug, and cache-set registration functions.

## Control Flow, State, and Persistence
This header has no standalone runtime control flow, but it defines the shared state machines used by the module. `cache_set` coordinates device attachment, bucket allocation, btree cache, garbage collection, journal, UUIDs, writeback throttling, congestion, and shutdown flags. `cache` tracks on-disk superblock data, bucket arrays, priority buckets, free lists, and allocator thread state. `cached_dev` tracks independent backing-device lifetime, dirty/writeback state, rate control, and sequential IO detection. Persistence is represented by superblocks, UUID metadata, journal roots, bucket priorities/generations, and btree keys declared in included on-disk structures.

## Dependencies and Integration Points
It includes Linux block, closure, kobject, bio, mempool, list, locking, workqueue, and kthread APIs, plus bcache-specific `bcache_ondisk.h`, `bset.h`, `journal.h`, `stats.h`, and `util.h`. Every major bcache implementation file depends on this contract.

## Risks and Test Signals
Risks include flag semantics drifting across files, refcount and closure lifetime bugs, stale pointer generation comparisons, shutdown with IO in flight, and mismatch between in-memory structures and disk metadata expectations. Tests should include attach/detach, flash-only volumes, dirty writeback recovery, GC under pressure, btree cache shrink/cannibalization, sysfs tuning, and debug builds with expensive checks.
