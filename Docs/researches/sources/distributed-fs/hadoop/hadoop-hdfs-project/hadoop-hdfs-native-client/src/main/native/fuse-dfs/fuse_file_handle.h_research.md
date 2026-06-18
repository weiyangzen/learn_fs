# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_file_handle.h

## Purpose
Defines per-open-file state stored in `struct fuse_file_info::fh`.

## Important APIs, Types, And Functions
`dfs_fh` contains `hdfsFile hdfsFH`, borrowed `struct hdfsConn *conn`, read buffer pointer, buffer size/start offset, and a pthread mutex.

## Control Flow
`dfs_open` allocates and initializes this struct, read/write/flush use it, and `dfs_release` closes the hdfs file, releases connection, destroys mutex, and frees memory.

## State, Persistence, And Dependencies
Persists for one open file descriptor. Read buffer state caches an HDFS pread window; write state relies on hdfs file offset and mutex serialization.

## Integration Points
Used by open/read/write/flush/release callbacks and connection cache APIs.

## Risks
Concurrent reads and writes depend on the per-handle mutex. Leaked handles block unmount and hold libhdfs connections. The stored `hdfsConn` must outlive all file operations.

## Test Signals
Read buffering, sequential writes, flush, and release tests validate this structure's lifecycle.
