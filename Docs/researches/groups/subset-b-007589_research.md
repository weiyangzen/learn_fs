# Group Research: subset-b-007589

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/fileContext/ITestS3AFileContextURI.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/fileContext/ITestS3AFileContextURI.java

## Purpose
`ITestS3AFileContextURI` adapts Hadoop's generic `FileContextURIBase` URI contract tests to an S3A-backed `FileContext`. It exists to make the common FileContext URI behavior suite run against S3A with the correct test filesystem wiring.

## Important APIs, Types, and Functions
- Extends `FileContextURIBase`, inheriting the actual URI tests and shared `fc1`/`fc2` fields.
- `setUp()` builds a `Configuration`, applies `S3ATestUtils.setPerformanceFlags()`, creates two S3A test FileContexts through `S3ATestUtils.createTestFileContext()`, then delegates to `super.setUp()`.
- `testFileStatus()` is locally disabled because the inherited statistics expectations are not relevant for S3A.

## Control Flow
Each inherited test starts by constructing two different FileContext objects against the same S3A filesystem, then the base class performs URI and status contract exercises. The only locally declared test is skipped.

## State and Persistence Behavior
State is limited to the instance configuration and inherited FileContext fields. Persistent effects are those of the inherited contract tests in the S3A test bucket; cleanup is delegated to the base class.

## Dependencies and Integration Points
The file integrates Hadoop common FileContext contract tests with S3A test utilities. It requires an integration-test S3A configuration and is tagged `@IntegrationTest`.

## Risks and Edge Cases
Failures may come from object-store semantics or test-bucket setup rather than local adapter logic. The disabled status test is a documented mismatch between generic filesystem statistics assumptions and S3A.

## Test Signals
Passing inherited tests signal FileContext URI operations work for S3A. The disabled test signals statistics coverage is intentionally excluded here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/fileContext/ITestS3AFileContextURI.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/fileContext/ITestS3AFileContextUtil.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/fileContext/ITestS3AFileContextUtil.java

## Purpose
`ITestS3AFileContextUtil` adapts Hadoop's `FileContextUtilBase` utility tests to S3A. It verifies common FileContext utility behavior using a live S3A-backed FileContext.

## Important APIs, Types, and Functions
- Extends `FileContextUtilBase`, inheriting the utility test methods.
- `setUp()` creates a default `Configuration`, initializes inherited `fc` with `S3ATestUtils.createTestFileContext(conf)`, and invokes `super.setUp()`.

## Control Flow
Before each inherited test, the S3A FileContext is created and registered with the base fixture. All test assertions come from `FileContextUtilBase`.

## State and Persistence Behavior
State is the inherited `fc` field. Any object-store paths created are owned by the inherited test fixture. This class adds no independent persistent state.

## Dependencies and Integration Points
It depends on S3A integration-test configuration and Hadoop common FileContext utility tests. The `@IntegrationTest` tag marks it as requiring live filesystem setup.

## Risks and Edge Cases
Because there are no local assertions, failures should be traced to inherited base behavior and S3A object-store semantics. Default configuration assumes test-site configuration supplies the S3A test bucket.

## Test Signals
Passing means S3A's FileContext adapter satisfies the generic FileContext utility contract exercised by Hadoop common tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/fileContext/ITestS3AFileContextUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestAwsSdkWorkarounds.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestAwsSdkWorkarounds.java

## Purpose
`ITestAwsSdkWorkarounds` validates S3A's AWS SDK workaround behavior around transfer-manager logging. It asserts that transfer-manager creation remains quiet even when noisy SDK logging has been restored.

## Important APIs, Types, and Functions
- Extends `AbstractS3ATestBase` for a live S3A filesystem.
- `deleteTestDirInTeardown()` is overridden as a no-op to avoid unnecessary cleanup for this client-only test.
- `testNoisyLogging()` skips client-side encryption, creates a fresh FS, restores noisy logging, forces transfer-manager construction, and asserts captured transfer-manager log output is empty.
- `newFileSystem()` initializes a separate `S3AFileSystem` with the base FS URI/config and closes it on failure.
- `createAndLogTransferManager()` captures `AwsSdkWorkarounds.TRANSFER_MANAGER` logs around `getOrCreateTransferManager()`.

## Control Flow
The single test creates an independent filesystem instance, enables logging through `AwsSdkWorkarounds.restoreNoisyLogging()`, captures the transfer-manager logger, triggers transfer-manager creation through S3A internals, stops capture, and checks no output was produced.

## State and Persistence Behavior
No S3 object data is written. Runtime state is a temporary filesystem instance and a temporary log capturer, both closed/stopped in local control flow.

## Dependencies and Integration Points
The test touches `S3AFileSystem`, internal store/client-manager paths, AWS SDK transfer manager creation, SLF4J/Log4J capture utilities, and S3A SDK workaround code.

## Risks and Edge Cases
The class comment notes brittleness across SDK updates. Logger names, SDK transfer-manager implementation, or encryption-specific client paths can change the expected output. It is skipped for client-side encryption.

## Test Signals
Passing signals S3A's SDK workaround keeps transfer-manager initialization from emitting unwanted log noise under restored noisy logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestAwsSdkWorkarounds.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestConnectionTimeouts.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestConnectionTimeouts.java

## Purpose
`ITestConnectionTimeouts` verifies S3A timeout behavior for connection-pool acquisition and request operations. It deliberately constructs brittle filesystems with tiny timeouts, then confirms pool exhaustion and delayed SDK calls produce expected failures while uploads honor longer upload-specific timeouts.

## Important APIs, Types, and Functions
- Extends `AbstractS3ATestBase`.
- `createConfiguration()` removes timeout/purge bucket overrides, sets `PART_UPLOAD_TIMEOUT`, and enables `DIRECTORY_OPERATIONS_PURGE_UPLOADS` for cleanup.
- `timingOutConfiguration()` disables prefetching, forces classic input streams, sets `MAXIMUM_CONNECTIONS=1`, disables retries, enables create performance, and sets 10 ms acquisition/establish timeouts.
- `testGeneratePoolTimeouts()` opens many `openFile()` streams with a known `FileStatus` until a `ConnectTimeoutException` is raised.
- `testObjectUploadTimeouts()` uses `SdkFaultInjector` to delay PUT, GET, and optional part-upload requests to distinguish upload timeout from general request timeout.

## Control Flow
The pool test writes a file with the stable base FS, opens a separate one-connection FS, repeatedly builds whole-file open streams, reads one byte to force GET requests, and expects connection acquisition failure. All streams are cleaned up in `finally`.

The upload test configures long `PART_UPLOAD_TIMEOUT` and shorter request/acquisition timeouts, installs an SDK fault action that sleeps under the upload timeout, then verifies normal PUT succeeds and takes longer than the short timeout. It then switches injection to GET and expects read failure. If magic commit is enabled, it also validates part-upload timeout behavior on a magic path.

## State and Persistence Behavior
Tests create method-path objects in S3. Static state in `AWSClientConfig` and `SdkFaultInjector` is reset around test execution. Open streams and temporary FS instances are explicitly closed.

## Dependencies and Integration Points
The file integrates S3A configuration constants, classic input streams, `FutureDataInputStreamBuilder`, `AWSClientConfig`, `SdkFaultInjector`, magic committer paths, and Hadoop contract utilities.

## Risks and Edge Cases
Timing tests are sensitive to parallel test runs and stream implementation, hence prefetch is disabled. Low-level read timeout exceptions vary, so the read failure assertion accepts generic `Exception`. Magic multipart coverage is conditional on magic commit support.

## Test Signals
Passing confirms connection-pool timeout translation, upload-specific timeout propagation to PUT/part upload, and shorter timeout enforcement on reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestConnectionTimeouts.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestPartialRenamesDeletes.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestPartialRenamesDeletes.java

## Purpose
`ITestPartialRenamesDeletes` tests S3A rename/delete behavior when IAM permissions allow only part of a directory tree to be read or written. It documents partial copy/delete outcomes and validates exception translation for both single-object and bulk-delete paths.

## Important APIs, Types, and Functions
- Parameterized over `multiDelete=false/true` with `@ParameterizedClass`.
- Extends `AbstractS3ATestBase`; uses a full-access FS for fixture creation and an assumed-role `roleFS` for restricted operations.
- `setup()` requires an assumed-role ARN, skips S3 Express, creates unique paths, binds role policies, and chooses scaled counts for bulk-delete scale runs.
- `createAssumedRoleConfig()` installs assumed-role credentials, disables FS caching/create sessions, and sets `ENABLE_MULTI_DELETE`.
- Helper methods `expectDeleteForbidden()`, `expectRenameForbidden()`, `listFilesUnderPath()`, and `pathMustExist()` centralize state and exception checks.

## Control Flow
Setup creates `writableDir`, `readOnlyDir`, `readOnlyChild`, and `noReadDir`, then binds policy statements granting broad reads, RW only under the writable subtree, and denies for the no-read subtree. Initial tests verify role assumptions and propagation of multi-delete mode.

Rename tests cover parent write constraints, delete-phase failures after successful copies, source-read failures, destination-write failures, and directory-tree behavior. `testRenameSingleFileFailsInDelete()` explicitly asserts both source and copied destination remain after delete fails. `testRenameDirFailsInDelete()` scales this to trees and checks nested `MultiObjectDeleteException` when bulk delete is enabled.

Delete tests verify empty directory cleanup under writable parents and partial failures for read-only subtrees. In bulk mode, metric diffs check object delete request counts, bulk delete request counts, number of keys in the failed request, and rejected-file counters. `testRenamePermissionRequirements()` verifies rename/delete do not require `s3:DeleteObjectVersion`.

## State and Persistence Behavior
Each test uses a timestamped method path to isolate S3 objects. Some operations intentionally leave partial destination copies or protected source objects, which are asserted and sometimes cleaned explicitly. `roleFS` is closed in teardown.

## Dependencies and Integration Points
This file integrates S3A rename/delete internals, IAM assumed roles, KMS policy allowances, multi-object delete translation, S3A metrics, contract file/tree helpers, and object-store copy-then-delete rename semantics.

## Risks and Edge Cases
Requires an assumed role ARN and is skipped without one; S3 Express is skipped. IAM propagation, provider-specific access-denied behavior, and scale settings affect run cost and stability. Future transactional rollback behavior would invalidate current partial-result assertions.

## Test Signals
Passing signals stable, documented behavior for restricted-permission rename/delete operations, correct access-denied translation, correct bulk-delete metrics, and correct permission requirements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestPartialRenamesDeletes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestRenameDeleteRace.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestRenameDeleteRace.java

## Purpose
`ITestRenameDeleteRace` reproduces HADOOP-16721: a race between deleting one child under a destination directory and renaming another source directory into that same destination. It verifies rename remains successful when the destination parent has temporarily disappeared due to delete behavior.

## Important APIs, Types, and Functions
- Extends `AbstractS3ATestBase`.
- Uses a static `BlockingThreadPoolExecutorService` plus `CallableSupplier.submit()` and `waitForCompletion()` for the concurrent delete.
- Inner `BlockingFakeDirMarkerFS` extends `S3AFileSystem` and overrides `maybeCreateFakeParentDirectory(Path)`.
- Two semaphores coordinate entry into fake parent directory creation and release of marker creation.

## Control Flow
The test creates `dest/subdir1/subfile1` and `src/subdir2/subfile2`. A special filesystem instance begins deleting `dest/subdir1` in another thread and blocks inside `maybeCreateFakeParentDirectory()`. The main thread waits for that block, confirms `dest` is absent, renames `src/subdir2` to `dest/subdir2`, verifies `dest` exists, then releases the delete thread and confirms the rename result survives.

## State and Persistence Behavior
The test persists a small S3 directory/file structure under the method path. Concurrency state is purely in semaphores. The blocking filesystem is closed in `finally`.

## Dependencies and Integration Points
It directly depends on S3A's fake parent directory marker hook, recursive delete behavior, rename behavior, object-store implicit directory semantics, and Hadoop executor utilities.

## Risks and Edge Cases
The test is coupled to internal delete sequencing. Changes to directory marker policy or `maybeCreateFakeParentDirectory()` invocation could make the choreography invalid. A semaphore error would risk hanging until the larger test framework times out.

## Test Signals
Passing signals that concurrent delete cleanup does not erase or prevent a rename into the same destination parent once the parent is recreated by rename.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestRenameDeleteRace.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestS3AConditionalCreateBehavior.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestS3AConditionalCreateBehavior.java

## Purpose
`ITestS3AConditionalCreateBehavior` verifies S3A create-file behavior around conditional create support, including feature toggling, ETag-based write options, and interaction with create performance mode.

## Important APIs, Types, and Functions
- Parameterized over `conditionalCreateEnabled=true/false`.
- `createConfiguration()` removes create/performance/multipart overrides, optionally disables `FS_S3A_CONDITIONAL_CREATE_ENABLED`, and disables filesystem caching.
- Uses `FSDataOutputStreamBuilder` options `FS_OPTION_CREATE_CONDITIONAL_OVERWRITE` and `FS_OPTION_CREATE_CONDITIONAL_OVERWRITE_ETAG`.
- `assertHasCapabilityConditionalCreate()` and `assertHasCapabilityEtagWrite()` verify stream capabilities.

## Control Flow
`testConditionalWrite()` creates a file, then attempts a conditional overwrite using `FS_OPTION_CREATE_CONDITIONAL_OVERWRITE=true`; it expects `PathIOException`. `testWriteWithEtag()` runs only when conditional create is disabled, fetches the existing file ETag, and verifies a builder requiring ETag overwrite also fails. `testWriteWithPerformanceFlagAndOverwriteFalse()` checks that overwrite false with the S3A create performance flag can write and collect stream statistics in the disabled-conditional-create mode.

## State and Persistence Behavior
Each test creates one method-path object and sometimes fetches its `S3AFileStatus` for ETag state. No static state is changed. Output stream statistics are local and currently not asserted due to TODO comments.

## Dependencies and Integration Points
The test integrates S3A create builder options, filesystem capability reporting, `S3AFileStatus` ETags, multipart threshold configuration cleanup, and the create performance flag.

## Risks and Edge Cases
Two tests assume conditional create is disabled by the parameter and use AssertJ assumptions to skip otherwise. The statistics assertions are commented out because conditional write counters are not initialized/implemented yet. Behavior depends on S3 provider ETag availability.

## Test Signals
Passing signals conditional overwrite and ETag write capabilities are advertised on streams and conflicting writes fail as expected under the configured feature mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestS3AConditionalCreateBehavior.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestS3APutIfMatchAndIfNoneMatch.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestS3APutIfMatchAndIfNoneMatch.java

## Purpose
`ITestS3APutIfMatchAndIfNoneMatch` is a broad integration suite for S3 conditional write semantics. It verifies If-None-Match create-only writes, If-Match ETag overwrites, multipart precondition races, error translation, and partially disabled conditional-write statistics tests.

## Important APIs, Types, and Functions
- Extends `AbstractS3ATestBase` and assumes conditional create is enabled in `setup()`.
- `createConfiguration()` disables FS caching, removes create/performance/multipart overrides, sets multipart threshold/part size, and limits multipart part count.
- Helpers `createFileWithFlags()` and `getStreamWithFlags()` build files with conditional overwrite, ETag, and forced multipart options.
- `expectPreconditionFailure()` accepts both classic S3 HTTP 412 and S3 Express-style HTTP 200 with `PreconditionFailed` error details.
- `verifyS3ExceptionStatusCode()` validates nested `S3Exception` status codes.

## Control Flow
If-None-Match tests first create a file conditionally, then verify repeated overwrites fail with `RemoteFileChangedException`, including empty-file cases and multipart uploads. Race tests keep one multipart stream open, write a competing file, then expect the first stream close to fail.

If-Match tests create a file, fetch its ETag from `S3AFileStatus`, overwrite successfully with the correct ETag, then verify stale ETags fail, deleted targets raise `FileNotFoundException`, and empty ETags are rejected as `IllegalArgumentException`. A multipart race starts two streams with the same ETag; the first close updates the object and the second close fails.

The performance-flag test verifies `overwrite(false)` with `FS_S3A_CREATE_PERFORMANCE` triggers conditional create failure on an existing path. Two statistics tests are disabled pending complete conditional-write counter implementation.

## State and Persistence Behavior
The suite creates and overwrites method-path objects, using object ETags as state. Open multipart streams intentionally survive across competing writes until close. The `statistics` field stores output-stream stats for disabled or TODO assertions.

## Dependencies and Integration Points
It exercises S3A create builder options, multipart upload support, S3 provider precondition behavior, S3 Express error shape, `RemoteFileChangedException`, ETag propagation, output-stream statistics, and store path capabilities for multipart upload.

## Risks and Edge Cases
Multipart tests skip when path capability says multipart upload is unsupported. Provider differences require permissive precondition-failure handling. Statistics coverage is disabled/commented because counters are not fully implemented.

## Test Signals
Passing confirms S3A maps conditional create/update APIs to S3 precondition semantics across single PUT, empty object, multipart, race, stale ETag, deleted target, and performance-create paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestS3APutIfMatchAndIfNoneMatch.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestTreewalkProblems.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestTreewalkProblems.java

## Purpose
`ITestTreewalkProblems` validates that S3A tree-walking clients behave sensibly when pending multipart uploads, especially magic-committer uploads, are present under a directory. It covers filesystem listings, content summary, FsShell commands, DistCp, globbing, contract treewalks, and MapReduce input splits.

## Important APIs, Types, and Functions
- Extends `AbstractS3ACostTest`, allowing cost/metric assertions in inherited helpers.
- `createConfiguration()` enables `DIRECTORY_OPERATIONS_PURGE_UPLOADS` and `MAGIC_COMMITTER_ENABLED` after removing overrides.
- `setup()` asserts purge capability, assumes multipart uploads, records whether directory listings are inconsistent, and clears existing uploads under the method path.
- `createDirWithUpload()` creates a magic file then deletes the magic path, leaving a pending upload targeting a real final key.
- `shell()` wraps `FsShell` execution and asserts expected exit codes.
- `listUploads()` uses `StoreContext` and `listUploadsUnderPrefix()` under an audit span.

## Control Flow
Most tests create a directory with one pending magic upload, then exercise a tree-walking API. Listing tests compare `listStatus`, `listStatusIterator`, `listFiles`, and `listLocatedStatus`. Content-summary tests assert directory/file counts. Shell tests run `-ls`, `-du`, `-df`, and `-find`, including expected pre-create failures. DistCp tests expect success on consistent listings and intentional assertion failure when upload visibility makes listings inconsistent. Glob and FileInputFormat tests confirm only real files become data inputs while pending upload pseudo-paths are handled according to capability.

## State and Persistence Behavior
The test leaves pending multipart uploads during API calls and clears/aborts them through setup or explicit calls. It creates method-path directories and real files, with magic upload state in S3 multipart upload listings rather than normal objects.

## Dependencies and Integration Points
It integrates S3A pending upload listing, magic committer paths, directory operation purge, Hadoop FsShell, DistCp, MapReduce `TextInputFormat`, `LocatedFileStatusFetcher`, globber behavior, `ContractTestUtils.treeWalk`, and audit spans.

## Risks and Edge Cases
Behavior differs when `DIRECTORY_LISTING_INCONSISTENT` is reported, so some assertions branch. DistCp currently fails in inconsistent stores when uploads are visible. Pending uploads and external cleanup can make tests sensitive to interrupted runs.

## Test Signals
Passing signals S3A treewalk-related callers either ignore, tolerate, or intentionally expose pending uploads according to advertised path capabilities, while directory cleanup APIs can abort the upload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestTreewalkProblems.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestUploadPurgeOnDirectoryOperations.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestUploadPurgeOnDirectoryOperations.java

## Purpose
`ITestUploadPurgeOnDirectoryOperations` verifies that directory delete and rename operations abort pending multipart uploads beneath the affected directory when `DIRECTORY_OPERATIONS_PURGE_UPLOADS` is enabled.

## Important APIs, Types, and Functions
- Extends `AbstractS3ACostTest` for operation-cost assertions.
- `createConfiguration()` enables upload purge and magic committer support after clearing overrides.
- `setup()` assumes multipart support, asserts purge capability on root, and clears uploads under the method path.
- `testDeleteWithPendingUpload()` creates a magic upload under a directory, deletes the directory, and checks abort/list metrics.
- `testRenameWithPendingUpload()` creates a magic upload under a source directory, renames it, and checks the same purge behavior.
- `listUploads()` uses `StoreContext.pathToKey()` and `listUploadsUnderPrefix()` inside an audit span.

## Control Flow
Each active test creates a magic file, asserts one pending upload, runs delete or rename through `verifyMetrics()`, and asserts upload count returns to zero. Expected metrics include one aborted multipart upload and one underlying multipart upload list HTTP request.

## State and Persistence Behavior
Persistent S3 multipart upload state is intentionally created then purged. Real object state is limited to method-specific paths. Metrics are observed through inherited cost-validation state.

## Dependencies and Integration Points
The class integrates directory operations, pending multipart upload enumeration/abort, magic committer test utilities, S3A path capabilities, audit spans, and S3A statistics such as `OBJECT_MULTIPART_UPLOAD_ABORTED`.

## Risks and Edge Cases
Requires multipart upload support. External pending uploads under the same prefix would alter counts, hence setup clears the path. Metric names distinguish API-level list calls from HTTP object multipart list calls, which can be easy to confuse.

## Test Signals
Passing confirms delete and rename purge pending uploads under their source prefixes and emit the expected abort/list statistics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestUploadPurgeOnDirectoryOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestXAttrCost.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestXAttrCost.java

## Purpose
`ITestXAttrCost` verifies S3A's xattr API, which exposes selected HTTP/S3 object headers as extended attributes, and asserts the request cost for file, directory, root, and missing-path cases.

## Important APIs, Types, and Functions
- Extends `AbstractS3ACostTest` for metric verification.
- Uses S3A xattr APIs `getXAttrs()`, `listXAttrs()`, and `getXAttr()`.
- Validates header keys from `HeaderProcessing`, including `XA_CONTENT_LENGTH`, `XA_CONTENT_TYPE`, and `XA_STANDARD_HEADERS`.
- Uses cost probes for `INVOCATION_XATTR_GET_MAP`, `INVOCATION_OP_XATTR_LIST`, and `INVOCATION_XATTR_GET_NAMED`.
- Helper `assertHeader()` decodes xattr bytes and asserts non-empty values.

## Control Flow
`testXAttrRoot()` fetches and lists root headers without asserting provider-specific header names. `testXAttrFile()` creates an empty file, retrieves all/listed/named xattrs, and checks length `0` plus octet-stream content type. `testXAttrDir()` creates a directory and expects directory xattrs to cost two metadata probes and report `application/x-directory` style content type. `testXAttrMissingFile()` verifies all xattr APIs throw `FileNotFoundException` with the expected missing-path cost.

## State and Persistence Behavior
The tests create method-path files and directories in S3. Xattr maps are derived from live S3 metadata; no local persistence is introduced. Metrics are reset/validated by the inherited cost framework.

## Dependencies and Integration Points
The class integrates xattr API implementations, header decoding, S3 metadata probes, create-performance cost differences, and provider-visible HTTP header metadata.

## Risks and Edge Cases
Root headers differ by provider, so root assertions only compare list size to map size. Directory metadata costs more than file metadata because S3A may probe object and directory marker forms. Missing-path cost is modeled as directory-style metadata probing.

## Test Signals
Passing indicates S3A xattr/header extraction returns expected standard headers and preserves known operation-cost profiles for files, directories, root, and missing paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestXAttrCost.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/StubContextAccessor.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/StubContextAccessor.java

## Purpose
`StubContextAccessor` is a lightweight test implementation of `ContextAccessors`. It supplies just enough behavior for unit tests that need key/path qualification, audit span access, and a request factory without a real S3A filesystem.

## Important APIs, Types, and Functions
- Implements `ContextAccessors`.
- Constructor stores a bucket name used by `keyToPath()`.
- `keyToPath(String)` returns `s3a://<bucket>/<key>`.
- `makeQualified(Path)` returns the path unchanged.
- `getActiveAuditSpan()` returns `AuditTestSupport.NOOP_SPAN`.
- `getRequestFactory()` returns `MockS3AFileSystem.REQUEST_FACTORY`.
- Unsupported or irrelevant methods return `null` or throw `UnsupportedOperationException`, including `pathToKey()`, `createTempFile()`, and `getBucketLocation()`.

## Control Flow
There is no branching beyond simple method returns. Tests instantiate it with a bucket and pass it into components expecting `ContextAccessors`.

## State and Persistence Behavior
The only state is the immutable bucket string. No filesystem, temporary-file, or network state is created.

## Dependencies and Integration Points
It integrates unit tests with `ContextAccessors`, mock S3A request factory infrastructure, and no-op audit spans. It is meant for code paths that do not need real key conversion back from paths or temp-file creation.

## Risks and Edge Cases
`pathToKey()` returns `null`, so any test using this stub must avoid code requiring reverse path conversion. The typo in the unsupported message is cosmetic. It is not a general-purpose fake context.

## Test Signals
Its presence supports unit tests that should stay isolated from real S3A clients while still satisfying constructor contracts for context-aware components.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/StubContextAccessor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestAwsClientConfig.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestAwsClientConfig.java

## Purpose
`TestAwsClientConfig` unit-tests `AWSClientConfig`, especially duration/default handling and custom request header parsing for different AWS service clients.

## Important APIs, Types, and Functions
- Extends `AbstractHadoopTestBase`.
- `teardown()` resets `AWSClientConfig` minimum operation duration.
- `conf()` creates a configuration with no default/site XML loading.
- Tests call `createConnectionSettings()`, `createApiConnectionSettings()`, `createClientConfigBuilder()`, and `ConfigurationHelper.enforceMinimumDuration()`.
- Header tests target `CUSTOM_HEADERS_S3`, `CUSTOM_HEADERS_STS`, `AWS_SERVICE_IDENTIFIER_S3`, and `AWS_SERVICE_IDENTIFIER_STS`.

## Control Flow
Duration tests verify minimum enforcement, default connection settings from an empty config, minimum duration winning for selected network operations, zero-minimum fields retaining configured values, and API request timeout propagation/defaults. Header tests set S3 or STS custom header strings, build client override configurations for both services, and verify headers are applied only to the targeted service, with whitespace trimming and duplicate values preserved.

## State and Persistence Behavior
All state is in in-memory `Configuration` and static AWSClientConfig minimum-duration settings. No persistent files or network calls are used. Static duration state is reset after each test.

## Dependencies and Integration Points
The tests integrate Hadoop configuration parsing, S3A constants, AWS SDK client override configuration, and Hadoop `Lists` utility for expected multi-value headers.

## Risks and Edge Cases
`testCreateApiConnectionSettingsDefault()` uses a default-loading `Configuration` and asserts no core-site/default value sets `REQUEST_TIMEOUT`; local site configuration drift could fail it. Header parsing tests depend on comma/semicolon/equal syntax.

## Test Signals
Passing indicates client connection defaults, minimum durations, request timeout propagation, and service-scoped custom header parsing remain stable and isolated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestAwsClientConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestChecksumSupport.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestChecksumSupport.java

## Purpose
`TestChecksumSupport` validates mapping from the S3A checksum configuration string to AWS SDK `ChecksumAlgorithm` enum values.

## Important APIs, Types, and Functions
- Tests `ChecksumSupport.getChecksumAlgorithm(Configuration)`.
- Uses `CHECKSUM_ALGORITHM` configuration key.
- Parameterized over supported SDK enum names `CRC32`, `CRC32_C`, `SHA1`, `SHA256`, and `CRC64_NVME`.
- Helper `assertChecksumAlgorithm()` sets the config and asserts the expected enum.

## Control Flow
The parameterized test verifies direct enum-name strings. Dedicated tests verify aliases `CRC32C`/`CRC32_C` and `CRC64NVME`/`CRC64_NVME`. Null/unset config returns `null`. An invalid string raises `IllegalArgumentException`.

## State and Persistence Behavior
All state is in memory in short-lived `Configuration` objects. No persistence or network interactions occur.

## Dependencies and Integration Points
The class integrates S3A configuration parsing with AWS SDK checksum algorithm enums, ensuring user-facing configuration strings map to request-factory checksum behavior.

## Risks and Edge Cases
Adding new supported algorithms in the SDK may require expanding the enum source list or aliases. Invalid values intentionally fail fast.

## Test Signals
Passing confirms checksum config accepts supported names and aliases, treats unset as no checksum algorithm, and rejects invalid input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestChecksumSupport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestClientManager.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestClientManager.java

## Purpose
`TestClientManager` verifies `ClientManagerImpl` lazy creation, singleton reuse, closure behavior, concurrency blocking, transfer-manager dependency on async clients, and retry after creation failure.

## Important APIs, Types, and Functions
- Uses mocked `S3Client`, `S3AsyncClient`, and `S3TransferManager`.
- `StubS3ClientFactory` supplies clients and records creation counts.
- `manager()` builds a `ClientManagerImpl` with `S3ClientCreationParameters.withPathUri()` and a stub duration tracker.
- Parallel tests use `CompletableFuture`, `Semaphore`, and factory sleeps to force contention.
- Failure test uses an `InvocationRaisingIOE` that throws `UnknownHostException` with incrementing messages.

## Control Flow
Single-client tests call manager getters twice and verify factory creation counts stay at one, then close the manager and assert later calls fail with `IllegalStateException`. Transfer-manager tests verify async client creation happens when needed and is not duplicated when already present. Parallel tests start one creation in another thread, wait until factory invocation begins, call the same getter on the main thread, and verify the second call blocks and receives the same created instance. Failure tests assert failed creations are not cached: each subsequent getter invokes the factory again and produces a new exception message.

## State and Persistence Behavior
State is entirely in mocks, atomic counters/references, semaphores, and the manager's lazy references. No persistent state or real AWS clients are created.

## Dependencies and Integration Points
The class integrates `ClientManagerImpl`, `S3ClientFactory` parameters, `StubS3ClientFactory`, Hadoop functional helpers such as `LazyAtomicReference`, and AWS SDK client abstractions.

## Risks and Edge Cases
Parallel tests use sleeps (`FACTORY_DELAY`, `SECOND_THREAD_DELAY`) and semaphores; slow environments can affect timing but the ordering is mostly semaphore-controlled. Swallowed interrupts in `sleep()` are acceptable for tests but not production logic.

## Test Signals
Passing confirms client/transfer-manager creation is thread-safe, lazy, singleton per manager, closed-state guarded, and resilient to retry after factory exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestClientManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestCreateFileBuilder.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestCreateFileBuilder.java

## Purpose
`TestCreateFileBuilder` unit-tests S3A's `CreateFileBuilder` option parsing and callback handoff without using a real S3A filesystem.

## Important APIs, Types, and Functions
- `mkBuilder()` creates a builder over the local filesystem path `/` with custom callbacks.
- `BuilderCallbacks.createFileFromBuilder()` wraps a `BuilderOutputStream` in `FSDataOutputStream` and exposes parsed options.
- Tests cover `.create()`, `.append()`, `FS_S3A_CREATE_PERFORMANCE`, and `FS_S3A_CREATE_HEADER.*` options.
- `unwrap()` and `build()` extract the custom output stream for assertions.

## Control Flow
`testSimpleBuild()` verifies a basic create has no overwrite and no performance flag. `testAppendForbidden()` confirms append is unsupported. `testPerformanceSupport()` sets the S3A create performance option and checks it reaches callbacks. `testHeaderOptions()` supplies mandatory and optional header options and validates header map entries, including `If-None-Match`. `testIncompleteHeader()` sets the header prefix without a suffix and expects `IllegalArgumentException`.

## State and Persistence Behavior
No real files are written; the output stream's `write()` is a no-op. Parsed builder options are retained in `BuilderOutputStream` for assertions.

## Dependencies and Integration Points
The test bridges Hadoop's `FSDataOutputStreamBuilder` API, S3A-specific create options, custom header mapping, and callback-based file creation.

## Risks and Edge Cases
The test uses local FS only as a builder parent, so it does not cover S3 upload behavior. Header validation focuses on option parsing, not downstream request construction.

## Test Signals
Passing confirms create-builder flags, performance option, custom headers, and append rejection are correctly parsed before S3A output stream creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestCreateFileBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestErrorTranslation.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestErrorTranslation.java

## Purpose
`TestErrorTranslation` validates S3A error translation helpers that extract meaningful IOExceptions from nested AWS SDK exceptions and handle special client-side encryption exception wrapping.

## Important APIs, Types, and Functions
- Tests `ErrorTranslation.maybeExtractIOException()` and `maybeProcessEncryptionClientException()`.
- `sdkException()` builds nested `SdkClientException` instances.
- Covers `UnknownHostException`, `NoRouteToHostException`, `ConnectException`, `UncheckedIOException` wrapping `SocketTimeoutException`, and a custom IOException without a matching constructor.
- Tests AWS encryption client `S3EncryptionClientException` wrapping `NoSuchKeyException`.
- `testMultiObjectExceptionFilledIn()` verifies `MultiObjectDeleteException` works with AWS SDK retry condition machinery.

## Control Flow
Network exception tests build nested SDK exception chains and assert translation rethrows the matching IOException type with the top-level message and original SDK exception as cause where expected. Encryption tests verify S3 encryption client wrappers are unwrapped only for SDK exceptions and not arbitrary runtime exceptions. The multi-delete test constructs an empty `MultiObjectDeleteException`, builds a retry context, and confirms retry-on-error-code does not retry it.

## State and Persistence Behavior
All state is in-memory exception objects. No filesystem or AWS calls occur.

## Dependencies and Integration Points
The class integrates AWS SDK exception types, S3 encryption client exceptions, Hadoop `PathIOException`, S3A credential exception wrappers, and AWS SDK retry policy contexts.

## Risks and Edge Cases
Constructor availability affects exception recreation; the custom no-constructor IOE checks fallback behavior. Encryption client dependency behavior may shift with library updates.

## Test Signals
Passing confirms low-level connection failures and encryption-client S3 errors are surfaced as useful Hadoop/S3A exceptions without losing the original cause chain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestErrorTranslation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestHeaderProcessing.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestHeaderProcessing.java

## Purpose
`TestHeaderProcessing` unit-tests `HeaderProcessing`, which exposes S3 object metadata and selected user metadata as xattrs and copies metadata while excluding magic commit markers.

## Important APIs, Types, and Functions
- Uses a static `XAttrContextAccessor` implementing both `ContextAccessors` and `HeaderProcessing.HeaderProcessingCallbacks`.
- `setup()` creates a mock `StoreContext`, initializes a magic marker user header, and constructs `HeaderProcessing`.
- Tests `encodeBytes()`, `decodeBytes()`, `getXAttr()`, `getXAttrs()`, `listXAttrs()`, `extractXAttrLongValue()`, and `cloneObjectMetadata()`.
- Constants include `XA_MAGIC_MARKER`, `X_HEADER_MAGIC_MARKER`, `XA_CONTENT_LENGTH`, and `XA_LAST_MODIFIED`.

## Control Flow
The fake accessor returns metadata only for `MAGIC_KEY`, including content length, last-modified instant, and user metadata. Tests verify byte encode/decode, retrieval of magic marker length, object length, and last-modified date. Unknown paths raise `FileNotFoundException`. Filtered and empty xattr requests return the expected subsets. Metadata-copy testing adds a normal user header, clones metadata, and confirms the magic marker header is skipped while the normal header is preserved.

## State and Persistence Behavior
State is in the fake accessor's mutable header map, content length, and date. No real S3 or local files are used. The header map is modified between setup and individual tests.

## Dependencies and Integration Points
The file integrates mock store context creation, S3 SDK `HeadObjectResponse`/`HeadBucketResponse`, request-factory callbacks, audit no-op spans, and magic committer metadata constants.

## Risks and Edge Cases
The fake accessor only recognizes one path, so test coverage is targeted. It verifies filtering by xattr key rather than raw header name, a subtle behavior important to callers.

## Test Signals
Passing confirms xattr header encoding, metadata extraction, filtering, missing-path behavior, and magic marker exclusion during metadata copy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestHeaderProcessing.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestNetworkBinding.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestNetworkBinding.java

## Purpose
`TestNetworkBinding` verifies S3A region normalization in `NetworkBinding.fixBucketRegion()`.

## Important APIs, Types, and Functions
- Extends `AbstractHadoopTestBase`.
- Tests `fixBucketRegion(String)` for ordinary regions, legacy `US`, and `null`.
- `assertRegionFixup()` centralizes the assertion.

## Control Flow
The tests pass `us-east-1` and `us-west-2` through unchanged, map legacy `US` to `us-east-1`, and map `null` to `us-east-1`.

## State and Persistence Behavior
No state beyond constants; no persistence or network operations.

## Dependencies and Integration Points
This unit test protects region normalization used during S3 bucket endpoint/client binding.

## Risks and Edge Cases
Only a small normalization table is covered. Future partition-specific rules would need additional tests.

## Test Signals
Passing confirms default/legacy bucket region values normalize to the expected AWS region string.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestNetworkBinding.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestOpenFileSupport.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestOpenFileSupport.java

## Purpose
`TestOpenFileSupport` unit-tests `OpenFileSupport` and `S3AInputPolicy` option handling for Hadoop's `openFile()` builder path. It validates read policy selection, readahead/buffer options, file status validation, and split/length interpretation.

## Important APIs, Types, and Functions
- Static `PREPARE` is an `OpenFileSupport` configured with a server-side change-detection policy, default username, buffer size, async drain threshold, and sequential input policy.
- Tests use `OpenFileParameters` with mandatory keys and `Configuration` options.
- Covers open-file options `FS_OPTION_OPENFILE_READ_POLICY`, `INPUT_FADVISE`, `READAHEAD_RANGE`, buffer size, file length, split start, and split end.
- Uses `S3AFileStatus` and `S3ALocatedFileStatus` to validate accepted status types.

## Control Flow
Policy tests verify random/adaptive/unknown/list handling and map standard aliases such as Parquet, ORC, HBase, vector, CSV, JSON, and whole-file to S3A input policies. Option tests verify readahead and buffer sizes are propagated. Status tests accept matching file statuses, unwrap located statuses, reject directory statuses, and reject statuses with inconsistent filenames. Length and split tests show explicit file length creates synthetic status, while split end remains a hint unless length is supplied.

## State and Persistence Behavior
All state is in memory. Synthetic paths and statuses are created, but no filesystem operations run.

## Dependencies and Integration Points
The test integrates Hadoop open-file option keys, S3A input policy mapping, change detection policy, S3A file status types, and open-file parameter validation used by S3A's actual open path.

## Risks and Edge Cases
One expression uses `2L ^ 34`, which is bitwise XOR rather than exponentiation; the test intent says greater than int size but the value is only 32. The split-start assertion expects normalization to zero in the specific path tested.

## Test Signals
Passing confirms open-file builder options are parsed compatibly with Hadoop standard names and S3A-specific names, and invalid mandatory/status inputs are rejected early.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestOpenFileSupport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestRequestFactory.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestRequestFactory.java

## Purpose
`TestRequestFactory` validates that `RequestFactoryImpl` builds S3 SDK request builders with expected bucket, ACL, encryption, checksum, timeout, request-preparer, multipart limit, and SSE-C completion metadata behavior.

## Important APIs, Types, and Functions
- Uses `RequestFactoryImpl.builder()` to construct factories.
- `createFactoryObjects()` creates/analyzes abort, complete MPU, copy, delete, bulk delete, directory marker, get/head, list v1/v2, list multipart, initiate MPU, and PUT request builders.
- `AWSRequestAnalyzer` inspects each built request, while `CountRequests` verifies preparer invocation count.
- `assertApiTimeouts()` validates request override `apiCallAttemptTimeout` and `apiCallTimeout`.
- Parameterized checksum test covers `CRC32`, `CRC32_C`, `SHA1`, and `SHA256`.

## Control Flow
Encryption and preparer tests build factories with encryption secrets or request preparers and exercise the common request set. ACL tests assert canned ACL propagates to PUT, COPY, and initiate-MPU requests. Multipart tests validate upload-part request creation up to a part-count limit and reject part numbers beyond it. Timeout tests verify default and configured upload timeouts apply to PUT and upload-part requests. Checksum tests verify checksum algorithm propagation to copy, put, create-MPU, and upload-part requests. SSE-C completion test builds encryption secrets, derives base64 and MD5 values, and verifies complete-MPU includes customer encryption fields.

## State and Persistence Behavior
No S3 calls are made; state is built SDK request objects and local counters. `requestsAnalyzed` is an instance counter used to compare with preparer invocations.

## Dependencies and Integration Points
The test integrates request factory construction, AWS SDK S3 request builders, S3A encryption secrets, `PutObjectOptions`, multipart upload limits, checksum configuration, and audit/request analysis tooling.

## Risks and Edge Cases
`requestsAnalyzed` accumulates within each test instance; assumptions rely on JUnit creating fresh instances. The request set in `createFactoryObjects()` must be updated when RequestFactory gains required request types.

## Test Signals
Passing confirms S3A request construction consistently applies cross-cutting options across all major S3 operation builders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestRequestFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestS3AEncryption.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestS3AEncryption.java

## Purpose
`TestS3AEncryption` validates parsing and encoding of S3 encryption context configuration, including per-bucket override precedence and base64 JSON output.

## Important APIs, Types, and Functions
- Tests `S3AEncryption.getS3EncryptionContext()` and `getS3EncryptionContextBase64Encoded()`.
- Uses global `S3_ENCRYPTION_CONTEXT` and bucket-scoped `fs.s3a.bucket.<bucket>.encryption.context` configuration keys.
- Uses Jackson `ObjectMapper` to parse decoded JSON context into a map.

## Control Flow
The per-bucket test sets both global and bucket contexts and expects the bucket-specific value. The global test requests another bucket and expects the trimmed global value. The unset test expects an empty string. The base64 test encodes the global context, decodes it, parses JSON, and verifies key/value pairs.

## State and Persistence Behavior
All state is in in-memory `Configuration` and decoded strings. No S3 or file I/O occurs.

## Dependencies and Integration Points
The test integrates S3A encryption context parsing, Hadoop bucket-option precedence, Apache Commons Base64 decoding, and Jackson JSON parsing.

## Risks and Edge Cases
Context parsing assumes comma-separated `key=value` pairs. More complex values or escaping rules would need additional tests.

## Test Signals
Passing confirms encryption context lookup precedence, trimming, empty default behavior, and base64 JSON encoding for AWS request use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestS3AEncryption.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestS3AMultipartUploaderSupport.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestS3AMultipartUploaderSupport.java

## Purpose
`TestS3AMultipartUploaderSupport` unit-tests helper methods and payload classes used by S3A's multipart uploader part handles, including checksum capture.

## Important APIs, Types, and Functions
- Tests `S3AMultipartUploader.buildPartHandlePayload()`, `parsePartHandlePayload()`, and `extractChecksum()`.
- Uses `PartHandlePayload` accessors for path, upload ID, part number, ETag, length, checksum algorithm, and checksum.
- Builds AWS SDK `UploadPartResponse` instances with checksum fields.

## Control Flow
Round-trip tests serialize and parse payloads with normal length, length beyond integer range, and checksum metadata. Validation tests reject missing ETag, negative length, empty payload, corrupted header, missing checksum algorithm, and missing checksum. Checksum extraction tests verify CRC32, CRC32C, SHA1, SHA256, and no-checksum responses.

## State and Persistence Behavior
All state is in byte arrays and SDK response objects. No filesystem or network operations occur.

## Dependencies and Integration Points
The test protects multipart uploader handle compatibility, upload response checksum integration, and validation used when completing multipart uploads through Hadoop's multipart uploader API.

## Risks and Edge Cases
Payload header format is a compatibility contract; changing it can break persisted part handles. Checksum algorithm names returned by `extractChecksum()` must match downstream complete-MPU expectations.

## Test Signals
Passing confirms part handles round-trip safely, reject malformed inputs, handle large part lengths, and capture per-part checksum metadata when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestS3AMultipartUploaderSupport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestS3ExpressStorage.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestS3ExpressStorage.java

## Purpose
`TestS3ExpressStorage` validates S3 Express bucket detection based on bucket naming and endpoint classification.

## Important APIs, Types, and Functions
- Tests `S3ExpressStorage.isS3ExpressStore(bucket, endpoint)`.
- Uses an S3 Express-style bucket name `bucket--usw2-az2--x-s3`.
- Covers empty/default endpoint, AWS regional endpoints, China/Gov/FIPS/accesspoint-style endpoints, and a third-party endpoint.

## Control Flow
Default endpoint tests classify the S3 Express-style bucket as Express and a normal bucket as non-Express. AWS endpoint tests preserve Express classification across known AWS endpoint forms. Third-party endpoint test forces non-Express even with an Express-shaped bucket name.

## State and Persistence Behavior
No persistent state. All checks are pure string classification.

## Dependencies and Integration Points
This protects logic used when deciding S3 Express-specific behavior such as create-session handling and feature differences.

## Risks and Edge Cases
Endpoint pattern matching must keep up with AWS endpoint variants. Third-party endpoints are deliberately excluded to avoid misclassifying compatible stores.

## Test Signals
Passing confirms S3 Express detection is tied to both bucket naming and AWS endpoint recognition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestS3ExpressStorage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestSDKStreamDrainer.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestSDKStreamDrainer.java

## Purpose
`TestSDKStreamDrainer` validates `SDKStreamDrainer`, which either drains unread bytes from an AWS SDK input stream for connection reuse or aborts the stream when requested or on failure.

## Important APIs, Types, and Functions
- Tests `SDKStreamDrainer.applyRaisingException()`, `aborted()`, and `getDrained()`.
- Uses `InternalConstants.DRAIN_BUFFER_SIZE` to cover buffer-boundary cases.
- `FakeSDKInputStream` extends `InputStream` and implements AWS SDK `Abortable`, tracking capacity, bytes read, close state, and abort state.
- Uses `EMPTY_INPUT_STREAM_STATISTICS` for statistics dependency injection.

## Control Flow
Abort tests verify requested abort does not drain. Drain tests cover normal length, empty stream, single byte, exactly one buffer, multiple buffers, and stream underflow. Failure tests configure the fake stream to throw after a threshold: normal draining surfaces `IOException` and aborts, while explicit abort suppresses read exceptions because no read occurs. A sanity test confirms fake single-byte reads produce the expected count.

## State and Persistence Behavior
State is fully in the fake input stream and drainer instance. No external persistence or network access occurs.

## Dependencies and Integration Points
The test integrates S3A stream close/drain behavior with AWS SDK abortable streams and input stream statistics plumbing.

## Risks and Edge Cases
`FakeSDKInputStream.read(byte[],...)` swallows exceptions after partial reads to mimic stream behavior, so failure only surfaces when exception occurs before any byte in a buffer read. This is intentional but subtle.

## Test Signals
Passing confirms stream close handling drains remaining bytes when safe, aborts when requested, and aborts on read failures without hiding unexpected drain exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestSDKStreamDrainer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/logging/TestLogControllerFactory.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/logging/TestLogControllerFactory.java

## Purpose
`TestLogControllerFactory` validates dynamic log controller creation and log-level control for S3A logging utilities.

## Important APIs, Types, and Functions
- Tests `LogControllerFactory.createController()` and `createLog4JController()`.
- Uses `GenericTestUtils.LogCapturer` to capture this test class logger output.
- `LevelFailingLogController` extends `LogControl` and throws from `setLevel()` to test downgrade behavior.
- Constants define expected messages at DEBUG, INFO, WARN, ERROR, and FATAL labels.

## Control Flow
Setup creates a Log4J controller and starts log capture; teardown stops capture. Instantiation tests verify wrong-class and missing-class names return `null`. Exception tests verify direct `setLevel()` throws from the failing controller while wrapper `setLogLevel()` catches and returns false. Level tests set ALL/INFO/WARN/ERROR/OFF, emit messages, and assert captured output includes/excludes the expected messages.

## State and Persistence Behavior
Runtime state includes logger level changes and a log capturer. No file persistence is introduced, though logging backend state is mutated during tests.

## Dependencies and Integration Points
The file integrates S3A log-control abstraction, Log4J backend controller, reflection-based controller creation, SLF4J logging, and Hadoop generic test log capture.

## Risks and Edge Cases
Logger backend behavior can vary by test runtime. The test class name constant must match the actual logger target. Log level changes may interact with parallel tests if logger configuration is shared.

## Test Signals
Passing confirms controller discovery is defensive, set-level failures downgrade through the public wrapper, and runtime log levels filter messages as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/logging/TestLogControllerFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/streams/TestStreamFactories.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/streams/TestStreamFactories.java

## Purpose
`TestStreamFactories` unit-tests S3A input stream factory selection, requirement flags, legacy prefetch enablement, and custom factory loading/failure behavior.

## Important APIs, Types, and Functions
- Tests `StreamIntegration.factoryFromConfig()` using `INPUT_STREAM_TYPE`, `PREFETCH_ENABLED_KEY`, and `INPUT_STREAM_CUSTOM_FACTORY`.
- Verifies default/analytics, classic, prefetch, and custom factories.
- Uses `StreamFactoryRequirements` flags `RequiresFuturePool` and `ExpectUnauditedGetRequests`.
- Defines `CustomFactory`, `FactoryFailsToInstantiate`, and `Callbacks` stubs.

## Control Flow
Default tests assert empty/default stream type maps to `AnalyticsStreamFactory`. Classic and prefetch tests assert concrete factory classes, stream types, and requirement flags. The legacy prefetch-enabled flag overrides even an invalid stream type. Requirement tests construct flag sets directly and assert helper methods. Unknown stream type and custom-without-classname tests expect `IllegalArgumentException`. Custom factory load creates an instance by class name. Constructor failure verifies reflective instantiation wraps the underlying `UncheckedIOException`.

## State and Persistence Behavior
All state is in memory in `Configuration` and factory instances. Factories are initialized and bound with callbacks that throw for real client/statistic calls, ensuring no S3 access.

## Dependencies and Integration Points
The test covers S3A stream factory integration, prefetch stream dependency on future pools, custom extension points, reflection loading, vectored IO context requirements, and legacy config compatibility.

## Risks and Edge Cases
Reflection exceptions are deeply wrapped, and tests assert that wrapping shape. Custom factories returning `null` requirements/read streams are acceptable here because behavior under test is loading, not IO.

## Test Signals
Passing confirms stream-type configuration maps to the right factory classes and failure modes before S3A opens object streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/streams/TestStreamFactories.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/AbstractS3ACostTest.java -->
# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/AbstractS3ACostTest.java

## Purpose
`AbstractS3ACostTest` is a shared base class for S3A integration tests that assert operation-cost metrics. It wraps `AbstractS3ATestBase` with metric-diff validation, common file/dir creation helpers, and status probe helpers.

## Important APIs, Types, and Functions
- Extends `AbstractS3ATestBase`.
- `createConfiguration()` disables filesystem caching and removes create-performance overrides while preserving access point ARN bucket config.
- `setup()` initializes an `OperationCostValidator`, records whether bulk delete is enabled, selects the delete marker statistic, and sets the audit span source.
- `setupCostValidator()` registers all counter and duration `Statistic` values as tracked metrics.
- Helpers include `buildFile()`, `dir()`, `file()`, `create()`, `execRename()`, `directoriesInPath()`, `resetStatistics()`, `verifyMetrics()`, `verifyMetricsIntercepting()`, `interceptOperation()`, `verify()`, `verifyInnerGetFileStatus()`, `interceptGetFileStatusFNFE()`, `isDir()`, `isFile()`, `with()`, and `assertEmptyDirStatus()`.

## Control Flow
Subclasses call inherited helpers around S3A operations. Each helper starts or relies on an audit span, executes a closure, and asks `OperationCostValidator` to compare metric diffs with expected probes. File helpers create or close objects through standard FS APIs, while status helpers call S3A internals to assert HEAD/LIST costs. Setup chooses the correct delete statistic depending on multi-delete configuration.

## State and Persistence Behavior
State includes the `OperationCostValidator`, `isBulkDelete`, and `deleteMarkerStatistic`. Helpers create S3 files/directories when used by subclasses. Metric baselines are reset with `resetStatistics()`.

## Dependencies and Integration Points
The class integrates S3A statistics, operation cost models, audit spans, file status internals, Hadoop contract utilities, and S3A test utilities such as `innerGetFileStatus()` and `isBulkDeleteEnabled()`.

## Risks and Edge Cases
Because it tracks every counter/duration statistic, new metrics or changed cost profiles can break many subclasses. It removes create-performance overrides to keep costs deterministic, but subclasses can still alter configuration. Access point ARN preservation avoids breaking access-point test buckets.

## Test Signals
Passing subclasses using this base signal not just functional correctness but stable S3A request/metric cost envelopes for filesystem operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/AbstractS3ACostTest.java -->
