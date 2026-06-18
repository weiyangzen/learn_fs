# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_create.c

## Purpose
Implements FUSE create by delegating to open.

## Important APIs, Types, And Functions
`dfs_create(const char *path, mode_t mode, struct fuse_file_info *fi)` ORs `mode` into `fi->flags` and calls `dfs_open`.

## Control Flow
Trace, mutate flags, return `dfs_open(path, fi)`.

## State, Persistence, And Dependencies
State effects occur in `dfs_open`: HDFS file creation and file-handle allocation. This file itself only changes the flags field.

## Integration Points
Registered as `.create` and shares all open behavior, including HDFS flag translation.

## Risks
ORing permission mode into open flags is semantically unusual; POSIX mode bits are not open flags. Actual chmod after create is not handled here.

## Test Signals
Create/touch tests validate that delegated open creates files, but mode propagation needs separate chmod/stat coverage.
