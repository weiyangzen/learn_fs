# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_statfs.c

## Purpose
Implements filesystem capacity reporting for FUSE.

## Important APIs, Types, And Functions
`dfs_statfs(const char *path, struct statvfs *st)` calls `hdfsGetCapacity`, `hdfsGetUsed`, and `hdfsGetDefaultBlockSize`.

## Control Flow
Zero the output struct, borrow connection, read HDFS capacity/used/block size, fill block counts and fixed inode fields, release connection.

## State, Persistence, And Dependencies
No persistence. Depends on HDFS cluster stats and default block size.

## Integration Points
Registered as `.statfs`; used by tools such as `df` and native workload `statvfs`.

## Risks
Inode fields and flags are hard-coded (`ST_RDONLY | ST_NOSUID`) and may not reflect mount mode. Division by zero would occur if default block size were zero. Capacity errors are not checked explicitly.

## Test Signals
Workload only checks that `statvfs` succeeds; stronger tests should validate plausible block values.
