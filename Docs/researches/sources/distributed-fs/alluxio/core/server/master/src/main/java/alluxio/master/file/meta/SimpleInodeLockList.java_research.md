# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/SimpleInodeLockList.java

## Purpose
`SimpleInodeLockList` is the concrete lock-list implementation for a root-based `LockedInodePath`. It records the alternating edge and inode locks held during path traversal, enforces ordering invariants, supports write-lock downgrades, and releases all locks on close.

## Important APIs, Types, and Functions
It implements `InodeLockList` methods: `lockInode()`, `lockEdge()`, `lockRootEdge()`, `pushWriteLockedEdge()`, `unlockLastInode()`, `unlockLastEdge()`, `downgradeToReadLocks()`, `downgradeLastEdge()`, `getLockMode()`, `getLockedInodes()`, `get(int)`, `numInodes()`, `isEmpty()`, `endsInInode()`, `getInodeLockManager()`, and `close()`. Helpers track the last edge, first write-lock index, and edge/inode consistency.

## Control Flow, State, and Persistence
Runtime state is a linked list of locked inodes, a linked list of `RWLockResource`s, optional `mLastEdge`, and `mFirstWriteLockIndex`. Locks must alternate edge/inode; after a write lock appears, `nextLockMode()` upgrades later requested read locks to write to preserve the invariant that no read lock follows a write lock. `pushWriteLockedEdge()` moves a structural write lock forward during create by acquiring read locks on the previous edge and new inode plus a write lock on the next edge, then releasing the old write edge.

## Dependencies and Integration Points
The class delegates actual lock acquisition to `InodeLockManager` and is used by `LockedInodePath` traversal. It depends on `Edge`, `Inode`, `LockMode`, and `RWLockResource`. Composite path locking builds on a separate `CompositeInodeLockList` but relies on the same interface semantics.

## Risks
`pushWriteLockedEdge()` temporarily holds both old and new locks and must preserve ordering to avoid deadlocks. `close()` clears inode state before closing lock resources; if close ever failed midstream, diagnostic state would be reduced. `checkInodeNameAndEdgeNameMatch()` guards against stale traversal but throws an unchecked exception with proto output that may be large for deep paths.

## Test Signals
Tests should cover lock alternation preconditions, root edge behavior, read-to-write upgrade invariants, write-edge push/downgrade sequences, unlocking last inode/edge, name mismatch detection, try-lock behavior propagation, close releasing all locks, and no leaked locks through `InodeLockManager.assertAllLocksReleased()`.
