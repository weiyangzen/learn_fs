# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_open.c

## Purpose
Opens HDFS files for FUSE and creates per-handle state with optional read buffering.

## Important APIs, Types, And Functions
`get_hdfs_open_flags` translates POSIX/FUSE flags to libhdfs flags. `dfs_open` allocates `dfs_fh`, borrows a connection, calls `hdfsOpenFile`, initializes a mutex, and allocates a read buffer for read handles.

## Control Flow
Flag translation returns read-only for reads, write-only for truncate/new files, append for existing write-only files, and read-only for existing non-empty `O_RDWR` files. `dfs_open` then opens libhdfs, initializes handle state, stores it in `fi->fh`, or unwinds all resources on failure.

## State, Persistence, And Dependencies
Per-open state includes hdfs file handle, connection reference, mutex, and read buffer. HDFS namespace state can change when `O_TRUNC` or create maps to `O_WRONLY`.

## Integration Points
Used by `.open` and `.create`, and underpins read/write/flush/release callbacks.

## Risks
POSIX semantics are intentionally approximated because libhdfs lacks true `O_RDWR` and overwrite semantics. Existing non-empty `O_RDWR` becomes read-only; existing `O_WRONLY` becomes append; append/random write behavior can surprise applications. Error path uses `ret = -flagRet` even when `flagRet` is already negative, which can return positive errno in the no-file/no-create case.

## Test Signals
Random-access tests expecting unsupported overwrite/append behavior and workload open/truncate tests validate these compromises.
