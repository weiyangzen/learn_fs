# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/meta/WorkerMetaLock.java

## Purpose
`WorkerMetaLock` is a `Lock` wrapper that acquires and releases multiple `MasterWorkerInfo` metadata-section locks in a fixed order. It gives `LockResource` a single lock object to manage.

## Important APIs and Types
- Constructor takes an `EnumSet<WorkerMetaLockSection>`, shared/exclusive flag, and target `MasterWorkerInfo`.
- `lock()` acquires selected read or write locks in enum declaration order.
- `unlock()` releases selected locks in reverse order.
- Interruptible, try-lock, timed try-lock, and conditions are unsupported.

## Control Flow
Callers normally create this through `MasterWorkerInfo.lockWorkerMeta`. `LockResource` calls `lock` on construction and `unlock` on close. Fixed acquisition and reverse release prevent deadlock among callers requesting multiple worker metadata sections.

## State and Persistence Behavior
This class has only runtime locking state and no persistence behavior.

## Dependencies and Integration Points
It depends on `WorkerMetaLockSection`, `MasterWorkerInfo.getLock`, Java `Lock`, and Guava `Lists.reverse`. It is central to all `DefaultBlockMaster` worker metadata access.

## Risks and Edge Cases
The wrapper does not implement `tryLock` or interruptible lock acquisition, so callers can block indefinitely if lock ordering contracts are violated elsewhere. It does not track whether `lock()` succeeded before `unlock()`, relying on `LockResource` normal usage. The enum order is the locking order, so changing enum declarations changes concurrency semantics.

## Test Signals
Indirect test coverage comes from `MasterWorkerInfoTest` and block master registration/heartbeat tests. There was no direct unit test found for unsupported `Lock` operations.
