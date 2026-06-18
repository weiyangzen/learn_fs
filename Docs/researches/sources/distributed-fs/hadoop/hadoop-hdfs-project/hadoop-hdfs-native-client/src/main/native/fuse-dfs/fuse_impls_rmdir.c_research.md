# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_rmdir.c

## Purpose
Implements directory removal, optionally using the trash emulation path.

## Important APIs, Types, And Functions
`dfs_rmdir` checks `is_protected`, lists directory contents with `hdfsListDirectory`, and deletes via `hdfsDeleteWithTrash`.

## Control Flow
Reject protected path, borrow connection, list directory, return `-ENOTEMPTY` if entries exist, call trash/delete helper, free listing, release connection.

## State, Persistence, And Dependencies
Persists directory deletion or trash rename in HDFS. Depends on HDFS listing/delete and mount `usetrash` option.

## Integration Points
Registered as `.rmdir`; shares deletion policy with unlink through `fuse_trash.c`.

## Risks
If `hdfsListDirectory` returns null for errors or nonexistent path with `numEntries` zero, the code may proceed to delete and return generic `-EIO`. Non-directory rmdir cases are listed as TODO in workload. Recursive delete may occur through `hdfsDeleteWithTrash` fallback.

## Test Signals
Basic mkdir/rmdir tests and workload recursive cleanup validate simple empty directory removal.
