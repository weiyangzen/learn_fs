# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_unlink.c

## Purpose
Implements file unlink, optionally routing through HDFS trash emulation.

## Important APIs, Types, And Functions
`dfs_unlink(const char *path)` checks `is_protected`, borrows a connection, and calls `hdfsDeleteWithTrash`.

## Control Flow
Validate absolute path and context, reject exact protected path, borrow connection, delete or move to trash based on mount option, map errno or `EIO`, release connection.

## State, Persistence, And Dependencies
Deletes or renames files in HDFS. Depends on mount `usetrash`, connection cache, and trash helper behavior.

## Integration Points
Registered as `.unlink`; also used by `dfs_truncate` for zero truncation.

## Risks
Exact protected matching does not protect descendants. Deleting an open file or write-in-progress is listed as untested. Trash fallback may permanently delete if move-to-trash fails.

## Test Signals
Create/remove and workload unlink/stat-ENOENT checks validate basic deletion.
