# Research: subset-b-007588

Grouped research for S3A committer and FileContext test sources. Each section is keyed by the original source path for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/ITestCommitOperations.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/ITestCommitOperations.java

## Purpose
Integration tests for the low-level S3A magic commit binding and `CommitOperations` behavior. The suite verifies magic path detection, marker/pending metadata creation, single and bulk multipart commit, abort/revert handling, upload-from-local staging, committer factory selection, and the distinction between normal and magic output streams.

## Important APIs, Types, and Functions
The class extends `AbstractCommitITest` and binds the S3A committer factory to `COMMITTER_NAME_MAGIC` in `createConfiguration()`. `setup()` closes cached filesystems, requires multipart uploads, verifies a magic-capable S3A filesystem, and resets a `ProgressCounter`. Helper methods include `newCommitOperations()`, `makeMagic(Path)`, `createCommitAndVerify()`, `commit()`, `commitOrFail()`, and `validatePendingCommitData()`. The test directly uses `MagicCommitIntegration`, `MagicCommitTracker`, `CommitOperations`, `CommitContext`, `SinglePendingCommit`, `UploadEtag`, `FSDataOutputStreamBuilder`, and `PathOutputCommitterFactory`.

## Control Flow and Behavior
Magic path tests build paths under `__magic/<job-id>/...`, split and reconstruct path elements through `MagicCommitPaths`, and assert that `MagicCommitIntegration.createTracker()` returns `MagicCommitTracker` only for real magic destinations. Commit tests write empty and small files to magic paths, verify zero-byte marker headers plus `.pending` JSON, load `SinglePendingCommit`, and complete it through `CommitContext.commitOrFail()`. Abort tests call `abortAllSinglePendingCommits()` or `abortPendingUploadsUnderPath()` and verify pending metadata and destination files are absent. Upload tests use `uploadFileToPendingCommit()` against local temp files, check progress callbacks, then complete the pending MPU. Bulk commit tests reuse one `CommitContext` for multiple pending commits and verify parent/subdirectory materialization.

## State, Persistence, and Dependencies
State is persisted in S3 as marker files and `.pending` JSON sidecars containing timestamps, destination keys, upload IDs, and `UploadEtag` part lists. Local temp files are used as upload sources. The suite depends on real S3A multipart upload support, commit constants such as `MAGIC_PATH_PREFIX`, `BASE`, `PENDING_SUFFIX`, S3A stream capability `STREAM_CAPABILITY_MAGIC_OUTPUT`, and test helpers from `ContractTestUtils`, `S3ATestUtils`, and `CommitterTestHelper`.

## Integration Points, Risks, and Test Signals
This is a high-signal integration suite for regressions in magic commit path parsing, pending metadata serialization, marker header handling, factory binding, upload abort cleanup, and local-to-S3 staged commit. Risks include dependence on S3 semantics, storage-class differences such as S3 Express directory visibility, stale pending uploads after interrupted runs, and behavior changes in multipart commit retry semantics. Passing tests demonstrate that magic writes remain invisible until committed and that normal S3A streams are not accidentally treated as magic output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/ITestCommitOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/ITestS3ACommitterFactory.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/ITestS3ACommitterFactory.java

## Purpose
Parameterized integration tests for `S3ACommitterFactory` selection rules. It verifies that committer names configured either in the filesystem configuration or in the task/job configuration produce the expected output committer class, and that invalid names fail with a path commit exception.

## Important APIs, Types, and Functions
The class extends `AbstractCommitITest` and is a JUnit 5 `@ParameterizedClass` over `BINDINGS`. It covers `FileOutputCommitter`, `PartitionedStagingCommitter`, `StagingCommitter`, `MagicS3GuardCommitter`, and `DirectoryStagingCommitter`. `maybeSetCommitterName()` mutates `FS_S3A_COMMITTER_NAME`, `createConfiguration()` clears bucket overrides, and `setup()` constructs a `JobConf`, `TaskAttemptID`, `TaskAttemptContextImpl`, output path, and `S3ACommitterFactory`.

## Control Flow and Behavior
Each parameter pair sets an optional filesystem-level committer name and an optional task-level committer name. `testBinding()` calls `assertFactoryCreatesExpectedCommitter()`, which either compares the exact class returned by `factory.createOutputCommitter(outDir, tContext)` or intercepts `PathCommitException` for invalid configuration. The setup explicitly closes cached filesystems for the current UGI so every parameter observes its own FS configuration.

## State, Persistence, and Dependencies
The test uses only configuration state and task attempt metadata; it does not rely on committed output. It depends on multipart upload availability, S3A committer constants, MR job/task config keys, and Hadoop filesystem caching behavior.

## Integration Points, Risks, and Test Signals
The main integration point is the precedence between filesystem and job-level committer options. A failure here usually means a regression in committer discovery, configuration override handling, or filesystem caching. The test is sensitive to default binding expectations: no committer name should produce `FileOutputCommitter`, while invalid names must be rejected rather than silently falling back.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/ITestS3ACommitterFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/ITestUploadRecovery.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/ITestUploadRecovery.java

## Purpose
Integration tests for recovery from injected S3 SDK failures during simple PUT, magic multipart writes, and `CommitOperations` upload/complete flows. The class is parameterized over S3A fast-upload buffer implementations.

## Important APIs, Types, and Functions
The class extends `AbstractS3ACostTest` and uses `SdkFaultInjector` as an SDK execution interceptor. Parameters cover `FAST_UPLOAD_BUFFER_ARRAY`, `FAST_UPLOAD_BUFFER_DISK`, and `FAST_UPLOAD_BYTEBUFFER`, with the full commit test run only once. Key methods are `createConfiguration()`, `setup()`, `teardown()`, `testPutRecovery()`, `testMagicWriteRecovery()`, and `testCommitOperations()`.

## Control Flow and Behavior
Configuration removes bucket overrides, selects the fast-upload buffer, enables create performance mode, sets up teardown upload purging, and installs the fault injector. `testPutRecovery()` injects failures for PUT responses and expects a normal stream close to recover. `testMagicWriteRecovery()` writes to a magic path and injects upload-part failures; with client-side encryption enabled, retrying MPU is expected to throw, otherwise the write must recover. `testCommitOperations()` creates a local staged file, injects part upload failures, uploads it to a pending commit, then injects complete-MPU failures and either expects a `FileNotFoundException` if complete consumes the upload ID or a successful retry otherwise.

## State, Persistence, and Dependencies
State includes fault-injector counters/evaluators, local temp files, pending commit metadata, multipart upload IDs, and S3A filesystem configuration. The test depends on SDK interceptor behavior, S3 multipart semantics, `MULTIPART_COMMIT_CONSUMES_UPLOAD_ID`, and whether client-side encryption is active.

## Integration Points, Risks, and Test Signals
This suite is a targeted signal for retry safety around multipart uploads. It exercises S3A stream upload, magic pending writes, and committer upload/complete paths under transient failures. Risks include provider-specific behavior after failed complete-MPU requests, CSE incompatibility with MPU retry, and accidental persistence of fault injection into cleanup; teardown resets the injector to reduce that risk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/ITestUploadRecovery.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/LoggingTextOutputFormat.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/LoggingTextOutputFormat.java

## Purpose
Test output format used by committer integration tests to expose and log the actual work-file destination while behaving like Hadoop `TextOutputFormat`.

## Important APIs, Types, and Functions
`LoggingTextOutputFormat<K,V>` extends `TextOutputFormat<K,V>`. `getRecordWriter()` reproduces the standard text output writer path, including compression support, but returns `LoggingLineRecordWriter`. The nested writer extends `LineRecordWriter<K,V>`, tracks `dest` and `lines`, overrides `write()`, exposes `getDest()` and `getLines()`, and logs close details. Static `bind(Configuration)` sets `MRJobConfig.OUTPUT_FORMAT_CLASS_ATTR`.

## Control Flow and Behavior
On writer creation the format resolves compression options, computes `getDefaultWorkFile()`, opens the target filesystem output stream, and wraps it in an optional codec stream. Each `write()` delegates to `LineRecordWriter` then increments a line counter. `close()` logs the target and count before closing the stream.

## State, Persistence, and Dependencies
Persistent state is the generated task output file, possibly compressed. In-memory state is limited to the destination path and line count. Dependencies include MR output-format APIs, `CompressionCodec`/`GzipCodec`, `ReflectionUtils`, `FileSystem`, and standard Hadoop text output constants such as `SEPARATOR`.

## Integration Points, Risks, and Test Signals
This helper is used by MR committer integration tests to validate task output paths and success marker file lists. It intentionally mirrors standard `TextOutputFormat`; risks are drift from upstream output behavior, compression edge cases, and `close()` bypassing superclass behavior by directly closing `out`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/LoggingTextOutputFormat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/MiniDFSClusterService.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/MiniDFSClusterService.java

## Purpose
Small service wrapper around a one-node `MiniDFSCluster` for staging committer tests that need an HDFS-like cluster filesystem for persisted pending-set files.

## Important APIs, Types, and Functions
`MiniDFSClusterService` extends `AbstractService`. `serviceStart()` builds a formatted `MiniDFSCluster`, records `clusterFS`, and creates a local filesystem from the cluster configuration. `serviceStop()` clears filesystem references and shuts down the cluster. Accessors expose `getCluster()`, `getClusterFS()`, and `getLocalFS()`.

## Control Flow and Behavior
The service follows Hadoop service lifecycle: init delegates to the superclass, start creates cluster resources, and stop releases them. It always starts one datanode and formats the cluster.

## State, Persistence, and Dependencies
State is held in `cluster`, `clusterFS`, and `localFS`. The cluster writes temporary HDFS metadata/data under the test environment and is not intended for durable persistence. Dependencies are `MiniDFSCluster`, `FileSystem`, `LocalFileSystem`, and Hadoop service lifecycle APIs.

## Integration Points, Risks, and Test Signals
Used by `StagingTestBase.MiniDFSTest` and staging committer tests to verify commit metadata written to an HDFS staging area. Risks include leaked cluster resources if shutdown is skipped and test fragility around local port/filesystem availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/MiniDFSClusterService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/TestMagicCommitPaths.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/TestMagicCommitPaths.java

## Purpose
Unit tests for pure path operations in `MagicCommitPaths`, especially splitting paths, extracting magic-path parents/children, resolving final destinations, and handling the `__base` marker.

## Important APIs, Types, and Functions
The test targets `splitPathToElements(Path)`, `magicPathParents(List<String>)`, `magicPathChildren(List<String>)`, `lastElement(List<String>)`, and `finalDestination(List<String>)`. It uses constants `MAGIC_PATH_PREFIX` and `BASE`, JUnit assertions, and `LambdaTestUtils.intercept()`.

## Control Flow and Behavior
The tests cover empty and root paths, trailing slashes, magic at root, magic nested under parents, paths with and without children, and deep magic paths. Final destination tests verify that elements before the magic marker are retained, elements between magic and `BASE` are stripped appropriately, and invalid magic/base forms throw `IllegalArgumentException`.

## State, Persistence, and Dependencies
There is no external state or persistence. The test depends only on Hadoop `Path` normalization and static magic path utilities.

## Integration Points, Risks, and Test Signals
These path rules underpin magic committer correctness; a regression can route committed data to the wrong destination or classify metadata sidecars as delayed writes. The test is a fast signal for edge cases that are harder to isolate in S3 integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/TestMagicCommitPaths.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/TestMagicCommitTrackerUtils.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/TestMagicCommitTrackerUtils.java

## Purpose
Unit test for extracting the MapReduce task attempt ID from a generated magic task attempt path.

## Important APIs, Types, and Functions
The class creates a random job ID via `AbstractCommitITest.randomJobId()`, builds a `TaskAttemptID`, wraps it in `TaskAttemptContextImpl`, calls `CommitUtilsWithMR.getBaseMagicTaskAttemptPath()`, and verifies `MagicCommitTrackerUtils.extractTaskAttemptIdFromPath()`.

## Control Flow and Behavior
`setup()` creates stable per-test `jobId`, textual attempt ID, and parsed `TaskAttemptID`. The test constructs a base magic attempt path for a dummy S3 destination and asserts that the utility recovers the original attempt ID string.

## State, Persistence, and Dependencies
There is no filesystem mutation. Dependencies include Hadoop MR task attempt classes, `CommitUtilsWithMR`, and magic tracker path conventions.

## Integration Points, Risks, and Test Signals
The extraction utility is important when magic commit tracking needs to associate pending uploads with task attempts. The test guards against path layout changes that would break that association.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/TestMagicCommitTrackerUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/files/TestUploadEtag.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/files/TestUploadEtag.java

## Purpose
Unit tests for conversion between AWS SDK `CompletedPart` and Hadoop `UploadEtag`, including optional per-part checksum metadata.

## Important APIs, Types, and Functions
The suite targets `UploadEtag.fromCompletedPart(CompletedPart)` and `UploadEtag.toCompletedPart(UploadEtag, int)`. It covers checksum algorithms `CRC32`, `CRC32C`, `SHA1`, `SHA256`, and the no-checksum case.

## Control Flow and Behavior
Each `fromCompletedPart` test builds a SDK `CompletedPart` with an ETag and exactly one checksum field, then verifies the resulting `UploadEtag` has the right ETag, algorithm string, and checksum value. Each `toCompletedPart` test creates an `UploadEtag` and asserts the corresponding SDK checksum getter is populated or null.

## State, Persistence, and Dependencies
There is no persistence. Dependencies are AWS SDK v2 S3 model classes and AssertJ.

## Integration Points, Risks, and Test Signals
The conversion is used when serializing pending multipart commit data and later completing an MPU. This test protects checksum preservation across pending commit files; a regression could cause complete-MPU requests to omit required checksum metadata for checksum-enabled uploads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/files/TestUploadEtag.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/integration/ITestS3ACommitterMRJob.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/integration/ITestS3ACommitterMRJob.java

## Purpose
YARN-backed MapReduce integration test that runs a real MR job against S3A using the directory, partitioned, and magic committers. It validates end-to-end committer binding, task output generation, success marker content, output visibility, and committer-specific cleanup.

## Important APIs, Types, and Functions
The class extends `AbstractYarnClusterITest` and is parameterized by `CommitterTestBinding` implementations: `DirectoryCommitterTestBinding`, `PartitionCommitterTestBinding`, and `MagicCommitterTestBinding`. It uses `LoggingTextOutputFormat`, `TextInputFormat`, `FileOutputFormat`, `Job`, `JobConf`, `SuccessData`, and MR/YARN cluster helpers. `MapClass` emits deterministic records per input file. Binding hooks include `validate()`, `test_100()`, `applyCustomConfigOptions()`, `validateResult()`, and `test_500()`.

## Control Flow and Behavior
`setup()` requires multipart uploads and binds the current cluster/filesystem to the selected committer binding. `test_000()` validates the binding, `test_100()` runs binding-specific preflight checks, `test_200_execute()` creates local text inputs, configures a no-reducer MR job, assigns a committer UUID, submits to the mini YARN cluster, waits for success, validates the `_SUCCESS` JSON, compares visible output files with expected `part-m-*` names, and checks that classic `_temporary` output is absent. `test_500()` delegates postflight checks. Magic validation logs and inspects any leftover magic directory rather than failing on it due to known speculative/partitioned task behavior.

## State, Persistence, and Dependencies
State spans local temp input files, YARN/MR job metadata, S3A output directories, success marker JSON, committer UUIDs, and optional local mock-results serialization. Directory binding validates private HDFS staging temp path construction under the current user. Dependencies include real S3A multipart capability, a mini YARN cluster, AWS region propagation to task environments, and Hadoop MR classpath/logging behavior.

## Integration Points, Risks, and Test Signals
This is one of the strongest end-to-end signals for S3A committer correctness in distributed execution. Risks include YARN process isolation, missing AWS region in child containers, filesystem cache leakage, log4j/classpath fragility, and S3 eventual/listing behavior. Passing tests show that each committer can run a real MR job, publish only final output, and write success metadata listing committed object keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/integration/ITestS3ACommitterMRJob.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/magic/ITestMagicCommitProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/magic/ITestMagicCommitProtocol.java

## Purpose
Integration tests for the low-level magic committer protocol, reusing the abstract committer protocol suite while specializing path, marker, cleanup, and fault-injection behavior for `MagicS3GuardCommitter`.

## Important APIs, Types, and Functions
The class extends `AbstractITCommitProtocol`, is parameterized over `FS_S3A_COMMITTER_MAGIC_TRACK_COMMITS_IN_MEMORY_ENABLED`, and returns `COMMITTER_NAME_MAGIC`. It creates `MagicS3GuardCommitter` instances, verifies magic FS support, overrides validation hooks, and defines `CommitterWithFailedThenSucceed` backed by `CommitterFaultInjectionImpl`.

## Control Flow and Behavior
Configuration removes bucket overrides and sets in-memory commit tracking on or off. During setup it verifies the S3A filesystem supports magic commits. Task write validation asserts paths contain `__magic/<uuid>/` and are not visible during write. After write, the test verifies the `.pending` sidecar, lists the marker as zero length, and checks marker xattrs. Working directory validation requires an `s3a` scheme and a magic UUID path. `testCommittersPathsHaveUUID()` checks task and temporary paths include or exclude magic/base/temp components appropriately. `testCommitterCleanup()` commits with cleanup enabled and disabled and asserts whether the job attempt path remains.

## State, Persistence, and Dependencies
State is persisted in S3 magic marker files, `.pending` metadata, and optional in-memory tracking lists. Dependencies include `AbstractITCommitProtocol`, `MagicS3GuardCommitter`, `CommitUtilsWithMR.getMagicJobPath()`, list/filter utilities, and fault-injection wrappers around committer lifecycle calls.

## Integration Points, Risks, and Test Signals
This file validates the magic committer contract against the shared MR output protocol tests. It is sensitive to UUID scoping, marker visibility, pending metadata discovery, cleanup settings, and retries after commit failure. Passing both in-memory tracking modes is important because production deployments may choose either metadata discovery strategy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/magic/ITestMagicCommitProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/magic/ITestMagicCommitProtocolFailure.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/magic/ITestMagicCommitProtocolFailure.java

## Purpose
Negative integration test proving the magic committer cannot be constructed when multipart uploads are disabled.

## Important APIs, Types, and Functions
The class extends `AbstractS3ATestBase`. `createConfiguration()` removes bucket overrides, disables `MULTIPART_UPLOADS_ENABLED`, binds the S3A committer factory, and selects `COMMITTER_NAME_MAGIC`. `testCreateCommitter()` constructs a `TaskAttemptContextImpl` and intercepts `PathCommitException` from `new MagicS3GuardCommitter(...)`.

## Control Flow and Behavior
The filesystem is deliberately configured without MPU support before the committer is created. The single test asserts construction fails immediately rather than allowing a committer that would fail later at upload or commit time.

## State, Persistence, and Dependencies
There is no output persistence. Dependencies are S3A configuration, bucket override removal, MR task context, and magic committer constructor validation.

## Integration Points, Risks, and Test Signals
The test protects a critical precondition: magic commits require multipart uploads. A failure indicates that validation has weakened or configuration overrides are not being removed correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/magic/ITestMagicCommitProtocolFailure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/magic/ITestS3AHugeMagicCommits.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/magic/ITestS3AHugeMagicCommits.java

## Purpose
Scale test for writing a huge file through the magic committer and then explicitly committing the generated pending multipart upload. It validates magic pending metadata for multi-part files larger than one part.

## Important APIs, Types, and Functions
The class extends `AbstractSTestS3AHugeFiles`, is tagged `@ScaleTest`, and uses disk fast-upload buffering. It overrides `getPathOfFileToCreate()` to return the magic output file, requires multipart uploads, and overrides read/rename tests to skip them. Core test methods are `test_000_CleanupPendingUploads()`, `test_030_postCreationAssertions()`, and `test_800_DeleteHugeFiles()`.

## Control Flow and Behavior
`setup()` verifies magic commit support and constructs `finalDirectory`, `magicDir`, `jobDir`, `magicOutputFile`, `pendingDataFile`, and the final hugefile destination. Cleanup aborts pre-existing MPUs under the final directory. After file creation, `test_030_postCreationAssertions()` verifies the final file is absent, the pending file exists, the marker file is zero bytes with `XA_MAGIC_MARKER` encoding the real length, lists pending uploads, loads pending commits from the job directory, commits each through `CommitContext.commitOrFail()`, verifies no pending uploads remain, and then delegates normal huge-file assertions to the superclass.

## State, Persistence, and Dependencies
Persistent state includes large S3 multipart uploads, magic marker xattrs, `.pending` metadata, and final committed object data. It depends on S3A huge-file scale configuration, `CommitOperations`, `PendingSet`, `SinglePendingCommit`, `listMultipartUploads()`, audit spans, and S3A header extraction.

## Integration Points, Risks, and Test Signals
This test is expensive but high value for multi-part magic commits. It catches bugs in marker length encoding, pending set loading, commit threading, and MPU cleanup. Risks include stale uploads after interrupted scale runs, long execution time, and provider-specific listing/abort behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/magic/ITestS3AHugeMagicCommits.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/MockedStagingCommitter.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/MockedStagingCommitter.java

## Purpose
Test-only `StagingCommitter` subclass that allows mocked S3A filesystems and clients to be used without strict destination-FS checks, and exposes recorded client outcomes to tests.

## Important APIs, Types, and Functions
The class overrides `getDestinationFS()`, `commitJob()`, and `maybeCreateSuccessMarker()`. It exposes `getResults()` and `getErrors()` by casting `getDestS3AFS()` to `MockS3AFileSystem` and reading the stored `ClientResults`/`ClientErrors` pair.

## Control Flow and Behavior
`commitJob()` delegates to the real staging committer, then optionally serializes `getResults()` to a local path configured as `mock-results-file`. Success marker creation is skipped because that path is not mocked for these unit tests.

## State, Persistence, and Dependencies
Persistent state may include a local serialized results object and the real staged pending files produced by the superclass. Dependencies include `MockS3AFileSystem`, `StagingTestBase` result/error containers, `SuccessData`, and `IOStatisticsSnapshot`.

## Integration Points, Risks, and Test Signals
This helper lets committer unit tests exercise real staging committer logic against mock S3 operations. Risks are that it deliberately skips success marker behavior and suppresses exceptions while serializing results, so tests using it should not infer success-marker correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/MockedStagingCommitter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/PartitionedCommitterForTesting.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/PartitionedCommitterForTesting.java

## Purpose
Small test subclass of `PartitionedStagingCommitter` that relaxes destination filesystem checking and records the output path after initialization.

## Important APIs, Types, and Functions
It overrides `initOutput(Path)` to call `super.initOutput(out)` and then `setOutputPath(out)`. It also overrides `getDestinationFS(Path, Configuration)` to return `out.getFileSystem(config)` directly.

## Control Flow and Behavior
Construction follows the normal partitioned committer path. During initialization, output metadata is initialized by the superclass, then forced into the committer for tests. Destination filesystem lookup bypasses S3A type enforcement so `MockS3AFileSystem` wrappers can be used.

## State, Persistence, and Dependencies
The subclass does not add persistent state. It depends on `PartitionedStagingCommitter`, `TaskAttemptContext`, `FileSystem`, and test mock filesystem binding.

## Integration Points, Risks, and Test Signals
Used by partitioned job commit tests to exercise partition conflict and replace behavior against mocks. The relaxation of destination FS checks is test-only and should not be interpreted as production behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/PartitionedCommitterForTesting.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/StagingTestBase.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/StagingTestBase.java

## Purpose
Shared fixture and mock infrastructure for staging committer unit tests. It binds mock S3A filesystems, creates mock AWS SDK clients, tracks MPU operations, injects failures, manages a MiniDFS cluster, and provides base classes for job and task committer tests.

## Important APIs, Types, and Functions
Static fixture methods include `createAndBindMockFSInstance()`, `lookupWrapperFS()`, path existence/delete stubbing helpers, `assertConflictResolution()`, `createTestOutputFiles()`, and `newMockS3Client()`. Nested classes include `MiniDFSTest`, `JobCommitterTest<C>`, `TaskCommitterTest<C>`, `ClientResults`, and `ClientErrors`. The mock client handles `createMultipartUpload`, `uploadPart`, `completeMultipartUpload`, `abortMultipartUpload`, `deleteObject`, and `listMultipartUploads`.

## Control Flow and Behavior
`createAndBindMockFSInstance()` creates a mocked `S3AFileSystem` with mocked internals/store/client, wraps it in `MockS3AFileSystem`, initializes it at `s3a://bucket/`, stores qualified output paths, and registers it with `FileSystemTestHelper`. `JobCommitterTest.setupJob()` creates a job config with a committer UUID, disables success marker creation, creates `ClientResults`/`ClientErrors`, binds a mock client, and constructs a `JobContext`. `TaskCommitterTest.setupTask()` creates the job committer, runs `setupJob()`, creates a task context, and configures local buffer and staging paths. `newMockS3Client()` records requests and can throw configured `AwsServiceException`s at specific operation counts, optionally recovering after the first failure.

## State, Persistence, and Dependencies
State is held in static output path/URI/root fields, MiniDFS cluster service state, per-test mock result/error containers, mock S3 active upload maps, pending local/HDFS files, and configured job/task contexts. Dependencies include Mockito, AWS SDK v2 S3 models/client, `MockS3AFileSystem`, `MiniDFSClusterService`, MR contexts, and Hadoop filesystem test helpers.

## Integration Points, Risks, and Test Signals
This base class is the backbone of staged committer unit coverage. It provides deterministic signals for MPU request counts, abort/commit behavior, destination key generation, and cleanup without real S3. Risks include mock drift from actual S3/S3A behavior, shared static paths across tests, and concurrency assumptions in synchronized mock-client handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/StagingTestBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/TestDirectoryCommitterScale.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/TestDirectoryCommitterScale.java

## Purpose
Mock scale test for `DirectoryStagingCommitter` job commit/abort behavior with many pending uploads. It stresses loading and committing thousands of pending entries without using real S3.

## Important APIs, Types, and Functions
The class extends `StagingTestBase.JobCommitterTest<DirectoryStagingCommitter>`. Constants define 500 tasks, 10 files per task, 5000 total commits, 1000 blocks per task, and 100 committer threads. It defines a `DirectoryCommitterForTesting` subclass that uses a prebuilt local staging path as the job attempt path and records `ActiveCommit`.

## Control Flow and Behavior
`setupStaging()` creates a local staging directory. `test_010_createTaskFiles()` calls `createTasks()`, which builds template `SinglePendingCommit` objects with many `CompletedPart` entries, writes `.pendingset` files per task, and records active upload IDs. `test_020_loadFilesToAttempt()` verifies `listPendingUploadsToCommit()` finds all task pending-set files. `test_030_commitFiles()` seeds active uploads into mock results, commits the job in append mode, and verifies 5000 complete-MPU requests plus success marker limits. `test_040_abortFiles()` exercises abort handling over the same scale.

## State, Persistence, and Dependencies
State includes local `.pendingset` files, `activeUploads` map, mock S3 results, and recorded `ActiveCommit`. Dependencies include `PendingSet`, `SinglePendingCommit`, `CompletedPart`, `CommitOperations`, `CommitContext`, `JsonSerialization`, and local filesystem staging.

## Integration Points, Risks, and Test Signals
This is a stress signal for staging job commit listing, active commit aggregation, success marker truncation, and high-thread commit execution. Risks are local disk use, static `activeUploads` lifecycle, and mock behavior not fully matching S3 latency/error patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/TestDirectoryCommitterScale.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/TestPaths.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/TestPaths.java

## Purpose
Unit tests for staging committer path utilities in `org.apache.hadoop.fs.s3a.commit.staging.Paths`.

## Important APIs, Types, and Functions
The test covers `addUUID(String, String)`, `getRelativePath(Path, Path)`, `getPartition(String)`, and `getMultipartUploadCommitsDirectory(FileSystem, Configuration, String)`.

## Control Flow and Behavior
UUID tests verify suffix insertion before file extensions, idempotence when a filename or parent already contains the UUID, and exceptions for directory-like paths, empty paths, and empty UUIDs. Relative path tests cover one-level, two-level, self, and parent cases. Partition extraction returns parent partition directories from file paths. MPU commit directory tests verify the local filesystem staging path ends with `<uuid>/__staging_uploads`.

## State, Persistence, and Dependencies
The test creates no durable state beyond local filesystem path resolution. Dependencies include `LocalFileSystem`, `Configuration`, Hadoop `Path`, and staging constants.

## Integration Points, Risks, and Test Signals
Path utility correctness affects destination key generation, partition replacement, and staging metadata layout. These tests catch naming regressions that could cause overwrites, wrong partition cleanup, or missing pending-set files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/TestPaths.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/TestStagingCommitter.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/TestStagingCommitter.java

## Purpose
Main mocked unit suite for `StagingCommitter`, parameterized by commit thread count and unique filename policy. It validates UUID selection, local attempt path construction, task commit upload and pending-set generation, error cleanup, job commit, and job abort.

## Important APIs, Types, and Functions
The class extends `StagingTestBase.MiniDFSTest` and uses `MockedStagingCommitter`, MiniDFS for committed task metadata, and the mock S3 client. Key tests cover `AbstractS3ACommitter.buildJobUUID()`, `Paths.getLocalTaskAttemptTempDir()`, `getCommittedTaskPath()`, `commitTask()`, `abortTask()`, `commitJob()`, and `abortJob()`. Helpers include `runTasks()`, `commitTask()`, `assertValidUpload()`, and `writeOutputFile()`.

## Control Flow and Behavior
Setup configures committer threads, unique filenames, UUID, retry policy, mock S3 client, job/task contexts, local buffer dirs, and a MiniDFS-backed staging area. Task commit tests create files under the task attempt path, run `commitTask()`, verify MPU initiation and part tags, and load a `PendingSet` from the committed task path. Failure tests inject init/upload/abort failures and assert attempted uploads are aborted and local attempt paths are removed. Job commit runs multiple synthetic tasks, completes all uploads, and deletes the job attempt path. Job commit failure verifies already committed objects are deleted and remaining uploads aborted. Job abort verifies all uploads are aborted with no commits/deletes.

## State, Persistence, and Dependencies
State includes temporary local output files, HDFS pending-set files, mock S3 upload/part/commit/abort/delete lists, committer UUID config, and job/task contexts. Dependencies include MiniDFS, AWS SDK S3 request models, `PendingSet`, `PersistentCommitData`, `SinglePendingCommit`, MR IDs, and staging path constants.

## Integration Points, Risks, and Test Signals
This suite is the primary signal for staging committer task/job lifecycle correctness without real S3. It tests cleanup on partial failure, unique filename destination keys, pending metadata validity, and rollback after commit failure. Risks include mock-client differences from real S3 and parameter interactions with static MiniDFS setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/TestStagingCommitter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/TestStagingDirectoryOutputCommitter.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/TestStagingDirectoryOutputCommitter.java

## Purpose
Mocking tests for `DirectoryStagingCommitter` conflict-mode handling and default configuration.

## Important APIs, Types, and Functions
The class extends `StagingTestBase.JobCommitterTest<DirectoryStagingCommitter>`. It creates `DirectoryStagingCommitter`, configures `FS_S3A_COMMITTER_STAGING_CONFLICT_MODE`, directly invokes `preCommitJob()` through a `CommitContext`, and uses mock FS verification helpers.

## Control Flow and Behavior
`testBadConflictMode()` rejects unsupported `merge`. Default and append modes set up and commit when the destination is a directory. Fail mode verifies `setupJob()` rejects an existing destination but `preCommitJob()` can be called directly for regression coverage. Replace mode deletes the destination during commit. Append/replace fail if the destination is a file. `testValidateDefaultConflictMode()` reads the default from a full configuration and asserts it is append.

## State, Persistence, and Dependencies
State is mock filesystem existence/delete interactions and job configuration. Dependencies include `PathExistsException`, `CommitOperations`, `CommitContext`, IO statistics context, staging conflict constants, and Mockito resets/verifications.

## Integration Points, Risks, and Test Signals
The suite protects directory committer semantics around overwrite/append/fail behavior. It is sensitive to config defaults and HADOOP-15469-style distinctions between setup-time and commit-time checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/TestStagingDirectoryOutputCommitter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/TestStagingPartitionedFileListing.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/TestStagingPartitionedFileListing.java

## Purpose
Tests partitioned staging committer task output discovery and partition inference from task output trees.

## Important APIs, Types, and Functions
The class extends `TaskCommitterTest<PartitionedStagingCommitter>` and uses `PartitionedStagingCommitter.getTaskOutput()`, `Paths.getRelativePath()`, `Paths.getPartitions()`, and `S3AUtils.mapLocatedFiles()`.

## Control Flow and Behavior
Task output listing tests create nested partition-like files under the task attempt path and compare discovered relative paths with expected paths. Hidden files such as `_metadata` and dot-prefixed partial files are created but must be filtered out. Partition resolution tests create a local tree, assert empty file lists yield no partitions, verify nested files produce partition strings, and verify root-level files map to `TABLE_ROOT`.

## State, Persistence, and Dependencies
State is local task-attempt output under the test temp directory, cleaned in `@AfterEach`. Dependencies include local/attempt filesystems, partition path utilities, hidden-file filtering, and task committer setup from `StagingTestBase`.

## Integration Points, Risks, and Test Signals
Correct listing and partition extraction drive partitioned commit conflict checks and replace/delete behavior. Risks include accidental inclusion of metadata/temporary files and incorrect table-root handling for non-partitioned outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/TestStagingPartitionedFileListing.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/TestStagingPartitionedJobCommit.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/TestStagingPartitionedJobCommit.java

## Purpose
Mocking tests for `PartitionedStagingCommitter` job commit behavior, especially conflict modes and partition replacement.

## Important APIs, Types, and Functions
The class extends `JobCommitterTest<PartitionedStagingCommitter>` and uses an inner `PartitionedStagingCommitterForTesting` subclass. The subclass overrides `listPendingUploadsToCommit()` to synthesize `.pendingset` files with partitioned destination keys and overrides `abortJobInternal()` to record aborts.

## Control Flow and Behavior
The synthetic active commit creates pending uploads for two dates and two hours, registers upload IDs in mock S3 results, and returns file statuses for pending-set files. Default/fail/append tests verify job commit succeeds regardless of existing parent/peer/leaf directories because fail is enforced at task level. Replace mode always deletes the four partitions represented in the pending set, plus any existing matching partition directories. Delete failure in replace mode throws `PathCommitException`, aborts the job, and still verifies cleanup interactions.

## State, Persistence, and Dependencies
State includes local temp `.pendingset` files, mock active uploads, mock S3 existence/delete interactions, and the subclass `aborted` flag. Dependencies include `PendingSet`, `SinglePendingCommit`, `UploadEtag`, `CommitContext`, partition conflict constants, and Mockito stubbing.

## Integration Points, Risks, and Test Signals
This suite protects the partitioned committer's replace semantics: only partitions touched by the job should be deleted before completing uploads. Risks include over-deleting parent paths, missing partition deletions, and not aborting pending uploads after delete failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/TestStagingPartitionedJobCommit.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/TestStagingPartitionedTaskCommit.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/TestStagingPartitionedTaskCommit.java

## Purpose
Mocking tests for partitioned staging task commit conflict handling and destination key generation.

## Important APIs, Types, and Functions
The class extends `TaskCommitterTest<PartitionedStagingCommitter>`. It uses `createTestOutputFiles()`, `PartitionedStagingCommitter.commitTask()`, `ConflictResolution`, `CreateMultipartUploadRequest`, and `Paths.addUUID()`.

## Control Flow and Behavior
`@BeforeAll` builds a static set of four partitioned relative files. Bad conflict mode is rejected. Default mode resolves to append. Fail mode creates task output files, mocks one existing partition to force `PathExistsException`, then retries with no conflict and verifies uploads. Append mode succeeds even with an existing partition. Replace mode also succeeds with an existing partition; deletion behavior is noted as a TODO at task level. `verifyFilesCreated()` asserts one MPU request per relative file and exact expected destination keys, including UUID suffixing when enabled.

## State, Persistence, and Dependencies
State is local task output files and mock S3 create-MPU requests. Dependencies include partitioned committer conflict config, staging test fixture, and AWS SDK request models.

## Integration Points, Risks, and Test Signals
The suite ensures task commit only uploads intended files and handles partition conflicts according to mode. It is a key signal for destination key construction, particularly unique filename policy with partitioned relative paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/TestStagingPartitionedTaskCommit.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/integration/ITestDirectoryCommitProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/integration/ITestDirectoryCommitProtocol.java

## Purpose
Integration protocol suite specialization for `DirectoryStagingCommitter`. It runs shared low-level committer protocol tests with directory committer behavior and validates default staging conflict configuration.

## Important APIs, Types, and Functions
The class extends `ITestStagingCommitProtocol`, returns `COMMITTER_NAME_DIRECTORY`, creates `DirectoryStagingCommitter`, disables experimental IO statistics collection, and defines a `CommitterWithFailedThenSucceed` using `CommitterFaultInjectionImpl`.

## Control Flow and Behavior
Shared protocol tests come from the superclass hierarchy. This class creates real directory staging committers for those tests and provides a fault-injecting variant for retry/failure cases. `testValidateDefaultConflictMode()` reads the default conflict mode from a base `Configuration` and the active filesystem config, asserting both are `append`.

## State, Persistence, and Dependencies
State includes staging local/HDFS pending metadata and S3A output from inherited integration tests. Dependencies include directory committer, fault injection, S3A committer constants, and the shared staging protocol suite.

## Integration Points, Risks, and Test Signals
The test confirms the directory committer conforms to the same protocol expectations as other S3A committers while preserving directory-specific config defaults. Failures commonly indicate config override leakage or lifecycle differences in setup/task/job commit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/integration/ITestDirectoryCommitProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/integration/ITestPartitionedCommitProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/integration/ITestPartitionedCommitProtocol.java

## Purpose
Integration protocol suite specialization for `PartitionedStagingCommitter`.

## Important APIs, Types, and Functions
The class extends `ITestStagingCommitProtocol`, returns `COMMITTER_NAME_PARTITIONED`, creates `PartitionedStagingCommitter`, and defines a fault-injecting committer wrapper. It overrides `testMapFileOutputCommitter()` to skip because the partitioned committer is not suitable for map output.

## Control Flow and Behavior
Inherited protocol tests run against the partitioned committer except the map-file output case. The failing committer class delegates lifecycle methods through `CommitterFaultInjectionImpl` before calling the superclass methods, enabling shared failure recovery tests.

## State, Persistence, and Dependencies
State is inherited staging task/job metadata and S3A output. Dependencies include partitioned and directory staging committer classes, fault-injection interfaces, and the abstract protocol test suite.

## Integration Points, Risks, and Test Signals
This file asserts that the partitioned committer honors the shared S3A committer protocol where applicable. The explicit skip documents an unsupported output format scenario and prevents a false failure from an incompatible test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/integration/ITestPartitionedCommitProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/integration/ITestStagingCommitProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/integration/ITestStagingCommitProtocol.java

## Purpose
Base integration protocol specialization for staging committers. It adapts `AbstractITCommitProtocol` expectations to local staging work directories and validates staging upload directory cleanup on success and failure.

## Important APIs, Types, and Functions
The class extends `AbstractITCommitProtocol`, uses `StagingCommitter` by default, configures committer threads and disables unique filenames, and uses `Paths.getLocalTaskAttemptTempDir()` and `Paths.getStagingUploadsParentDirectory()`. It defines a fault-injecting `CommitterWithFailedThenSucceed`.

## Control Flow and Behavior
`setup()` generates a Spark write UUID, verifies `AbstractS3ACommitter.buildJobUUID()` selects it, and removes any existing local task attempt temp dir. Working directory validation expects local `file` scheme, while task attempt write validation asserts local file existence and length. Staging committers are expected not to create success markers in these protocol tests. Cleanup tests start a job, verify the staging uploads directory exists after `setupJob`, commit or fail the job, and then assert the staging uploads parent directory has been deleted.

## State, Persistence, and Dependencies
State includes local task attempt files, staging uploads directories, pending commit metadata, S3A final output, and job UUID configuration. Dependencies include the abstract protocol suite, staging path utilities, MR contexts, local filesystem, and committer fault injection.

## Integration Points, Risks, and Test Signals
This is the common protocol bridge for staging, directory, and partitioned committers. It catches regressions in local staging path lifecycle, Spark UUID propagation, cleanup on failed commit, and mismatch between expected local work paths and S3 final output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/integration/ITestStagingCommitProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/integration/ITestStagingCommitProtocolFailure.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/integration/ITestStagingCommitProtocolFailure.java

## Purpose
Negative integration test proving the staging committer cannot be created when multipart uploads are disabled.

## Important APIs, Types, and Functions
The class extends `AbstractS3ATestBase`. `createConfiguration()` removes bucket overrides, disables `MULTIPART_UPLOADS_ENABLED`, binds the S3A committer factory and staging committer name, and disables filesystem caching. `testCreateCommitter()` expects `PathCommitException` from `new StagingCommitter(...)`.

## Control Flow and Behavior
The test constructs a task attempt context against a deliberately MPU-disabled configuration and asserts immediate constructor failure.

## State, Persistence, and Dependencies
There is no output persistence. Dependencies are S3A configuration, staging committer constructor validation, and MR task context classes.

## Integration Points, Risks, and Test Signals
Like the magic failure test, this protects an essential committer precondition. It also verifies bucket overrides and filesystem caches do not mask the disabled-MPU setting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/staging/integration/ITestStagingCommitProtocolFailure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/terasort/ITestTerasortOnS3A.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/terasort/ITestTerasortOnS3A.java

## Purpose
Scale test running the full Teragen, Terasort, and Teravalidate pipeline on S3A with S3A committers. It compares directory staging with magic committer modes, including magic in-memory commit tracking.

## Important APIs, Types, and Functions
The class extends `AbstractYarnClusterITest`, is tagged `@ScaleTest`, and is parameterized over `DirectoryStagingCommitter.NAME`, `MagicS3GuardCommitter.NAME` with tracking disabled, and magic with tracking enabled. It uses Hadoop examples `TeraGen`, `TeraSort`, `TeraValidate`, `ToolRunner`, `DurationInfo`, success marker validation, and committer configuration patching.

## Control Flow and Behavior
`setup()` requires scale tests and multipart uploads, then creates unique S3A paths for the parameter. `applyCustomConfigOptions()` sets small partition/sample parameters and magic tracking mode. Ordered tests delete previous data, run teragen, require its success before terasort, require terasort success before teravalidate, validate `_SUCCESS` at each stage, record durations in a static map, write a CSV report, reset duration state, and finally delete the test directory.

## State, Persistence, and Dependencies
State spans S3A input/output/validate directories, MR/YARN job state, success marker JSON files, static duration tracking, and a local CSV report under the test report directory. Dependencies include scale-test enablement, mini YARN cluster, S3A multipart support, Hadoop terasort tools, and S3A committer config injection.

## Integration Points, Risks, and Test Signals
This is an expensive but realistic signal for production-style MR workloads on S3A. It validates that committers handle chained MR jobs, success-file loading between stages, and final cleanup. Risks include long runtime, scale-test gating, static state across parameterized runs, and YARN/S3 operational flakiness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/terasort/ITestTerasortOnS3A.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/fileContext/ITestS3AFileContext.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/fileContext/ITestS3AFileContext.java

## Purpose
Integration test for S3A `FileContext` scheme binding through Hadoop `AbstractFileSystem`.

## Important APIs, Types, and Functions
The class extends `TestFileContext`. `testScheme()` creates a configuration mapping `fs.AbstractFileSystem.s3.impl` to `org.apache.hadoop.fs.s3a.S3A`, obtains a `FileContext` for `s3://mybucket/path`, and checks default filesystem and qualified path schemes.

## Control Flow and Behavior
The test constructs a URI using the `s3` scheme rather than `s3a`, binds the abstract filesystem implementation, then verifies both `fc.getDefaultFileSystem().getUri().getScheme()` and `fc.makeQualified(new Path("tmp/path"))` preserve `s3`.

## State, Persistence, and Dependencies
No remote IO is required by the test itself. Dependencies include `FileContext`, `TestFileContext`, Hadoop `Path`, and S3A abstract filesystem binding configuration.

## Integration Points, Risks, and Test Signals
This guards FileContext URI binding and qualification behavior for the legacy `s3` abstract scheme. A failure suggests misconfiguration in abstract filesystem implementation mapping or path qualification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/fileContext/ITestS3AFileContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/fileContext/ITestS3AFileContextCreateMkdir.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/fileContext/ITestS3AFileContextCreateMkdir.java

## Purpose
S3A implementation of Hadoop `FileContextCreateMkdirBaseTest`, covering create and mkdir behavior through `FileContext`.

## Important APIs, Types, and Functions
The class extends `FileContextCreateMkdirBaseTest`. `setUp()` creates a configuration via `S3ATestUtils.setPerformanceFlags(new Configuration(), null)`, creates a test `FileContext`, and delegates to the superclass setup. `tearDown()` only delegates if `fc` was created.

## Control Flow and Behavior
All actual create/mkdir test methods are inherited from the base test. This class supplies an S3A-backed `FileContext` with default performance flag behavior.

## State, Persistence, and Dependencies
State is the S3A test filesystem paths created by inherited tests and `fc`. Dependencies include S3A test utilities, FileContext base tests, and integration test bucket configuration.

## Integration Points, Risks, and Test Signals
The suite validates S3A FileContext behavior against common Hadoop filesystem create/mkdir contracts. Risks include S3 directory marker semantics and cleanup only running when setup succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/fileContext/ITestS3AFileContextCreateMkdir.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/fileContext/ITestS3AFileContextCreateMkdirCreatePerf.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/fileContext/ITestS3AFileContextCreateMkdirCreatePerf.java

## Purpose
Variant of the S3A FileContext create/mkdir contract tests with mkdir create-performance mode enabled.

## Important APIs, Types, and Functions
The class extends `FileContextCreateMkdirBaseTest`, uses `S3ATestUtils.setPerformanceFlags(new Configuration(), "mkdir")`, and overrides `testMkdirRecursiveWithExistingFile()`.

## Control Flow and Behavior
Setup creates an S3A test FileContext with mkdir performance flags and delegates to inherited setup. Most tests are inherited. The overridden existing-file mkdir test expects the base test to fail with `AssertionError` containing `MKDIR_FILE_PRESENT_ERROR`, documenting that performance mode skips parent status checks and can therefore create dirs without detecting a parent file in the usual way.

## State, Persistence, and Dependencies
State is inherited FileContext test output under the S3A test path. Dependencies include S3A performance flags, base FileContext mkdir tests, and `LambdaTestUtils.intercept()`.

## Integration Points, Risks, and Test Signals
This is a focused signal for the behavioral tradeoff of mkdir performance mode. It makes the altered semantics explicit so future changes do not silently reintroduce status checks or change expected failure shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/fileContext/ITestS3AFileContextCreateMkdirCreatePerf.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/fileContext/ITestS3AFileContextMainOperations.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/fileContext/ITestS3AFileContextMainOperations.java

## Purpose
S3A implementation of Hadoop `FileContextMainOperationsBaseTest`, covering the main FileContext operations against an S3A-backed context while disabling unsupported append/checksum tests.

## Important APIs, Types, and Functions
The class extends `FileContextMainOperationsBaseTest`. `setUp()` creates a FileContext with S3A performance flags. `createFileContextHelper()` supplies a unique test path using a random UUID. `listCorruptedBlocksSupported()` returns false. Several inherited tests are overridden and disabled because append and checksum verification are unsupported/ignored.

## Control Flow and Behavior
The inherited base test performs the main create, list, rename, delete, and related FileContext operations. This class supplies S3A setup and documents unsupported operations via disabled methods: append-existing-file variants, builder append, and set/verify checksum.

## State, Persistence, and Dependencies
State is S3A test data rooted under a randomized path. Dependencies include `S3ATestUtils`, `FileContextTestHelper`, base FileContext operation tests, and integration bucket configuration.

## Integration Points, Risks, and Test Signals
The file aligns generic Hadoop FileContext contract coverage with S3A capabilities. Disabled tests are important signals: enabling append/checksum assertions without S3A support would create false failures, while removing the disables would require feature support changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/fileContext/ITestS3AFileContextMainOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/fileContext/ITestS3AFileContextStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/fileContext/ITestS3AFileContextStatistics.java

## Purpose
S3A implementation of `FCStatisticsBaseTest`, validating FileContext filesystem statistics accounting for bytes read and written.

## Important APIs, Types, and Functions
The class extends `FCStatisticsBaseTest`. `setUp()` creates an S3A FileContext, creates a test root directory, and clears FileContext statistics. `tearDown()` deletes the test root quietly. It overrides `verifyReadBytes()`, `verifyWrittenBytes()`, and `getFsUri()`.

## Control Flow and Behavior
Inherited statistics tests perform reads and writes. S3A-specific assertions expect reads to count two block sizes, one for sequential read and one for positional read, and writes to count exactly one block size. The FS URI comes from the FileContext home directory.

## State, Persistence, and Dependencies
State includes a test root path in S3A, FileContext statistics counters, and inherited test files. Dependencies include `S3ATestUtils`, `FileContext`, `FileSystem.Statistics`, and quiet cleanup logging.

## Integration Points, Risks, and Test Signals
This guards S3A FileContext statistics behavior against generic Hadoop expectations. Risks include statistic counter changes in S3A read paths, cleanup failures leaving test data, and differences between sequential and positioned read accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/fileContext/ITestS3AFileContextStatistics.java -->
