# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/test_libhdfs_mini_stress.c

## Purpose
`test_libhdfs_mini_stress.c` is a concurrent native stress test for libhdfs reads against MiniDFSCluster. It focuses on shared-client read behavior, short-circuit paths, injected libhdfspp file event failures, and optional Valgrind-friendly cluster isolation.

## Important APIs and types
`tlhThreadInfo` records thread index, status, shared `hdfsFS`, and file name. `hdfsNameNodeConnect` builds a forced-new libhdfs connection with block size, replication, and IPC retry options. Data setup is either `hdfsWriteData` through libhdfs or `hdfsCurlData` through WebHDFS when `VALGRIND` is defined. `fileEventCallback1` randomly returns `DEBUG_SIMULATE_ERROR`; `fileEventCallback2` is a no-op. `doTestHdfsMiniStress` performs the read loop.

## Control flow
The normal path starts a formatted MiniDFSCluster with WebHDFS and short-circuit enabled, connects once, writes a 2 MiB file containing repeated path text, then shares the same `hdfsFS` across up to `TLH_MAX_THREADS` worker threads. Each worker first runs with error injection enabled, then with no injection and strict success expectations. The read loop repeatedly closes and reopens the file, seeks to a random record-aligned position, reads exactly the file-name string length, and validates the bytes.

Under `VALGRIND`, the program forks/execs a child process to host the JVM/MiniDFSCluster and sends RPC/HTTP connection data to the parent through a socket pair. The parent writes data through WebHDFS/curl, performs native reads under Valgrind, then signals the child to shut down.

## State and persistence
The test creates `/tlhMiniStressData/file` inside the temporary MiniDFSCluster. It uses environment variables `TLH_NUM_THREADS`, `TLH_NUM_DNS`, and `RANDOM_ERROR_RATIO`. Shared state includes one `hdfsFS` handle used by many threads and per-thread success fields. It also registers a pre-attach file monitor callback through `hdfsPreAttachFileMonitor`.

## Dependencies
It depends on `native_mini_dfs`, libhdfs C APIs, libhdfspp extension hooks from `hdfspp/hdfs_ext.h`, Hadoop short-circuit support, native thread abstraction, `expect.h`, x-platform temp-file APIs, and optional POSIX `socketpair`, `fork`, `exec`, `waitpid`, and password lookup.

## Risks
The test intentionally tolerates failures during the injected pass and relies on the following clean pass to catch memory corruption or unrecovered state. Sharing one `hdfsFS` across many threads stresses thread safety but can also make failures timing-dependent. The Valgrind path shells out to curl and depends on WebHDFS availability and local user identity. Large `TLH_MAX_THREADS` allows aggressive stress but can overwhelm small systems if configured too high.

## Test signals
Success is all worker `success` fields equal zero after the non-injected pass, clean disconnect, cluster shutdown, and protobuf cleanup. Failures point to read correctness, seek/read errno handling, shared-client safety, file event callback error recovery, or MiniDFS/WebHDFS setup.
