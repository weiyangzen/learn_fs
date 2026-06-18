# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/test_libhdfs_ops.c

## Purpose
`test_libhdfs_ops.c` is the broad MiniDFS-backed smoke and regression test for the libhdfs C API. It validates connection modes, file I/O, direct and fallback reads, positioned reads, async open-file builder APIs, filesystem operations, metadata, permissions, append, local filesystem behavior, and connecting as a specific user.

## Important APIs and helpers
`permission_disp` converts a permission short to an `rwx` string for diagnostic output. `shutdown_and_exit` centralizes failing cleanup by shutting down and freeing the MiniDFSCluster before process exit. The `main` function directly exercises the public libhdfs API surface plus the private hooks from `hdfs_test.h`.

## Control flow
The test starts a formatted MiniDFSCluster, builds a forced-new HDFS connection to localhost, disables datanode replacement on append failure, and also connects to the local filesystem. It writes `/tmp/testfile.txt`, verifies `tell`, `flush`, and `hflush`, then reads it through the direct read path and forced non-direct fallback path.

The positioned-read section opens the same file, validates direct `hdfsPread` and `hdfsPreadFully`, confirms positioned reads do not alter file position, disables only direct pread, and repeats through the fallback path. It then tests that local filesystem streams do not falsely report direct read or pread support.

The async open section uses `hdfsOpenFileBuilderAlloc`, `hdfsOpenFileBuilderOpt`, `hdfsOpenFileBuilderBuild`, `hdfsOpenFileFutureGet`, `hdfsOpenFileFutureGetWithTimeout`, cancellation after completion, and future cleanup. Generic operations then cover copy, move, rename, mkdir, replication, working directory, capacity/used, path info, empty and non-empty list, block hosts, chown, chmod, utime, and deletes. Later blocks test append semantics and connection as user `nobody`.

## State and persistence
All remote paths live under `/tmp` in the MiniDFSCluster, and local filesystem paths reuse `/tmp/testfile.txt` and `/tmp/testfile2.txt`. The test accumulates `totalResult`; many operation failures add to this counter rather than exiting immediately. On severe setup or correctness failures it calls `shutdown_and_exit`.

## Dependencies
The test depends on `native_mini_dfs`, `hdfs/hdfs.h`, private `hdfs_test.h`, `expect.h`, POSIX flags and sleep, time functions, and Hadoop Java behavior behind libhdfs.

## Risks
The test assumes the user and group names `root`, `users`, and `nobody` are meaningful enough in the MiniDFS permission model. It uses fixed `/tmp` paths, so stale state could matter if cleanup fails, although the cluster is formatted. It does not always free host arrays from `hdfsGetHosts` in the visible path, making it more of a process-level test than a leak-sensitive loop. Many checks are sequential and broad, so one early failure can obscure later coverage.

## Test signals
Important assertions include direct read and pread capability bits, preservation of file position after positioned reads, correct fallback after disabling direct flags, async open/future behavior, metadata matching after chown/chmod/utime, append file size and contents, local filesystem direct-capability negatives, and owner correctness for `hdfsConnectAsUserNewInstance`.
