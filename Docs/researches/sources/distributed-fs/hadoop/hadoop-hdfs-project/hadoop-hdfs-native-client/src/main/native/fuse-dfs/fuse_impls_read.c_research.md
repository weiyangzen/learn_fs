# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_read.c

## Purpose
Implements FUSE reads using direct HDFS positional reads or a per-handle read-ahead buffer.

## Important APIs, Types, And Functions
`dfs_read` uses `hdfsPread`, `dfs_fh` buffer fields, and a per-file mutex. Helper `min` selects copy length.

## Control Flow
Zero-size reads return immediately. Reads at least as large as the configured buffer bypass buffering and loop directly into the caller buffer. Smaller reads lock the handle, refill the read buffer when the requested range is outside it, copy from the buffer, unlock, and assert FUSE's full-read-or-EOF rule.

## State, Persistence, And Dependencies
Updates only per-open read buffer state. Depends on immutable HDFS file contents for cached ranges, libhdfs positional read, and `dfs_context.rdbuffer_size`.

## Integration Points
Registered as `.read`; driven by shell tools, Java tests, and native workload file-read checks.

## Risks
No invalidation occurs if another writer changes the same path while a handle is open. Error handling maps pread failures to `-EIO`. Assertions use unsigned `size_t` comparisons that are always true. Large direct reads return `size_t` cast through int callback return expectations.

## Test Signals
Copy/read/cat workloads, long-string reads, EOF behavior, and concurrent file reads validate this callback.
