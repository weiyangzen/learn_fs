# sources/distributed-fs/ceph/src/osd/object_state.h

## Purpose

`object_state.h` defines the small in-memory state carriers used by OSD object context code. `ObjectState` holds projected `object_info_t` plus an `exists` bit. `RWState` implements the per-object read/write/exclusive lock state machine used to serialize client IO, recovery, snap trimming, and other object-scoped operations.

## Important APIs and Types

`ObjectState` has constructors from `object_info_t`, moved `object_info_t`, and `hobject_t`; an object constructed only from an object id starts as non-existent. `RWState::State` has `RWNONE`, `RWREAD`, `RWWRITE`, and `RWEXCL`. `RWState` exposes `get_read_lock()`, `get_write_lock(bool greedy=false)`, `get_excl_lock()`, `take_write_lock()`, `put_read()`, `put_write()`, `put_excl()`, waiter counters, `empty()`, `get_snaptrimmer_write()`, and `get_recovery_read()`. The stream operator renders state name, active count, and waiter count.

## Control Flow

Read locks are admitted only when there are no waiters, preventing starvation. Multiple readers can share `RWREAD`; multiple writers can share `RWWRITE`, which reflects Ceph's ability to pipeline compatible writes under higher-level ordering. Exclusive locks require `RWNONE`. Non-greedy writes also refuse admission if waiters exist or a recovery read marker is set; greedy and `take_write_lock()` paths bypass part of the fairness policy. `dec()` decrements the active count and resets state to `RWNONE` when the count reaches zero.

## State and Persistence Behavior

All state is volatile and object-context-local. `count`, `waiters`, `state`, `recovery_read_marker`, and `snaptrimmer_write_marker` coordinate in-memory scheduling only; they are not encoded or persisted. The markers remember that recovery or snap trimming should be requeued once the lock drains.

## Dependencies and Integration Points

The header depends on `osd_types.h` for `object_info_t`, `hobject_t`, and Ceph assertions. It is included by `osd_internal_types.h`, which embeds `RWState` into `ObjectContext`. `PrimaryLogPG` chooses lock types based on operation classification and calls through `ObjectContext`/`ObcLockManager` to acquire and release them.

## Risks and Test Signals

The risk surface is concurrency semantics: starvation policy, count/state invariants, marker clearing, and multi-writer assumptions. `ceph_assert` and `ceph_abort_msg` catch impossible unlocks or state values in debug/crash paths, but production correctness depends on every caller releasing the matching lock type. Useful tests exercise read sharing, read/write/exclusive exclusion, waiter blocking, greedy writes, recovery marker requeue, snaptrimmer marker requeue, and stream formatting used in diagnostics.
