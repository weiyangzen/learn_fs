# sources/distributed-fs/ceph-client/include/linux/shrinker.h

## Purpose

`shrinker.h` defines the kernel reclaim shrinker API used by caches to expose reclaimable objects to memory pressure. It includes memcg-aware deferred tracking, shrink-control input, shrinker allocation/registration/freeing, refcount lifetime helpers, and optional debugfs renaming.

## Important APIs, Types, And Functions

Types are `struct shrinker_info_unit`, `struct shrinker_info`, `struct shrink_control`, and `struct shrinker`. `shrink_control` carries GFP mask, NUMA node, target scan count, actual scanned count, and current memory cgroup. `struct shrinker` contains `count_objects()` and `scan_objects()` callbacks, batch size, seeks cost, flags, refcount, completion, RCU head, private data, global list node, optional memcg ID, optional debugfs identity, and per-node deferred object counters.

Constants include `SHRINK_STOP`, `SHRINK_EMPTY`, `DEFAULT_SEEKS`, internal flags `SHRINKER_REGISTERED` and `SHRINKER_ALLOCATED`, and public flags `SHRINKER_NUMA_AWARE`, `SHRINKER_MEMCG_AWARE`, and `SHRINKER_NONSLAB`. APIs are `shrinker_alloc()`, `shrinker_register()`, `shrinker_free()`, `shrinker_try_get()`, `shrinker_put()`, and optional `shrinker_debugfs_rename()`.

## Control Flow

A subsystem allocates or embeds a shrinker, fills count and scan callbacks, registers it, and the page reclaim path calls `count_objects()` followed by `scan_objects()` when there is reclaimable work. Callback return values drive control flow: `SHRINK_EMPTY` means no objects, zero means skip or unknown, and `SHRINK_STOP` stops current-context scanning due to possible deadlock. Unregistration drops the initial refcount and waits for concurrent users to release references before RCU freeing.

## State And Persistence

Persistent shrinker state includes callback pointers, flags, private data, refcount, completion, deferred counters, memcg ID, and debugfs metadata. `shrinker_info` stores per-memcg bitmaps and deferred counts indexed by shrinker ID units.

## Dependencies And Integration Points

Dependencies include atomics, refcounts, completions, RCU, optional memcg, optional debugfs, and reclaim code. Integration points are slab and non-slab caches, filesystem inode/dentry caches, driver caches, memcg reclaim, NUMA-aware reclaim, and debugfs diagnostics.

## Risks And Test Signals

Risks are deadlocks in `count_objects()`, failure to return `SHRINK_STOP` when locks cannot be safely acquired, refcount use-after-free during unregistration, wrong memcg-aware flags, and inaccurate `nr_scanned` accounting. Test signals include memory pressure reclaim, memcg reclaim, shrinker debugfs output, unregister under concurrent reclaim, lockdep, and cache-specific object leak checks.
