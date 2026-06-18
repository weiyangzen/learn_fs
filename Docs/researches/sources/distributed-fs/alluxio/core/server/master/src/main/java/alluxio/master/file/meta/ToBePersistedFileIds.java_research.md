# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/ToBePersistedFileIds.java

## Purpose
`ToBePersistedFileIds` is a checkpointed set of inode ids whose persistence state is `TO_BE_PERSISTED`. It gives persistence workers an efficient derived view of files awaiting asynchronous persistence.

## Important APIs, Types, and Functions
The class extends `CheckpointedIdHashSet` and overrides `getCheckpointName()` to return `CheckpointName.TO_BE_PERSISTED_FILE_IDS`. Set mutation and checkpoint read/write behavior are inherited.

## Control Flow, State, and Persistence
`InodeTreePersistentState.updateToBePersistedIds()` adds an inode id when its persistence state is `TO_BE_PERSISTED` and removes it for all other states. The set is checkpointed with the inode tree auxiliary state and restored alongside the inode store.

## Dependencies and Integration Points
`InodeTree.getToBePersistedIds()` exposes an unmodifiable view for persistence scheduling. File creation with async-through writes, async persist journal replay, and persistence-completion updates all depend on this derived set being maintained accurately.

## Risks
The class itself is thin; the risk is drift if any code changes persistence state without going through `InodeTreePersistentState.applyUpdateInode()` or equivalent derived-index maintenance. Checkpoint restore must keep the set consistent with inode persistence states.

## Test Signals
Tests should cover async-through file creation, async persist request replay, transition to persisted/not-persisted, delete cleanup, checkpoint restore, and consistency scans comparing the set to inode fields.
