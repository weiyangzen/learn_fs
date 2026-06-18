# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/ReplicationLimitedFileIds.java

## Purpose
`ReplicationLimitedFileIds` is a checkpointed set of file inode ids whose maximum replication is not the default infinity value. It gives the master an efficient derived index for files with replication ceilings.

## Important APIs, Types, and Functions
The class extends `CheckpointedIdHashSet` and overrides `getCheckpointName()` to return `CheckpointName.REPLICATION_LIMITED_FILE_IDS`. All set and checkpoint mechanics are inherited.

## Control Flow, State, and Persistence
`InodeTreePersistentState.applyUpdateInodeFile()` adds or removes file ids when `replicationMax` changes. `setReplicationForPin()` can also add ids when pinning adjusts replication constraints. The set is written and restored as part of inode-tree checkpointing.

## Dependencies and Integration Points
`InodeTree.getReplicationLimitedFileIds()` exposes the set through persistent state. Replication management and block placement logic can use this index to find files requiring special replication enforcement.

## Risks
The set is only updated when specific journal/update paths run; any future mutation path that changes `replicationMax` must update this derived index or it will drift. The pinning helper adds ids when max is finite but does not explicitly remove ids in all unpin scenarios, so replay/update coverage is important.

## Test Signals
Tests should cover file creation with finite and infinite max replication, `UpdateInodeFileEntry` changes in both directions, pin/unpin interactions, delete cleanup, and checkpoint restore consistency against inode fields.
