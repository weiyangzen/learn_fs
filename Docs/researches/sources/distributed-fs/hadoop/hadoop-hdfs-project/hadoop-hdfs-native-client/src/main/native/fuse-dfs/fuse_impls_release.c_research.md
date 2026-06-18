# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_release.c

## Purpose
Closes and frees per-file FUSE state when a file handle is released.

## Important APIs, Types, And Functions
`dfs_release(const char *path, struct fuse_file_info *fi)` calls `hdfsCloseFile`, frees read buffer, releases `hdfsConn`, destroys mutex, frees `dfs_fh`, and clears `fi->fh`.

## Control Flow
Validate context and path, close the hdfs handle if present, record `-EIO` on close failure, free all associated resources, return status.

## State, Persistence, And Dependencies
Persists close effects to HDFS and drops connection references. Depends on libhdfs close and correct `dfs_fh` lifetime.

## Integration Points
Registered as `.release`; complements open/read/write/flush.

## Risks
Close can occur asynchronously from application perspective, which test workload works around. Multiple writers to same HDFS path can overwrite each other because handles are independent.

## Test Signals
Unmount success, close-length retry workaround, and no leaked file descriptors/handles are key signals.
