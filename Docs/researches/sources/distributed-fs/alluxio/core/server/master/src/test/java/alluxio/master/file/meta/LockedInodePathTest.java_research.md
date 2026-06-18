# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/LockedInodePathTest.java

## Purpose
`LockedInodePathTest` is the detailed lock-state contract for path traversal and extension. It validates which inode locks and edge locks are held for existing, partially missing, root, child, and descendant paths.

## Important APIs, Types, and Functions
The test constructs `LockedInodePath` with `LockPattern.READ`, `WRITE_INODE`, and `WRITE_EDGE`, then exercises `traverse`, `fullPathExists`, inode accessors, `removeLastInode`, `addNextInode`, `downgradeToRead`, `lockChild`, `lockDescendant`, and `lockFinalEdgeWrite`. It also uses `FileSystemMergeJournalContext` to test flush behavior.

## Control Flow, State, and Persistence
Tests create canonical `/a/b/c` fixtures from `BaseInodeLockingTest`, traverse paths, then assert both semantic path state and exact held locks through helper checks. Adding or removing path components moves write-edge ownership forward or releases final inode state. Merge-journal mode verifies flushes when adding intermediate inodes, downgrading, and closing.

## Dependencies and Integration Points
The file integrates `LockedInodePath` with `InodeStore`, `InodeLockManager`, `JournalContext`, global merge-inode-journals configuration, and Alluxio path parsing.

## Risks
This suite is sensitive to lock ordering and lock ownership details, which is intentional because these are deadlock and race-prevention contracts. Journal flush counts depend on exact implementation timing.

## Test Signals
Signals include existing vs missing path accessors, root lock special cases, implicit locks on descendants, child lock release after close, write-edge downgrades, final-edge locking for missing paths, and merge journal flush counts.
