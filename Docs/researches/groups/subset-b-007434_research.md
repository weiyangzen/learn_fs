# subset-b-007434 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/hdfs_test.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/hdfs_test.h

## Purpose
`hdfs_test.h` is a private test-only header for libhdfs internals. It exposes a narrow set of functions from `libhdfs/hdfs.c` that are intentionally not part of the normal exported API but are needed by native tests to force and inspect direct-read behavior and domain socket security.

## Important APIs and types
The file forward-declares `struct hdfsFile_internal`, matching the private `hdfsFile` implementation in `hdfs.c`. It declares `hdfsFileUsesDirectRead`, `hdfsFileDisableDirectRead`, `hdfsFileUsesDirectPread`, `hdfsFileDisableDirectPread`, and `hdfsDisableDomainSocketSecurity`.

## Control flow and integration
Tests include this header to verify capability detection after `hdfsOpenFile` or async open creates an input stream. The disable functions mutate the `flags` field inside `hdfsFile_internal` so tests can drive the fallback Java byte-array read paths after first exercising the direct `ByteBuffer` paths.

## State and persistence
The header itself has no persistent state. It exposes mutators for per-file in-memory capability bits and a process/JVM-level helper that disables Hadoop domain socket bind-path validation for short-circuit read tests.

## Dependencies
It depends only on the private shape of libhdfs, specifically the existence of `struct hdfsFile_internal` and the corresponding implementations in `hdfs.c`. It is guarded for C++ callers with `extern "C"`.

## Risks
Because this is a test-only header, accidentally installing or treating it as a public ABI would expose private internals and allow callers to corrupt stream capability state. Tests using the disable functions must keep direct-read and direct-pread semantics separate; `test_libhdfs_ops.c` explicitly checks that disabling one flag does not disable the other.

## Test signals
`test_libhdfs_ops.c` uses this header to validate direct read and direct pread capability detection and fallback. Zero-copy and stress tests indirectly rely on the same short-circuit/domain-socket support but use public zero-copy APIs rather than these test hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/hdfs_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/native_mini_dfs.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/native_mini_dfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/native_mini_dfs.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/native_mini_dfs.h

## Purpose
`native_mini_dfs.h` defines the C test-facing interface for controlling a Java `MiniDFSCluster` from native libhdfs tests.

## Important APIs and types
The key type is `struct NativeMiniDfsConf`, with `doFormat`, `webhdfsEnabled`, `namenodeHttpPort`, `configureShortCircuit`, and `numDataNodes`. The cluster object is opaque as `struct NativeMiniDfsCluster`. The header declares lifecycle, wait, NameNode port, NameNode HTTP address, and domain socket path accessors.

## Control flow and integration
Tests initialize `NativeMiniDfsConf`, call `nmdCreate`, wait with `nmdWaitClusterUp`, read the RPC port with `nmdGetNameNodePort`, connect with `hdfsBuilder`, then call `nmdShutdown` and `nmdFree`. Zero-copy tests additionally enable `configureShortCircuit` and pass `hdfsGetDomainSocketPath` into the libhdfs builder configuration.

## State and persistence
The header describes the desired Java cluster state but owns no storage. The configuration fields are consumed at cluster construction time. The opaque cluster owns runtime state inside `native_mini_dfs.c`.

## Dependencies
It includes `jni.h` for `jboolean` and `jint`, forward-declares `struct hdfsBuilder`, and uses C++ linkage guards.

## Risks
The struct is a native test contract, so changing field order or meaning can silently alter test cluster setup. The comments mention non-HA assumptions for NameNode accessors; future HA MiniDFS support would need API changes or clearer selection semantics.

## Test signals
Every MiniDFS native integration test includes this header. Basic lifecycle coverage is in `test_native_mini_dfs.c`; operational, threaded, stress, and zero-copy tests exercise richer combinations of its configuration fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/native_mini_dfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/test_libhdfs_mini_stress.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/test_libhdfs_mini_stress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/test_libhdfs_ops.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/test_libhdfs_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/test_libhdfs_threaded.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/test_libhdfs_threaded.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/test_libhdfs_zerocopy.c -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/test_libhdfs_zerocopy.c

## Purpose
`test_libhdfs_zerocopy.c` validates libhdfs zero-copy read APIs against a MiniDFSCluster configured for short-circuit reads. It checks buffer contents, read statistics, checksum/pool option behavior, zero-length reads, EOF handling, and release semantics.

## Important APIs and helpers
`getZeroCopyBlockData` creates deterministic block contents. `getZeroCopyBlockLen` models five full blocks and one shorter final block. `createZeroCopyTestFile` writes the deterministic file. `nmdConfigureHdfsBuilder` configures the builder with NameNode port and optional short-circuit domain socket path. `doTestZeroCopyReads` exercises `hadoopRzOptions`, `hadoopReadZero`, `hadoopRzBufferGet`, `hadoopRzBufferLength`, and `hadoopRzBufferFree`.

## Control flow
The test starts a formatted MiniDFSCluster with `configureShortCircuit=1`, configures a forced-new HDFS builder with block size and `dfs.client.read.shortcircuit.skip.checksum=true`, writes a deterministic file, then reads it through zero-copy. It first reads half-block chunks and a small read with `skipChecksum` enabled, validates file statistics, disables skip-checksum with no `ByteBufferPool` and expects `EPROTONOSUPPORT`, then sets `ElasticByteBufferPool` and verifies reads succeed. It finally checks zero-length read returns a non-NULL empty buffer and EOF returns a buffer with NULL data.

## State and persistence
The test creates a random `/zeroCopyTestFile.<pid>.<rand>` path in the MiniDFSCluster. `hadoopRzOptions` caches options and optional byte buffer pool state. Each returned `hadoopRzBuffer` must be released to the stream with `hadoopRzBufferFree`.

## Dependencies
It depends on `native_mini_dfs`, libhdfs zero-copy APIs, `expectFileStats` from `expect.c`, short-circuit local reads, domain socket configuration, and Java `ElasticByteBufferPool`.

## Risks
Zero-copy behavior is sensitive to platform support for domain sockets, mmap/direct buffers, short-circuit configuration, and checksum settings. The test exits directly on allocation failure in `getZeroCopyBlockData`, so failures there bypass cluster cleanup. The expected statistics depend on Hadoop `ReadStatistics` semantics and can break if counters change.

## Test signals
Primary signals are exact byte comparisons for split block boundaries, expected `hdfsTell`, read statistics totals including zero-copy bytes, `EPROTONOSUPPORT` when no pool/checksum combination is unsupported, success with a ByteBufferPool, correct zero-length and EOF buffer shapes, and clean cluster shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/test_libhdfs_zerocopy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/test_native_mini_dfs.c -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/test_native_mini_dfs.c

## Purpose
`test_native_mini_dfs.c` is the smallest lifecycle test for the native MiniDFSCluster wrapper. It verifies that the JNI bridge can create a formatted cluster, wait for it to become active, shut it down, and free native resources.

## Important APIs and types
The file defines a static `NativeMiniDfsConf` with `doFormat=1` and uses `nmdCreate`, `nmdWaitClusterUp`, `nmdShutdown`, and `nmdFree`.

## Control flow
`main` creates the cluster, expects a non-NULL pointer, waits for startup, shuts down, frees the wrapper, and returns zero. Failures are handled by `EXPECT_*` macros from `expect.h`.

## State and persistence
The only state is the formatted MiniDFSCluster created for the test process. No files are created through libhdfs in this test.

## Dependencies
It depends on `native_mini_dfs.h`, `expect.h`, JNI and Hadoop classes loaded by the implementation, and errno only through included support.

## Risks
This test does not cover NameNode port lookup, WebHDFS, short-circuit setup, datanode count, or libhdfs connections. It is a fast sentinel for JVM/classpath/MiniDFS lifecycle breakage rather than functional HDFS behavior.

## Test signals
Passing this test confirms that native tests can start the embedded Java MiniDFSCluster and tear it down cleanly. Failure usually indicates classpath, JNI initialization, MiniDFS construction, or shutdown invocation problems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/test_native_mini_dfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/vecsum.c -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/vecsum.c

## Purpose
`vecsum.c` is a native benchmark and correctness utility for comparing local mmap reads, normal libhdfs reads, and libhdfs zero-copy reads while summing deterministic double values. It is built as `test_libhdfs_vecsum` on non-Windows platforms but behaves more like a configurable microbenchmark than a self-contained unit test.

## Important APIs and types
Key types are `options`, `local_data`, `libhdfs_data`, and `stopwatch`. `parse_vecsum_type` accepts `local`, `libhdfs`, or `zcr`. Data setup uses `test_file_chunk_setup`, `local_data_create_file`, `local_data_create`, `libhdfs_data_create_file`, and `libhdfs_data_create`. Read paths are `vecsum_local`, `vecsum_libhdfs` through `hdfsReadFully`, and `vecsum_zcr` through `hadoopReadZero`. The summation implementation uses SSE intrinsics when `HAVE_INTEL_SSE_INTRINSICS` is defined and scalar fallback otherwise.

## Control flow
`main` validates chunk-size alignment, reads environment-driven options, prepares either local or HDFS data, starts a stopwatch, runs the selected read/sum mode for `VECSUM_PASSES`, prints per-pass sums, and reports aggregate throughput. If the target file is absent or has the wrong length, setup rewrites it with deterministic chunks. HDFS setup connects using `VECSUM_RPC_ADDRESS` or `default`, enables short-circuit checksum skipping, validates path info, and opens the file for reading.

## State and persistence
The benchmark may create or rewrite `VECSUM_PATH` either locally or in HDFS to `VECSUM_LENGTH` bytes. It allocates 8 MiB chunks and read buffers. Local mode mmaps the file; HDFS mode keeps an `hdfsFS` and `hdfsFile`; zero-copy mode keeps `hadoopRzOptions` and releases each returned buffer.

## Dependencies
It depends on POSIX file APIs, `mmap`, `clock_gettime` or Mach clock APIs on macOS, optional SSE2 intrinsics, `config.h`, and libhdfs read and zero-copy APIs. CMake links it with threads and `rt` on non-Darwin Unix.

## Risks
The environment contract is strict: `VECSUM_PATH`, `VECSUM_PASSES`, and `VECSUM_TYPE` are required, while `VECSUM_LENGTH` must be an 8 MiB multiple. The HDFS writer expects full 8 MiB writes and treats short writes as errors. Zero-copy mode treats partial reads smaller than the configured chunk as invalid, so it assumes file length and read size alignment. The local cleanup frees the struct but does not itself unlink files; benchmark data persists by design.

## Test signals
Useful signals are successful deterministic file creation, equal-looking per-pass sums across local/libhdfs/zcr modes, no partial reads, no zero-copy errors, and stopwatch throughput output. It is skipped on Windows because it uses `sys/mman.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/vecsum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/CMakeLists.txt

## Purpose
This CMake file defines the native libhdfs build target, object reuse, link dependencies, output configuration, and several native test executables for Hadoop's HDFS native client.

## Important build targets
`HDFS_SOURCES` includes `exception.c`, `jni_helper.c`, `hdfs.c`, `jclasses.c`, and OS-specific mutex and thread-local storage implementations. `hdfs_obj` is an object library built as position-independent code. `hadoop_add_dual_library(hdfs ...)` creates the dual static/shared libhdfs target from `hdfs_obj`, x-platform objects, and x-platform C API objects. Test targets include `test_libhdfs_ops`, `test_libhdfs_threaded`, `test_libhdfs_zerocopy` on non-Windows/non-Apple, and `test_libhdfs_vecsum` on non-Windows.

## Control flow and integration
The file sets `LIBHDFS_DLL_EXPORT`, configures include directories for generated JNI headers, native sources, OS abstractions, and libhdfspp, then builds reusable objects before linking the public hdfs library with JVM, optional `dl`, and OS libraries. Test helper macros build, link, and register tests against `hdfs_static`, `native_mini_dfs`, OS thread code, and platform-specific libraries.

## State and persistence
Build state is CMake target state. It sets libhdfs `SOVERSION` to `0.0.0` and uses `hadoop_dual_output_directory` to place outputs under `${OUT_DIR}`.

## Dependencies
It depends on Hadoop's native CMake helper macros, `${JNI_INCLUDE_DIRS}`, `${JAVA_JVM_LIBRARY}`, `${OS_DIR}`, `${OS_LINK_LIBRARIES}`, `x_platform` object targets, and platform tests for `NEED_LINK_DL`, `WIN32`, `APPLE`, and `CMAKE_SYSTEM_NAME`.

## Risks
Tests are platform-gated, so zero-copy and vecsum coverage can disappear on Windows/macOS. `hdfs_obj` exists to reuse objects without public link dependencies; changes to target linking can accidentally pull JVM linkage into helper binaries or omit required platform objects. The include path reaches into `../libhdfspp/lib`, making libhdfs tests sensitive to adjacent native-client layout.

## Test signals
Successful configuration should produce libhdfs and register the native tests. Link failures usually reveal missing JNI, JVM, dl, thread, rt, or OS abstraction dependencies. Platform-specific skips are intentional.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/exception.c -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/exception.c

## Purpose
`exception.c` centralizes libhdfs conversion of Java exceptions into POSIX-style errno values, stderr diagnostics, and thread-local root-cause/stack-trace strings.

## Important APIs and data
`gExceptionInfo` maps Java class names to no-print flags and errno values for file-not-found, access control, unresolved link, parent-not-directory, illegal argument, out-of-memory, safe mode, already-exists, quota exceeded, unsupported operation, and lease expired. Public functions include `getExceptionInfo`, `printExceptionAndFreeV`, `printExceptionAndFree`, `printPendingExceptionAndFree`, `getPendingExceptionAndClear`, and `newRuntimeError`. `getExceptionUtilString` calls Hadoop `ExceptionUtils` methods to extract root cause and stack trace strings.

## Control flow
Callers pass either an explicit `jthrowable` or rely on the pending JNI exception. The code determines the Java exception class, maps it to errno and print suppression policy, fetches root cause and stack trace, saves both in thread-local storage through `setTLSExceptionStrings`, optionally prints the supplied context plus exception details, deletes the local exception reference, and returns the mapped errno.

`printPendingExceptionAndFree` checks `ExceptionOccurred`, clears it if present, and delegates to the varargs implementation. `newRuntimeError` formats a C message into a Java `RuntimeException`, returning pending OOM exceptions if string or object construction fails.

## State and persistence
The persistent effect is per-thread exception diagnostic state exposed by `hdfsGetLastExceptionRootCause` and `hdfsGetLastExceptionStackTrace` in `hdfs.c`. The mapping table is static read-only process state. JNI local references are explicitly destroyed.

## Dependencies
It depends on `jni_helper` for method invocation, class-name extraction, and C string conversion; `jclasses` for `ExceptionUtils`; `platform.h`; and thread-local exception string storage from the JNI helper layer.

## Risks
Unknown exception classes map to `EINTERNAL`, which may hide more specific Java failures. `getExceptionInfo` uses `strstr(gExceptionInfo[i].name, excName)`, while `printExceptionAndFreeV` uses exact class-name comparison; callers passing partial names can see different behavior. If `ExceptionUtils` itself fails, diagnostics are degraded but the original exception is still consumed. Root cause and stack trace strings must be managed correctly by TLS storage to avoid leaks across repeated failures.

## Test signals
`test_libhdfs_threaded.c` checks TLS root cause and stack trace after an expected missing-file failure. Many tests depend on specific errno mappings such as `ENOENT`, `EACCES`, `EINVAL`, and `EPROTONOSUPPORT` for assertions and expected failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/exception.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/exception.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/exception.h

## Purpose
`exception.h` documents and declares the libhdfs JNI exception handling contract: clear Java exceptions promptly, return local `jthrowable` references to callers, translate handled exceptions to errno, and store last exception diagnostics in thread-local state.

## Important APIs and definitions
The header defines print-suppression flags `PRINT_EXC_ALL`, `NOPRINT_EXC_FILE_NOT_FOUND`, `NOPRINT_EXC_ACCESS_CONTROL`, `NOPRINT_EXC_UNRESOLVED_LINK`, `NOPRINT_EXC_PARENT_NOT_DIRECTORY`, and `NOPRINT_EXC_ILLEGAL_ARGUMENT`. It declares `getExceptionInfo`, `printExceptionAndFreeV`, `printExceptionAndFree`, `printPendingExceptionAndFree`, `getPendingExceptionAndClear`, and `newRuntimeError`, with printf-format checking where available.

## Control flow and integration
libhdfs JNI wrappers call helper functions such as `invokeMethod`; when those helpers return a `jthrowable`, callers pass it to `printExceptionAndFree` with contextual text and optional no-print flags, then propagate the returned errno through `errno` and conventional C return values. Functions that detect a still-pending JNI exception call `printPendingExceptionAndFree` or `getPendingExceptionAndClear`.

## State and persistence
The header states the key state rule: root cause and stack trace strings from the last exception on a thread are stored in thread-local state and read later by public libhdfs APIs. The header itself owns no storage.

## Dependencies
It includes `platform.h`, JNI, stdio, stdlib, stdarg, search, and errno. The implementation depends on JNI helper and class cache modules.

## Risks
The correctness of the whole libhdfs C API depends on this convention. Leaving pending Java exceptions uncleared can cause undefined JNI behavior in later calls, while freeing an exception too early would lose diagnostics. No-print flags reduce log noise but can also hide unexpected recurrent failures if used too broadly.

## Test signals
Expected-error tests in threaded and ops coverage validate errno and TLS diagnostics. Compilation with `TYPE_CHECKED_PRINTF_FORMAT` catches mismatched format arguments in exception-context calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/exception.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/hdfs.c -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/hdfs.c

## Purpose
`hdfs.c` is the primary C implementation of libhdfs. It adapts the public `hdfs/hdfs.h` API to Hadoop Java `FileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FutureDataInputStreamBuilder`, zero-copy reads, file metadata, and exception/errno behavior through JNI.

## Important types and state
`hdfsFS` values are Java `FileSystem` global references cast to C handles. `struct hdfsFile_internal` wraps a Java stream global reference, an `hdfsStreamType` (`input` or `output`), and capability flags. Direct read and direct pread support are represented by `HDFS_FILE_SUPPORTS_DIRECT_READ` and `HDFS_FILE_SUPPORTS_DIRECT_PREAD`, discovered through `FSDataInputStream#hasCapability`.

Builder state is held in `struct hdfsBuilder` and linked `hdfsBuilderConfOpt` nodes until `hdfsBuilderConnect` consumes and frees the builder. Stream builder state is held in `struct hdfsStreamBuilder`. Async open uses `hdfsOpenFileBuilder` and `hdfsOpenFileFuture`, each owning Java global references. Zero-copy state is held in `hadoopRzOptions` and `hadoopRzBuffer`; options cache an EnumSet and optional ByteBufferPool, while buffers own or point to Java ByteBuffer memory until released.

## Connection and configuration control flow
`hdfsNewBuilder` creates a builder; setters record NameNode, port, user, Kerberos ticket cache, force-new flag, and configuration key/value pairs. `hdfsBuilderConnect` creates a Java `Configuration`, applies options, chooses local/default/URI connection mode, handles Kerberos cache path and user string, calls either `FileSystem#get`, `newInstance`, `getLocal`, or `newInstanceLocal`, promotes the result to a global reference, frees local references and the builder, and returns the `hdfsFS` handle. `calcEffectiveURI` prepends `hdfs://` and appends the explicit port when appropriate, rejecting duplicate URI ports.

`hdfsConfGetStr`, `hdfsConfGetInt`, and `hdfsConfStrFree` expose configuration reads through a temporary Java `Configuration`.

## File open, async open, and lifecycle
`hdfsOpenFile` wraps the stream-builder API. `hdfsOpenFileImpl` validates access mode, constructs a `Path`, fetches configuration defaults, dispatches to `FileSystem#open`, `#append`, or `#create`, stores the stream as a global reference, tags it as input or output, and sets direct-read capability flags for input streams. `hdfsCloseFile` calls the appropriate Java `close`, deletes the global ref, and frees the C wrapper. `hdfsDisconnect` closes the Java `FileSystem` and deletes the global ref.

Async open wraps Java `FutureDataInputStreamBuilder`: allocation calls `FileSystem#openFile`, `hdfsOpenFileBuilderMust` and `Opt` update builder options, build returns a Java `Future`, get methods call `Future#get` with or without `TimeUnit`, cancel maps Java boolean false to `-1`, and free methods delete global references.

## I/O control flow
`hdfsRead` and `hdfsPread` validate stream type and length. If capability flags are set, they use `NewDirectByteBuffer` and Java ByteBuffer read methods to avoid heap array copies. Otherwise they allocate Java byte arrays, call the Java read overloads, copy the returned region to the caller buffer, return zero at EOF, and return `-1` with `EINTR` for zero-byte reads. `hdfsPreadFully` has direct and byte-array variants around `readFully`.

`hdfsWrite` validates output stream type, copies C bytes into a Java byte array, calls `FSDataOutputStream#write`, and returns the full requested length because the Java stream does not report partial writes. `hdfsSeek`, `hdfsTell`, `hdfsFlush`, `hdfsHFlush`, `hdfsHSync`, `hdfsAvailable`, and `hdfsUnbufferFile` delegate to the corresponding Java stream methods.

## Metadata and filesystem operations
Path operations construct Java `Path` objects and delegate to Java `FileSystem`: `hdfsExists`, `hdfsCopy`, `hdfsMove`, `hdfsDelete`, `hdfsRename` with `Options.Rename.NONE`, working directory get/set, directory create, replication, chown, chmod, and utime. Capacity and used space come from `FsStatus`. Default block size has both filesystem and path-aware variants.

`hdfsGetHosts` calls `getFileStatus` and `getFileBlockLocations`, then builds a NULL-terminated `char***` host matrix freed by `hdfsFreeHosts`. `hdfsGetPathInfo` and `hdfsListDirectory` convert Java `FileStatus` values to `hdfsFileInfo`. To preserve binary compatibility, extended encrypted-file state is stored in padded space after the owner string and read by `hdfsFileIsEncrypted`.

## Zero-copy behavior
`hadoopRzOptionsAlloc`, `hadoopRzOptionsSetSkipChecksum`, `hadoopRzOptionsSetByteBufferPool`, and `hadoopRzOptionsFree` manage zero-copy options and cached `ReadOption` EnumSet state. `hadoopReadZero` calls `FSDataInputStream#read(ByteBufferPool, int, EnumSet)`, translates `UnsupportedOperationException` to `EPROTONOSUPPORT`, stores returned ByteBuffer as a global ref, and extracts either a direct pointer or a copied heap-backed buffer. `hadoopRzBufferFree` calls `releaseBuffer`, deletes the global ByteBuffer ref, frees copied memory if needed, and clears the buffer.

## Dependencies and integration points
This file depends heavily on `jni_helper` for JVM attachment, method invocation, class/object construction, C/Java string conversion, enum lookup, and TLS exception strings; `exception` for mapping Java failures to errno; `jclasses` for cached Java classes; and Hadoop Java classes from `org.apache.hadoop.fs`, `org.apache.hadoop.hdfs`, `java.net.URI`, `java.util.EnumSet`, `java.nio.ByteBuffer`, and `java.util.concurrent`.

## Risks
JNI reference ownership is the main risk: every successful handle stores a global ref and must delete it exactly once. Several APIs return heap memory (`hdfsFileInfo`, host matrices, config strings, read-stat structs, hedged metrics) with paired free functions. Error mapping depends on Java exception class names; new Java exception classes can become `EINTERNAL`. Direct ByteBuffer paths require stream capability detection and JVM support. The extended encrypted flag stored behind `mOwner` is ABI-preserving but fragile if callers mutate owner strings or assume allocation size. Some functions set `errno` to positive Java-mapped errors while a few internal paths use negative local values in diagnostics, so callers should rely on public return contracts.

## Test signals
`test_libhdfs_ops.c` covers basic I/O, direct/fallback read and pread, async open, metadata, permissions, append, local FS, and user connections. `test_libhdfs_threaded.c` covers concurrency, exception TLS, statistics, hedged metrics, permissions, and large listings. `test_libhdfs_zerocopy.c` covers zero-copy options and buffer semantics. `test_libhdfs_mini_stress.c` stresses concurrent shared-FS reads and injected libhdfspp errors. `vecsum.c` provides performance and zero-copy benchmark coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/hdfs.c -->
