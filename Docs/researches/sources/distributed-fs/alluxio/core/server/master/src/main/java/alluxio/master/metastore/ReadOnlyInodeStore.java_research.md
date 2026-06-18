# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/ReadOnlyInodeStore.java

## Purpose
`ReadOnlyInodeStore` defines read and traversal operations for inode metadata. It provides default implementations for child iteration and descendant traversal, including closeable/skippable iterators that interact with inode path locks.

## Important APIs and Types
- `get(long, ReadOption)` fetches an inode.
- `getChildIds`, `getChildId`, `getChild`, `getChildren`, and prefix/from variants provide directory listing primitives.
- `getSkippableChildrenIterator(ReadOption, DescendantType, boolean, LockedInodePath)` returns iterators for base-only, one-level, or recursive traversal.
- `hasChildren` checks directory children.
- `allEdges` and `allInodes` are testing/debug accessors.

## Control Flow
Default `getChildren` maps child IDs to inodes and skips missing inode metadata to tolerate weakly consistent concurrent modifications. `getSkippableChildrenIterator` handles missing base paths with an empty iterator, `DescendantType.ALL` with `RecursiveInodeIterator`, `DescendantType.NONE` with a single base result, and one-level traversal by locking each child path as it is returned. The one-level iterator closes the previously locked path before advancing.

## State and Persistence
The interface owns no state. Traversal state lives in iterator objects and locked paths; persistence is implementation-specific.

## Dependencies and Integration Points
Uses `LockedInodePath`, `InodeTree.LockPattern`, `DescendantType`, `CloseableIterator`, and inode view/result types. It is a central read abstraction for file-master path resolution, listing, and recursive operations.

## Risks and Edge Cases
- Iterators are weakly consistent under concurrent mutation; callers must tolerate skipped removed inodes and uncertain inclusion of new ones.
- Iterator close discipline is important because traversal can hold inode path locks.
- One-level traversal uses `WRITE_EDGE` locking, so incorrect caller lock ordering can deadlock elsewhere.
- Empty iterator for missing base path hides `FileDoesNotExistException` by design.

## Test Signals
Tests should cover default child iteration skipping missing inodes, prefix/from listing, all descendant modes, close releasing locked paths, `skipChildrenOfTheCurrent`, and behavior when base path disappears.
