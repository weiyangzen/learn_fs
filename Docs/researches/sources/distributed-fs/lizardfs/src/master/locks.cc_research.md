# sources/distributed-fs/lizardfs/src/master/locks.cc

Purpose: implements byte-range lock normalization, collision detection, pending lock queues, lock listing, and lock persistence for flock/POSIX lock state.

Important APIs/types/functions: `LockRanges::findCollision()` finds incompatible overlaps; `fits()` wraps collision check; `insert()` splits, merges, overwrites, stacks shared owners, and removes unlock ranges; `FileLocks::sharedLock()`, `exclusiveLock()`, `unlock()`, `apply()`, `findCollision()`, `gatherCandidates()`, `removePending()` manage per-inode active and queued locks; copy helpers export locks to `lzfs_locks::Info`; `load()`/`store()` serialize active and pending maps.

Control flow: `FileLocks::apply()` creates an inode entry, inserts immediately if the range fits, or enqueues blocking non-unlock requests. Unlock is represented as a lock range of type `kUnlock` and is inserted through the same range-splitting machinery. After unlocks, callers gather overlapping pending candidates and retry them. Serialization writes counts and one `Info` per owner.

State and persistence behavior: active locks and pending locks are stored in unordered maps by inode. Metadata persistence writes both active and pending queues in the `FLCK 1.0` metadata section through `filesystem_store.cc`.

Dependencies/integration: depends on `compact_vector`, protocol `lock_info`, serialization helpers, and syslog for write errors. Used by client lock operations and metadata load/store.

Risks and test signals: `LockRanges::insert()` mutates iterators while inserting and later erases unlocking ranges over a saved range, so vector iterator math is delicate. Shared lock owner sets must remain sorted for binary search and merge. `FileLocks::clear()` only clears active locks, leaving pending locks untouched, which may be intentional or a bug depending on caller expectations. Pending load uses `push_back()` without sorting, while enqueue keeps sorted order. Tests should cover range splitting/merging, stacked shared locks, owner removal, pending queue gather/reapply, nonblocking semantics, serialization round trips, clear behavior, and loaded pending order.
