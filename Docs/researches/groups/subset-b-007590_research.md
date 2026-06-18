# Research: subset-b-007590

This grouped report covers Hadoop S3A performance, prefetch, S3Guard, and scale test sources. Each section preserves the source path and is bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestCreateFileCost.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestCreateFileCost.java

Purpose: parameterized integration cost tests for S3A create paths with `fs.s3a.create.performance` disabled and enabled. It validates legacy `create`, `createFile`, builder `must()` options, recursive/nonrecursive creation, overwrite behavior, custom create headers exposed as xattrs, and the intentional safety tradeoff of performance creation.

Important APIs/types/functions: `ITestCreateFileCost` extends `AbstractS3ACostTest`; `params()` runs `{false,true}`; `expected()` maps normal `OperationCost` expectations to `NO_HEAD_OR_LIST` under the performance flag; tests call `create`, `file`, `buildFile`, `verifyMetrics`, `interceptOperation`, and raw `S3AFileSystem` builders. It checks `OBJECT_BULK_DELETE_REQUEST`, `OBJECT_DELETE_REQUEST`, `FS_S3A_CREATE_HEADER`, `FS_S3A_CREATE_PERFORMANCE`, `FS_S3A_CONDITIONAL_CREATE_ENABLED`, and `RemoteFileChangedException`.

Control flow: setup disables filesystem caching and toggles performance flags. Each test constructs an isolated method path, performs one create variant, then verifies HEAD/LIST/delete metrics or expected exceptions. The final invalid-store test creates a child beneath a path, writes a file over that parent with performance mode, verifies both objects coexist, then repairs state in `finally`.

State and persistence: creates and deletes real S3A objects and directory markers; custom headers persist as object metadata/xattrs. Performance mode can produce an ill-formed namespace where a path is both file and parent prefix.

Dependencies/integration: S3A create builder, contract utilities, cost constants, S3A instrumentation, conditional create support, and object metadata headers.

Risks: expected request costs vary with conditional-create availability and third-party stores; performance mode deliberately skips safety checks; failed cleanup can leave inconsistent test data.

Test signals: success is exact counter diffs, expected `FileAlreadyExistsException`/`RemoteFileChangedException`, progress callback activity, xattr header equality, and final namespace assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestCreateFileCost.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestCreateSessionTimeout.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestCreateSessionTimeout.java

Purpose: S3 Express integration test proving the S3A CreateSession call honors the configured request timeout instead of a hardcoded longer timeout.

Important APIs/types/functions: `ITestCreateSessionTimeout` extends `AbstractS3ACostTest`; `createConfiguration()` requires an S3 Express bucket, disables FS caching, removes bucket overrides, enables HTTP signer customization, sets `SlowSigner`, `REQUEST_TIMEOUT=10ms`, and `RETRY_LIMIT=1`. `SlowSigner` extends `CustomHttpSigner` and sleeps in sync/async signing. `setup()` temporarily lowers `AWSClientConfig` minimum durations.

Control flow: the test invokes `fs.getFileStatus(path("testShortTimeout"))`, expects `AWSApiCallTimeoutException`, measures elapsed time with `DurationInfo`, verifies it is below a five-second threshold, confirms the signer sleep was interrupted, and scans the nested stack trace for `createSession`.

State and persistence: no test directory cleanup or mkdir work is needed; the test avoids persistent data and only creates a new filesystem session path probe. Static `AtomicLong` and `AtomicBoolean` coordinate sleep duration and interruption observation.

Dependencies/integration: AWS SDK HTTP signer SPI, S3A custom signer plumbing, S3 Express session creation, S3A timeout wrapping, and bucket capability assumptions.

Risks: only meaningful on S3 Express; timing assertions are environment-sensitive; static interruption state could be affected by repeated runs if not reset externally.

Test signals: expected timeout exception, bounded call duration, interrupted signing sleep, and evidence that the failing path went through CreateSession.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestCreateSessionTimeout.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestDirectoryMarkerListing.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestDirectoryMarkerListing.java

Purpose: semantic integration tests ensuring retained S3 directory markers are not mistaken for empty directories when listing, globbing, creating, deleting, or renaming. It is intentionally backport-friendly and does not use newer metric-cost helpers.

Important APIs/types/functions: `ITestDirectoryMarkerListing` extends `AbstractS3ATestBase`; `createConfiguration()` disables create-performance flags. `setup()` obtains an AWS SDK `S3Client`, computes S3 keys from `S3AFileSystem.pathToKey`, uses `fs.mkdirs`, `touch`, and direct `putObject` to create a marker directory, a peer object, and a real file below the marker. Helpers `head`, `head404`, `exec`, `toList`, `assertContainsExactlyStatusOfPaths`, and `assertRenamed` wrap assertions.

Control flow: tests first verify raw marker/file existence, then exercise `listStatus`, `listFiles`, `globStatus`, and `listLocatedStatus`; create APIs must reject no-overwrite attempts; nonrecursive delete must fail while recursive delete removes marker and child; rename tests validate base-directory moves, file moves into marker directories, explicit destination path moves, and failed empty-dir-over-marker rename.

State and persistence: real bucket objects are created through both S3A and low-level SDK calls. Teardown deletes exact marker, marker-with-slash, peer, and child keys before superclass cleanup to avoid audit failures from surplus markers.

Dependencies/integration: AWS SDK S3 model, S3A path/key conversion, audit spans for raw calls, exception translation, filesystem listing/glob/rename/delete semantics.

Risks: direct SDK setup bypasses normal S3A invariants; object ordering differs between objects and common prefixes; parameterized path characters require glob escaping.

Test signals: exact `FileStatus` path sets, expected `FileAlreadyExistsException` and `PathIsNotEmptyDirectoryException`, HEAD/404 checks, and post-rename/delete namespace checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestDirectoryMarkerListing.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestS3ADeleteCost.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestS3ADeleteCost.java

Purpose: integration cost tests for S3A delete and directory-marker cleanup behavior, focusing on request counts and marker state after deleting files and deep directory trees.

Important APIs/types/functions: `ITestS3ADeleteCost` extends `AbstractS3ACostTest`; it uses `verifyMetrics`, `verifyInnerGetFileStatus`, `assertEmptyDirStatus`, `getDeleteMarkerStatistic`, `directoriesInPath`, `verifyNoListing`, and statistics such as `OBJECT_METADATA_REQUESTS`, `OBJECT_LIST_REQUEST`, `OBJECT_DELETE_REQUEST`, `OBJECT_DELETE_OBJECTS`, `DIRECTORIES_CREATED`, `DIRECTORIES_DELETED`, `FILES_DELETED`, and `FAKE_DIRECTORIES_DELETED`.

Control flow: file-delete tests create directories/files, delete one target, then assert file deletion counters and parent directory status. Deep-marker tests create sibling state to avoid parent recreation ambiguity, create nested directories, delete the parent recursively, assert delete-object count, verify no listings remain, and recreate the parent. File-creation marker tests ensure creating a file inside an existing deep marker tree does not delete parent markers.

State and persistence: creates and removes real objects and markers in the test bucket. Teardown explicitly deletes the test directory before superclass teardown to avoid audit failures from leftover markers.

Dependencies/integration: S3A delete implementation, bulk-versus-single marker delete accounting, directory marker statistics, S3A file status `Tristate`, and listing failure behavior.

Risks: exact counters vary with bulk delete configuration; marker recreation/deletion can be affected by sibling objects and store behavior.

Test signals: exact metric diffs, object/delete counters, empty-dir status after file removal, `FileNotFoundException` for removed listings, and successful parent recreation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestS3ADeleteCost.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestS3AMiscOperationCost.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestS3AMiscOperationCost.java

Purpose: cost tests for miscellaneous S3A operations, especially `mkdirs` over existing directories and `getContentSummary` paths, with audit span accounting enabled.

Important APIs/types/functions: `ITestS3AMiscOperationCost` extends `AbstractS3ACostTest`; `createConfiguration()` enables `AUDIT_ENABLED`. `withAuditCount()` builds an `AUDIT_SPAN_CREATION` probe. Tests use `getContentSummary`, `verifyMetrics`, `verifyMetricsIntercepting`, `touch`, and `ContentSummary` assertions.

Control flow: `testMkdirOverDir` creates a marker directory and repeats `mkdirs`, checking only a directory LIST and one audit span. Root content summary checks invocation count. Directory summary creates a nested child file, calls `getContentSummary`, verifies expected file/directory totals and cost of file probe plus list. Missing-path summary expects `FileNotFoundException` after repeated file probes and lists.

State and persistence: uses real S3A paths and directory/file objects under method paths. Audit state is tracked through metrics rather than persistent data.

Dependencies/integration: S3A audit subsystem, content summary traversal, object metadata/list counters, and `AbstractS3ACostTest` probe helpers.

Risks: audit count assumptions require audit to remain enabled; content summary implementation changes can legitimately alter list/probe counts.

Test signals: exact invocation/audit/HEAD/LIST metric diffs, expected missing-path exception, and `ContentSummary` directory/file counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestS3AMiscOperationCost.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestS3AMkdirCost.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestS3AMkdirCost.java

Purpose: integration cost tests for `S3AFileSystem.mkdirs`, documenting expected HEAD/LIST behavior for existing dirs, child/grandchild creation, sibling creation, and mkdir over file failures.

Important APIs/types/functions: `ITestS3AMkdirCost` extends `AbstractS3ACostTest`; it uses `verifyMetrics`, `verifyMetricsIntercepting`, `dir`, `touch`, and metrics `OBJECT_METADATA_REQUESTS` and `OBJECT_LIST_REQUEST` with `OperationCost` constants `FILESTATUS_*`.

Control flow: tests create a base marker directory, run `mkdirs` over it, then create child or grandchild paths and assert the sequence of file and directory probes. After a grandchild exists, sibling creation is asserted to cost less because the immediate parent can be found by listing. The over-file test touches a file and expects `FileAlreadyExistsException`.

State and persistence: real S3 directory markers and file objects are created in the test bucket; no custom teardown beyond base class is defined.

Dependencies/integration: S3A mkdir implementation, directory marker lookup, file status probing, and cost helper infrastructure.

Risks: exact request counts are coupled to current mkdir status-probe order; marker retention policy or parent discovery changes will break assertions.

Test signals: exact HEAD/LIST metric diffs and expected failure when a target path is already a file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestS3AMkdirCost.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestS3AOpenCost.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestS3AOpenCost.java

Purpose: integration tests for `openFile()` cost, stream statistics, checksum disabling, supplied file length semantics, EOF behavior, positioned reads, and vectored reads across Classic, Prefetch, and Analytics stream implementations.

Important APIs/types/functions: `ITestS3AOpenCost` extends `AbstractS3ACostTest`; setup writes a fixed text file, stores `FileStatus` and length, and detects stream type with `S3ATestUtils.streamType`. Helpers include `openFile`, `assumeNoPrefetching`, `assumeNotAnalytics`, `assertS3StreamClosed`, and `assertS3StreamOpen`. Tests use open-file options for length, read policy, footer cache, and buffer size, plus IOStatistics assertions for `ACTION_FILE_OPENED`, `ACTION_HTTP_GET_REQUEST`, and `ACTION_HTTP_HEAD_REQUEST`.

Control flow: the class verifies opening with a status from another filesystem avoids initial IO, reads trigger stream opens, checksum validation is disabled, shorter supplied lengths truncate reads, longer lengths produce EOF behavior, and read/readFully/positioned/vectored reads past EOF differ by stream implementation. Several tests skip when prefetching or Analytics invalidates the Classic assumptions.

State and persistence: creates a small real S3 object per test. Stream state is tracked through FS/stream IOStatistics and inner `S3AInputStream` open/closed flags.

Dependencies/integration: S3A open-file builder, stream type selection, S3A input stream internals, Hadoop `FileRange` vectored IO, futures for vectored ranges, and checksum configuration.

Risks: assertions are stream-implementation-specific; Analytics may issue HEAD where Classic would not; counters update only on stream close.

Test signals: exact metric/statistic diffs, EOF exceptions, `-1` reads past EOF, stream open/closed assertions, and vectored future failure checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestS3AOpenCost.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestS3ARenameCost.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestS3ARenameCost.java

Purpose: integration cost tests for S3A file rename and root-file delete/rename behavior.

Important APIs/types/functions: `ITestS3ARenameCost` extends `AbstractS3ACostTest`; it uses `OperationCost.RENAME_SINGLE_FILE_DIFFERENT_DIR`, `RENAME_SINGLE_FILE_SAME_DIR`, `GET_FILE_STATUS_FNFE`, `COPY_OP`, `FILE_STATUS_FILE_PROBE`, and metrics including `OBJECT_COPY_REQUESTS`, `OBJECT_DELETE_REQUEST`, `OBJECT_DELETE_OBJECTS`, `FILES_DELETED`, and directory-marker counters.

Control flow: different-directory rename creates a deep source directory with a second sibling source file so the parent should remain, creates destination parents, renames one file, then verifies request-cost and namespace outcomes. Same-directory rename verifies a lower-cost copy/delete path. Root rename/delete use UUID root paths and `finally` cleanup to assert no parent directory marker operations happen at root.

State and persistence: creates real S3A files/directories and performs copy/delete-based rename. Root tests deliberately write to `/src-uuid` and `/dest-uuid` to avoid parallel collision.

Dependencies/integration: S3A rename implementation, copy metadata read cost, directory-marker recreation/deletion logic, and metric validator helpers.

Risks: exact costs depend on status-probe sequence and marker policy; root path tests must clean up even on assertion failure.

Test signals: exact metric diffs, successful rename boolean, file/directory existence checks, and absence of source paths after rename.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestS3ARenameCost.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestUnbufferDraining.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestUnbufferDraining.java

Purpose: integration tests for Classic S3A stream `unbuffer()` behavior when async draining versus aborting is expected.

Important APIs/types/functions: `ITestUnbufferDraining` extends `AbstractS3ACostTest`; `createConfiguration()` disables prefetching, forces `INPUT_STREAM_TYPE=Classic`, removes timeout/connection/read-ahead overrides, and disables checksums. `setup()` creates a separate brittle filesystem with `ASYNC_DRAIN_THRESHOLD=1`, tiny connection pool, low retry/timeouts, and `READAHEAD=1000`. Helpers include `createTestFile`, `lookupCounter`, `assertReadPolicy`, and inner-stream extraction.

Control flow: `testUnbufferDraining` opens near the end of a 50 KB file with file status and low drain threshold, repeatedly seeks/reads/unbuffers, expects Random policy, counts unbuffer events, no aborts, and two policy changes. `testUnbufferAborting` opens with whole-file policy, repeatedly reads/unbuffers at the beginning, expects abort count equal to attempts and Sequential policy retained. Teardown aggregates brittle FS IOStatistics and closes it.

State and persistence: writes a real S3 object for each test and uses a separate filesystem instance whose statistics are inspected after stream close.

Dependencies/integration: Classic `S3AInputStream`, async drain threshold parsing, open-file builder options, IOStatistics propagation, AWS client duration limits.

Risks: intentionally brittle connection/timeouts can make cleanup fragile; behavior is Classic-only and depends on read policy.

Test signals: stream-level and filesystem-level `STREAM_READ_UNBUFFERED`, `STREAM_READ_ABORTED`, and `STREAM_READ_SEEK_POLICY_CHANGED` counters, plus input policy assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestUnbufferDraining.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/OperationCost.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/OperationCost.java

Purpose: immutable value type and catalog of expected S3A HEAD/LIST request costs used by performance integration tests.

Important APIs/types/functions: `OperationCost` stores `head` and `list` counts, exposes package-private `head()`/`list()`, `plus(OperationCost)`, and `toString()`. Constants model individual probes (`HEAD_OPERATION`, `LIST_OPERATION`, `FILE_STATUS_FILE_PROBE`, `FILE_STATUS_DIR_PROBE`) and aggregate operations such as `GET_FILE_STATUS_ON_FILE`, `GET_FILE_STATUS_ON_DIR`, `GET_FILE_STATUS_FNFE`, `COPY_OP`, `RENAME_SINGLE_FILE_DIFFERENT_DIR`, `RENAME_SINGLE_FILE_SAME_DIR`, `CREATE_FILE_OVERWRITE`, and `CREATE_FILE_NO_OVERWRITE`.

Control flow: no runtime side effects; aggregate constants are composed at class initialization with `plus()`.

State and persistence: immutable in-memory counts only; no external persistence.

Dependencies/integration: consumed by `OperationCostValidator` and `AbstractS3ACostTest` callers to turn semantic operations into metric probes for `OBJECT_METADATA_REQUESTS` and `OBJECT_LIST_REQUEST`.

Risks: constants are tightly coupled to S3A implementation probe order; when S3A optimizes or changes marker/status logic, tests using these constants must be updated.

Test signals: this file is not itself a test, but all cost tests indirectly validate its constants by asserting live metric diffs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/OperationCost.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/OperationCostValidator.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/OperationCostValidator.java

Purpose: reusable test harness for declarative assertions over S3A instrumentation counters around an operation or expected exception.

Important APIs/types/functions: `OperationCostValidator.builder(S3AFileSystem)` creates a `Builder` with selected metrics or all counters/durations. The validator tracks `S3ATestUtils.MetricDiff` objects for mutable counter metrics from `S3AInstrumentation`, exposes `exec`, `intercepting`, `get`, `resetMetricDiffs`, and static probe builders `always`, `probe`, `probes`, and `expect`. Nested `ExpectedProbe`, `ExpectSingleStatistic`, `ProbeList`, and `EmptyProbe` implement conditional verification.

Control flow: construction filters requested statistics to mutable counters. `exec()` resets diffs, skips the test through AssertJ assumptions if every probe is disabled, executes the callable, logs operation state and IOStatistics, then verifies each enabled probe. `intercepting()` wraps `LambdaTestUtils.intercept` inside `exec()` so exception paths also get metric validation.

State and persistence: stores metric-diff baselines and instrumentation `IOStatistics` references in memory only. It clears builder metric lists after construction.

Dependencies/integration: S3A instrumentation, Hadoop metrics2 `MutableCounter`, `StatisticTypeEnum`, AssertJ assumptions, LambdaTestUtils, and pretty IOStatistics logging.

Risks: non-counter metrics are silently ignored; disabled probes skip execution, which can hide coverage on stores without those metrics; exact counter names must be tracked.

Test signals: downstream tests fail on mismatched metric diffs and log complete instrumentation state for diagnosis.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/OperationCostValidator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/prefetch/MockS3ARemoteObject.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/prefetch/MockS3ARemoteObject.java

Purpose: in-memory mock `S3ARemoteObject` for prefetch unit tests, with deterministic content and one-shot fault injection.

Important APIs/types/functions: package-private `MockS3ARemoteObject` extends `S3ARemoteObject`; constructors create fake read context, object attributes, callbacks, empty statistics, and change tracker. `openForRead(offset,size)` validates ranges, optionally throws one `IOException`, and returns an AWS `ResponseInputStream<GetObjectResponse>` over a `ByteArrayInputStream`. `close()` is a no-op. `byteAtOffset()` returns `offset % 128`. `createClient()` builds minimal `ObjectInputStreamCallbacks`.

Control flow: construction fills `contents` with predictable bytes. A test can set `throwExceptionOnOpen`; the first open clears the flag and fails, while later opens succeed.

State and persistence: keeps byte-array contents and fault flag in memory; no S3 or local filesystem access.

Dependencies/integration: AWS SDK response streams, Hadoop prefetch `Validate`, S3A fake factories, and `S3ARemoteObjectReader` tests.

Risks: callbacks return null for real object retrieval/submission, so this mock is only valid for code paths using overridden `openForRead`; range validation uses requested `size` and object size assumptions.

Test signals: consumers verify retry behavior, byte content by offset, EOF/range behavior, and close paths without external IO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/prefetch/MockS3ARemoteObject.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/prefetch/S3APrefetchFakes.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/prefetch/S3APrefetchFakes.java

Purpose: factory and fake implementation suite for testing S3A prefetch streams and block managers without S3 or local disk dependency.

Important APIs/types/functions: static factories create `S3AFileStatus`, `S3ObjectAttributes`, `S3AReadOpContext`, S3A URIs, `ChangeTracker`, AWS response streams, object callbacks, fake in-memory/caching streams, and fake caches. Nested `FakeS3AInMemoryInputStream`, `FakeS3FilePerBlockCache`, `FakeS3ACachingBlockManager`, and `FakeS3ACachingInputStream` override remote-object acquisition, cache paths, cache reads/writes, and block-manager creation.

Control flow: fake streams create `MockS3ARemoteObject` on demand with randomized short delays to exercise concurrency. The fake block cache stores cache-file bytes in a `ConcurrentHashMap<Path, byte[]>`, allocates monotonically numbered paths, and injects configurable read/write delay. The fake caching block manager delegates reads to its reader and uses the fake cache.

State and persistence: all status/attribute/context data is synthetic; cached blocks live only in memory and are cleared on close. No real S3 store or filesystem writes occur.

Dependencies/integration: Hadoop prefetch `BlockManager`, `SingleFilePerBlockCache`, `LocalDirAllocator`, `ExecutorServiceFuturePool`, S3A read contexts/statistics/change detection, and AWS SDK response objects.

Risks: random sleeps can affect timing; null callback `submit()` is unsuitable outside tested paths; static configuration may miss production options.

Test signals: used by unit tests to validate read, seek, caching, prefetch, and failure handling deterministically enough without external services.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/prefetch/S3APrefetchFakes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/prefetch/TestS3ABlockManager.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/prefetch/TestS3ABlockManager.java

Purpose: unit tests for basic `S3ABlockManager` argument validation and block reads from a mock remote object.

Important APIs/types/functions: `TestS3ABlockManager` extends `AbstractHadoopTestBase`; constants define `FILE_SIZE=12` and `BLOCK_SIZE=3`. Tests instantiate `BlockData`, `MockS3ARemoteObject`, `S3ARemoteObjectReader`, and `S3ABlockManager`, then inspect returned `BufferData` and `ByteBuffer`.

Control flow: `testArgChecks` verifies valid construction and expected `IllegalArgumentException` messages for null reader, null block data, negative block number, and null release data. `testGet` loops over all blocks, gets each block, and checks every byte equals its absolute source offset.

State and persistence: all data is in-memory mock object content; block buffers are transient.

Dependencies/integration: Hadoop prefetch `BlockData`/`BufferData`, S3A remote reader, and LambdaTestUtils intercept.

Risks: only fixed-size even block boundaries are covered; no async caching or release semantics beyond null validation.

Test signals: exception message matching and byte-for-byte block content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/prefetch/TestS3ABlockManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/prefetch/TestS3ACachingBlockManager.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/prefetch/TestS3ACachingBlockManager.java

Purpose: unit tests for `S3ACachingBlockManager` construction validation, synchronous `get`, asynchronous prefetch, cache population, and injected read/cache failures.

Important APIs/types/functions: constants define small file, block, and buffer-pool sizes. Test state includes an `ExecutorServiceFuturePool`, empty S3A stream statistics, and `BlockData`. `BlockManagerForTesting` extends `S3ACachingBlockManager` and exposes one-shot `forceNextReadToFail` and `forceNextCachePutToFail`. Helpers build `BlockManagerParameters`, wait for async cache completion, sum errors, and assert initial state.

Control flow: constructor tests cover missing future pool, reader, block data, positive pool size, and statistics. Operational tests iterate through blocks, optionally force failures, verify content, release buffers, and assert pool availability. Prefetch/caching tests schedule async operations, cancel prefetches where appropriate, wait for expected cache counts, and compare read/caching error totals.

State and persistence: uses in-memory mock remote object and cache; asynchronous tasks mutate cache/error counters and buffer pool state.

Dependencies/integration: prefetch `BlockManagerParameters`, `LocalDirAllocator`, configured max cached blocks, S3A statistics, executor services, and Hadoop test intercept utilities.

Risks: wait loop can run long before failure; async ordering can make failures timing-sensitive; comments show previously disabled tests are now active.

Test signals: exception assertions, byte content checks, available buffer pool count, `numCached`, `numReadErrors`, and `numCachingErrors`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/prefetch/TestS3ACachingBlockManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/prefetch/TestS3ARemoteInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/prefetch/TestS3ARemoteInputStream.java

Purpose: shared unit tests for `S3AInMemoryInputStream` and `S3ACachingInputStream` remote-input-stream behavior.

Important APIs/types/functions: creates fake streams through `S3APrefetchFakes`, with an `ExecutorServiceFuturePool` and mock callbacks. Tests cover constructor null checks, zero-sized reads, sequential reads, seeks, random seeks, close semantics, `available`, `getPos`, and Hadoop `FSExceptionMessages`.

Control flow: each behavioral test runs once for in-memory stream and once for caching stream, adjusting expected buffer sizes. Read tests validate byte sequence, buffer-offset reads, EOF `-1` stability, and repeated reads after EOF. Seek tests move to block boundaries, read from every offset, allow seeking exactly to EOF, and reject negative/past-EOF seeks. Close tests verify operations fail after close and second close is harmless.

State and persistence: all content is deterministic in-memory mock data; stream position and internal buffers are the main mutable state.

Dependencies/integration: S3A prefetch stream implementations, fake contexts/statistics, Hadoop exception message contracts, and AssertJ/JUnit assertions.

Risks: no real S3 callbacks are exercised; executor services are not explicitly shut down in this file; cache behavior is tested through high-level stream semantics only.

Test signals: exact bytes returned, available counts, stream position, EOF values, and expected IO/EOF exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/prefetch/TestS3ARemoteInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/prefetch/TestS3ARemoteObject.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/prefetch/TestS3ARemoteObject.java

Purpose: unit test for `S3ARemoteObject` constructor argument validation.

Important APIs/types/functions: `TestS3ARemoteObject` creates an executor-backed future pool, mock client callbacks, fake `S3AReadOpContext`, `S3ObjectAttributes`, `S3AInputStreamStatistics`, and `ChangeTracker`. It uses `ExceptionAsserts.assertThrows` for validation failures.

Control flow: the test first constructs a valid `S3ARemoteObject`, then verifies null `context`, `s3Attributes`, `client`, `streamStatistics`, and `changeTracker` are rejected with the expected messages.

State and persistence: all state is synthetic and in-memory; no remote object is opened and no data is persisted.

Dependencies/integration: S3A prefetch fake factories, change tracking, statistics context, executor future pool, and object input callbacks.

Risks: coverage is limited to constructor preconditions; it does not validate object reads, close behavior, or callback use.

Test signals: expected exception class and message for each invalid constructor argument.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/prefetch/TestS3ARemoteObject.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/prefetch/TestS3ARemoteObjectReader.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/prefetch/TestS3ARemoteObjectReader.java

Purpose: unit tests for `S3ARemoteObjectReader` preconditions, offset/size bounds, partial buffer reads, and retry-visible read behavior.

Important APIs/types/functions: constants `FILE_SIZE=9` and `BUFFER_SIZE=2`; a `MockS3ARemoteObject` backs reads. `testArgChecks` validates null object/buffer, bad offsets, and nonpositive sizes. `testGetWithOffset` calls `testGetHelper` for every start offset with and without one-shot open failure.

Control flow: for each offset, the helper iterates buffer sizes from 0 through file size + 1 and read sizes from 1 through file size, clears the buffer, reads, computes expected bytes as the min of requested size, remaining object bytes, and buffer capacity, then verifies byte content starts at the requested offset.

State and persistence: only in-memory mock object content and `ByteBuffer` state are used; one-shot failure flag is reset by the mock after the first failed open.

Dependencies/integration: S3A remote object reader, mock remote object, Java NIO buffers, and LambdaTestUtils.

Risks: expected byte assertion compares to small offsets where `byteAtOffset` equals offset; larger offsets would need modulo handling.

Test signals: exact exception messages, bytes-read counts, and byte sequence validation across offset/buffer/read-size matrix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/prefetch/TestS3ARemoteObjectReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/s3guard/AbstractS3GuardToolTestBase.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/s3guard/AbstractS3GuardToolTestBase.java

Purpose: shared integration-test base for S3Guard tool CLI tests, including common command execution helpers and baseline bucket/tool behavior checks.

Important APIs/types/functions: extends `AbstractS3ATestBase`; tracks `toolsToClose`; exposes `toClose`, `expectResult`, `expectSuccess`, `run`, `runToFailure`, and `assertExitCode`. Tests exercise `S3GuardTool.BucketInfo`, `S3GuardTool.Uploads`, unsupported command list, marker policy options, missing bucket, missing arguments, and magic commit capability flag.

Control flow: setup delegates to superclass; teardown closes registered tools after superclass teardown. Tests instantiate command classes with current configuration, execute through helper methods, and assert command output or `ExitUtil.ExitException` status.

State and persistence: uses live S3A filesystem URI and command instances; no durable data beyond possible tool probes. A nonexistent bucket URI constant is used for failure tests.

Dependencies/integration: S3GuardTool command classes, marker tool option names, launcher exit codes, S3A unknown-store exception behavior, and `S3GuardToolTestHelper`.

Risks: S3Guard is deprecated/unsupported in newer flows, so tests encode compatibility behavior rather than active metadata-store behavior; missing bucket behavior depends on store probing.

Test signals: command exit codes, output containing S3A client info, unknown marker policy rejection, unsupported command rejection, and expected exceptions for missing buckets/args.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/s3guard/AbstractS3GuardToolTestBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/s3guard/ITestS3GuardTool.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/s3guard/ITestS3GuardTool.java

Purpose: integration tests for S3Guard CLI bucket-info and multipart-upload commands against real S3A stores and public/external bucket configuration.

Important APIs/types/functions: extends `AbstractS3GuardToolTestBase`; uses `BucketInfo`, `Uploads`, `MultipartTestUtils` helpers (`createPartUpload`, `countUploadsAt`, `clearAnyUploads`, `assertNoUploadsAt`), public dataset utilities, and command output parsing through `Csvout`-style fields.

Control flow: encryption tests run bucket-info against an external bucket, expecting success for no encryption and `E_BAD_STATE` for AES256. Store-info tests run normal and FIPS bucket probes. Upload tests clear stale uploads, create one MPU part, assert API and CLI listing counts, delete via CLI, and recheck. Age tests verify `-seconds` filtering before and after sleeping. Negative expect verifies `Uploads -expect` failure for a missing path.

State and persistence: creates and aborts real multipart uploads under method paths; cleans uploads on failure. External-bucket tests may remove bucket overrides when default public dataset is used.

Dependencies/integration: live multipart upload capability, S3A configuration, FIPS capability, S3GuardTool command output, and public dataset configuration.

Risks: relies on external bucket availability and multipart support; age checks are timing-sensitive; command-output parsing assumes four whitespace fields on `TOTAL` lines.

Test signals: command exit codes, upload counts via API and CLI, deletion counts, aged listing/deletion behavior, and FIPS skip behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/s3guard/ITestS3GuardTool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/s3guard/S3GuardToolTestHelper.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/s3guard/S3GuardToolTestHelper.java

Purpose: utility class for S3Guard CLI tests, centralizing command invocation, output capture, varargs conversion, and expected exit-code handling.

Important APIs/types/functions: static `exec(S3GuardTool,Object...)`, `expectExecResult`, low-level `exec(expectedResult,errorText,cmd,buf,args)`, `varargsToString`, `runS3GuardCommand`, and `runS3GuardCommandToFailure`.

Control flow: object arguments are converted to strings, commands are run with a `PrintStream` backed by `ByteArrayOutputStream`, and output is returned or logged on failure. Exceptions implementing `ExitCodeProvider` are treated as success when their code matches the expected result; otherwise they are rethrown. Return-code mismatches become JUnit `assertEquals` failures including command output.

State and persistence: captures command stdout in memory only; no persistent state.

Dependencies/integration: `S3GuardTool.run`, Hadoop `ExitCodeProvider`, `ExitUtil.ExitException`, LambdaTestUtils, and SLF4J logging.

Risks: if a command opens a cached filesystem, `S3GuardTool.run` may close it afterward as warned; helper assumes output fits memory; expected-result handling differs for returned codes versus thrown exit-code providers.

Test signals: helper itself has no tests here, but callers rely on captured output, exact exit-code matching, and logged buffers for diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/s3guard/S3GuardToolTestHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/s3guard/TestMetastoreChecking.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/s3guard/TestMetastoreChecking.java

Purpose: unit tests for deprecated S3Guard metastore configuration validation through `S3Guard.checkNoS3Guard`.

Important APIs/types/functions: `TestMetastoreChecking` extends `AbstractHadoopTestBase`; it builds a URI for `s3a://bucket/`, creates minimal `Configuration(false)` instances with `S3_METADATA_STORE_IMPL`, and checks constants `NULL_METADATA_STORE`, `S3GUARD_METASTORE_LOCAL`, and `S3GUARD_METASTORE_DYNAMO`.

Control flow: setup initializes the test filesystem URI. `chooseStore` optionally sets the configured metastore class. Tests assert no class returns false, null/local stores return true, DynamoDB store raises `PathIOException`, and unknown class raises `PathIOException` containing the class name.

State and persistence: no external store is contacted; only configuration keys and URI are used.

Dependencies/integration: S3Guard compatibility checks, Hadoop `PathIOException`, AssertJ assertions, and LambdaTestUtils.

Risks: because the code is marked deprecated, behavior is compatibility-focused; adding/removing accepted metastore names requires test updates.

Test signals: boolean outcomes for allowed/missing stores and exact exception behavior for forbidden/unknown stores.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/s3guard/TestMetastoreChecking.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/s3guard/TestS3GuardCLI.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/s3guard/TestS3GuardCLI.java

Purpose: small unit tests for the top-level `S3GuardTool.run` CLI dispatch and argument validation.

Important APIs/types/functions: `TestS3GuardCLI` extends JUnit `Assertions`; helper `run` uses `new Configuration(false)` and `S3GuardTool.run`; `runToFailure` intercepts `ExitUtil.ExitException`. Static imports cover `BucketInfo.NAME`, `INVALID_ARGUMENT`, `E_USAGE`, and other tool constants.

Control flow: tests call the CLI dispatcher with no bucket-info args, wrong filesystem scheme, no command, and unknown command, expecting the correct exit status for each case.

State and persistence: no filesystem state or persistent data is used.

Dependencies/integration: S3GuardTool command parser, Hadoop `ExitUtil`, LambdaTestUtils, and configuration defaults.

Risks: validates only dispatch/usage paths, not command execution; status-code changes in CLI policy will break exact assertions.

Test signals: intercepted exit exceptions with `INVALID_ARGUMENT` or `E_USAGE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/s3guard/TestS3GuardCLI.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/AbstractSTestS3AHugeFiles.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/AbstractSTestS3AHugeFiles.java

Purpose: abstract ordered scale-test suite for creating, validating, reading, vectored-reading, renaming, encryption-checking, deleting, and dumping statistics for huge S3A files.

Important APIs/types/functions: extends `S3AScaleTestBase`; subclasses provide `getBlockOutputBufferName()` and may override multipart/encryption/vector-buffer hooks. Configuration sets multipart partition size, socket buffers, vector active reads, user agent, fast upload buffer, and disables FS caching. Tests are alphanumerically ordered (`test_010` through `test_900`). Key helpers include `assumeHugeFileExists`, `listFile`, `renameFile`, `deleteHugeFile`, and getters for generated paths/sizes.

Control flow: setup derives scale directory, source/destination paths, upload block size, partition size, and file size. Create test deletes leftovers, writes deterministic blocks with `CountingProgressListener`, logs progress/statistics, closes stream, and validates multipart/single PUT counters and gauges. Later tests assert status/etag, perform positioned and vectored reads, sequentially read whole file, verify encryption hooks before/after rename, rename there and back, clean up, and dump FS IOStatistics.

State and persistence: deliberately keeps huge file across ordered tests by disabling per-test directory cleanup; final cleanup removes source/dest/test path. Uses live S3 object data and FS/stream statistics.

Dependencies/integration: S3A scale configuration, multipart upload, block output stream stats, open-file builder, vectored IO, byte-buffer pools, encryption hooks, and contract utilities.

Risks: order dependence means partial runs rely on `assumeHugeFileExists`; large object operations are time/cost sensitive; timeout and file-size divisibility are enforced; subclass hooks can change visibility/encryption expectations.

Test signals: upload progress without failures, exact stream/FS counters/gauges, file length and etag consistency, read validation, timing/bandwidth logs, successful rename, and cleanup completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/AbstractSTestS3AHugeFiles.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/CountingProgressListener.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/CountingProgressListener.java

Purpose: progress listener for S3A scale tests that counts upload lifecycle events, transferred bytes, and failures while logging bandwidth.

Important APIs/types/functions: implements Hadoop `Progressable` and S3A `ProgressListener`; stores an `EnumMap<ProgressListenerEvent, AtomicLong>`, total bytes, and a `NanoTimer`. Public methods include `progressChanged`, `get`, `getBytesTransferred`, `getUploadEvents`, `getStartedEvents`, `getFailures`, `verifyNoFailures`, and `assertEventCount`.

Control flow: `progress()` is a no-op for generic Hadoop progress. `progressChanged()` increments the event counter, logs started events, accumulates bytes on completed PUT/part events and computes effective bandwidth, logs failures, and ignores other events.

State and persistence: thread-safe atomic counters and byte totals live in memory for one test listener instance; no external persistence.

Dependencies/integration: S3A progress event enum, Hadoop contract `NanoTimer`, AssertJ assertions, and scale-test `_1MB` constant.

Risks: logger category points at `AbstractSTestS3AHugeFiles`; bandwidth division assumes nonzero elapsed seconds; only selected failure events contribute to `getFailures`.

Test signals: scale tests use no-failure assertions, upload-event counts, byte totals, and optional exact event count assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/CountingProgressListener.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ILoadTestS3ABulkDeleteThrottling.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ILoadTestS3ABulkDeleteThrottling.java

Purpose: parameterized load/scale test that stresses S3 bulk-delete throttling behavior by issuing many concurrent `removeKeys` calls with different bulk page sizes and AWS internal throttling settings.

Important APIs/types/functions: extends `S3AScaleTestBase` and is tagged `@LoadTest`/`@ScaleTest`; parameter tuples cover throttle on/off and default/max delete page sizes. It uses a 20-thread Hadoop executor, `ExecutorCompletionService`, `ObjectIdentifier` lists, `Csvout`, `NanoTimerStats`, and an `Outcome` record writer.

Control flow: configuration removes relevant overrides, sets `EXPERIMENTAL_AWS_INTERNAL_THROTTLING`, `BULK_DELETE_PAGE_SIZE`, user agent, and disables FS caching. Setup requires multi-delete, creates a local results directory, and verifies page size. Ordered tests reset static throttle state, run delete stress, then optionally sleep/recovery-delete if throttling was observed. `deleteFiles` builds one synthetic key list, submits request tasks, each task wraps `fs.removeKeys` in an audit span, records success/failure/timing, writes TSV output, and logs aggregate success/throttle stats and TPS.

State and persistence: no test objects need to exist for deletion keys; result CSV/TSV files are written under the local test dir. Static `testWasThrottled` coordinates recovery sleep, though this file records exceptions locally and does not visibly set the flag.

Dependencies/integration: S3A bulk delete, AWS throttling config, audit spans, local test directory utilities, Guava thread factory, and scale timing stats.

Risks: expensive and potentially disruptive to a bucket/shard; local result files accumulate; static throttle flag behavior may be incomplete; concurrency/timing can be environment-dependent.

Test signals: completion without unhandled failures, per-request outcome rows, aggregate throttle counts, and logged throughput.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ILoadTestS3ABulkDeleteThrottling.java -->
