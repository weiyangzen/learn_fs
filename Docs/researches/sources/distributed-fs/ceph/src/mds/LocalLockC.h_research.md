# sources/distributed-fs/ceph/src/mds/LocalLockC.h

## Purpose

`LocalLockC.h` declares a local-only metadata cache lock built on `SimpleLock`. It is used for lock types that do not participate in distributed lock state the same way normal inode/dentry locks do, while still supporting local xlock/wrlock coordination inside the MDS.

## Important APIs, Types, And Functions

`LocalLockC(MDSCacheObject*, const LockType*)` forwards to `SimpleLock` and immediately sets state to `LOCK_LOCK`, meaning the lock is always considered locally locked. `is_locallock()` overrides the base to return true.

`can_xlock_local()` permits a local exclusive lock when there are no write locks and no existing xlock owner. `can_wrlock()` permits a write lock when the lock is not xlocked and there is no waiter for `SimpleLock::WAIT_XLOCK`.

`get_wrlock(client_t client)` asserts `can_wrlock()`, takes the base write lock, and records `last_wrlock_client`. `put_wrlock()` releases a base write lock and clears `last_wrlock_client` once the write-lock count drops to zero. `get_last_wrlock_client()` exposes that recorded client. `print()` extends base lock printing with `last_client` when nonnegative.

## Control Flow And Data Flow

Locker code treats `LocalLockC` specially through `local_wrlock_grab()`, `local_wrlock_start()`, and `local_xlock_start()`. Cache objects such as `CInode` and `CDentry` embed local locks for version/quiesce-style coordination. Lock acquisition flows through the base `SimpleLock` counters/waiters, with this wrapper adding client attribution for the latest write lock.

## State And Persistence Behavior

The lock state is purely in-memory and is not encoded. Persistent metadata is protected by operations using the lock, but the lock itself resets with the cache object. The only local field is `last_wrlock_client`, which is cleared when no write locks remain.

## Dependencies And Integration Points

The class depends on `SimpleLock`, `MDSCacheObject`, `LockType`, `client_t`, base lock waiters, and output printing. Integration points include `CInode`'s `quiescelock` and `versionlock`, `CDentry`'s `versionlock`, and `Locker.cc` local lock acquisition paths.

## Risks And Edge Cases

`last_wrlock_client` is not explicitly initialized in the constructor. It is printed only if `>= 0`, but without initialization the first print or read before `get_wrlock()` can be undefined. `get_wrlock()` records only one client even if multiple write locks are held; it represents the last acquisition, not a complete owner set. `can_wrlock()` blocks new write locks when an xlock waiter exists, which gives xlock waiters priority but can affect write-heavy paths.

Because the lock is always in `LOCK_LOCK`, code expecting normal distributed lock state transitions should not use this class. Misclassifying a distributed lock as local would bypass inter-MDS coordination.

## Test Signals

Tests should validate constructor state, `is_locallock()`, wrlock/xlock exclusion rules, xlock waiter priority, `last_wrlock_client` set/clear behavior across nested write locks, and print output. A regression test should initialize or check `last_wrlock_client` before first use to prevent undefined diagnostics.
