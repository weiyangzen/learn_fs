# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_flush.c

## Purpose
Implements FUSE flush for write handles.

## Important APIs, Types, And Functions
`dfs_flush(const char *path, struct fuse_file_info *fi)` checks `fi->fh`, tests `O_WRONLY`, and calls `hdfsFlush`.

## Control Flow
Validate path/context/file info. If no file handle, return success. If opened write-only, retrieve `dfs_fh`, call `hdfsFlush`, return `-EIO` on failure. Read-only flush is ignored because HDFS rejects it.

## State, Persistence, And Dependencies
Persists buffered HDFS writes to the DataNode pipeline. Depends on the per-file handle and libhdfs flush semantics.

## Integration Points
Registered as `.flush`, complements `.write` and `.release`.

## Risks
Only tests `O_WRONLY`, not full `O_ACCMODE`, so flags combinations can be mishandled. Flush failure is always `-EIO`, losing errno.

## Test Signals
Write-close-read workloads indirectly validate flush/release durability; explicit fsync/flush coverage would be stronger.
