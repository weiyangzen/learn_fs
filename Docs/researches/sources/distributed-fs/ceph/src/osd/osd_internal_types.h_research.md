# sources/distributed-fs/ceph/src/osd/osd_internal_types.h

## Purpose

`osd_internal_types.h` defines core in-memory OSD object coordination types. It ties projected object state, snapset state, watcher maps, xattr cache, per-object locks, blocked-copy state, and lock-manager release behavior into the `ObjectContext` abstraction used heavily by `PrimaryLogPG` and backend code.

## Important APIs and Types

`SnapSetContext` stores an object id, `SnapSet`, reference count, registration bit, and existence bit. `ObjectContext` contains `ObjectState obs`, optional `SnapSetContext *ssc`, a destructor callback, watcher map keyed by `(cookie, entity_name_t)`, attribute cache, `RWState`, waiter queue, block flags, and methods for acquiring/releasing read, write, exclusive, recovery, and snaptrimmer locks. `ObcLockManager` owns a map from `hobject_t` to `{ObjectContextRef, RWState::State}` and releases all held locks in `put_locks()`.

## Control Flow

Object lock acquisition first tries the embedded `RWState`. If the lock is unavailable, `ObjectContext` appends the `OpRequestRef` to `waiters` when provided and increments `rwstate.waiters`. Unlock paths call `put_read()`, `put_write()`, or `put_excl()` and splice waiters into a caller-provided requeue list when the state drains. `put_lock_type()` also converts recovery and snaptrimmer markers into requeue booleans after the lock becomes empty. `ObcLockManager` records successfully acquired locks and later iterates them to release locks, collect per-object waiters, and clear its map.

## State and Persistence Behavior

All types here describe volatile projected state, not on-disk layout. `ObjectState::obs` mirrors projected object metadata before writes are committed. `SnapSetContext` mirrors snapset metadata and reference/registration status. Watcher and attr-cache maps are memory caches around durable object metadata. `blocked` and `requeue_scrub_on_unblock` coordinate in-progress copy-from and scrub scheduling. The `ObjectContext` destructor asserts no active locks remain and completes an optional callback, allowing `PrimaryLogPG` cache cleanup to observe destruction.

## Dependencies and Integration Points

The file depends on `osd_types.h`, `OpRequest.h`, `object_state.h`, and `Watch.h`. `PrimaryLogPG` creates, caches, locks, unlocks, blocks, and destroys `ObjectContext` instances across request processing, recovery, copy-from, cache tiering, snap trimming, and watcher management. `ReplicatedBackend`, EC code, scrubber paths, and watch code pass `ObjectContextRef` around as the in-memory handle for object-local coordination.

## Risks and Test Signals

Risks are lock leaks, waiter loss, stale projected state, raw `SnapSetContext *` lifetime errors, watcher/cache inconsistency, and missed requeue markers causing recovery or snaptrim stalls. `ObcLockManager`'s destructor assert is a useful guard but makes early returns dangerous unless `put_locks()` is reliably called. Test signals include operation ordering tests in `PrimaryLogPG`, copy-from block/unblock behavior, watcher timeout/blocklist tests, recovery and snaptrim requeue tests, and stress tests with simultaneous client IO and recovery.
