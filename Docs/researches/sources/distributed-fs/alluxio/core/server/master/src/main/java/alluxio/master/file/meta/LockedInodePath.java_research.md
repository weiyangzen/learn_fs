# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/LockedInodePath.java

## Purpose
`LockedInodePath` represents a path from the inode-tree root with the corresponding inode and edge locks held according to a chosen `LockPattern`. It is the main scoped object that higher-level file master operations use to safely inspect or mutate namespace paths.

## Important APIs, Types, and Functions
Key APIs include `traverse()`, `getInode()`, `getInodeOrNull()`, `getParentInodeDirectory()`, `getLastExistingInode()`, `getInodeList()`, `fullPathExists()`, `removeLastInode()`, `addNextInode()`, `downgradeToRead()`, `lockDescendant()`, `lockChild()`, `lockChildByName()`, `lockFinalEdgeWrite()`, and `close()`. Constructors create either a root-based lock path or a composite child path built from an existing locked prefix.

## Control Flow, State, and Persistence
The immutable target state is the URI and path components. The mutable lock state lives in an `InodeLockList`, typically `SimpleInodeLockList` or `CompositeInodeLockList` for derived paths. `traverse()` bootstraps the root edge and root inode, alternates edge and inode locks, reads children from `ReadOnlyInodeStore`, and stops when the full path exists or the next component is missing. `WRITE_EDGE` upgrades the first missing non-final edge to a write lock so structural creation can proceed. `WRITE_INODE` write-locks the final inode if it exists.

The object owns a `JournalContext` only for flushing before reducing/releasing lock scope when `MASTER_FILE_SYSTEM_MERGE_INODE_JOURNALS` is enabled and the context is a `FileSystemMergeJournalContext`. `addNextInode()`, `removeLastInode()`, `downgradeToRead()`, and `close()` call `maybeFlushJournals()` before releasing or downgrading locks.

## Dependencies and Integration Points
`InodeTree.lockInodePath()` creates these objects for almost every namespace operation. It depends on `PathUtils`, `ReadOnlyInodeStore`, `InodeLockManager`, lock-list implementations, Netty resource leak tracking, and journal contexts. Descendant and child lock methods are used by recursive delete, pinning, replication, and metadata sync.

## Risks
The class is explicitly not thread-safe and derived child paths can be invalidated by mutating the original path. Methods such as `fullPathExists()` and `getExistingInodeCount()` can become stale after local mutation unless traversal is repeated or the path object is updated. Journal flushing during lock release can throw and is wrapped as runtime failure. Composite paths require careful ownership: closing a child path must not close the prefix locks owned by the parent.

## Test Signals
Tests should exercise all three lock patterns on existing, partially existing, and missing paths; traversal through a file-as-parent failure; lock upgrade/downgrade paths; `addNextInode()` pushing the write edge forward during create; journal flush before close/downgrade when merge journals are enabled; leak detection or close discipline; and composite child path close behavior.
