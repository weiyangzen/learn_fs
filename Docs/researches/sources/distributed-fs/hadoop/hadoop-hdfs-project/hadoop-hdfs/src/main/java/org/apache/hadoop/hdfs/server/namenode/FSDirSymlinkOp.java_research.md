# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirSymlinkOp.java

## Purpose
`FSDirSymlinkOp` creates HDFS symbolic links and replays symlink creation edits.

## Important APIs, Types, And Functions
- `createSymlinkInt` is the checked operation.
- `unprotectedAddSymlink` constructs and inserts an `INodeSymlink`.
- `addSymlink` handles parent creation, inode ID allocation, edit logging, and metrics/logging.

## Control Flow
The checked path validates the link name, rejects reserved or empty targets, resolves the link with `WRITE_LINK`, optionally verifies the parent exists, rejects existing/invalid targets for creation, checks ancestor write access, checks object limits, then calls `addSymlink` under the directory write lock. Parent directories may be created through `FSDirMkdirOp.createAncestorDirectories`. The created symlink gets default symlink permission with user from directory permissions and no group.

## State And Persistence Behavior
The operation allocates an inode ID, inserts `INodeSymlink`, sets local name/target/mtime/atime, logs `logSymlink`, and increments create-symlink metrics. Replay uses `unprotectedAddSymlink` with supplied inode ID and timestamps.

## Dependencies And Integration Points
It depends on `DFSUtil` name validation, `FSDirectory` path/create checks and quota insertion, `FSNamesystem` object-limit checks, `FSDirMkdirOp` for implicit ancestors, `INodeSymlink`, and `FSEditLog`.

## Risks And Edge Cases
The target is a string and is not resolved, but reserved or empty target names are rejected. The link path uses `WRITE_LINK` so the link itself is created rather than following a symlink. Parent creation must use directory permissions while the symlink inode itself gets default symlink permissions. Failure to add after parent creation returns null from the helper, but the checked wrapper still returns audit info for the original IIP.

## Test Signals
Tests should cover invalid link names, reserved/empty targets, createParent true/false, existing path rejection, ancestor permission denial, object-limit failure, edit-log replay preserving ID/times/target, symlink metrics, and link creation in paths containing symlink components.
