# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_write.c

## Purpose
Implements sequential writes to HDFS files.

## Important APIs, Types, And Functions
`dfs_write` uses `hdfsTell` to enforce current offset, `hdfsWrite` to append bytes, and the `dfs_fh` mutex to serialize handle writes.

## Control Flow
Validate context and handle, lock the file mutex, compare HDFS current offset with requested FUSE offset, reject mismatches with `-ENOTSUP`, otherwise write requested bytes and map errors, unlock, return byte count or error.

## State, Persistence, And Dependencies
Persists file data through libhdfs. Maintains no separate write buffer. Depends on HDFS stream offset semantics.

## Integration Points
Registered as `.write`; paired with `flush` and `release`.

## Risks
Random writes and overwrites are unsupported. Partial positive writes less than requested are logged but still returned as length if no error was set, which can produce short-write behavior. Offset logging casts offsets to int.

## Test Signals
Java random-access tests expect append/overwrite failures; native workload validates sequential writes and readback.
