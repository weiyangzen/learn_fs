# subset-b-007433 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestHTestCase.java -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestHTestCase.java

## Purpose
JUnit 5 coverage for the `HTestCase` helper stack used by HttpFS tests. It verifies that directory and Jetty helpers are only available when their marker annotations are present, that wait/sleep timing helpers respect the configured ratio, that an embedded Jetty server can serve a servlet, and that `@TestException` accepts expected exceptions and message patterns.

## Important APIs, Types, And Functions
`TestHTestCase` extends `HTestCase`. Test methods cover `TestDirHelper.getTestDir()`, `TestJettyHelper.getJettyServer()`, `TestJettyHelper.getJettyURL()`, `waitFor()`, `setWaitForRatio()`, `getWaitForRatio()`, `sleep()`, `@TestDir`, `@TestJetty`, and `@TestException`. `MyServlet` is a minimal `HttpServlet` that writes `foo`.

## Control Flow
Negative tests call helper accessors without annotations and expect `IllegalStateException`. Timing tests measure wall-clock elapsed time around predicates that immediately succeed or never succeed. The Jetty test installs `MyServlet` under `/bar`, starts the server returned by `TestJettyHelper`, opens the helper URL, and asserts HTTP 200 plus body content.

## State, Persistence, And Dependencies
State is per-test and comes from JUnit extensions inherited through `HTestCase`. The Jetty test opens a local socket and HTTP connection but leaves cleanup to `TestJettyHelper.afterEach`. Timing assertions depend on `org.apache.hadoop.util.Time` and tolerate 50 ms drift.

## Integration Points
This file validates the helper annotations implemented by nearby `TestDirHelper`, `TestJettyHelper`, and exception handling support in `HTestCase`. It is a signal for HttpFS tests that rely on annotation-driven test directories, servlet containers, and expected-exception wrappers.

## Risks
The timing tests can be flaky on heavily loaded hosts because they assert coarse elapsed time windows. `sleepRatio2` sets the ratio to `1` while naming suggests ratio 2, so it does not validate a non-default ratio. The Jetty test depends on local loopback networking and servlet container startup.

## Test Signals
Failures indicate broken JUnit extension setup, helper thread-local leakage, incorrect wait ratio behavior, servlet registration/startup regression, or changed exception annotation semantics.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestHTestCase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestHdfs.java -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestHdfs.java

## Purpose
Marker annotation for test methods that require a HDFS test filesystem. It is consumed by `TestHdfsHelper` during JUnit 5 extension callbacks.

## Important APIs, Types, And Functions
`@interface TestHdfs` is retained at runtime and targets methods. It has no attributes; presence alone enables setup.

## Control Flow
There is no executable control flow in the annotation. At runtime `TestHdfsHelper.beforeEach` reflects on the current test method and checks for this annotation before creating a mini-HDFS-backed configuration and test path.

## State, Persistence, And Dependencies
The annotation stores no state. Runtime retention is the key dependency because helper setup uses reflection.

## Integration Points
Used with `HTestCase`/`TestHdfsHelper` to expose `TestHdfsHelper.getHdfsConf()` and `getHdfsTestDir()` only for annotated test methods.

## Risks
Because there are no parameters, all annotated tests share the helper's fixed mini-cluster behavior unless controlled by system properties. Missing runtime retention or wrong target would silently break helper activation.

## Test Signals
Tests that call HDFS helper accessors without this annotation should fail with `IllegalStateException`; annotated tests should receive a per-test HDFS directory and configuration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestHdfs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestHdfsHelper.java -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestHdfsHelper.java

## Purpose
JUnit 5 extension helper that provisions HDFS configuration and a per-test HDFS directory for methods annotated with `@TestHdfs`. It can start a shared `MiniDFSCluster` with HttpFS-relevant features enabled.

## Important APIs, Types, And Functions
`TestHdfsHelper` extends `TestDirHelper`. Public accessors are `getMiniDFSCluster()`, `getHdfsTestDir()`, and `getHdfsConf()`. `HdfsStatement.evaluate()` prepares configuration and test path. `startMiniHdfs()` builds the singleton cluster. Constants expose test paths for encryption zone and erasure coding fixtures.

## Control Flow
`beforeEach` runs directory setup first, reflects the current method, and if `@TestHdfs` is present creates an `HdfsStatement` keyed by method name. The statement starts or reuses a mini cluster depending on `test.hadoop.hdfs`, puts the configuration and a reset `/tmp/<test>-<counter>` path into inheritable thread-locals, and returns. `afterEach` clears the HDFS thread-locals after superclass cleanup.

## State, Persistence, And Dependencies
The shared `MINI_DFS` static persists across tests. Per-test state is stored in `InheritableThreadLocal<Configuration>` and `InheritableThreadLocal<Path>`. The mini cluster uses test directories under `TEST_DIR_ROOT`, a JCEKS key provider, ACLs, xattrs, storage policy satisfier mode, WebHDFS regexes, an encryption zone, and an erasure-coded directory/file.

## Integration Points
Integrates Hadoop user test configuration, `MiniDFSCluster`, `DistributedFileSystem`, `DFSTestUtil`, `JavaKeyStoreProvider`, WebHDFS client patterns, encryption zone support, and erasure coding policy setup. HttpFS tests consume the returned conf and paths.

## Risks
The singleton cluster creates shared mutable state across tests; only the per-test path is reset. The mini cluster starts many data nodes based on the erasure coding policy, which can be expensive. A failure in encryption or erasure-coding setup blocks all annotated tests. Thread-local state must be removed to avoid cross-test contamination.

## Test Signals
Annotated tests should see non-null HDFS config and paths, writable `/tmp` and `/user`, valid encryption and erasure-coding fixtures, and expected user/ACL regex behavior. Repeated failures often point to MiniDFS startup, key-provider, or cleanup issues.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestHdfsHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestJetty.java -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestJetty.java

## Purpose
Marker annotation for test methods that need an embedded Jetty server.

## Important APIs, Types, And Functions
`@interface TestJetty` has runtime retention and method target. It has no members; marker presence activates `TestJettyHelper`.

## Control Flow
The annotation has no control flow. `TestJettyHelper.beforeEach` detects it via reflection and creates a server that tests can configure and start.

## State, Persistence, And Dependencies
No state is stored in the annotation. Runtime visibility is required for JUnit extension code.

## Integration Points
Used by `HTestCase`-style tests with `TestJettyHelper.getJettyServer()`, `getJettyURL()`, and `getAuthority()`.

## Risks
Because it carries no configuration, SSL mode or keystore selection must come from the helper instance rather than the annotation. Forgetting the annotation makes helper accessors throw `IllegalStateException`.

## Test Signals
Tests annotated with `@TestJetty` should receive a bindable Jetty server; unannotated tests should not.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestJetty.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestJettyHelper.java -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestJettyHelper.java

## Purpose
JUnit 5 extension that creates and tears down an embedded Jetty server for methods annotated with `@TestJetty`. It supports HTTP and optional HTTPS keystore configuration.

## Important APIs, Types, And Functions
Constructors choose HTTP or SSL mode. `createJettyServer()` binds a `ServerConnector` to `localhost` and a free ephemeral port. Static accessors `getAuthority()`, `getJettyServer()`, and `getJettyURL()` use an inheritable thread-local helper. `beforeEach` and `afterEach` implement JUnit extension lifecycle.

## Control Flow
On `beforeEach`, the helper checks the current method for `@TestJetty`; when present it creates a `Server` but does not start it. It then stores itself in `TEST_JETTY_TL`. Tests configure handlers and call `start()`. On `afterEach`, the thread-local is removed and a running server is stopped.

## State, Persistence, And Dependencies
Per-test server state is held in the helper instance and exposed through `InheritableThreadLocal`. Port selection briefly opens a `ServerSocket(0)` and then closes it before Jetty binds. HTTPS uses `SslContextFactory.Server` and keystore fields supplied to the constructor.

## Integration Points
Depends on Jetty `Server`, `ServerConnector`, `HttpConfiguration`, `HttpConnectionFactory`, optional `SslConnectionFactory`, and Hadoop `JettyUtils.HEADER_SIZE`. Test code obtains URL/authority through this helper rather than constructing ports manually.

## Risks
The free-port probe has a race between closing the probe socket and Jetty binding. The thread-local is set even for unannotated tests, but accessors still reject missing `server`. SSL tests rely on valid keystore path/type/password. Stop failures are wrapped in runtime exceptions during teardown.

## Test Signals
Expected signals are successful loopback binding, correct HTTP/HTTPS URL construction, header-size configuration, and guaranteed server stop after each annotated test.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestJettyHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/resources/hdfs-site.xml -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/resources/hdfs-site.xml

## Purpose
Test HDFS site override used by HttpFS/HDFS tests.

## Important APIs, Types, And Functions
Defines `dfs.namenode.fs-limits.min-block-size=0` in Hadoop XML configuration format.

## Control Flow
Loaded by Hadoop configuration machinery from test resources; there is no procedural control flow.

## State, Persistence, And Dependencies
The property changes in-memory test configuration and allows very small block sizes. It does not persist runtime state.

## Integration Points
Applies to tests that create tiny files or blocks in MiniDFS/HttpFS scenarios where production NameNode minimum block-size validation would otherwise reject inputs.

## Risks
Behavior differs from production defaults, so tests may pass with unrealistically small blocks. XML shape must remain standard `<configuration><property><name>...`.

## Test Signals
Failures involving tiny block-size creation can indicate this resource was not on the test classpath or the property was overridden later.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/resources/hdfs-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/resources/krb5.conf -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/resources/krb5.conf

## Purpose
Parameterized Kerberos client configuration template for security-enabled tests.

## Important APIs, Types, And Functions
Defines `[libdefaults]`, `[realms]`, and `[domain_realm]` entries using `${kerberos.realm}` substitution, localhost KDC/admin endpoints, UDP preference limit, and loopback extra address.

## Control Flow
Consumed by Kerberos-aware test setup after placeholder expansion; no code runs in this file.

## State, Persistence, And Dependencies
State is configuration-only and points all Kerberos operations at localhost port 88. Correct behavior depends on external test harness replacement of `${kerberos.realm}`.

## Integration Points
Used by HttpFS/Hadoop security tests that need a local KDC realm mapping for localhost.

## Risks
If placeholders are not substituted, Kerberos clients will see invalid realm names. Fixed localhost:88 requires the test KDC to bind that address or remap configuration.

## Test Signals
Authentication failures, missing realm errors, or KDC connection refused errors point to this resource or its test harness substitution.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/resources/krb5.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/resources/test-compact-format-property.xml -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/resources/test-compact-format-property.xml

## Purpose
Compact Hadoop configuration fixture for tests that verify XML property parsing of attributes rather than nested elements.

## Important APIs, Types, And Functions
Contains two self-closing `<property>` elements with `name` and `value` attributes: `key.1=val1` and `key.2=val2`.

## Control Flow
Loaded by configuration parsers; it has no runtime code.

## State, Persistence, And Dependencies
No persistent state. It depends on Hadoop configuration parsing support for compact property syntax.

## Integration Points
Useful for tests around HttpFS server/testserver configuration loading where both standard and compact XML forms must be accepted.

## Risks
Some XML readers or validation paths may only expect child `<name>`/`<value>` elements, so this fixture guards compatibility with attribute form.

## Test Signals
Expected signal is that both keys resolve to their values after loading. Missing values indicate parser regression for compact properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/resources/test-compact-format-property.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/resources/testserver-default.xml -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/resources/testserver-default.xml

## Purpose
Default testserver configuration fixture.

## Important APIs, Types, And Functions
Defines `testserver.a=default` in standard Hadoop XML property form.

## Control Flow
Loaded as a resource by tests; no executable code.

## State, Persistence, And Dependencies
Configuration-only state. It relies on standard Hadoop XML config parsing and classpath resource availability.

## Integration Points
Used by test-server configuration loading paths to verify default property resolution and override behavior.

## Risks
The file is intentionally small; it only validates one property and cannot detect broader parser issues.

## Test Signals
Tests should observe `testserver.a` resolving to `default` unless another resource overrides it.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/resources/testserver-default.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/pom.xml -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/pom.xml

## Purpose
Maven module descriptor for the HDFS native client jar and native build/test profiles.

## Important APIs, Types, And Functions
Declares module metadata, properties such as `require.fuse`, `require.libwebhdfs`, `native_ctest_args`, dependencies on HDFS client/common/test jars and JUnit, RAT exclusions for native trees, and profiles `native-win`, `native`, and `native-clang`.

## Control Flow
Default build produces a jar. Native profiles drive CMake compilation and CTest execution through Hadoop Maven plugin or antrun. Windows uses `cmake` plus `msbuild`; Unix and clang profiles call `cmake-compile`, then run `ctest --output-on-failure` with classpath and native library path environment variables.

## State, Persistence, And Dependencies
Generated native outputs live under Maven target directories, with distribution copies under `target/bin` on Windows and `target/native/target/usr/local/lib` on non-Windows. Tests depend on correct `CLASSPATH`, `LD_LIBRARY_PATH`/`DYLD_LIBRARY_PATH`, `HADOOP_HOME` on Windows, and optional OpenSSL/FUSE/libwebhdfs requirements.

## Integration Points
Bridges Maven lifecycle to `src/CMakeLists.txt`, native libhdfs, libhdfs++/libwebhdfs, FUSE, native tests, and Hadoop common native libraries.

## Risks
Profile behavior is platform-sensitive. Optional native components can be skipped unless their `require.*` properties are true, which can hide missing dependencies. Environment variables are central to JNI loading; incorrect library paths cause native tests to fail before assertions.

## Test Signals
Signals include successful `cmake-compile`, `msbuild` on Windows, `ctest` native test pass, and failures when required OpenSSL/FUSE/libwebhdfs components are absent.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/CMakeLists.txt -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/CMakeLists.txt

## Purpose
Top-level CMake build for the HDFS native client subtree.

## Important APIs, Types, And Functions
Configures project settings, compiler feature checks (`HAVE_BETTER_TLS`, `HAVE_INTEL_SSE_INTRINSICS`), generated `config.h`, OpenSSL detection, JNI setup, helper functions `build_libhdfs_test`, `add_libhdfs_test`, `link_libhdfs_test`, and subdirectories for libhdfs, tests, examples, libhdfs++, libwebhdfs, and FUSE.

## Control Flow
CMake sets MSVC or POSIX flags, configures JNI, checks `dlopen`, probes OpenSSL, adds core native subdirectories, conditionally builds libhdfs++ if `thread_local` works, conditionally adds libwebhdfs when required, and only adds FUSE on Linux when pkg-config finds `fuse`.

## State, Persistence, And Dependencies
Build state includes generated `config.h`, selected `OS_DIR`, output directory selection, detected OpenSSL and FUSE variables, and target objects reused by tests. It depends on `HadoopCommon`, `HadoopJNI`, C/C++ compilers, JNI headers, OpenSSL, pkg-config, and platform threading.

## Integration Points
This file is the native build entry invoked by Maven profiles. It wires libhdfs C API, native tests, examples, libhdfs++, optional libwebhdfs, and Linux FUSE client.

## Risks
Feature and library detection controls build coverage; missing optional dependencies silently skip components unless required. CMake standard toggles from C++17 to C++11 around thread_local checks can surprise subdirectories. Linux-only FUSE gating means FUSE code may be unbuilt on non-Linux CI.

## Test Signals
Configuration messages about OpenSSL, libhdfs++, libwebhdfs, and FUSE indicate coverage. `ctest` targets added by subdirectories are the runtime validation signal.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/config.h.cmake -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/config.h.cmake

## Purpose
CMake template for generated native configuration header.

## Important APIs, Types, And Functions
Defines include guard `CONFIG_H` and exposes `_FUSE_DFS_VERSION`, `HAVE_BETTER_TLS`, and `HAVE_INTEL_SSE_INTRINSICS` through `#cmakedefine`.

## Control Flow
Processed by `configure_file` in `src/CMakeLists.txt`; no runtime control flow.

## State, Persistence, And Dependencies
Persists build-time feature probes into `config.h` under the binary directory. Values depend on compiler checks and `_FUSE_DFS_VERSION`.

## Integration Points
Included by `fuse_dfs.h` and other native code needing build feature macros.

## Risks
Incorrect CMake probe values can compile code paths unsupported by the compiler or hide optimized features. The generated header must be in include directories for native targets.

## Test Signals
Build failures around undefined version or feature macros indicate configuration/header include path issues.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/config.h.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/CMakeLists.txt -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/CMakeLists.txt

## Purpose
CMake sub-build for the Linux `fuse_dfs` executable and its native integration test.

## Important APIs, Types, And Functions
Defines `flatten_list`, applies `FUSE_CFLAGS`/`FUSE_LDFLAGS`, includes JNI/libhdfs/FUSE headers, builds `fuse_dfs` from all FUSE operation and support C files, and builds `test_fuse_dfs` from C test workload utilities.

## Control Flow
The parent only enters this directory when Linux FUSE is found. This file flattens pkg-config lists into strings, sets compiler/linker flags, creates the executables, and links `fuse_dfs` with FUSE, JVM, hdfs, math, pthread, and rt.

## State, Persistence, And Dependencies
Build outputs are executables in the native build tree. Dependencies include libfuse, libjvm, libhdfs, pthread, realtime library, and the `native_mini_dfs` test library.

## Integration Points
Connects the operation files registered by `fuse_dfs.c` with libhdfs and creates the executable invoked by wrapper scripts and FUSE tests.

## Risks
`CMAKE_SKIP_RPATH TRUE` makes runtime library paths environment-dependent. FUSE flags are appended globally. The test target is not explicitly added as a CTest here, so coverage depends on parent/test wiring.

## Test Signals
Successful link of `fuse_dfs` and `test_fuse_dfs`, plus runtime mount tests, validate this build file.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_connect.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_connect.c

## Purpose
Connection manager for `fuse_dfs`, caching libhdfs filesystem handles by OS user and Kerberos ticket cache while expiring idle or stale connections.

## Important APIs, Types, And Functions
Public functions are `fuseConnectInit`, `fuseConnectAsThreadUid`, `fuseConnectTest`, `hdfsConnGetFs`, and `hdfsConnRelease`. Internals include `struct hdfsConn`, red-black tree `gConnTree`, `discoverAuthConf`, `findKerbTicketCachePath`, `fuseNewConnect`, `fuseConnect`, `hdfsConnExpiry`, and the timer thread.

## Control Flow
Initialization reads Hadoop config keys for auth, timer, and connection timeout, stores NameNode URI/port, initializes the tree mutex, and starts the expiry thread. Each FUSE operation asks for a connection as the calling UID, resolves username and optionally ticket cache path, reuses or creates a libhdfs builder-backed connection, increments refcount, and later releases it. The timer periodically condemns Kerberos connections whose ticket cache mtime changed and frees idle expired entries.

## State, Persistence, And Dependencies
Global process state includes URI, port, auth mode, timeout settings, red-black tree, mutex, and timer thread. Each connection holds username, optional ticket path/mtime, hdfsFS, refcount, condemned flag, and expiration count. It depends on libhdfs builder APIs, FUSE context UID/PID, `/proc/<pid>/environ`, Kerberos cache files, pthreads, monotonic clock, and `util/tree.h`.

## Integration Points
All operation callbacks use this module through `fuseConnectAsThreadUid` and `hdfsConnGetFs`. `dfs_init` calls `fuseConnectInit` and optional `fuseConnectTest`.

## Risks
Connection tree operations rely on correct mutex discipline. Kerberos support assumes file ticket caches and `/proc` environment readability. `hdfsConnCompare` returns a raw `strcmp` expression only under Kerberos; null kpath assumptions must hold. The expiry thread never exits cleanly. Errors are often mapped to `-EIO`, reducing diagnosability at the FUSE layer.

## Test Signals
Signals include successful initial connection, reuse across operations, expiration after timeout, refresh after Kerberos ticket update, and no leaked or double-freed connections under concurrent FUSE traffic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_connect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_connect.h -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_connect.h

## Purpose
Public interface for the `fuse_dfs` libhdfs connection cache.

## Important APIs, Types, And Functions
Forward-declares `struct hdfsConn`, `struct hdfs_internal`, and exposes `fuseConnectInit`, `fuseConnectAsThreadUid`, `fuseConnectTest`, `hdfsConnGetFs`, and `hdfsConnRelease`.

## Control Flow
Callers initialize once during mount setup, borrow a connection for each operation, use the returned hdfsFS, and release the handle when finished.

## State, Persistence, And Dependencies
The header hides connection-cache state behind opaque types. It depends on caller discipline: every successful borrow requires `hdfsConnRelease`.

## Integration Points
Included by FUSE operation implementations, `fuse_init.c`, and `fuse_dfs.c`.

## Risks
The API does not express ownership in types, so missed releases leak refs and prevent expiry. `hdfsConnGetFs` returns an internal libhdfs pointer tied to the borrowed connection lifetime.

## Test Signals
Static and runtime validation should check that all operation paths release successful connections on cleanup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_connect.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_context_handle.h -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_context_handle.h

## Purpose
Defines mount-level private context stored in FUSE and retrieved by operation callbacks.

## Important APIs, Types, And Functions
`dfs_context` contains `debug`, `usetrash`, `direct_io`, `protectedpaths`, and `rdbuffer_size`.

## Control Flow
`dfs_init` allocates and fills this structure, returns it to FUSE, and callbacks retrieve it through `fuse_get_context()->private_data`.

## State, Persistence, And Dependencies
The context persists for the lifetime of the mount and stores parsed options plus protected path array.

## Integration Points
Used by nearly every FUSE operation to read mount settings, protected path behavior, trash behavior, and read-buffer size.

## Risks
`dfs_destroy` currently does not free this context or `protectedpaths`, so unmount cleanup is incomplete. Callbacks use assertions rather than defensive errors if private data is missing.

## Test Signals
Mount initialization should populate the context, and operation callbacks should see consistent option values.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_context_handle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_dfs.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_dfs.c

## Purpose
Main executable entry for the HDFS FUSE client. It parses mount options, registers FUSE callbacks, and starts `fuse_main`.

## Important APIs, Types, And Functions
`is_protected()` checks mount-protected paths from `dfs_context`. `dfs_oper` maps FUSE operations to `dfs_*` implementations. `main()` initializes defaults, parses `dfs_opts`, translates options to FUSE arguments, and invokes `fuse_main`.

## Control Flow
Process startup clears umask, initializes global `options`, parses command-line and mount options, adds `allow_other` unless private, adds default permission enforcement unless disabled, translates read-only mode and cache timeouts to FUSE args, requires a NameNode URI, then enters FUSE. libhdfs initialization is intentionally deferred to `dfs_init` after FUSE daemonization/fork.

## State, Persistence, And Dependencies
Global `options` persists through startup and mount initialization. FUSE owns callback lifecycle after `fuse_main`. Protected path checks depend on the mount context created later.

## Integration Points
This file binds all operation modules, option parsing, initialization, and connection management into the runnable `fuse_dfs` binary.

## Risks
Option parsing is order-sensitive for URI/server handling. FUSE args are constructed manually. `is_protected` only checks exact paths, not descendants. Read-only behavior is delegated to kernel FUSE rather than operation checks.

## Test Signals
Successful mount, option translation (`ro`, `allow_other`, `default_permissions`, timeout settings), and correct callback dispatch are the primary signals.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_dfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_dfs.h -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_dfs.h

## Purpose
Common header for the FUSE client, defining FUSE API version, shared includes, logging macros, tracing macros, and protected path API.

## Important APIs, Types, And Functions
Defines `FUSE_USE_VERSION 26`, declares `is_protected`, and provides `INFO`, `DEBUG`, `ERROR`, `TRACE`, and `TRACE1` macros.

## Control Flow
No runtime flow beyond macro expansion. Logging writes to stdout/stderr and syslog. Tracing is compiled out unless `DOTRACE` is defined.

## State, Persistence, And Dependencies
Depends on generated `config.h`, libfuse headers, syslog, errno, assertions, and xattr headers.

## Integration Points
Included by most FUSE implementation files for common logging, assertions, and FUSE version selection.

## Risks
Logging macros evaluate arguments in both stdio and syslog calls, so side-effect arguments would run twice. Assertions are used for input validation and may disappear in `NDEBUG` builds.

## Test Signals
Build failures around FUSE version or missing generated config surface here; runtime logs identify operation failures with file and line.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_dfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_dfs_wrapper.sh -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_dfs_wrapper.sh

## Purpose
Convenience wrapper to launch `fuse_dfs` from a Hadoop source/build tree with classpath and native library paths set.

## Important APIs, Types, And Functions
Validates `HADOOP_HOME`, sets `FUSEDFS_PATH`, `LIBHDFS_PATH`, default `OS_ARCH` and `JAVA_HOME`, builds `CLASSPATH` by finding jars under `hadoop-client` and `hadoop-hdfs-project`, updates `PATH` and `LD_LIBRARY_PATH`, then execs `fuse_dfs "$@"`.

## Control Flow
The script exits if `HADOOP_HOME` is empty, applies defaults, iterates over jar files with null-delimited `find`, prepends configuration and library paths, and launches the binary.

## State, Persistence, And Dependencies
Environment variables are the primary state. It depends on bash, `find`, a source-tree layout, compiled native artifacts under target paths, and JVM server library layout.

## Integration Points
Used by developers or tests to run the built FUSE client without manually constructing JNI/libhdfs classpath and library paths.

## Risks
Hard-coded target paths and `$JAVA_HOME/jre/lib/$OS_ARCH/server` may not match modern JDK layouts. It overwrites `LD_LIBRARY_PATH` at the end rather than preserving all earlier content. Missing `HADOOP_CONF_DIR` produces an empty classpath component.

## Test Signals
Successful wrapper launch means jars are found, libhdfs and libjvm are loadable, and `fuse_dfs` is on `PATH`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_dfs_wrapper.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_file_handle.h -->

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_file_handle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls.h -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls.h

## Purpose
Central declaration header for all FUSE operation callback implementations.

## Important APIs, Types, And Functions
Declares `dfs_mkdir`, `dfs_rename`, `dfs_getattr`, `dfs_readdir`, `dfs_read`, `dfs_statfs`, `dfs_rmdir`, `dfs_unlink`, `dfs_utimens`, `dfs_chmod`, `dfs_chown`, `dfs_open`, `dfs_write`, `dfs_release`, `dfs_mknod`, `dfs_create`, `dfs_flush`, `dfs_access`, `dfs_truncate`, and `dfs_symlink`.

## Control Flow
No executable flow; `fuse_dfs.c` uses these declarations to populate the FUSE operations table.

## State, Persistence, And Dependencies
Includes FUSE and mount context types. State lives in individual implementation files.

## Integration Points
This header is the contract between callback registration and operation implementations.

## Risks
Duplicate declarations for `dfs_mkdir` and `dfs_rename` are harmless but noisy. Signature mismatches with libfuse version would break callback registration.

## Test Signals
Compile success and callback dispatch through `fuse_main` validate this contract.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_access.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_access.c

## Purpose
Implements the FUSE `access` callback.

## Important APIs, Types, And Functions
`dfs_access(const char *path, int mask)` asserts the path and returns success.

## Control Flow
The function traces, checks `path != NULL`, ignores `mask`, and returns `0`.

## State, Persistence, And Dependencies
No state is read or written. It depends only on common FUSE logging/assert headers.

## Integration Points
Registered in `fuse_dfs.c` as `.access`. Kernel permission behavior is mostly delegated to FUSE options such as `default_permissions` unless `nopermissions` is used.

## Risks
This is a permissive stub (`TODO: HDFS-428`), so it does not ask HDFS for access checks and can report access success incorrectly when kernel-side checks are disabled.

## Test Signals
Current tests do not deeply validate `access`; permission-sensitive tests should cover `nopermissions` and HDFS ACL interactions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_chmod.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_chmod.c

## Purpose
Implements POSIX chmod by forwarding to HDFS permission changes.

## Important APIs, Types, And Functions
`dfs_chmod(const char *path, mode_t mode)` obtains a thread-UID connection and calls `hdfsChmod(fs, path, (short)mode)`.

## Control Flow
Validate path/context, borrow connection, call HDFS chmod, map errno to negative FUSE error, release connection, return.

## State, Persistence, And Dependencies
Persists only HDFS metadata changes. Depends on FUSE private context, connection cache, libhdfs chmod, and errno.

## Integration Points
Registered as `.chmod`; uses user-specific HDFS connections from `fuse_connect`.

## Risks
Mode is truncated to `short`. Protected path checks are not applied here, so protected files can still have permissions changed. Most connection errors collapse to `-EIO`.

## Test Signals
Native workload TODOs note chmod coverage is missing; tests should verify mode propagation and permission-denied mapping.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_chmod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_chown.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_chown.c

## Purpose
Implements POSIX chown/chgrp using OS UID/GID name lookup and HDFS ownership APIs.

## Important APIs, Types, And Functions
`dfs_chown(const char *path, uid_t uid, gid_t gid)` uses `getUsername`, `getGroup`, `fuseConnectAsThreadUid`, and `hdfsChown`.

## Control Flow
If both uid and gid are `-1`, it returns success. Otherwise it resolves provided UID/GID to names, borrows an HDFS connection as the calling thread UID, calls `hdfsChown`, maps errno, releases connection, and frees lookup strings.

## State, Persistence, And Dependencies
Persists HDFS owner/group metadata. Depends on local passwd/group databases, global lookup mutexes in `fuse_users.c`, and libhdfs.

## Integration Points
Registered as `.chown`. Converts local numeric identities into HDFS string identities.

## Risks
Local OS names may not match HDFS users/groups. Protected paths are not checked. UID/GID are compared with `-1` despite unsigned platform typedefs, which is conventional but type-sensitive.

## Test Signals
Coverage should check owner/group updates, lookup failure mapping, and behavior under concurrent calls.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_chown.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_create.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_create.c

## Purpose
Implements FUSE create by delegating to open.

## Important APIs, Types, And Functions
`dfs_create(const char *path, mode_t mode, struct fuse_file_info *fi)` ORs `mode` into `fi->flags` and calls `dfs_open`.

## Control Flow
Trace, mutate flags, return `dfs_open(path, fi)`.

## State, Persistence, And Dependencies
State effects occur in `dfs_open`: HDFS file creation and file-handle allocation. This file itself only changes the flags field.

## Integration Points
Registered as `.create` and shares all open behavior, including HDFS flag translation.

## Risks
ORing permission mode into open flags is semantically unusual; POSIX mode bits are not open flags. Actual chmod after create is not handled here.

## Test Signals
Create/touch tests validate that delegated open creates files, but mode propagation needs separate chmod/stat coverage.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_create.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_flush.c -->

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_flush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_getattr.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_getattr.c

## Purpose
Implements stat/getattr by translating HDFS file metadata to POSIX `struct stat`.

## Important APIs, Types, And Functions
`dfs_getattr` calls `hdfsGetPathInfo`, `fill_stat_structure`, `hdfsListDirectory` for directory link counts, and `hdfsFreeFileInfo`.

## Control Flow
Borrow a connection, fetch path info, return `-ENOENT` if missing, fill stat metadata, list directories to set `st_nlink = entries + 2`, set regular files to one link, free HDFS info, release connection.

## State, Persistence, And Dependencies
No persistence. Depends on libhdfs metadata calls, `fuse_stat_struct.c`, and current HDFS namespace state.

## Integration Points
Registered as `.getattr` and used heavily by shell tools, readdir consumers, and test workload stat checks.

## Risks
Missing path is always `-ENOENT`; other I/O failures can be misreported. Directory `hdfsListDirectory` failure leaves `numEntries` at zero and may produce inaccurate link count. Time/owner translation risks live in `fill_stat_structure`.

## Test Signals
`stat`, `ls`, and workload checks for file type, size, and directory mtime validate this path.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_getattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_mkdir.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_mkdir.c

## Purpose
Implements directory creation in HDFS.

## Important APIs, Types, And Functions
`dfs_mkdir(const char *path, mode_t mode)` checks `is_protected`, calls `hdfsCreateDirectory`, then `hdfsChmod`.

## Control Flow
Validate context and absolute path, reject exact protected paths, borrow connection, create directory, chmod it to requested mode, release connection, return mapped errno.

## State, Persistence, And Dependencies
Persists new HDFS directories and permission metadata. Depends on connection cache, libhdfs create/chmod, and protected path option state.

## Integration Points
Registered as `.mkdir`; used by workload tests and trash directory creation indirectly in `fuse_trash.c`.

## Risks
Create and chmod are not atomic. The code sets `ret = 0` after chmod block even if chmod set an error, so chmod failure may be swallowed. Protected path matching is exact.

## Test Signals
Directory create/list/remove tests validate basic behavior; permission-mode tests should catch the chmod return issue.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_mkdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_mknod.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_mknod.c

## Purpose
Stub implementation for FUSE mknod.

## Important APIs, Types, And Functions
`dfs_mknod(const char *path, mode_t mode, dev_t rdev)` traces/debugs and returns success.

## Control Flow
No HDFS call is made; the function always returns `0`.

## State, Persistence, And Dependencies
No state changes. It depends only on common logging macros.

## Integration Points
Registered as `.mknod`, but FUSE create/open paths handle normal file creation elsewhere.

## Risks
Returning success without creating anything can confuse callers that use mknod for special files or creation. HDFS cannot represent POSIX device nodes, so success is misleading.

## Test Signals
Native workload TODOs explicitly list mknod as untested; tests should verify expected unsupported behavior rather than silent success.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_mknod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_open.c -->

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_read.c -->

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_readdir.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_readdir.c

## Purpose
Implements directory listing for FUSE.

## Important APIs, Types, And Functions
`dfs_readdir` calls `hdfsListDirectory`, `fill_stat_structure`, extracts basename with `strrchr`, and calls the FUSE `filler` callback for entries plus `.` and `..`.

## Control Flow
Borrow connection, list HDFS directory, map null result to errno or `ENOENT`, iterate entries, fill stat metadata and basename into FUSE buffer, then append synthetic dot entries with generic directory stats.

## State, Persistence, And Dependencies
No persistence. Depends on HDFS directory listing shape, where `mName` is a full path string.

## Integration Points
Registered as `.readdir` and exercised by `ls`, `find`, copy recursion, and native workload directory expectations.

## Risks
Filler errors are logged but do not stop iteration or change return code. Dot entries use placeholder ownership/timestamps. Offset and file-info parameters are ignored, so very large directories may not support incremental reads well.

## Test Signals
Workload checks directory membership before and after mkdir/rename; `find`/`ls` tests also validate this path.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_readdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_release.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_release.c

## Purpose
Closes and frees per-file FUSE state when a file handle is released.

## Important APIs, Types, And Functions
`dfs_release(const char *path, struct fuse_file_info *fi)` calls `hdfsCloseFile`, frees read buffer, releases `hdfsConn`, destroys mutex, frees `dfs_fh`, and clears `fi->fh`.

## Control Flow
Validate context and path, close the hdfs handle if present, record `-EIO` on close failure, free all associated resources, return status.

## State, Persistence, And Dependencies
Persists close effects to HDFS and drops connection references. Depends on libhdfs close and correct `dfs_fh` lifetime.

## Integration Points
Registered as `.release`; complements open/read/write/flush.

## Risks
Close can occur asynchronously from application perspective, which test workload works around. Multiple writers to same HDFS path can overwrite each other because handles are independent.

## Test Signals
Unmount success, close-length retry workaround, and no leaked file descriptors/handles are key signals.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_release.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_rename.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_rename.c

## Purpose
Implements POSIX rename through HDFS rename.

## Important APIs, Types, And Functions
`dfs_rename(const char *from, const char *to)` checks protected paths and calls `hdfsRename`.

## Control Flow
Validate source/destination paths, reject if either exact path is protected, borrow HDFS connection, call rename, map errno, release connection.

## State, Persistence, And Dependencies
Persists namespace movement in HDFS. Depends on libhdfs rename semantics and connection cache.

## Integration Points
Registered as `.rename`; also used conceptually by trash move implementation.

## Risks
Protected descendants are not protected by exact matching. POSIX overwrite/atomicity semantics may differ from HDFS rename behavior.

## Test Signals
Native workload renames directory `a` to `c` and validates directory listing changes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_rename.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_rmdir.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_rmdir.c

## Purpose
Implements directory removal, optionally using the trash emulation path.

## Important APIs, Types, And Functions
`dfs_rmdir` checks `is_protected`, lists directory contents with `hdfsListDirectory`, and deletes via `hdfsDeleteWithTrash`.

## Control Flow
Reject protected path, borrow connection, list directory, return `-ENOTEMPTY` if entries exist, call trash/delete helper, free listing, release connection.

## State, Persistence, And Dependencies
Persists directory deletion or trash rename in HDFS. Depends on HDFS listing/delete and mount `usetrash` option.

## Integration Points
Registered as `.rmdir`; shares deletion policy with unlink through `fuse_trash.c`.

## Risks
If `hdfsListDirectory` returns null for errors or nonexistent path with `numEntries` zero, the code may proceed to delete and return generic `-EIO`. Non-directory rmdir cases are listed as TODO in workload. Recursive delete may occur through `hdfsDeleteWithTrash` fallback.

## Test Signals
Basic mkdir/rmdir tests and workload recursive cleanup validate simple empty directory removal.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_rmdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_statfs.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_statfs.c

## Purpose
Implements filesystem capacity reporting for FUSE.

## Important APIs, Types, And Functions
`dfs_statfs(const char *path, struct statvfs *st)` calls `hdfsGetCapacity`, `hdfsGetUsed`, and `hdfsGetDefaultBlockSize`.

## Control Flow
Zero the output struct, borrow connection, read HDFS capacity/used/block size, fill block counts and fixed inode fields, release connection.

## State, Persistence, And Dependencies
No persistence. Depends on HDFS cluster stats and default block size.

## Integration Points
Registered as `.statfs`; used by tools such as `df` and native workload `statvfs`.

## Risks
Inode fields and flags are hard-coded (`ST_RDONLY | ST_NOSUID`) and may not reflect mount mode. Division by zero would occur if default block size were zero. Capacity errors are not checked explicitly.

## Test Signals
Workload only checks that `statvfs` succeeds; stronger tests should validate plausible block values.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_statfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_symlink.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_symlink.c

## Purpose
Declares symlink unsupported for the FUSE HDFS client.

## Important APIs, Types, And Functions
`dfs_symlink(const char *from, const char *to)` ignores arguments and returns `-ENOTSUP`.

## Control Flow
Trace and return unsupported.

## State, Persistence, And Dependencies
No state changes and no HDFS calls.

## Integration Points
Registered as `.symlink`.

## Risks
Applications expecting symlink support fail. This is safer than silent success, unlike `mknod`.

## Test Signals
Native workload TODO notes symlink tests are absent; a test should assert `ENOTSUP`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_truncate.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_truncate.c

## Purpose
Implements a limited truncate operation for size zero.

## Important APIs, Types, And Functions
`dfs_truncate(const char *path, off_t size)` delegates deletion to `dfs_unlink`, then recreates an empty file with `hdfsOpenFile(O_WRONLY | O_CREAT)` and closes it.

## Control Flow
If size is nonzero, return success without changing the file. For size zero, delete the path, borrow connection, create an empty file, close it, release connection.

## State, Persistence, And Dependencies
Persists file replacement in HDFS. It does not preserve old metadata such as owner, group, permissions, or times.

## Integration Points
Registered as `.truncate` and used by workload tests that truncate written files to zero length.

## Risks
Nonzero truncate is a no-op success, which is semantically wrong. Zero truncate is delete-and-recreate, so metadata and atomicity are lost and protected path behavior depends on `dfs_unlink`.

## Test Signals
Workload verifies truncate-to-zero size. Tests should add nonzero truncate and metadata preservation expectations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_truncate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_unlink.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_unlink.c

## Purpose
Implements file unlink, optionally routing through HDFS trash emulation.

## Important APIs, Types, And Functions
`dfs_unlink(const char *path)` checks `is_protected`, borrows a connection, and calls `hdfsDeleteWithTrash`.

## Control Flow
Validate absolute path and context, reject exact protected path, borrow connection, delete or move to trash based on mount option, map errno or `EIO`, release connection.

## State, Persistence, And Dependencies
Deletes or renames files in HDFS. Depends on mount `usetrash`, connection cache, and trash helper behavior.

## Integration Points
Registered as `.unlink`; also used by `dfs_truncate` for zero truncation.

## Risks
Exact protected matching does not protect descendants. Deleting an open file or write-in-progress is listed as untested. Trash fallback may permanently delete if move-to-trash fails.

## Test Signals
Create/remove and workload unlink/stat-ENOENT checks validate basic deletion.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_unlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_utimens.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_utimens.c

## Purpose
Implements timestamp update through HDFS utime.

## Important APIs, Types, And Functions
`dfs_utimens(const char *path, const struct timespec ts[2])` converts access and modification seconds and calls `hdfsUtime`.

## Control Flow
Borrow connection, call `hdfsUtime(fs, path, mTime, aTime)`. On failure, fetch path info; missing path returns errno/ENOENT, directory failures are ignored for compatibility with tools like tar, and file failures map to errno or `EACCES`.

## State, Persistence, And Dependencies
Persists HDFS access/modification times where supported. Nanoseconds are discarded.

## Integration Points
Registered as `.utimens`; native workload uses `utime` and validates directory mtime.

## Risks
Directory timestamp failures are silently ignored. `hdfsFileInfo` fetched on failure is not freed, leaking memory. Nanosecond precision is lost.

## Test Signals
Workload validates setting directory mtime to 456; file timestamp and leak tests would improve coverage.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_utimens.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_write.c -->

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_impls_write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_init.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_init.c

## Purpose
Mount-time initialization for `fuse_dfs`, creating private context, parsing protected paths, initializing connection cache, and negotiating FUSE capabilities.

## Important APIs, Types, And Functions
`dfs_init`, `dfs_destroy`, `init_protectedpaths`, `dfsPrintOptions`, and `print_env_vars`.

## Control Flow
`dfs_init` allocates `dfs_context`, copies selected global options, logs options, splits colon-separated protected paths, normalizes read buffer size, initializes libhdfs connection subsystem, optionally tests connection, and sets desired FUSE capabilities for atomic truncate, async read, big writes, and dont-mask permissions. `dfs_destroy` only traces.

## State, Persistence, And Dependencies
Mount context persists in FUSE private data. Connection cache globals are initialized here. Protected paths are allocated dynamically. Depends on global `options`, libfuse capability flags, and `fuse_connect`.

## Integration Points
Registered as `.init` and `.destroy` in `fuse_dfs.c`; the only place libhdfs is initialized after FUSE daemonization.

## Risks
`dfs_destroy` does not free allocated context/protected path memory. Fatal init failures call `exit`, terminating mount. Protected path parser only supports colon separation and exact later matching. Capability negotiation depends on compile-time FUSE macros.

## Test Signals
Mount startup, initchecks, read buffer defaults, and capability-sensitive open(O_TRUNC)/big-write workloads validate this file.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_init.h -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_init.h

## Purpose
Declares mount lifecycle callbacks for the FUSE client.

## Important APIs, Types, And Functions
Forward-declares `struct fuse_conn_info` and declares `dfs_init` and `dfs_destroy`.

## Control Flow
No executable flow; FUSE invokes the declared callbacks through the operations table.

## State, Persistence, And Dependencies
Lifecycle state is implemented in `fuse_init.c`. This header only exposes the callback signatures.

## Integration Points
Included by `fuse_dfs.c` for callback registration and by initialization-related code.

## Risks
Signature must match the libfuse API version selected by `FUSE_USE_VERSION 26`.

## Test Signals
Compile/link success and mount/unmount callback invocation validate the declarations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_options.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_options.c

## Purpose
Command-line and mount-option parser for `fuse_dfs`.

## Important APIs, Types, And Functions
Defines `program`, `dfs_opts`, option keys, `print_options`, `print_usage`, and `dfs_options`. Recognized options include server/port/protected/cache timeouts/read buffer/max background/private/ro/rw/debug/initchecks/nopermissions/big_writes/usetrash/notrash/direct_io.

## Control Flow
`fuse_opt_parse` uses `dfs_opts` and calls `dfs_options` for special keys. Version/help print and exit. Debug adds `-d` to FUSE args. `big_writes` forwards to FUSE when supported. Unknown non-URI options are passed through to FUSE. URI arguments set `options.nn_uri`, translating legacy `dfs://` to `hdfs://`.

## State, Persistence, And Dependencies
Mutates the global `options` struct declared in the header and the outgoing FUSE arg list. Depends on libfuse option parsing and C allocation for URI translation.

## Integration Points
Called from `main` before `fuse_main`; its parsed state is consumed by `dfs_init`, `fuse_dfs.c`, and operation callbacks.

## Risks
The usage string contains typos and stale option spelling. URI memory is allocated and never freed. Unknown options are mostly passed through, which can hide misspellings. Multiple URI/server options are ignored after first.

## Test Signals
Mounts with URI, server/port, ro/rw, debug, cache timeout, and legacy `dfs://` forms validate this parser.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_options.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_options.h -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_options.h

## Purpose
Defines the global option structure and parser API for `fuse_dfs`.

## Important APIs, Types, And Functions
`struct options` stores protected paths, NameNode URI/port, debug/read-only/initchecks/no-permissions/trash/cache/private/read-buffer/direct-io/max-background fields. It declares global `options`, `dfs_opts`, `print_options`, `print_usage`, and `dfs_options`.

## Control Flow
No executable flow in the header; parser implementation fills the global struct before mount initialization.

## State, Persistence, And Dependencies
The global `options` variable is defined in this header, so every translation unit including it risks a tentative definition under old C behavior. The top-level CMake uses `-fcommon` on GCC >= 10 to preserve this pattern.

## Integration Points
Included by startup, init, and option parsing code.

## Risks
Defining storage in a header is fragile and non-idiomatic. Fields have mixed ownership: some strings point to argv/storage, others are heap-allocated.

## Test Signals
Build/link success depends on compiler common-symbol behavior; runtime option tests validate field propagation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_stat_struct.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_stat_struct.c

## Purpose
Translates libhdfs `hdfsFileInfo` metadata into POSIX `struct stat`.

## Important APIs, Types, And Functions
`fill_stat_structure(hdfsFileInfo *info, struct stat *st)` uses `getpwnam`, `getgrnam`, global mutexes from `fuse_users.c`, `default_id=99`, and `blksize=512`.

## Control Flow
Zero stat, derive link count, map HDFS owner/group names to local UID/GID with fallback, derive file type and permissions, set size/block fields, and copy access/modification times.

## State, Persistence, And Dependencies
No persistent changes. Depends on local passwd/group databases, global lookup mutex ordering, HDFS metadata, and math `ceil`.

## Integration Points
Used by `getattr` and `readdir` to present HDFS metadata to POSIX consumers.

## Risks
Owner/group names may not exist locally and fall back to nobody id. `ceil(st_size/st_blksize)` uses integer division before conversion, undercounting partial blocks. Directory mode defaults to permissive 0777 when HDFS permissions are absent.

## Test Signals
Stat tests should validate file type, size, permission bits, owner/group fallback, and timestamps.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_stat_struct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_stat_struct.h -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_stat_struct.h

## Purpose
Header for HDFS-to-POSIX stat conversion.

## Important APIs, Types, And Functions
Declares `fill_stat_structure`, `default_id`, and `blksize`.

## Control Flow
No executable flow; used by metadata callbacks.

## State, Persistence, And Dependencies
Exposes constants defined in `fuse_stat_struct.c`; depends on `hdfs/hdfs.h` and POSIX stat types.

## Integration Points
Included by `getattr` and `readdir`.

## Risks
The conversion helper assumes valid `hdfsFileInfo` lifetime. Constants are globally visible and not configurable.

## Test Signals
Compile-time inclusion plus stat/readdir behavior validate the header contract.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_stat_struct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_trash.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_trash.c

## Purpose
Implements a C approximation of Hadoop Trash behavior for FUSE deletes.

## Important APIs, Types, And Functions
`hdfsDeleteWithTrash` is public. Internals include `get_parent_dir`, `get_trash_base`, and `move_to_trash`. Constants include `TRASH_RENAME_TRIES` and `ALREADY_IN_TRASH_ERR`.

## Control Flow
When trash is enabled, deletion tries to split the absolute path, construct `/user/<caller>/.Trash/Current<parent>/<name>`, create trash directories, choose a numbered target if needed, and rename the file there. If move fails or path is already in trash, fallback deletes recursively with `hdfsDelete`.

## State, Persistence, And Dependencies
Persists HDFS renames, trash directory creation, or final deletion. Depends on FUSE caller UID, local username lookup, libhdfs existence/create/rename/delete calls, and heap allocation via `strdup`/`asprintf`.

## Integration Points
Called by `dfs_unlink` and `dfs_rmdir` using the user-specific hdfsFS.

## Risks
Fallback after trash failure can permanently delete data. Trash path construction assumes `/user/<name>` convention. Existing trash collisions only try 99 suffixes. Parent split rejects root or malformed non-absolute paths.

## Test Signals
Tests should validate move-to-trash success, collision suffixing, already-in-trash deletion, and fallback delete behavior; current basic unlink/rmdir tests mostly cover deletion.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_trash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_trash.h -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_trash.h

## Purpose
Public declaration for FUSE delete-with-trash support.

## Important APIs, Types, And Functions
Declares `hdfsDeleteWithTrash(hdfsFS userFS, const char *path, int useTrash)`.

## Control Flow
Callers pass a user-specific HDFS filesystem, path, and boolean trash flag; implementation either moves to trash or deletes.

## State, Persistence, And Dependencies
State changes occur in HDFS through the supplied `hdfsFS`. The header depends on libhdfs types.

## Integration Points
Included by unlink/rmdir implementations.

## Risks
The API returns integer error codes with mixed sign conventions internally; callers must treat nonzero as failure.

## Test Signals
Unlink/rmdir tests with trash enabled and disabled validate the contract.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_trash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_users.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_users.c

## Purpose
Thread-safe wrappers around local passwd/group lookups for FUSE identity mapping.

## Important APIs, Types, And Functions
Defines global mutexes `passwdstruct_mutex` and `groupstruct_mutex`. Exposes `getUsername`, `freeGroups`, `getGroup`, `getGroupUid`, `getGidUid`, and `getGroups`.

## Control Flow
Lookup functions lock the relevant mutex around non-reentrant libc calls, duplicate returned names, and unlock. `getGroups` has an inactive `GETGROUPS_T` branch; the active branch attempts to return the username and primary group.

## State, Persistence, And Dependencies
No persistent external state, but global mutexes serialize identity lookup. Depends on local `/etc/passwd`/NSS and `/etc/group`/NSS.

## Integration Points
Used by connection creation, chown, stat conversion, and trash path construction.

## Risks
The active `getGroups` branch writes to `groupnames[i]` while `groupnames` is still NULL, which is a latent crash if used. Local identity names may not match HDFS identities. Lock ordering must remain passwd then group when both are needed.

## Test Signals
Connection-as-UID, chown, stat owner mapping, and trash path tests validate these helpers; `getGroups` needs direct coverage because normal operation may not call it.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_users.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_users.h -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_users.h

## Purpose
Public identity lookup API for the FUSE client.

## Important APIs, Types, And Functions
Declares `getUsername`, `freeGroups`, `getGroup`, `getGroupUid`, `getGidUid`, and `getGroups`.

## Control Flow
No executable flow; callers receive heap-allocated strings or arrays that must be freed.

## State, Persistence, And Dependencies
Depends on POSIX uid/gid types and pthread-capable implementation. Ownership convention is documented in comments.

## Integration Points
Included by connection, chown, trash, and stat modules.

## Risks
Caller ownership is manual; missed frees leak, and using NULL returns without checks can crash.

## Test Signals
Unit tests around valid/invalid uid/gid and array cleanup would validate the API.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_users.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/test/TestFuseDFS.java -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/test/TestFuseDFS.java

## Purpose
JUnit integration tests for a `fuse_dfs` mount backed by a Java `MiniDFSCluster`.

## Important APIs, Types, And Functions
Class state includes `MiniDFSCluster`, `FileSystem`, `Process fuseProcess`, runtime, and mount point. Helpers execute shell commands, create/check files, redirect process output, establish and tear down FUSE mount. Tests cover directories, create/read/delete, touch, unsupported random writes, recursive copy, and concurrent threads.

## Control Flow
`startUp` builds a MiniDFSCluster with permissions disabled, establishes the mount by launching `fuse_dfs` with classpath/native env, and waits. Each test uses local file APIs and shell commands against the mount. `tearDown` unmounts before shutting down HDFS.

## State, Persistence, And Dependencies
State includes real FUSE mount, external `fusermount`, native binary paths relative to `build.test`, JVM/libhdfs library paths, and MiniDFS files. Tests mutate the mounted HDFS namespace and host mount table.

## Integration Points
Exercises Java build output, native `fuse_dfs`, libhdfs JNI, MiniDFSCluster, and common POSIX tools (`mkdir`, `ls`, `rm`, `cp`, `find`, `cat`, `stat`).

## Risks
Very environment-sensitive: requires FUSE privileges/config (`user_allow_other`), Linux utilities, correct native library paths, and long sleeps. Shell command strings are not escaped. Fixed 50-second mount wait slows tests and may still be flaky.

## Test Signals
Passes indicate end-to-end mount functionality for basic metadata, data I/O, deletion, copy, and concurrency. Failures often point to environment setup rather than pure code regressions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/test/TestFuseDFS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/test/fuse_workload.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/test/fuse_workload.c

## Purpose
Portable C workload that exercises common filesystem operations against a FUSE mount, also self-validated on a local filesystem.

## Important APIs, Types, And Functions
Main entry `runFuseWorkload`. Helpers include directory readers, `safeWrite`, `safeRead`, `closeWorkaroundHdfs2551`, optional `testOpenTrunc`, and `runFuseWorkloadImpl`. `struct fileCtx` tracks test files.

## Control Flow
The workload verifies root directory, creates/removes directories, checks readdir results, renames, calls statvfs and utime, creates several files, writes and reads back varied string sizes, truncates them to zero, unlinks them, optionally tests `open(O_TRUNC)`, then recursively deletes the base directory.

## State, Persistence, And Dependencies
Mutates the filesystem under `<root>/<pcomp>`. Uses local POSIX syscalls, FUSE headers for capability guards, test macros, and `sleepNoSig`. The close workaround polls stat to account for asynchronous FUSE release.

## Integration Points
Called by `test_fuse_dfs.c` against both local FS and mounted HDFS FUSE. It validates operation callbacks in combination rather than as isolated units.

## Risks
TODO comments call out missing coverage for access, mknod, symlink, non-dir rmdir, non-empty rmdir, unlink during write, weird open flags, chown, and chmod. Polling for close visibility can make failures slow.

## Test Signals
Any nonzero return pinpoints a POSIX operation mismatch. Directory membership, file contents, truncate sizes, and cleanup are the strongest signals.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/test/fuse_workload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/test/fuse_workload.h -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/test/fuse_workload.h

## Purpose
Declares the reusable FUSE workload test entry point.

## Important APIs, Types, And Functions
`runFuseWorkload(const char *root, const char *pcomp)` performs operations under `<root>/<pcomp>`.

## Control Flow
No executable flow; implementation creates and cleans a test subtree.

## State, Persistence, And Dependencies
Callers must provide a root directory and unique path component not used concurrently. The workload mutates and then removes that subtree.

## Integration Points
Included by `test_fuse_dfs.c` and linked into the native FUSE test executable.

## Risks
Concurrent callers sharing the same root/component would conflict. The API only returns negative error codes, not structured failure details.

## Test Signals
Return zero means the workload completed and cleanup succeeded.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/test/fuse_workload.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/test/test_fuse_dfs.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/test/test_fuse_dfs.c

## Purpose
Native end-to-end test runner for `fuse_dfs` using a native MiniDFS cluster wrapper and real FUSE mount.

## Important APIs, Types, And Functions
Helpers include `verifyFuseWorkload`, `fuserMount`, `isMounted`, `waitForMount`, `cleanupFuse`, and `spawnFuseServer`. `main` orchestrates temp mount creation, cluster lifecycle, FUSE process lifecycle, workload execution, and cleanup.

## Control Flow
The test optionally uses `TLH_FUSE_MNT_POINT` or creates a temp dir, verifies the workload on local FS, starts a formatted MiniDFS cluster, forks/execs `fuse_dfs` with server/port/init options, waits for `/proc/mounts` to show the mount, runs workload, unmounts, waits for the FUSE process, shuts down cluster, and removes temp dir.

## State, Persistence, And Dependencies
Touches local mount table, temp directories, child processes, MiniDFS cluster JVM, and HDFS namespace. Depends on `fusermount`, `/proc/mounts`, `native_mini_dfs`, libhdfs, and POSIX process APIs.

## Integration Points
Connects C workload, native cluster wrapper, built `fuse_dfs` binary, and libhdfs/JNI runtime.

## Risks
Linux/FUSE specific. Cleanup is best effort but failed mount/unmount can leave processes or mountpoints. `fusermount` exec errors use a reserved status. Signal handling expects SIGTERM after unmount as acceptable.

## Test Signals
`FUSE_TEST: SUCCESS` indicates local workload, HDFS mount workload, unmount, process exit, and cluster shutdown all succeeded.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/test/test_fuse_dfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/util/posix_util.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/util/posix_util.c

## Purpose
Small POSIX utility library for native FUSE tests.

## Important APIs, Types, And Functions
Implements `recursiveDeleteContents`, `recursiveDelete`, `createTempDir`, and `sleepNoSig`. Uses static mutex `gTempdirLock` and nonce for temp names.

## Control Flow
Recursive deletion stats paths, descends into directories, skips dot entries, unlinks files, and removes directories. Temp dir creation chooses `$TMPDIR` or `/tmp`, canonicalizes relative TMPDIR, combines pid and nonce, and calls mkdir. Sleep loops on `EINTR`.

## State, Persistence, And Dependencies
Mutates local filesystem and sleeps. The nonce is process-global and protected by a mutex. Depends on POSIX dir/stat/unlink/rmdir/realpath/nanosleep APIs.

## Integration Points
Used by native FUSE workload and test runner for temp mount dirs and cleanup.

## Risks
Deletion follows `stat`, not `lstat`, so symlink behavior may be unsafe if symlinks appear. Temp names are predictable and `mkdir` failure is returned rather than retried. Some error sign conventions are inconsistent (`rmdir` returns positive errno in one path).

## Test Signals
Local workload verification and cleanup success exercise these utilities.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/util/posix_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/util/posix_util.h -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/util/posix_util.h

## Purpose
Header for POSIX test utilities.

## Important APIs, Types, And Functions
Declares `recursiveDeleteContents`, `recursiveDelete`, `createTempDir`, and `sleepNoSig`.

## Control Flow
No executable flow; exposes cleanup/temp/sleep helpers.

## State, Persistence, And Dependencies
State changes are local filesystem mutations and sleep timing in the implementation.

## Integration Points
Included by FUSE workload and test runner.

## Risks
Callers must not pass paths that should be preserved; recursive delete is destructive.

## Test Signals
Compile inclusion and successful temp/cleanup operations validate this API.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/util/posix_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/util/tree.h -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/util/tree.h

## Purpose
Vendored BSD-style intrusive splay tree and red-black tree macro library.

## Important APIs, Types, And Functions
Defines `SPLAY_HEAD`, `SPLAY_ENTRY`, `SPLAY_PROTOTYPE`, `SPLAY_GENERATE`, traversal macros, `RB_HEAD`, `RB_ENTRY`, `RB_PROTOTYPE`, `RB_GENERATE`, `RB_INSERT`, `RB_REMOVE`, `RB_FIND`, `RB_FOREACH`, and min/max helpers.

## Control Flow
Macros generate type-specific tree functions that manipulate caller-embedded left/right/parent/color fields and call a caller-supplied comparator.

## State, Persistence, And Dependencies
No standalone state. Tree nodes and roots are owned by callers. It depends on macro expansion and intrusive struct layout.

## Integration Points
`fuse_connect.c` uses RB macros to maintain the connection cache keyed by username and Kerberos ticket path.

## Risks
Macro code is hard to debug and not type-safe beyond compile-time expansion. Callers must protect trees with locks when used concurrently. Vendored code is excluded from RAT checks.

## Test Signals
Connection cache insert/find/remove/expiry behavior indirectly validates the RB subset used here.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/util/tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-examples/CMakeLists.txt -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-examples/CMakeLists.txt

## Purpose
Builds small libhdfs example binaries.

## Important APIs, Types, And Functions
Includes libhdfs/JNI/generated headers and creates executables `hdfs_read` from `libhdfs_read.c` and `hdfs_write` from `libhdfs_write.c`, both linked with `hdfs`.

## Control Flow
CMake configures include directories, adds two executables, and links them.

## State, Persistence, And Dependencies
Build outputs are example binaries. Dependencies include libhdfs target, JNI headers, generated javah headers, OS-specific native directory, and generated config.

## Integration Points
Entered from top-level native CMake; examples demonstrate the public C API and can be manually run against a configured HDFS cluster.

## Risks
No tests are registered here, so examples may compile but not be exercised. Runtime still depends on classpath and libjvm/libhdfs paths.

## Test Signals
Successful build and manual read/write execution validate the examples.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-examples/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-examples/libhdfs_read.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-examples/libhdfs_read.c

## Purpose
Minimal example program showing how to read a file through libhdfs.

## Important APIs, Types, And Functions
`main` uses `hdfsConnect`, `hdfsOpenFile` with `O_RDONLY`, `hdfsRead`, `hdfsCloseFile`, and `hdfsDisconnect`.

## Control Flow
The program expects filename, file size, and buffer size arguments, connects to default HDFS, opens the file, allocates a buffer, repeatedly reads until a short read/EOF, frees resources, closes, and disconnects.

## State, Persistence, And Dependencies
No HDFS mutation; reads remote file data. Depends on libhdfs runtime configuration, default FS, classpath, and heap allocation.

## Integration Points
Built by `libhdfs-examples/CMakeLists.txt` as `hdfs_read`.

## Risks
It reads `argv[1]` and `argv[3]` before checking `argc`, so missing args can crash. The `<filesize>` argument is documented but unused. It prints “for writing” on open-read failure.

## Test Signals
Successful run against an existing file validates basic connect/open/read/close flow; argument validation is weak.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-examples/libhdfs_read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-examples/libhdfs_write.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-examples/libhdfs_write.c

## Purpose
Minimal example program showing how to write a patterned file through libhdfs.

## Important APIs, Types, And Functions
`main` uses `hdfsConnect`, `hdfsOpenFile` with `O_WRONLY`, `hdfsWrite`, `hdfsCloseFile`, and `hdfsDisconnect`.

## Control Flow
The program expects filename, total file size, and buffer size, connects to default HDFS, validates size conversions, opens the file, fills a buffer with repeating letters, writes chunks until requested size is written, then frees/closes/disconnects.

## State, Persistence, And Dependencies
Creates or overwrites remote HDFS file content. Depends on libhdfs and default filesystem configuration.

## Integration Points
Built as `hdfs_write`; pairs with `hdfs_read` and test shell script.

## Risks
Reads argv before argc validation. `errno` is checked after `strtoul` without clearing it first. File writes are simple and do not call explicit flush/hsync before close.

## Test Signals
Successful write followed by readback validates basic write path and buffer chunking.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-examples/libhdfs_write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-examples/test-libhdfs.sh -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-examples/test-libhdfs.sh

## Purpose
Legacy shell integration harness for running libhdfs tests against a MiniDFSCluster launched from Hadoop jars.

## Important APIs, Types, And Functions
Requires `HADOOP_HOME`; optional env vars include `HDFS_TEST_CONF_DIR`, `LIBHDFS_BUILD_DIR`, `OS_NAME`, and `CLOVER_JAR`. Function `findlibjvm` locates JVM library directories. It launches `MiniDFSClusterManager` and runs `hdfs_test` with `LD_PRELOAD`.

## Control Flow
Validate environment, find HDFS test jar, assemble classpath from Hadoop jars, locate libjvm, remove old core-site, start a background MiniDFSClusterManager that writes config, wait up to 30 seconds, run native test with preloaded libjvm/libhdfs, kill cluster, exit with test status.

## State, Persistence, And Dependencies
Writes/removes `core-site.xml` in test conf dir, writes `/tmp/libhdfs-test-cluster.out`, starts/kills a background JVM, and uses native libraries from Hadoop install paths.

## Integration Points
Connects installed Hadoop layout, Java MiniDFSCluster manager, and native libhdfs test executable.

## Risks
Uses `kill -9` for cleanup, unquoted paths in places, fixed NameNode port 20300, and `LD_PRELOAD` assumptions. `rm core-site.xml` can fail or remove caller-provided config. Modern JVM layouts may break `tools.jar` or libjvm assumptions.

## Test Signals
Cluster config file creation, native test exit status, and cluster cleanup messages are the main signals.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-examples/test-libhdfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/CMakeLists.txt -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/CMakeLists.txt

## Purpose
CMake setup for native libhdfs test support library and one native MiniDFS test target.

## Important APIs, Types, And Functions
Includes libhdfs/JNI/libhdfspp headers, builds `native_mini_dfs` from native cluster wrapper and JNI helper sources, builds `test_native_mini_dfs`, links with JVM, and registers `test_test_native_mini_dfs`.

## Control Flow
CMake declares include directories, creates a static/shared support library target from C sources and platform objects, creates executable test target, links it, and adds it to CTest.

## State, Persistence, And Dependencies
Build outputs include support library and test executable. Depends on Java JVM library, JNI headers, libhdfs internal sources, platform mutex/TLS sources, and x-platform objects.

## Integration Points
The `native_mini_dfs` library is linked by FUSE tests and other native libhdfs tests.

## Risks
This file only registers `test_native_mini_dfs`; other libhdfs tests may be defined elsewhere via top-level helper functions. It compiles internal libhdfs implementation files directly, so source layout changes affect tests.

## Test Signals
CTest target `test_test_native_mini_dfs` validates native MiniDFS wrapper construction/linking.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/expect.c -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/expect.c

## Purpose
Implements read-statistics expectation helper for native libhdfs tests.

## Important APIs, Types, And Functions
`expectFileStats` calls `hdfsFileGetReadStatistics`, compares selected fields with `EXPECT_UINT64_EQ`, prints observed and expected counters, and frees stats with `hdfsFileFreeReadStatistics`.

## Control Flow
Fetch stats, log expected/actual counters, skip fields whose expected value is `UINT64_MAX`, compare specified fields, free stats, return zero or first expectation failure.

## State, Persistence, And Dependencies
Reads per-file libhdfs statistics and frees allocated stats object. No persistent state.

## Integration Points
Used by native libhdfs tests, especially zero-copy/direct-read tests, to verify read accounting.

## Risks
If an expectation fails before the final free, stats may leak because macros return immediately. The implementation signature uses `hdfsFile` while header forward-doc refers to internal struct, but typedef compatibility is expected.

## Test Signals
Counter mismatch errors include file/line and observed counters; success means read path accounting matched expectations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/expect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/expect.h -->

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/expect.h

## Purpose
Assertion macro library for native libhdfs and FUSE C tests.

## Important APIs, Types, And Functions
Macros include `EXPECT_ZERO`, `EXPECT_NULL`, `EXPECT_NULL_WITH_ERRNO`, `EXPECT_NONNULL`, errno/integer comparison helpers, `ASSERT_INT64_EQ`, `EXPECT_STR_CONTAINS`, and `RETRY_ON_EINTR_GET_ERRNO`. Declares `expectFileStats`.

## Control Flow
Most macros evaluate an expression, print a diagnostic with `__FILE__`, `__LINE__`, errno, and expected value, then return an error from the enclosing function on failure. `ASSERT_INT64_EQ` exits the process.

## State, Persistence, And Dependencies
Macros rely on `errno` being meaningful immediately after expression evaluation. They do not persist state, but they control function returns.

## Integration Points
Used throughout native C tests including FUSE workload and libhdfs tests.

## Risks
Expression arguments with side effects are evaluated once in most macros but some macros reference string arguments more than once. Immediate returns can skip caller cleanup unless tests structure cleanup carefully. `RETRY_ON_EINTR_GET_ERRNO` expects POSIX `-1` failure style.

## Test Signals
Clear stderr diagnostics from these macros are the main native test failure signal.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/expect.h -->
