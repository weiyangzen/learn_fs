# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_mkdir.c

## Purpose
Implements directory creation in HDFS.

## Important APIs, Types, And Functions
`dfs_mkdir(const char *path, mode_t mode)` checks `is_protected`, calls `hdfsCreateDirectory`, then `hdfsChmod`.

## Control Flow
Validate context and absolute path, reject exact protected paths, borrow connection, create directory, chmod it to requested mode, release connection, return mapped errno.

## State, Persistence, And Dependencies
Persists new HDFS directories and permission metadata. Depends on connection cache, libhdfs create/chmod, and protected path option state.

## Integration Points
Registered as `.mkdir`; used by workload tests and trash directory creation indirectly in `fuse_trash.c`.

## Risks
Create and chmod are not atomic. The code sets `ret = 0` after chmod block even if chmod set an error, so chmod failure may be swallowed. Protected path matching is exact.

## Test Signals
Directory create/list/remove tests validate basic behavior; permission-mode tests should catch the chmod return issue.
