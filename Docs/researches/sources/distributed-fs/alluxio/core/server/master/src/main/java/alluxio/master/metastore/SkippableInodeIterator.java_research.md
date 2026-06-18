# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/SkippableInodeIterator.java

## Purpose
`SkippableInodeIterator` is the closeable iterator interface for inode traversal that can prune descendants of the current inode.

## Important APIs and Types
- Extends Java `Iterator<InodeIterationResult>` and `Closeable`.
- Adds default `skipChildrenOfTheCurrent()` that throws `UnsupportedOperationException`.

## Control Flow
Consumers call `next()` to receive an inode plus its locked path, and may call an implementation-supported `skipChildrenOfTheCurrent` before the next advance to avoid traversing the current inode's children.

## State and Persistence
No state in the interface. Implementations carry traversal and lock state.

## Dependencies and Integration Points
Implemented by `RecursiveInodeIterator` and anonymous iterators in `ReadOnlyInodeStore`. Used by recursive file-master operations that may prune subtrees.

## Risks and Edge Cases
Semantics depend on implementation: unsupported implementations inherit the throwing default, base-only and one-level anonymous iterators override skip as a no-op, and recursive traversal prunes directories.

## Test Signals
Interface-level tests should exercise the default throwing behavior plus concrete implementations for skip behavior and close discipline.
