# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/RecursiveInodeIterator.java

## Purpose
`RecursiveInodeIterator` implements depth-first recursive traversal over inode metadata while managing `LockedInodePath` lifetimes. It supports skipping children of the current inode and resuming from a `ReadOption.startFrom` path component sequence.

## Important APIs and Types
- Implements `SkippableInodeIterator`.
- Holds a stack of child iterators paired with locked paths.
- Tracks current name components, optional `startAfter` components, the root path, the first/base inode, and whether the current inode is a directory.
- `skipChildrenOfTheCurrent()` pops the current directory iterator when the last returned inode was a directory.
- `hasNext()` computes and caches availability.
- `next()` returns `InodeIterationResult`.
- `close()` closes all stacked iterators/paths.

## Control Flow
The iterator starts with the base inode when requested, then lists directory children in sorted order. For each directory child, it locks the child path and pushes a new iterator for its children. It closes the previous locked path when advancing away. `populateStartAfter` uses the configured start path components to seek into child listings and skip earlier subtrees. `tryOnIterator` wraps iterator operations and converts checked close failures.

## State and Persistence
Traversal state is in-memory and lock-bearing. No metadata persistence occurs.

## Dependencies and Integration Points
Used by `ReadOnlyInodeStore.getSkippableChildrenIterator` for `DescendantType.ALL`. Depends on `LockedInodePath`, `InodeTree` lock patterns, `ReadOption`, and `CloseableIterator`.

## Risks and Edge Cases
- Close order is critical; leaked iterators can leak locks.
- Recursive traversal under concurrent mutation is weakly consistent and must handle disappeared children.
- `skipChildrenOfTheCurrent` only affects the current inode when it was a directory.
- Start-after path handling depends on sorted child iteration semantics from the backing store.

## Test Signals
Tests should cover depth-first order, include/exclude base, start-from resume, prefix interactions through `ReadOption`, skip-children behavior, close on partial traversal, and concurrent missing child handling.
