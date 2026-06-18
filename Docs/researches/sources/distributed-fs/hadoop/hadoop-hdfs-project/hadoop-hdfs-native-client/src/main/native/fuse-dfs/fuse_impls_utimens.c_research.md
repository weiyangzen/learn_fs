# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_utimens.c

## Purpose
Implements timestamp update through HDFS utime.

## Important APIs, Types, And Functions
`dfs_utimens(const char *path, const struct timespec ts[2])` converts access and modification seconds and calls `hdfsUtime`.

## Control Flow
Borrow connection, call `hdfsUtime(fs, path, mTime, aTime)`. On failure, fetch path info; missing path returns errno/ENOENT, directory failures are ignored for compatibility with tools like tar, and file failures map to errno or `EACCES`.

## State, Persistence, And Dependencies
Persists HDFS access/modification times where supported. Nanoseconds are discarded.

## Integration Points
Registered as `.utimens`; native workload uses `utime` and validates directory mtime.

## Risks
Directory timestamp failures are silently ignored. `hdfsFileInfo` fetched on failure is not freed, leaking memory. Nanosecond precision is lost.

## Test Signals
Workload validates setting directory mtime to 456; file timestamp and leak tests would improve coverage.
