# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_access.c

## Purpose
Implements the FUSE `access` callback.

## Important APIs, Types, And Functions
`dfs_access(const char *path, int mask)` asserts the path and returns success.

## Control Flow
The function traces, checks `path != NULL`, ignores `mask`, and returns `0`.

## State, Persistence, And Dependencies
No state is read or written. It depends only on common FUSE logging/assert headers.

## Integration Points
Registered in `fuse_dfs.c` as `.access`. Kernel permission behavior is mostly delegated to FUSE options such as `default_permissions` unless `nopermissions` is used.

## Risks
This is a permissive stub (`TODO: HDFS-428`), so it does not ask HDFS for access checks and can report access success incorrectly when kernel-side checks are disabled.

## Test Signals
Current tests do not deeply validate `access`; permission-sensitive tests should cover `nopermissions` and HDFS ACL interactions.
