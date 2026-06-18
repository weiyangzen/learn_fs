# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_mknod.c

## Purpose
Stub implementation for FUSE mknod.

## Important APIs, Types, And Functions
`dfs_mknod(const char *path, mode_t mode, dev_t rdev)` traces/debugs and returns success.

## Control Flow
No HDFS call is made; the function always returns `0`.

## State, Persistence, And Dependencies
No state changes. It depends only on common logging macros.

## Integration Points
Registered as `.mknod`, but FUSE create/open paths handle normal file creation elsewhere.

## Risks
Returning success without creating anything can confuse callers that use mknod for special files or creation. HDFS cannot represent POSIX device nodes, so success is misleading.

## Test Signals
Native workload TODOs explicitly list mknod as untested; tests should verify expected unsupported behavior rather than silent success.
