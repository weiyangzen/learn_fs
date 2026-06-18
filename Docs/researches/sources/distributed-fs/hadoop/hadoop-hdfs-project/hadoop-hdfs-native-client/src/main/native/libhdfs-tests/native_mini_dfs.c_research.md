# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/native_mini_dfs.c

## Purpose
`native_mini_dfs.c` is the JNI-backed native test harness for creating, configuring, waiting on, querying, and shutting down Hadoop `MiniDFSCluster` instances from C tests. It lets native libhdfs tests run against an in-process Java HDFS cluster without duplicating Java-side setup code in every test.

## Important APIs and types
The private `NativeMiniDfsCluster` struct owns a global JNI reference to the Java `MiniDFSCluster` object and a `domainSocketPath` buffer. Public functions implement the declarations in `native_mini_dfs.h`: `nmdCreate`, `nmdWaitClusterUp`, `nmdShutdown`, `nmdFree`, `nmdGetNameNodePort`, `nmdGetNameNodeHttpAddress`, and `hdfsGetDomainSocketPath`. Internal helpers include a local `hdfsDisableDomainSocketSecurity` and `nmdConfigureShortCircuit`.

## Control flow
`nmdCreate` gets a `JNIEnv`, allocates the cluster wrapper, creates a Hadoop `Configuration`, disables minimum block-size validation, constructs `MiniDFSCluster$Builder`, applies requested options (`format`, `nameNodeHttpPort`, `numDataNodes`, short-circuit configuration), calls `build`, and promotes the Java cluster object to a global reference. On any failure it prints and clears the Java exception, deletes local references, frees the wrapper, and returns `NULL`.

`nmdConfigureShortCircuit` disables domain socket path validation, sets `dfs.client.read.shortcircuit=true`, creates a per-process temporary socket path under `$TMPDIR` or `/tmp`, and stores it into `dfs.domain.socket.path`. `nmdWaitClusterUp` and `nmdShutdown` are thin JNI calls to `MiniDFSCluster#waitClusterUp` and `#shutdown`. `nmdGetNameNodeHttpAddress` walks `MiniDFSCluster#getNameNode`, `NameNode#getHttpAddress`, then `InetSocketAddress#getPort` and `getHostName`.

## State and persistence
State is entirely runtime: a Java global reference and an optional domain socket path string. The MiniDFS storage lifecycle is controlled by the Java cluster and by `doFormat` in `NativeMiniDfsConf`. The HTTP hostname returned by `nmdGetNameNodeHttpAddress` is `strdup`ed and must be freed by callers.

## Dependencies
This file depends on `jni_helper` for object construction, method invocation, and C/Java string conversion; `jclasses` for cached class IDs; `exception` for errno mapping and diagnostics; Hadoop Java classes `MiniDFSCluster`, `MiniDFSCluster$Builder`, `NameNode`, and `InetSocketAddress`; and POSIX APIs for `getpid`, `getenv`, and path sizing.

## Risks
The domain socket path is produced with `rand()` and process id, so collision risk is low but not cryptographically strong. The code contains a duplicated `snprintf` for `domainSocketPath`, which is harmless but suspicious. `nmdFree` assumes a non-NULL cluster pointer and valid JNI environment; callers must call it only for successfully created clusters. HTTP hostname ownership is transferred as a heap string, and failure to free it leaks memory in long-running tests.

## Test signals
`test_native_mini_dfs.c` covers basic create, wait, shutdown, and free. `test_libhdfs_ops.c`, `test_libhdfs_threaded.c`, `test_libhdfs_zerocopy.c`, and `test_libhdfs_mini_stress.c` all depend on this harness for real HDFS integration coverage, including short-circuit reads and configurable datanode counts.
