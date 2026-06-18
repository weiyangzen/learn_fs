# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/PinnedInodeFileIds.java

## Purpose
`PinnedInodeFileIds` is a checkpointed set of file inode ids whose files are pinned. It is a small type marker over `CheckpointedIdHashSet` so this derived index has a distinct checkpoint name.

## Important APIs, Types, and Functions
The only override is `getCheckpointName()`, returning `CheckpointName.PINNED_INODE_FILE_IDS`. Set operations, checkpoint serialization, and restoration are inherited from `CheckpointedIdHashSet`.

## Control Flow, State, and Persistence
The set is maintained by `InodeTreePersistentState`, especially through `setReplicationForPin()` and delete/create replay. It is checkpointed with the inode tree's auxiliary state but is not directly journaled as standalone operations.

## Dependencies and Integration Points
`InodeTreePersistentState.getPinnedInodeFileIds()` exposes an unmodifiable view, and `InodeTree.getPinIdSet()` forwards it. Pinning operations, replication minimum updates, and checkpoint restore depend on this set for efficient scans of pinned files.

## Risks
Because this is a derived index, bugs in inode update replay can desynchronize it from actual inode fields. Tests should validate index consistency after replay and checkpoint restore, not just direct set behavior.

## Test Signals
Signals include pin/unpin file operations, directory recursive pinning, deleting pinned files, checkpoint restore, and journal replay where pinned state and replication min interact.
