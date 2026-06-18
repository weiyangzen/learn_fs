# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeLockManager.java

## Purpose
`InodeLockManager` centralizes all inode-tree locking for the Alluxio file master. It supplies read/write locks for inode ids and parent-child edges without embedding locks in every inode, so large namespaces do not carry permanent lock objects for millions of files. It also provides auxiliary locks for parent metadata updates and synchronous UFS persistence exclusion.

## Important APIs, Types, and Functions
The main APIs are `lockInode(InodeView, LockMode, boolean)`, `lockInode(Long, LockMode)`, `tryLockInode(Long, LockMode)`, `lockEdge(Edge, LockMode, boolean)`, `tryLockEdge(Edge, LockMode)`, `tryAcquirePersistingLock(long)`, and `lockUpdate(long)`. The constructor registers gauges for inode and edge lock pool sizes. Testing helpers report whether the current thread holds inode or edge read/write locks and `assertAllLocksReleased()` scans both pools for leaked locks.

## Control Flow, State, and Persistence
There is no journaled state here. Runtime state is a pair of `LockPool` instances keyed by inode id and `Edge`, a striped lock array for parent timestamp/child-count updates, and a weak-valued Guava `LoadingCache<Long, AtomicBoolean>` for per-inode persistence locks. `tryAcquirePersistingLock()` uses `compareAndSet(false, true)` and returns a `Scoped` releaser that resets the boolean; callers that fail to acquire know another thread is already persisting the inode.

## Dependencies and Integration Points
`LockedInodePath`, `SimpleInodeLockList`, and `InodeTreePersistentState` are the main consumers. `InodeTree.syncPersistExistingDirectory()` uses the persisting lock to serialize UFS directory creation. `InodeTreePersistentState.updateTimestampsAndChildCount()` and `InodeTree.createPath()` use `lockUpdate()` while modifying parent metadata under only read-level inode-tree locks. Metrics are exported through `MetricsSystem` and lock-pool behavior is driven by master lock pool configuration keys.

## Risks
The parent update lock has a strict ordering rule documented in the class: callers should not hold more than one such lock and should not acquire other locks while holding it. Violating that rule can deadlock. The persisting-lock cache uses weak values, which is memory-friendly but means correctness depends on the returned `Scoped` retaining the `AtomicBoolean` while held. `lockInode(..., useTryLock=true)` still blocks through the `LockPool` retry behavior, so it should not be confused with the non-blocking `tryLockInode`.

## Test Signals
Useful tests assert current-thread read/write lock visibility, no leaked locks after path operations, correct edge/inode lock release on exceptions, parent update serialization under concurrent create/delete/rename, and single-writer behavior for concurrent `syncPersistExistingDirectory()` calls. Metrics assertions can check lock pool gauges after acquiring and releasing locks.
