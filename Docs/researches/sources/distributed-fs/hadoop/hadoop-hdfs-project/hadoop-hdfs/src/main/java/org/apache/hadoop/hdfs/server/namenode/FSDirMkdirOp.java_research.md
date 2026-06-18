# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirMkdirOp.java

## Purpose
`FSDirMkdirOp` creates HDFS directories for `mkdirs`, implicit parent creation used by file and symlink creation, and edit-log replay of directory creation.

## Important APIs, Types, And Functions
- `mkdirs` is the checked user operation.
- `createAncestorDirectories` and `createParentDirectories` create missing ancestors.
- `mkdirForEditLog` replays mkdir edits.
- `createSingleDirectory`, `addImplicitUwx`, and `unprotectedMkdir` allocate and insert `INodeDirectory` instances.

## Control Flow
`mkdirs` resolves with `DirOp.CREATE`, rejects an existing file at the target, checks ancestor write access, optionally verifies parent existence, checks FS object limits, creates missing parents with implicit user write/execute bits, creates the final directory, logs each created directory, increments file-created metrics, and returns audit status. Ancestor creation finds existing prefix inodes, computes how many components are missing, and creates each missing component under the write lock.

## State And Persistence Behavior
The operation allocates inode IDs, inserts `INodeDirectory` objects into the namespace, optionally applies ACLs on replay, updates quotas through `FSDirectory.addLastINode`, and logs each created directory with `logMkDir`. Directory creation increments the files-created metric to balance delete metrics.

## Dependencies And Integration Points
It integrates with `FSDirectory` path resolution, object-limit checks through `FSNamesystem`, ACL storage for replay, `Snapshot.CURRENT_STATE_ID`, and callers such as `FSDirWriteFileOp` and `FSDirSymlinkOp` that need implicit ancestors.

## Risks And Edge Cases
The implicit `u+wx` behavior is required so users can traverse auto-created ancestors. `createParent=false` must reject missing parents. Existing target directories are treated as success for `mkdirs`, while existing target files fail. Replay assumes parent exists and must preserve inode IDs, permissions, ACLs, and timestamps.

## Test Signals
Tests should cover existing file rejection, existing directory idempotence, parent creation on/off, implicit ancestor permissions with masked/unmasked modes, object-limit failure, ACL replay, edit-log inode ID preservation, and metrics/edit-log records per created directory.
