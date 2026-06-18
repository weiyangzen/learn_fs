# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_truncate.c

## Purpose
Implements a limited truncate operation for size zero.

## Important APIs, Types, And Functions
`dfs_truncate(const char *path, off_t size)` delegates deletion to `dfs_unlink`, then recreates an empty file with `hdfsOpenFile(O_WRONLY | O_CREAT)` and closes it.

## Control Flow
If size is nonzero, return success without changing the file. For size zero, delete the path, borrow connection, create an empty file, close it, release connection.

## State, Persistence, And Dependencies
Persists file replacement in HDFS. It does not preserve old metadata such as owner, group, permissions, or times.

## Integration Points
Registered as `.truncate` and used by workload tests that truncate written files to zero length.

## Risks
Nonzero truncate is a no-op success, which is semantically wrong. Zero truncate is delete-and-recreate, so metadata and atomicity are lost and protected path behavior depends on `dfs_unlink`.

## Test Signals
Workload verifies truncate-to-zero size. Tests should add nonzero truncate and metadata preservation expectations.
