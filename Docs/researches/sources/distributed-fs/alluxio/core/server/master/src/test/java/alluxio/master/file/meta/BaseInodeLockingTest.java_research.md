# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/BaseInodeLockingTest.java

## Purpose
Base fixture for inode locking tests. It builds a small inode tree `/a/b/c`, provides assertions for inode and edge lock state, and verifies teardown leaves no locks held.

## Important APIs/types/functions
- Fields: `InodeLockManager`, `HeapInodeStore`, `mRootDir`, `mDirA`, `mDirB`, `mFileC`, and `mAllInodes`.
- `after()` checks no node or edge read/write locks remain.
- Assertion helpers: `checkOnlyNodesReadLocked`, `checkOnlyNodesWriteLocked`, `checkOnlyIncomingEdgesReadLocked`, `checkOnlyIncomingEdgesWriteLocked`, `checkIncomingEdgeReadLocked`, and `checkIncomingEdgeWriteLocked`.
- Factory helpers: `inodeDir` and `inodeFile` write mutable inodes into the store and link children.

## Control flow
- Fixture construction writes root, `/a`, `/a/b`, and `/a/b/c` to the heap inode store.
- Lock checks build expected sets, assert specified locks are held by current thread, then assert all other fixture inodes/edges are unlocked.
- Subclasses perform locking and call superclass teardown to enforce cleanup.

## State and persistence behavior
- Uses in-memory heap inode store only.
- Lock state is thread-local/current-thread observable through `InodeLockManager` methods.

## Dependencies and integration points
- Supports tests for `SimpleInodeLockList`, `CompositeInodeLockList`, and related lock-list classes.
- Integrates inode store child relationships with lock manager edge identity.

## Risks and edge cases
- Fixture is fixed-depth and does not cover wide trees unless subclasses add more.
- `after()` can obscure a test's original failure if cleanup also fails, but it is valuable for leak detection.

## Test signals
- Infrastructure signal: catches lock leaks in subclasses and provides precise lock-state diagnostics.
