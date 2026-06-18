# sources/distributed-fs/ceph-client/fs/xfs/xfs_mru_cache.c

Purpose: Implements a generic XFS most-recently-used cache with radix-tree lookup and time-bucketed LRU reaping. Clients provide element lifetime, bucket count, callback data, and a free callback.

Important APIs, types, and functions: Public APIs include `xfs_mru_cache_init`, `xfs_mru_cache_uninit`, `xfs_mru_cache_create`, `xfs_mru_cache_destroy`, `xfs_mru_cache_insert`, `xfs_mru_cache_remove`, `xfs_mru_cache_delete`, `xfs_mru_cache_lookup`, and `xfs_mru_cache_done`. Internal `struct xfs_mru_cache` stores the radix tree, list array, reap list, spinlock, bucket timing, delayed work, free callback, and client data. `_xfs_mru_cache_migrate`, `_xfs_mru_cache_list_insert`, `_xfs_mru_cache_clear_reap_list`, and `_xfs_mru_cache_reap` implement expiration and workqueue processing.

Control flow: Module initialization creates a reclaim-safe per-cpu workqueue. Cache creation allocates one extra group to avoid early reaping, initializes lists and radix tree, and arms delayed work on first insert. Insert preloads radix-tree memory, adds the element under lock, and assigns it to the current MRU bucket. Lookup holds the spinlock on successful return, moves the element to the current MRU bucket, and requires the caller to call `xfs_mru_cache_done`. Migration advances `time_zero`, moves expired bucket contents to `reap_list`, and returns the next wakeup time. Reaping removes expired entries from the radix tree under lock and invokes client free callbacks without the lock.

State and persistence behavior: Cache state is memory-only. Time is represented in jiffies; expiration granularity is `lifetime / group_count` plus one extra bucket. Work scheduling state is kept in `queued`. No disk state is changed, but callers may use free callbacks for filesystem-specific teardown.

Dependencies and integration points: Uses Linux radix trees, delayed work, workqueues, spinlocks, and lists. The header exposes an opaque cache type and element node contract so XFS features such as filestreams can cache keyed objects without embedding cache internals.

Risks: Successful lookup returns with the cache spinlock held, which is easy to misuse. Free callbacks run unlocked and must tolerate concurrent cache state changes. Jiffies wrap and delayed reaper lag are handled by migration logic but remain sensitive to bucket arithmetic. Duplicate keys fail insertion and the passed element is freed through the callback.

Test signals: Validate create parameter rejection, insert/lookup/touch movement, duplicate insert cleanup, remove without callback, delete with callback, expiration timing across buckets, destroy while work is queued, and callback execution outside the spinlock. Stress with many keys and delayed reaper execution to ensure no leaked list entries or radix-tree entries.
