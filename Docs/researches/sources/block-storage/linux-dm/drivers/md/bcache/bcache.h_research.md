# File Research: sources/block-storage/linux-dm/drivers/md/bcache/bcache.h

## Purpose
Provides bcache's central in-kernel declarations, high-level design notes, primary structs, state flags, bucket/key helpers, error macros, lifecycle prototypes, and cross-file entry points.

## Main Interfaces
- Core structs: `bucket`, `bcache_device`, `cached_dev`, `cache`, `cache_set`, `bbio`, `keybuf`, and `gc_stat`.
- Bucket and key helpers: GC mark bitmasks, pointer bucket lookup, generation/staleness checks, priority constants, bucket/block sizing, and checksum helper `csum_set()`.
- Cache-set flags: unregistering, stopping, running, and IO-disabled states.
- Public prototypes for IO error accounting, bbio submission/allocation, allocation, superblock writes, cache/device attach/detach/run/stop, btree cache, moving GC, debug, request, and btree init/exit.

## Control Flow
This header does not execute policy directly, but its inline helpers define common fast-path behavior. `closure_bio_submit()` takes a closure ref and fails IO immediately if `CACHE_SET_IO_DISABLE` is set. `cached_dev_get/put()` manage cached device lifetime, and `wake_up_allocators()` wakes the single cache allocator thread.

## State And Synchronization
Documents and declares the major synchronization primitives: `bucket_lock`, btree cache lists and wait queues, `btree_cannibalize_lock`, `prio_blocked`, `bucket_wait`, GC wait state, moving GC semaphores/workqueues, data bucket spinlock, journal state, sysfs/debug flags, and writeback locks in `cached_dev`.

## Integration Points
Included by most bcache implementation files. It ties together on-disk definitions from `bcache_ondisk.h`, bset iteration from `bset.h`, closure async control, journal/stats headers, block layer bios, kobjects/sysfs, workqueues, and bcache module lifecycle.

## Notable Behaviors
- The top comment is architectural documentation for cache sets, backing devices, flash-only volumes, bucket generation invalidation, log-structured btree nodes, GC, and journal purpose.
- Bcache is described as COW for both data and metadata.
- Multiple cache-device support is mostly plumbed but not complete; much code still assumes `c->cache`.
- `wait_for_kthread_stop()` prevents allocator/GC kthreads from exiting before `kthread_stop()` observes them.

## Risks And Review Focus
- Struct layout and flags are shared across many files; small semantic changes can affect allocation, writeback, GC, and sysfs.
- `ptr_available()` and single-cache assumptions are important limitations.
- IO-disable handling must be observed by all external and internal IO submission paths.
