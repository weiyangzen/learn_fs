# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/test_libhdfs_threaded.c

## Purpose
`test_libhdfs_threaded.c` validates libhdfs behavior under multiple native threads, with each thread performing a broad set of filesystem operations against a shared MiniDFSCluster. It also tests recursive JVM mutex behavior and thread-local exception capture.

## Important APIs and types
`tlhThreadInfo` holds per-thread index, success code, and native thread handle. `tlhCluster` is a global MiniDFSCluster pointer. `hdfsSingleNameNodeConnect` builds a forced-new HDFS connection and optionally sets a user name. `doTestGetDefaultBlockSize`, `setupPaths`, and `doTestHdfsOperations` are the main operation helpers. `testRecursiveJvmMutex` verifies exception printing while the global JVM mutex is already locked.

## Control flow
`main` validates recursive mutex behavior, reads `TLH_NUM_THREADS` with default 3, starts a formatted MiniDFSCluster, then spawns each native thread. Each thread connects to HDFS, creates a unique `/tlhDataNNNN` prefix, tests default block size, nonexistent and empty directory listing, failed open and TLS exception strings, invalid open mode, create/write/flush/hsync/close, directory listing, a 10,000-file listing workload, read statistics and hedged read metrics, read correctness, copy/rename/delete behavior, chown/chmod metadata, encrypted flag access, nonexistent path errors, and permission errors after reconnecting as another user.

After the main operation pass, each thread reconnects as `foo` to validate `hdfsChown` permission denial, reconnects as default user for cleanup, and deletes its prefix. `main` joins all threads, shuts down the cluster, and reports failed thread indexes.

## State and persistence
State is partitioned by thread path prefix. The test writes many files under each prefix for list pagination and stores Java exception root cause and stack trace in per-thread TLS through libhdfs. Shared global state includes `tlhCluster`, JVM state, and cached Java classes.

## Dependencies
It depends on libhdfs, `native_mini_dfs`, `jni_helper`, `exception`, native mutex and thread abstractions, and `expect.h`. It also relies on Hadoop permission enforcement and `ReadStatistics`/`DFSHedgedReadMetrics` Java APIs.

## Risks
Creating 10,000 files per thread is intentionally heavy and can dominate runtime. Threaded failures can be nondeterministic if JVM attachment, local references, global references, or exception TLS are mishandled. The test assumes permission errors map to `EACCES` and missing paths map to `ENOENT`; changes in Java exception classes can affect errno expectations.

## Test signals
Strong signals include all threads completing, TLS exception strings containing file-not-found information, read statistics increasing then clearing, hedged metrics retrieval, exact 10,000-entry directory listings, permission-denied checks for alternate users, and successful cleanup. `testRecursiveJvmMutex` specifically guards deadlock/regression risk in exception printing under recursive mutex locking.
