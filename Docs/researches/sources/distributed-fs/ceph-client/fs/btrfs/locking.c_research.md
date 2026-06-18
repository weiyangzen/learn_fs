# sources/distributed-fs/ceph-client/fs/btrfs/locking.c

## Purpose
`locking.c` implements Btrfs extent-buffer tree locking and the double-reader-writer-exclusion lock used by snapshot/COW coordination. It also assigns debug lockdep classes to tree blocks based on Btrfs root objectid and tree level. The source was read as a complete 383-line file.

## Important APIs, Types, and Functions
Lockdep helpers are `btrfs_set_buffer_lockdep_class()` and `btrfs_maybe_reset_lockdep_class()` under `CONFIG_DEBUG_LOCK_ALLOC`. Tree-locking APIs are `btrfs_tree_read_lock_nested()`, `btrfs_try_tree_read_lock()`, `btrfs_tree_read_unlock()`, `btrfs_tree_lock_nested()`, `btrfs_tree_unlock()`, `btrfs_unlock_up_safe()`, `btrfs_lock_root_node()`, `btrfs_read_lock_root_node()`, and `btrfs_try_read_lock_root_node()`. DREW APIs are `btrfs_drew_lock_init()`, `btrfs_drew_try_write_lock()`, `btrfs_drew_write_lock()`, `btrfs_drew_write_unlock()`, `btrfs_drew_read_lock()`, and `btrfs_drew_read_unlock()`.

## Control Flow
Extent-buffer locking is a thin rwsem wrapper. Read and write lock calls optionally capture start timestamps for tracepoints, acquire the rwsem with a lockdep nesting subclass, and emit trace events. Write locking records `eb->lock_owner` in debug builds and clears it on unlock.

Root-node locking loops until the locked extent buffer reference is still the current `root->node`; if the root changed after taking a reference, the code unlocks/frees that buffer and retries. The try-read variant returns `ERR_PTR(-EAGAIN)` instead of sleeping when the initial read lock cannot be acquired.

DREW write acquisition increments the writer count only if there are no readers, then uses a memory barrier before rechecking readers. If a reader appeared, it releases and retries through a waitqueue. Reader acquisition increments the reader count first, barriers, then waits for writers to drain, which gives pending readers priority over new writers. Unlock paths wake the opposite side when the active count drops to zero.

## State and Persistence Behavior
There is no durable state. Runtime state lives in extent-buffer rwsems, optional debug lock-owner fields, per-root/per-level lockdep class keys, `btrfs_path->locks[]`, and `struct btrfs_drew_lock` atomics/waitqueues.

## Dependencies and Integration Points
The file depends on Btrfs `ctree.h`, `extent_io.h`, and `locking.h`, Linux rwsem/spin/page/scheduler facilities, lockdep, and Btrfs tracepoints. Tree traversal, COW, balancing, root replacement, snapshot creation, and path cleanup rely on these primitives.

## Risks and Edge Cases
Incorrect lockdep class assignment can hide real deadlocks or create false positives across roots and tree levels. Root-node locking must retry because root replacement can race with grabbing a buffer reference. `btrfs_unlock_up_safe()` intentionally ignores normal search-slot lock retention rules and is only valid when higher-level updates are done. DREW is reader-priority; sustained readers can delay writers, and its memory barriers are essential for preventing A/B overlap.

## Test Signals
Signals include lockdep-enabled fstests for tree COW/split/balance/snapshot paths, tracepoint sanity for read/write lock timings, stress tests with root node replacement during traversal, nowait root read-lock returning `-EAGAIN`, and snapshot/delalloc stress that validates DREW exclusion without reader/writer overlap.
