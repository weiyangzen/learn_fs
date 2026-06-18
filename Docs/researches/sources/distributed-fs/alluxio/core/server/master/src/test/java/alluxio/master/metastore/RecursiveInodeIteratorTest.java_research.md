# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/RecursiveInodeIteratorTest.java

Purpose: verifies recursive inode traversal order, locked path consistency, child skipping, and read-from resume behavior across inode store implementations.

Important APIs/types/functions: extends `InodeStoreTestBase`; uses `RecursiveInodeIterator`, `ReadOption`, `DescendantType.ALL`, `InodeTree`, `LockedInodePath`, `LockingScheme`, `InodeIterationResult`, `MountTable`, and mocked container/directory-id/UFS dependencies.

Control flow: `createInodeTree` builds a fixed tree under `/` with nested directories and files. `recursiveListing` locks root, obtains a skippable children iterator, and verifies each returned path and inode id in expected depth-first order, including `LockedInodePath.traverse`. `recursiveListingSkipChildren` calls `skipChildrenOfTheCurrent` for selected directories and verifies their descendants are omitted. `recursiveListingStartFrom1` uses `readFrom("a/b/c/f11")` to skip `/a/b/c/f1` but include later siblings. `recursiveListingStartFrom2` starts from `a/c/f3`, skipping earlier branches and children before that key. `recursiveListingStartFromSkipAll` starts from `z` and expects only root.

State and persistence behavior: inode/edge state is written to the parameterized store. Iteration state includes cursor position, locked path, and optional subtree skip flags.

Dependencies and integration points: tests the iterator used by recursive listing operations in the file-system master with lock-aware path traversal.

Risks: expected orders are hard-coded to current lexical/depth-first semantics. Mount behavior is mocked, so mount boundary traversal is not covered.

Test signals: strong signal for recursive listing correctness, resume cursors, and skip behavior across heap/Rocks/caching stores.
