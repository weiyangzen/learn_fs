# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_chmod.c

## Purpose
Implements POSIX chmod by forwarding to HDFS permission changes.

## Important APIs, Types, And Functions
`dfs_chmod(const char *path, mode_t mode)` obtains a thread-UID connection and calls `hdfsChmod(fs, path, (short)mode)`.

## Control Flow
Validate path/context, borrow connection, call HDFS chmod, map errno to negative FUSE error, release connection, return.

## State, Persistence, And Dependencies
Persists only HDFS metadata changes. Depends on FUSE private context, connection cache, libhdfs chmod, and errno.

## Integration Points
Registered as `.chmod`; uses user-specific HDFS connections from `fuse_connect`.

## Risks
Mode is truncated to `short`. Protected path checks are not applied here, so protected files can still have permissions changed. Most connection errors collapse to `-EIO`.

## Test Signals
Native workload TODOs note chmod coverage is missing; tests should verify mode propagation and permission-denied mapping.
