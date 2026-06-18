# Research Report: subset-b-007388

This grouped report covers Hadoop common `org.apache.hadoop.fs` test sources for subset `subset-b-007388`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDFCachingGetSpaceUsed.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDFCachingGetSpaceUsed.java

Purpose: verifies that `CachingGetSpaceUsed.Builder` can instantiate `DFCachingGetSpaceUsed`, initialize it against a real local file, and report a non-trivial used-space value. It is a narrow integration test for the `GetSpaceUsed` builder path that selects a concrete implementation class.

Important APIs/types/functions: `CachingGetSpaceUsed.Builder`, `GetSpaceUsed`, `DFCachingGetSpaceUsed`, `FileUtil.fullyDelete`, `GenericTestUtils.getTestDir`, `RandomAccessFile`, and `RandomStringUtils.randomAlphabetic`. The helper `writeFile` creates and fsyncs a local file of roughly `FILE_SIZE` bytes before the builder is invoked.

Control flow: `setUp` deletes and recreates the test directory, `testCanBuildRun` writes a file, builds the space-used implementation with a long refresh interval, checks the runtime type and usage lower bound, and closes the instance. `tearDown` deletes the directory.

State and persistence: the test creates local files under the Hadoop test directory and explicitly syncs file contents to disk, so the space-used query is not racing only buffered data. The `DFCachingGetSpaceUsed` instance likely starts background/cache state and is explicitly closed.

Dependencies/integration points: depends on local filesystem semantics, disk accounting via `df`, and the Hadoop `FileUtil` cleanup helper. It exercises the builder's reflection/class-selection integration with `DFCachingGetSpaceUsed`.

Risks and test signals: the assertion allows a small slack below `FILE_SIZE`, but still depends on platform disk accounting and test-directory writability. A regression would show as build failure, wrong implementation type, negative/zero reported usage, or leaked background resources if `close` behavior changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDFCachingGetSpaceUsed.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDFVariations.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDFVariations.java

Purpose: exercises `DF` parsing, mount/filesystem extraction, invalid-path handling, and current-directory mount resolution across Unix and Windows. It protects Hadoop's wrapper around the platform `df` command from malformed output and authority/mount assumptions.

Important APIs/types/functions: `DF`, overridden `DF.getExecString`, `DF.parseExecResult`, `DF.parseOutput`, `DF.getMount`, `DF.getFilesystem`, `Shell.WINDOWS`, and `GenericTestUtils.assertExceptionContains`. The inner `XXDF` class injects deterministic `df` output with a header-like ignored line and one filesystem row.

Control flow: setup creates a test root and teardown makes it writable before deleting it. `testMount` and `testFileSystem` compare parsed values, with Windows expecting drive-prefix behavior. `testDFInvalidPath` generates a non-existent random path and expects `FileNotFoundException`. `testDFMalformedOutput` feeds valid, missing, empty, and short-field outputs into parser methods. `testGetMountCurrentDirectory` resolves the canonical working directory and validates that the returned mount exists and encloses it.

State and persistence: uses only local temporary directories and in-memory `StringReader` output for parser tests. Permission reset in teardown handles tests that may alter directory writability.

Dependencies/integration points: integrates with Hadoop `Shell` platform checks, Java `File` canonical paths, and the `DF` command parser used by disk-space reporting.

Risks and test signals: vulnerable to platform-specific mount formatting and filesystem root behavior. Timeout annotations catch hangs in shell execution or parser loops. Expected failures are precise message checks for malformed `df` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDFVariations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDU.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDU.java

Purpose: validates `DU`, Hadoop's disk-usage monitor, especially cached/background refresh behavior, non-negative accounting, and honoring an initial used-space value.

Important APIs/types/functions: `DU`, `DU.init`, `DU.getUsed`, `DU.close`, `DU.incDfsUsed`, `CommonConfigurationKeys.FS_DU_INTERVAL_KEY`, `Shell.WINDOWS` assumptions, and local `RandomAccessFile` writes. `createFile` writes random bytes to avoid filesystem compression effects.

Control flow: setup skips Windows, clears and recreates a temp directory. `testDU` writes a 32 KiB file, waits for metadata, then checks three modes: background updater with interval, zero interval without a thread, and initialized object before close. `testDUGetUsedWillNotReturnNegative` applies a very large negative delta and asserts clamping at zero. `testDUSetInitialValue` starts with an explicit initial value, waits for a background refresh, then expects actual usage.

State and persistence: creates real files and syncs data to disk. Background refresh threads are initialized and closed in most paths; one branch intentionally checks a non-closed-before-read path and relies on test cleanup.

Dependencies/integration points: local filesystem block accounting, POSIX permissions/metadata timing, `Shell.WINDOWS`, and `FileUtil` cleanup. It protects callers that depend on `DU` not invoking external `du` on every `getUsed`.

Risks and test signals: sleeps make it timing-sensitive. Disk slack is allowed, but compression, delayed allocation, or unusual block sizes can affect reported values. Non-negative and initial-value assertions are strong regression signals for accounting state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDU.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDefaultUri.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDefaultUri.java

Purpose: tests `FileSystem` default URI parsing and the compatibility rule that a bare host without a scheme is treated as HDFS, while malformed bare-host paths with a trailing slash fail.

Important APIs/types/functions: `FileSystem.FS_DEFAULT_NAME_KEY`, `FileSystem.getDefaultUri`, `FileSystem.get`, `FileSystem.setDefaultUri` indirectly via config, `LocalFileSystem`, `UnsupportedFileSystemException`, and `LambdaTestUtils.intercept`.

Control flow: each test sets `fs.defaultFS` to a different string and then validates parsed URI scheme/authority or expected failure. Cases include `hdfs://nn_host`, a port, a trailing slash, bare `nn_host`, invalid `nn_host/`, `file:///`, and `FileSystem.get` on scheme-less values.

State and persistence: only mutates an instance `Configuration`; no filesystem state is written. The class-level configuration is reused across tests, so each test overwrites the relevant key before assertions.

Dependencies/integration points: documents the public configuration contract consumed by Hadoop clients, shell commands, and filesystem factory resolution. `file:///` integration confirms local filesystem lookup still works through `FileSystem.get`.

Risks and test signals: the bare-host-to-HDFS compatibility behavior is subtle and easy to break while tightening URI validation. The test method names contain `tet` typos but are still discovered through `@Test`. Expected exception messages are part of the behavioral contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDefaultUri.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDelegateToFileSystem.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDelegateToFileSystem.java

Purpose: verifies that `AbstractFileSystem.get` for FTP normalizes a URI without an explicit port to the FTP default port regardless of the configured default filesystem URI.

Important APIs/types/functions: `AbstractFileSystem.get`, `FileSystem.setDefaultUri`, `FTP.DEFAULT_PORT`, `DelegateToFileSystem` indirectly through the FTP AFS implementation, and `Configuration`.

Control flow: `testDefaultUriInternal` sets the default filesystem to either `hdfs://dummyhost` or `hdfs://dummyhost:8020`, then resolves `ftp://dummyhost`. It asserts that the resulting AFS URI includes `FTP.DEFAULT_PORT`.

State and persistence: no local files are created. State is confined to a fresh `Configuration`.

Dependencies/integration points: integrates the AFS factory with Apache Commons Net's FTP default port constant and Hadoop's default URI handling. It guards against default-FS authority/port leakage into unrelated schemes.

Risks and test signals: a failure means delegated filesystem construction, URI default-port insertion, or default-FS isolation has regressed. The test uses a dummy FTP host and should not perform network I/O; unexpected network dependency would be a risk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDelegateToFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDelegateToFsCheckPath.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDelegateToFsCheckPath.java

Purpose: verifies that `DelegateToFileSystem` derives its default port behavior from the child `FileSystem` when available, and that `AbstractFileSystem.checkPath` accepts paths with implicit default ports.

Important APIs/types/functions: `DelegateToFileSystem`, `AbstractFileSystem.checkPath`, `FileSystem.getDefaultPort`, `Path`, and dummy `FileSystem` subclasses. `DummyDelegateToFileSystem` wires a custom child filesystem into the delegate.

Control flow: `testCheckPathWithoutDefaultPort` constructs `dummy://dummy-host` with a child filesystem that does not override `getDefaultPort` and checks a matching path. `testCheckPathWithDefaultPort` constructs a URI with port `1234`, then checks a path omitting the port; the overridden child default port should make this acceptable.

State and persistence: no external state. Dummy filesystem methods are stubs returning null/false/empty arrays because only URI/path validation is under test.

Dependencies/integration points: protects the bridge between old `FileSystem` implementations and `AbstractFileSystem` delegates. This is important for schemes where legacy file systems define a meaningful default port.

Risks and test signals: if default-port propagation changes, checkPath may reject paths that should target the same FS. The dummy implementations intentionally avoid real I/O; accidental calls to methods beyond `getDefaultPort` would likely produce null behavior and expose a control-flow regression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDelegateToFsCheckPath.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDelegationTokenRenewer.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDelegationTokenRenewer.java

Purpose: validates the singleton `DelegationTokenRenewer` lifecycle: adding/removing renewable filesystems, periodic renewal, replacement after renewal failure, weak-reference cleanup, cancellation, and avoiding deadlock with multiple tokens.

Important APIs/types/functions: `DelegationTokenRenewer`, `DelegationTokenRenewer.Renewable`, `DelegationTokenRenewer.reset`, `addRenewAction`, `removeRenewAction`, `getRenewQueueLength`, `Token.renew`, `Token.cancel`, `FileSystem.getRenewToken`, `addDelegationTokens`, `setDelegationToken`, Mockito, and `Time.now`.

Control flow: setup resets the singleton and sets a short `renewCycle`. Tests cover normal renewal and cancellation, no-token no-op, renewal failure followed by fetching a replacement token, cleanup after the filesystem weak reference is GC'd, and removing two future-renewing tokens without deadlock.

State and persistence: mutates static `DelegationTokenRenewer.renewCycle` and the singleton renewer queue. The tests rely on background scheduling and weak references, not persistent files.

Dependencies/integration points: integrates with Hadoop security tokens, `Configuration`, filesystem token APIs, and Java GC behavior. Mockito answers provide future renewal times and failure injection.

Risks and test signals: timing sleeps and `System.gc()` make this suite sensitive to scheduler delays and GC nondeterminism. Queue-length assertions, token renewal counts, and cancellation verification are the core signals. Deadlock coverage is enforced with a four-second timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDelegationTokenRenewer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFSMainOperationsLocalFileSystem.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFSMainOperationsLocalFileSystem.java

Purpose: binds the shared `FSMainOperationsBaseTest` contract to Hadoop's `LocalFileSystem`, providing broad inherited coverage for main `FileSystem` operations on the local implementation.

Important APIs/types/functions: `FSMainOperationsBaseTest`, `FileSystem.getLocal`, `Configuration`, `Path`, `createFileSystem`, and `getDefaultWorkingDirectory`.

Control flow: the subclass overrides only two hooks. `createFileSystem` returns a fresh local filesystem from a new configuration. `getDefaultWorkingDirectory` lazily caches the local filesystem working directory in a static `Path wd`.

State and persistence: inherited tests create and delete local filesystem data according to the base class. This subclass adds static caching of the working directory, which can persist across test methods in the same JVM.

Dependencies/integration points: integration point is the test framework's abstract filesystem contract. It ensures local FS behavior stays aligned with common operations expected from all Hadoop `FileSystem` implementations.

Risks and test signals: most behavior and risk live in the base class. The subclass risk is stale static working-directory state if the process working directory or local FS configuration changes during a test run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFSMainOperationsLocalFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFcLocalFsPermission.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFcLocalFsPermission.java

Purpose: attaches the shared `FileContextPermissionBase` permission contract to the local `FileContext` implementation.

Important APIs/types/functions: `FileContextPermissionBase`, `FileContext.getLocalFSFileContext`, JUnit `@BeforeEach`/`@AfterEach`, and `UnsupportedFileSystemException`.

Control flow: the class delegates setup and teardown to the base class and overrides `getFileContext` to return the local FS context. The inherited base tests perform permission operations.

State and persistence: inherited tests create local files/directories and mutate permissions. This subclass has no additional state.

Dependencies/integration points: covers `FileContext` permission behavior for local filesystems, including the `FsPermission` path through the FileContext API rather than the older `FileSystem` API.

Risks and test signals: behavior depends on local OS permission support and user privileges. Windows or permissive filesystems may behave differently depending on assumptions in the base class. Failures point to local `FileContext` permission regression or environment limitations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFcLocalFsPermission.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFcLocalFsUtil.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFcLocalFsUtil.java

Purpose: binds the shared `FileContextUtilBase` utility tests to the local `FileContext`.

Important APIs/types/functions: `FileContextUtilBase`, `FileContext.getLocalFSFileContext`, and the inherited `fc` field from the base class.

Control flow: setup initializes `fc` with the local FS context and then calls `super.setUp()`. All substantive tests are inherited.

State and persistence: local filesystem state is managed by the base class. This subclass only selects the implementation under test.

Dependencies/integration points: integration point is the FileContext utility contract for local filesystem paths. It complements `TestFcLocalFsPermission` by focusing on utility-level behavior rather than permissions.

Risks and test signals: failures are likely either local filesystem environment issues or regressions in FileContext utility methods exercised by the base class. Because the file is a thin adapter, reporting should trace failures back to inherited tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFcLocalFsUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileContext.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileContext.java

Purpose: tests `FileContext` initialization with invalid default URIs and the interaction between configuration-driven and API-driven umask settings.

Important APIs/types/functions: `FileContext.getFileContext`, `FileSystem.FS_DEFAULT_NAME_KEY`, `CommonConfigurationKeys.FS_PERMISSIONS_UMASK_KEY`, `FileContext.getUMask`, `FileContext.setUMask`, `FsPermission.createImmutable`, and `UnsupportedFileSystemException`.

Control flow: `testDefaultURIWithoutScheme` sets the default FS to `/` and expects `UnsupportedFileSystemException`. `testConfBasedAndAPIBasedSetUMask` creates two file contexts from different file URIs, verifies default `022`, mutates the config to `011` and observes both contexts, then explicitly sets each context's umask and verifies later config changes no longer affect that context.

State and persistence: no files are created. State is held in shared `Configuration` and in per-`FileContext` umask override fields.

Dependencies/integration points: covers config propagation in `FileContext`, URI-based context selection, and permission defaults used by file creation across FileContext users.

Risks and test signals: the important regression signal is whether explicit `setUMask` freezes a context's setting while contexts without explicit settings continue reflecting configuration. URI parsing behavior overlaps with default-FS tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileContextDeleteOnExit.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileContextDeleteOnExit.java

Purpose: validates `FileContext.deleteOnExit(Path)` registration, global shutdown-hook installation, finalizer execution, and cleanup of registered paths.

Important APIs/types/functions: `FileContext.getLocalFSFileContext`, `FileContext.deleteOnExit`, static `FileContext.DELETE_ON_EXIT`, static `FileContext.FINALIZER`, `ShutdownHookManager`, `FileContextTestHelper`, and `createFile`/`exists` helpers from `FileContextTestHelper`.

Control flow: setup obtains local `FileContext`; teardown deletes the test root. `testDeleteOnExit` creates two files and one nested path, registers each with delete-on-exit, checks that the global map has one context entry containing the expected paths, verifies the shutdown hook exists, then runs `FileContext.FINALIZER` directly and asserts the map is empty and paths are gone.

State and persistence: creates local files under the FileContext test root and mutates static global delete-on-exit state. Direct finalizer invocation resets that state for the tested context.

Dependencies/integration points: integrates FileContext with Hadoop's `ShutdownHookManager`, local filesystem deletion, and static finalization behavior used at JVM shutdown.

Risks and test signals: because static `DELETE_ON_EXIT` is global, test isolation is important. Failures can indicate hook registration changes, incorrect map cleanup, or recursive delete semantics regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileContextDeleteOnExit.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileContextResolveAfs.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileContextResolveAfs.java

Purpose: tests `FileContext.resolveAbstractFileSystems` when resolving a symlink to a local path. It ensures symlink traversal returns the expected abstract filesystem set.

Important APIs/types/functions: `FileSystem.enableSymlinks`, `FileContext.getFileContext`, `FileSystem.get`, `FileSystem.makeQualified`, `FileContext.createSymlink`, `FileContext.resolveAbstractFileSystems`, and `AbstractFileSystem`.

Control flow: a static block enables symlinks globally. Setup creates a default FileContext. The test creates a local source path and qualified link path, ensures the test root exists, creates the target file, creates a symlink, resolves AFS instances for the link, expects a singleton set, then deletes link and target and closes the local filesystem.

State and persistence: mutates global symlink enablement and creates local files/symlinks under `GenericTestUtils.getTestDir`. Cleanup is performed inline rather than through teardown.

Dependencies/integration points: local symlink support, FileContext symlink creation, `FileSystem`/`AbstractFileSystem` resolution bridge, and default configuration.

Risks and test signals: symlink permissions or platform limitations can affect the test. The 30-second timeout protects against recursive symlink resolution hangs. A result size other than one indicates incorrect AFS deduplication or symlink target resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileContextResolveAfs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileStatus.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileStatus.java

Purpose: verifies `FileStatus` constructors, Writable serialization, Java serialization, equality/ordering semantics, symlink fields, default values, and exact `toString` formatting.

Important APIs/types/functions: `FileStatus`, `Path`, `FsPermission`, `Writable.write/readFields`, `ObjectOutputStream/ObjectInputStream`, `compareTo`, `equals`, and helpers `validateAccessors`/`validateToString`.

Control flow: tests write multiple `FileStatus` instances to a byte array and read them back; exercise full, no-symlink, no-owner, and blank constructors; assert equality depends on path rather than metadata; check ordering by path; validate `toString` for files, directories, and symlinks; and serialize/deserialize a status through Java object serialization.

State and persistence: all state is in memory. No filesystem calls are made beyond constructing `Path` values.

Dependencies/integration points: protects binary compatibility for Hadoop Writable serialization and Java serialization, plus user-visible string formatting consumed by logs/tools. It also documents defaults for owner/group/permission when omitted.

Risks and test signals: exact string assertions make intended output changes noisy but catch accidental regressions. Equality-by-path is subtle and may surprise callers; this test preserves that contract. Serialization failures would be high impact for IPC and persisted metadata paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileSystemCaching.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileSystemCaching.java

Purpose: comprehensively tests `FileSystem` cache identity, cache disablement, default-URI resolution, UGI/user cache keys, close-all behavior, delete-on-exit on close, URI user-info keying, and semaphore-limited concurrent filesystem construction.

Important APIs/types/functions: `FileSystem.get`, `FileSystem.newInstance`, `FileSystem.Cache`, `FileSystem.Cache.Key`, `FileSystem.closeAllForUGI`, `UserGroupInformation`, `FilterFileSystem`, `LocalFileSystem`, `FS_CREATION_PARALLEL_COUNT`, `BlockingThreadPoolExecutorService`, `SubjectInheritingThread`, and Mockito.

Control flow: early tests compare cached and uncached schemes and default FS URI variants. UGI tests use `doAs` to ensure same subject gives same FS and different subjects/users do not. Delete-on-exit tests mock raw filesystem status/delete behavior across close, missing files, removed files, and cancellation. Concurrent construction tests create a custom cache with one, two, or many semaphores and assert how many surplus instances are discarded while all callers receive the same cached instance.

State and persistence: uses static semaphores in inner filesystem classes, FileSystem global cache behavior, UGI subject/token state, and mocked filesystem close/delete state. Most file operations are mocked except local FS instantiation.

Dependencies/integration points: integrates with Hadoop security, cache configuration keys, URI normalization, thread pools, cache construction throttling, and FilterFileSystem delete forwarding.

Risks and test signals: concurrency tests can expose deadlocks or excessive discarded instances. Cache-key regressions can leak credentials across users or conflate URI user-info. Delete-on-exit tests protect close-time cleanup semantics and avoid deleting paths that no longer exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileSystemCaching.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileSystemCanonicalization.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileSystemCanonicalization.java

Purpose: validates `FileSystem` URI canonicalization and `checkPath`/`makeQualified` compatibility across short hostnames, FQDNs, IP addresses, default ports, non-default ports, null authority, mismatched schemes, and authority inherited from the default FS.

Important APIs/types/functions: `FileSystem.getCanonicalUri`, `FileSystem.makeQualified`, `FileSystem.checkPath` indirectly, `NetUtils.getCanonicalUri`, `NetUtilsTestResolver.install`, `CommonConfigurationKeys.FS_DEFAULT_NAME_KEY`, and inner `DummyFileSystem`.

Control flow: `@BeforeAll` installs a deterministic resolver. Each test creates a `DummyFileSystem` from an authority and expected canonical URI, then calls `verifyPaths` over host and IP URI variants with/without ports. `verifyCheckPath` expects either successful qualification preserving authority or an `IllegalArgumentException` with `Wrong FS`.

State and persistence: no filesystem data is written. Static resolver state and `DummyFileSystem.defaultPort` define canonicalization behavior.

Dependencies/integration points: protects the name-resolution logic used by `FileSystem` path validation, especially how default port `123` is supplied. It integrates Hadoop net utilities with FS path qualification.

Risks and test signals: DNS/canonical-host behavior is normally unstable, so the test resolver is essential. Failures indicate path validation becoming too permissive or too strict, especially around default ports and default-FS authority fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileSystemCanonicalization.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileSystemInitialization.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileSystemInitialization.java

Purpose: tests filesystem creation edge cases: URL stream handler registration, missing optional filesystem libraries, and cleanup when `FileSystem.newInstance` initialization fails.

Important APIs/types/functions: `URL.setURLStreamHandlerFactory`, `FsUrlStreamHandlerFactory`, `FileSystem.getFileSystemClass`, `FileSystem.newInstance`, `LambdaTestUtils.intercept`, and inner `FailingFileSystem`.

Control flow: `testInitializationWithRegisteredStreamFactory` registers a Hadoop URL handler factory and then resolves the `file` filesystem class, allowing unrelated `IOException` but guarding against infinite recursion. `testMissingLibraries` expects failure for `s3a` when libraries are absent. `testNewInstanceFailure` registers `FailingFileSystem`, expects initialize failure, and verifies both initialize and close counters are incremented once.

State and persistence: registering a URL stream handler factory is JVM-global and can only be done once. `FailingFileSystem` uses static counters. No files are persisted.

Dependencies/integration points: integration with Java URL handling, service/provider discovery, optional S3A classpath behavior, and FileSystem lifecycle cleanup.

Risks and test signals: JVM-global URL factory registration can conflict with other tests. The cleanup assertion is important: a filesystem that fails during `initialize` must still be closed to avoid leaks, and close failures must not hide the original initialize error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileSystemInitialization.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileSystemStorageStatistics.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileSystemStorageStatistics.java

Purpose: validates `FileSystemStorageStatistics` as an adapter over `FileSystem.Statistics`, including long-statistic iteration, named lookup, distance-bucketed reads, erasure-coded reads, remote read time, and classloader hygiene of the statistics cleaner thread.

Important APIs/types/functions: `FileSystem.Statistics`, `FileSystemStorageStatistics`, `StorageStatistics.LongStatistic`, `getLongStatistics`, `getLong`, `incrementBytesReadByDistance`, `incrementBytesReadErasureCoded`, and `increaseRemoteReadTime`.

Control flow: setup randomly increments multiple statistics. `testGetLongStatistics` iterates all long statistics and compares each value to `getStatisticsValue`. `testGetLong` checks every known key explicitly. `testStatisticsDataReferenceCleanerClassLoader` finds the cleaner thread and asserts its context classloader is null.

State and persistence: all statistics are in memory. Random increments make exact numbers variable, but expected values are computed from the same `FileSystem.Statistics` instance.

Dependencies/integration points: integrates FS operation counters with generic storage-statistics reporting and JVM background cleaner thread behavior.

Risks and test signals: adding/removing statistic keys requires updating the switch or the explicit key list. The cleaner-thread assertion protects against classloader leaks in long-running applications and tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileSystemStorageStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileSystemTokens.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileSystemTokens.java

Purpose: verifies `FileSystem.addDelegationTokens` behavior for filesystems with no token, own token, existing credentials, child filesystems, duplicate children, nested filters, and duplicate service names.

Important APIs/types/functions: `FileSystemTestHelper.MockFileSystem`, `FileSystem.addDelegationTokens`, `getCanonicalServiceName`, `getDelegationToken`, `getChildFileSystems`, `Credentials`, `Token`, `Text`, `FilterFileSystem`, Mockito answers, and helper `verifyTokenFetch`.

Control flow: each test creates mock filesystems with configured service names and child relationships, invokes `addDelegationTokens`, verifies whether token fetches occurred, and asserts credential token counts/services. The deepest test builds nested duplicate children and filtered filesystems to ensure deduplication recurses correctly without fetching tokens already present.

State and persistence: all state is in-memory mocks and `Credentials`. Tokens created in answers have their service set to the requested `Text`.

Dependencies/integration points: protects Hadoop security credential collection for composite filesystems and filters. It ensures callers avoid duplicate token requests and preserve existing credentials.

Risks and test signals: regressions can over-fetch tokens, miss child tokens, or replace existing tokens. The test verifies canonical service lookup is always performed and child traversal occurs even when the current FS has no token.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileSystemTokens.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileUtil.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileUtil.java

Purpose: broad contract suite for `FileUtil`: directory listing, recursive deletion, permission-assisted deletion, symlink handling, disk usage, archive extraction, copy/replace/temp-file helpers, stat conversion, jar/classpath utilities, filesystem comparison, Java untar symlink safety, link reading, regular-file detection, and write helpers for both `FileSystem` and `FileContext`.

Important APIs/types/functions: `FileUtil.list/listFiles/fullyDelete/fullyDeleteContents/getDU/unTar/unTarUsingJava/unZip/copy/stat2Paths/symLink/readLink/isRegularFile/write/createJarWithClassPath/getJarsInDirectory/compareFs`, `FileUtils`, Commons Compress tar/zip streams, Hadoop `Path`, `FileSystem`, `FileContext`, `FsPermission`, and helper classes `Verify` and `MyFile`.

Control flow: setup builds a temp tree with files, directories, symlinks to files/dirs, partitioned files, and a symlink cycle. Deletion tests verify symlinks are removed without deleting targets, dangling links are handled, and permission failures return false while optionally granting permissions can recover. Archive tests create tar/zip inputs, test permissions, reject traversal entries like `../foo`, and verify Java untar preserves in-tree symlinks but rejects arbitrary symlink escapes. Copy tests cover file/dir copy and source deletion. Later tests cover classpath jar manifest expansion, jar discovery, compareFs URI behavior, symlink creation edge cases, readLink edge cases, and writing bytes/strings to FS and FC.

State and persistence: uses JUnit `@TempDir` plus some `tmp` relative directories in Java untar tests, cleaned in finally blocks. It changes file permissions, creates symlinks, creates archives, and writes local files.

Dependencies/integration points: local OS symlink and permission semantics, Commons IO/Compress, Hadoop local FS, classpath manifest behavior, path traversal protections, and Java NIO symlink APIs.

Risks and test signals: high platform sensitivity around permissions, symlinks, Windows behavior, and archive file modes. Security-sensitive signals include rejecting zip/tar outputs outside the destination and avoiding symlink target deletion. Exact file lengths, jar manifest classpaths, and write/read equality protect data correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFilterFileSystem.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFilterFileSystem.java

Purpose: protects the `FilterFileSystem` delegation surface and initialization/configuration behavior. It ensures methods that should be overridden are overridden, methods that should rely on base defaults are not, and embedded/raw filesystems receive configuration correctly.

Important APIs/types/functions: `FilterFileSystem`, `LocalFileSystem`, reflection on `FileSystem.getDeclaredMethods`, marker interface `MustNotImplement`, `FileSystem.getLocal`, `FileSystem.get`, checksum setters, `rename` with `Options.Rename`, `hasPathCapability`, and inner `FilterLocalFileSystem`.

Control flow: `testFilterFileSystem` iterates non-static/non-private/non-final `FileSystem` methods and checks whether `FilterFileSystem` implements or does not implement each based on `MustNotImplement`. Initialization tests use mocks to verify embedded FS initialization is skipped when it already has a config and performed when it does not. Configuration-depth tests walk nested filter chains and verify conf propagation. Passthrough tests verify checksum flags and rename options delegate to the raw FS. Multipart capability is expected false on the filter.

State and persistence: mostly mocks and configuration. `@BeforeAll` configures custom schemes and disables caching for deterministic instances.

Dependencies/integration points: reflection catches API drift in `FileSystem`, while config tests cover local/filter filesystem construction paths used by production schemes.

Risks and test signals: when `FileSystem` gains new methods, this test may fail deliberately to force a conscious wrapper decision. Incorrect passthrough can silently bypass filter-specific semantics or fail to apply raw FS options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFilterFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFilterFs.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFilterFs.java

Purpose: verifies that `FilterFs` implements the required `AbstractFileSystem` delegation surface and can wrap an AFS whose authority is optional, such as ViewFs.

Important APIs/types/functions: `FilterFs`, `AbstractFileSystem`, reflection, `DontCheck` exclusions, `ConfigUtil.addLink`, `FileContext.getFileContext`, and ViewFs URI `viewfs://custom/`.

Control flow: `testFilterFileSystem` iterates non-static/non-private/non-final methods declared on `AbstractFileSystem`; unless listed in `DontCheck`, each must be declared on `FilterFs`. `testFilteringWithNonrequiredAuthority` configures a ViewFs link and constructs an anonymous `FilterFs` over the default AFS.

State and persistence: uses only configuration and FileContext/AFS objects. No files are written.

Dependencies/integration points: protects API parity for AbstractFileSystem wrappers and integration with ViewFs mount-table configuration where authorities are not always required like ordinary schemes.

Risks and test signals: reflection failures indicate wrapper drift after adding or changing AFS methods. The ViewFs wrapping test guards against over-strict authority validation in filter constructors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFilterFs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsOptions.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsOptions.java

Purpose: tests `Options.ChecksumOpt.processChecksumOpt` merging rules for default checksum options, optional custom options, and bytes-per-checksum overrides.

Important APIs/types/functions: `Options.ChecksumOpt`, `DataChecksum.Type.CRC32`, `DataChecksum.Type.CRC32C`, `processChecksumOpt`, `getChecksumType`, and `getBytesPerChecksum`.

Control flow: the test builds a default CRC32/512 option, processes null custom options with and without explicit bytes-per-checksum, processes an empty custom option that should inherit defaults, then processes a CRC32C/2048 option with and without an explicit `4096` bytes-per-checksum override.

State and persistence: all state is in memory and immutable option-like objects.

Dependencies/integration points: checksum option processing is consumed by filesystem create paths, so this test protects caller/default merging semantics before lower-level data checksum creation.

Risks and test signals: regressions can select the wrong checksum algorithm or block size, affecting compatibility and data verification. The helper assertions keep the expected type and bytes-per-checksum pair explicit for every case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsShell.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsShell.java

Purpose: tests generic `FsShell` command-runner behavior: invalid `--conf` handling, help/tracing path execution, invalid command messaging, and null exception message rendering.

Important APIs/types/functions: `FsShell.main`, `FsShell`, `ToolRunner.run`, `CommandFactory`, `Command`, `GenericTestUtils.SystemErrCapturer`, and Mockito.

Control flow: `testConfWithInvalidFile` calls `FsShell.main` with `--conf=invalidFile` and expects a runtime exception. `testTracing` runs `-help ls cat` through a configured shell and closes it. `testDFSWithInvalidCommmand` runs a malformed single-token `dfs -mkdirs` command and checks stderr contains unknown-command and usage text. `testExceptionNullMessage` installs a mocked command that throws `IllegalArgumentException` without a message and expects `Null exception message`.

State and persistence: no filesystem data is written. Tests capture and restore stderr via utility capturers or try/finally shell close.

Dependencies/integration points: command factory dispatch, ToolRunner, generic config parsing, stderr formatting, and shell help/usage generation.

Risks and test signals: user-facing diagnostics are the main contract. Null exception messages must not produce confusing output or secondary failures. The tracing test is mostly a smoke path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsShell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsShellCopy.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsShellCopy.java

Purpose: broad tests for FsShell copy commands: `-get`, `-put`, `-copyFromLocal`, `-moveFromLocal`, `-getmerge`, checksum handling, Windows local path parsing, direct writes, lazy-persist overwrite behavior, destination resolution, missing parents, and permission-denied reporting.

Important APIs/types/functions: `FsShell.run`, `LocalFileSystem`, checksum files via `getChecksumFile`, `FsPermission`, `GenericTestUtils.getTempPath`, helpers `checkPut`, `prepPut`, `readFile`, `pathAsString`, and shell commands `-get`, `-put`, `-getmerge`, `-moveFromLocal`, `-copyFromLocal`, `-cat`, `-rm`.

Control flow: setup creates a shared local shell root and source/destination paths; per-test setup recreates a checksum-protected source file. Tests cover copying with/without CRC, corrupted checksum failure, ignoring CRC, file and directory put behavior for existing/missing destinations, Windows path variants, directory-looking destination suffixes, getmerge ordering/newline/skip-empty behavior, moveFromLocal source deletion and conflict handling, direct-copy temp-file behavior, missing parent failures, source permission failures, and lazy-persist direct overwrite rules.

State and persistence: uses local filesystem files, checksum sidecars, working-directory changes, permission mutations, stderr capture, and shared static shell/local FS state.

Dependencies/integration points: local filesystem checksum implementation, shell command parsing, path qualification, platform-specific Windows path support, and permission error propagation.

Risks and test signals: destination resolution is subtle, especially `.` and trailing `/`/`/.`. Permission tests must restore permissions. Checksum tests catch data-integrity regressions, and direct-write tests ensure `._COPYING_` cleanup changes only when expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsShellCopy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsShellList.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsShellList.java

Purpose: tests `FsShell -ls` on local files, including checksum-enabled files, special character names on non-Windows platforms, quoted output mode, and security configuration validation.

Important APIs/types/functions: `FsShell.run`, `LocalFileSystem`, `FileSystem.getLocal`, `setVerifyChecksum`, `setWriteChecksum`, `getChecksumFile`, `CommonConfigurationKeysPublic.HADOOP_SECURITY_AUTHENTICATION`, and AssertJ/JUnit assertions.

Control flow: `@BeforeAll` creates a local shell and test root with checksum verification/writing enabled. `createFile` writes a local file and asserts its checksum sidecar exists. `testList` lists the root after creating normal files and, on non-Windows, names with backspace/tab/carriage-return characters; it also runs `-ls -q`. `testListWithUGI` sets an invalid authentication method and expects `IllegalArgumentException`.

State and persistence: creates local files under `test.build.data` and removes the root in `@AfterAll`. Static shell/local FS state persists across tests.

Dependencies/integration points: local filesystem listing, checksum sidecar behavior, special-character rendering, shell quote mode, and UGI/security config initialization.

Risks and test signals: platform-specific filename legality is handled by skipping special names on Windows. Failures point to list command formatting, security config validation, or local checksum setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsShellList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsShellReturnCode.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsShellReturnCode.java

Purpose: validates FsShell exit codes and diagnostics for chmod/chown/chgrp, invalid copy sources, nonexistent glob removal, invalid default FS fallback, interrupted command execution, and owner/group argument validation.

Important APIs/types/functions: `FsShell`, `FsShellPermissions.Chown/Chgrp`, `FsCommand`, `PathData`, `CommandFactory`, `LocalFileSystemExtn`, `RawLocalFileSystemExtn`, `InterruptedIOException`, `HADOOP_SHELL_MISSING_DEFAULT_FS_WARNING_KEY`, `FS_DEFAULT_NAME_KEY`, and stderr capture through `ByteArrayOutputStream`.

Control flow: setup registers an extended local filesystem whose raw layer records owner/group changes. `testChmod`, `testChown`, and `testChgrp` create files and assert exit codes for existing paths, missing paths, and globs; helper `change` also verifies owner/group changes. Diagnostic tests check `-get` invalid source output, `-rm` with/without `-f`, and `-ls file:///` despite an invalid default FS. `testInterrupt` registers a custom command that throws `InterruptedIOException` on files and expects exit 130. Fake Chown/Chgrp classes test parser validity for user/group names, including Windows-specific spaces.

State and persistence: creates local test files, mutates static owner/group maps in the raw FS extension, captures/restores stderr, and uses static shell/configuration objects.

Dependencies/integration points: command exit-code aggregation, glob expansion, shell permissions commands, local FS owner/group APIs, default FS resolution, and interrupt mapping to shell exit code 130.

Risks and test signals: exit codes must reflect any failed argument, not just the last item. Diagnostics must avoid `null`. Argument validation differs on Windows. Static owner/group maps could leak if paths overlap, but test paths are scoped under a temp root.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsShellReturnCode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsShellTouch.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsShellTouch.java

Purpose: tests FsShell touch commands, including `-touchz`, `-touch`, timestamp parsing, create/no-create behavior, access-time-only and modification-time-only updates, and directory timestamp updates.

Important APIs/types/functions: `FsShell.run`, `LocalFileSystem`, `TouchCommands.Touch.getDateFormat`, `FileStatus.getAccessTime`, `FileStatus.getModificationTime`, `GenericTestUtils.getTempPath`, and shell options `-touchz`, `-touch`, `-c`, `-t`, `-a`, `-m`.

Control flow: static setup creates a local shell rooted in a temp directory. Each test enables checksum verification/writing. `testTouchz` creates a zero-length file, allows repeated touchz, and fails when parent does not exist. `testTouch` checks `-c` on missing files, explicit timestamp creation, access-only, modification-only, both-times updates, missing timestamp failure, and `-c` on an existing file. `testTouchDir` repeats timestamp updates for an existing directory and verifies selective time changes.

State and persistence: creates/deletes local files and directories under the shell working directory. Uses short sleeps to ensure distinct timestamps for directory checks.

Dependencies/integration points: shell command parser, local FS timestamp setters, FileStatus timestamp reporting, and Touch command date format.

Risks and test signals: timestamp precision and filesystem support for access time can vary. The tests compare exact parsed millisecond values, so regressions or platform truncation are visible. Parent existence behavior is an important user-facing contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsShellTouch.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsUrlConnectionPath.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsUrlConnectionPath.java

Purpose: verifies `FsUrlStreamHandlerFactory`/`FsUrlConnection` can open file URLs for absolute and relative paths, including paths containing encoded spaces.

Important APIs/types/functions: `URL.setURLStreamHandlerFactory`, `FsUrlStreamHandlerFactory`, Java `URL.openStream`, local `FileWriter`, and helper `readStream`.

Control flow: `@BeforeAll` writes four files: absolute, relative, absolute with a space, and relative with a space, then registers the FS URL stream handler. Tests open URL strings for absolute/relative paths and encoded-space variants and assert stream availability is greater than one. `@AfterAll` deletes the created files.

State and persistence: writes files in the current working directory and absolute current directory. The URL stream handler factory registration is JVM-global.

Dependencies/integration points: Java URL handling, Hadoop FS URL stream factory, file scheme path parsing, relative path resolution, and percent-decoding of spaces.

Risks and test signals: global URL factory setup can conflict with other tests if already registered. `InputStream.available()` is a weak proxy for content but sufficient for non-empty local files. The import creates a `Configuration` constant that is unused.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsUrlConnectionPath.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestGetEnclosingRoot.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestGetEnclosingRoot.java

Purpose: tests the default `FileSystem.getEnclosingRoot` behavior for the local/default filesystem. It verifies root equivalence, idempotence, behavior for existing and non-existing child paths, and use through a wrapped UGI context.

Important APIs/types/functions: `FileSystem.get`, `FileSystem.getEnclosingRoot`, `FileSystem.makeQualified`, `UserGroupInformation.doAs`, and `HadoopTestBase` assertions.

Control flow: helper `getFileSystem` obtains a default FS from a new configuration, and helper `path` qualifies path strings. Tests compare root and `/foo/bar` results, create `/foo/bar` for existing-path behavior, check non-existing path behavior, and call the method under a remote user through `doAs`.

State and persistence: may create a `/foo/bar` path on the default filesystem for `testEnclosingRootPathExists`; no explicit teardown is present in this file.

Dependencies/integration points: default filesystem configuration, local filesystem root semantics, path qualification, and UGI-wrapped filesystem access.

Risks and test signals: creating `/foo/bar` can be sensitive if the default FS is not an isolated test filesystem. The expected default contract is simple: all tested paths enclose to the filesystem root and repeated calls are idempotent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestGetEnclosingRoot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestGetFileBlockLocations.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestGetFileBlockLocations.java

Purpose: validates `FileSystem.getFileBlockLocations(FileStatus, start, len)` parameter checks and coverage invariants for a local/default filesystem file.

Important APIs/types/functions: `FileSystem.getFileBlockLocations`, `BlockLocation`, `FileStatus`, `FSDataOutputStream`, `GenericTestUtils.getTempPath`, `Path.getFileSystem`, and local helper `oneTest`.

Control flow: setup creates a 4 MiB file by writing 1 KiB zero buffers until the target length. `testFailureNegativeParameters` expects `IllegalArgumentException` for negative start or length. `testGetFileBlockLocations1` checks deterministic ranges before, within, and beyond EOF. `testGetFileBlockLocations2` runs 1000 random start/end pairs. `oneTest` normalizes range order, obtains locations, sorts by offset/length, and asserts the returned locations cover the requested interval clipped to file length, or return empty when starting beyond EOF.

State and persistence: creates and deletes a temp file per test and closes the filesystem in teardown.

Dependencies/integration points: filesystem block location implementation, local/default FS file creation, and block-location range semantics.

Risks and test signals: random testing can expose edge cases but is nondeterministic due to `System.nanoTime` seeding. Invariants focus on coverage rather than exact block layout, making the test portable across filesystems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestGetFileBlockLocations.java -->
