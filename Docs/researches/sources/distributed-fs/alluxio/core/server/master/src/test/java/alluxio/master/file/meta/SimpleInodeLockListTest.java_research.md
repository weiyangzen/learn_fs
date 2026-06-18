# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/SimpleInodeLockListTest.java

## Purpose
This test validates `SimpleInodeLockList`, the low-level ordered container for inode and edge locks used by path locking.

## Important APIs, Types, and Functions
The suite exercises `lockRootEdge`, `lockInode`, `lockEdge`, `pushWriteLockedEdge`, `unlockLastInode`, `unlockLastEdge`, `downgradeToReadLocks`, `downgradeLastEdge`, `getLockMode`, `endsInInode`, `getLockedInodes`, and `numInodes`.

## Control Flow, State, and Persistence
Tests build lock sequences over `/a/b/c`, verify the aggregate lock mode, then release or downgrade from the tail. Invalid sequencing tests expect `IllegalStateException` when callers try to lock root after other locks, lock inode after inode, edge after edge, wrong edge/inode pairings, or unlock the wrong terminal type.

## Dependencies and Integration Points
The test uses `BaseInodeLockingTest`, `InodeLockManager`, and `LockMode`. It is the unit foundation for `LockedInodePath` correctness.

## Risks
The lock list enforces strict alternation and parent-child consistency. Any relaxation could introduce deadlocks or allow callers to believe a path is protected when the wrong edge is locked.

## Test Signals
Signals include read-to-write escalation tracking, write-edge push-forward behavior, full unlock to empty, root downgrade, read-after-write aggregate mode, non-root starts, invalid operation exceptions, and inode count accounting.
