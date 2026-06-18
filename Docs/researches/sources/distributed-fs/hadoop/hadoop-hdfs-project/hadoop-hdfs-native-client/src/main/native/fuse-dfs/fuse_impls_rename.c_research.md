# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_rename.c

## Purpose
Implements POSIX rename through HDFS rename.

## Important APIs, Types, And Functions
`dfs_rename(const char *from, const char *to)` checks protected paths and calls `hdfsRename`.

## Control Flow
Validate source/destination paths, reject if either exact path is protected, borrow HDFS connection, call rename, map errno, release connection.

## State, Persistence, And Dependencies
Persists namespace movement in HDFS. Depends on libhdfs rename semantics and connection cache.

## Integration Points
Registered as `.rename`; also used conceptually by trash move implementation.

## Risks
Protected descendants are not protected by exact matching. POSIX overwrite/atomicity semantics may differ from HDFS rename behavior.

## Test Signals
Native workload renames directory `a` to `c` and validates directory listing changes.
