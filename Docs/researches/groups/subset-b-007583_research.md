# subset-b-007583 research

This grouped report covers Hadoop `hadoop-aws` S3A/S3N helper and integration-test files. Each section is bounded by the reconciliation markers required to split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3native/S3xLoginHelper.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3native/S3xLoginHelper.java

Purpose: private evolving utility shared by Hadoop S3 filesystem implementations for URI construction, URI canonicalization, and path ownership checks after URI-embedded login extraction was removed.

Important APIs/types/functions: `buildFSURI(URI)` validates non-null URI, scheme, and host and returns `scheme://host` without user info, path, query, or fragment. `canonicalizeUri(URI, int)` injects a positive default port when the URI lacks one. `checkPath(Configuration, URI, Path, int)` mirrors `FileSystem.checkPath` semantics while comparing `URI.getHost()` instead of authority, so embedded auth is ignored. Nested `Login` is a simple immutable user/password tuple with `hasLogin()`, equality, hash, and accessors.

Control flow: `checkPath()` returns immediately for relative paths. For matching schemes, it compares canonicalized host names case-insensitively; if the path host is absent, it may substitute `FileSystem.getDefaultUri(conf)` when schemes match. Any mismatch throws `IllegalArgumentException` with sanitized URI strings.

State and persistence: no persistent state; `Login` only holds immutable strings. The helper is stateless and thread-safe.

Dependencies and integration: depends on Hadoop `Configuration`, `FileSystem`, and `Path`, plus Apache Commons `StringUtils`. It is packaged under legacy `s3native` so S3A/S3N-style code can share it.

Risks: `buildFSURI()` intentionally drops ports, paths, query, and fragments; callers needing port retention must use `canonicalizeUri()`. `checkPath()` relies on host comparison, so URI forms with unusual authority parsing may behave differently from generic filesystem checks. Error text still includes `pathUri` and `fsUri`, but `buildFSURI()` avoids secrets in authority.

Test signals: this file contains no local tests; coverage is indirect through S3A/S3N filesystem URI/path qualification tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3native/S3xLoginHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/shellprofile.d/hadoop-s3guard.sh -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/shellprofile.d/hadoop-s3guard.sh

Purpose: shell profile fragment registering the `hadoop s3guard` subcommand when the Hadoop shell command dispatcher is running.

Important APIs/types/functions: defines `hadoop_subcommand_s3guard` once. When invoked, the function sets `HADOOP_CLASSNAME=org.apache.hadoop.fs.s3a.s3guard.S3GuardTool` and adds the `hadoop-aws` tool jar to the classpath through `hadoop_add_to_classpath_tools`.

Control flow: guarded by `declare -f hadoop_subcommand_s3guard` to avoid redefining the function. If `HADOOP_SHELL_EXECNAME` is `hadoop`, it calls `hadoop_add_subcommand "s3guard" client "S3 Commands"` before defining the implementation.

State and persistence: mutates shell process variables and command registry only; no filesystem state.

Dependencies and integration: depends on Hadoop shell helper functions provided by the surrounding shell framework. Integrates S3Guard tooling into the `hadoop` CLI.

Risks: assumes shell dispatcher helpers are already sourced. The command points at S3Guard, a feature area with changing support status, so downstream packaging must ensure the class still exists.

Test signals: no local tests; behavior is normally validated by shell command discovery or packaging tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/shellprofile.d/hadoop-s3guard.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractAnalyticsStreamVectoredRead.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractAnalyticsStreamVectoredRead.java

Purpose: S3A contract test proving Hadoop's base `PositionedReadable.readVectored()` behavior works when S3A uses the Analytics Accelerator stream.

Important APIs/types/functions: extends `AbstractContractVectoredReadTest`, parameterized by buffer type. `createConfiguration()` disables filesystem caching, removes Analytics Accelerator bucket overrides, configures coalescing/read-buffer/cache options, enables AAL, and skips unsupported encryption modes. Overrides `testNegativeOffsetRange()` to expect `IllegalArgumentException` and skips `testNullReleaseOperation()` for a known AAL null-release gap. Adds `testReadVectoredWithAALStatsCollection()`.

Control flow: the stats test builds four ranges, reads them through `FSDataInputStream.readVectored()`, validates data, then verifies AAL stream-open, vectored operation, incoming/combined range, HTTP GET, and cache-hit counters. It rereads the same ranges to assert no extra GETs.

State and persistence: creates S3 test objects inherited from the contract suite; modifies only per-test configuration.

Dependencies and integration: depends on AAL configuration keys under `ANALYTICS_ACCELERATOR_CONFIGURATION_PREFIX`, S3A test utilities, contract vector helpers, and IOStatistics counters.

Risks: sensitive to AAL implementation details, cache timeout, coalescing tolerance, and encryption/eTag behavior. Counter values can be brittle across AAL upgrades.

Test signals: integration and parameterized contract coverage for analytics-stream vectored read correctness and statistics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractAnalyticsStreamVectoredRead.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractBulkDelete.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractBulkDelete.java

Purpose: S3A implementation of the Hadoop bulk-delete contract, validating both multi-object delete and single-delete fallback behavior.

Important APIs/types/functions: extends `AbstractContractBulkDeleteTest`, parameterized by `enableMultiObjectDelete`. `createConfiguration()` disables FS caching, propagates bucket options, sets `BULK_DELETE_PAGE_SIZE=20`, and toggles `ENABLE_MULTI_DELETE`. Overrides `getExpectedPageSize()` and `validatePageSize()`. Adds tests for zero page-size preconditions, disabled multi-delete page size, directory inputs, parent directories, and rate limiting.

Control flow: tests create paths under contract `basePath`, call wrapped `bulkDelete_delete()`, and assert S3A-specific directory markers remain directories. Rate-limit test creates 20 files, deletes repeatedly, and checks `STORE_IO_RATE_LIMITED_DURATION.mean` grows after repeated calls.

State and persistence: mutates bucket objects during tests; uses fresh uncached filesystems for some configuration variants.

Dependencies and integration: integrates `BulkDelete`, S3A constants, `S3AUtils.propagateBucketOptions`, wrapped IO bulk-delete APIs, and store IOStatistics.

Risks: expected directory retention is S3A-specific and differs from real hierarchical filesystems. Rate-limit assertions depend on configured throttling and repeated operations. Disabled multi-delete mode must keep page size at 1.

Test signals: integration and parameterized coverage for page-size validation, directory non-deletion semantics, and rate-limit metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractBulkDelete.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractContentSummary.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractContentSummary.java

Purpose: S3A content-summary contract coverage with an extra S3 object-store directory-count assertion.

Important APIs/types/functions: extends `AbstractContractContentSummaryTest`; overrides `createContract()` and `getFileSystem()` to return `S3AContract`/`S3AFileSystem`. `testGetContentSummaryDir()` constructs nested directories and one file, then asserts summary directory/file counts.

Control flow: creates `a`, `a/b`, `a/b/a`, and `d/e/f`; touches `a/b/file`; calls `fs.getContentSummary(baseDir)` and expects 7 directories and 1 file.

State and persistence: writes directories and one marker/file under the method path.

Dependencies and integration: uses `S3AFileSystem.getContentSummary`, Hadoop `ContentSummary`, AssertJ, and `ContractTestUtils.touch`.

Risks: directory counts depend on how S3A synthesizes directories and marker objects from listings.

Test signals: integration coverage for content-summary traversal over explicit and implicit directory objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractContentSummary.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractCreate.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractCreate.java

Purpose: S3A file-create contract tests across normal create mode and create performance mode.

Important APIs/types/functions: extends `AbstractContractCreateTest`, parameterized by `createPerformance` and `expectContinue`. `createConfiguration()` sets performance flags, clears `CONNECTION_EXPECT_CONTINUE`, toggles 100-continue, skips performance mode unless enabled, and disables FS caching.

Control flow: overwrite/error tests invoke superclass behavior, but in create performance mode expected assertion failures are swallowed; if they pass unexpectedly, `failWithCreatePerformance()` fails the test.

State and persistence: creates and overwrites S3 paths through inherited contract tests; no static state.

Dependencies and integration: uses `S3AContract`, `S3ATestUtils.setPerformanceFlags`, performance-test enable flags, and S3A connection options.

Risks: deliberately changes expected behavior under create performance mode, where overwrite conflict detection may be relaxed for speed. Parameter set only covers `{false,false}` and `{true,true}` combinations.

Test signals: parameterized integration coverage of create semantics and expected-continue interaction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractCreate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractDelete.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractDelete.java

Purpose: binds Hadoop's generic delete contract suite to the S3A filesystem.

Important APIs/types/functions: extends `AbstractContractDeleteTest`; only overrides `createContract(Configuration)` to return `new S3AContract(conf)`.

Control flow: all delete scenarios are inherited from the contract framework.

State and persistence: inherited tests create and delete S3 objects under contract test paths.

Dependencies and integration: S3A contract binding and Hadoop contract-test framework.

Risks: because it has no local overrides, S3A-specific delete edge cases must be represented in the base contract or separate tests.

Test signals: integration coverage for standard Hadoop delete semantics on S3A.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractDelete.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractDistCp.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractDistCp.java

Purpose: validates DistCp behavior against S3A, especially direct-write behavior that avoids rename-heavy commit flows.

Important APIs/types/functions: extends `AbstractContractDistCpTest`; configures multipart size to `MULTIPART_MIN_SIZE` and `FAST_UPLOAD_BUFFER_DISK`; returns `shouldUseDirectWrite() == true`; uses scale-test timeout. `getRenameOperationCount()` reads `OP_RENAME` from storage statistics.

Control flow: `testDistCpWithIterator()` records rename count, runs superclass direct-write test, and asserts no rename increase. `testNonDirectWrite()` expects exactly two renames. Update/check-file skip delegates to superclass.

State and persistence: writes DistCp source/destination paths and reads FS storage statistics.

Dependencies and integration: integrates Hadoop DistCp contract tests, S3A multipart upload configuration, disk buffering, and storage statistics.

Risks: rename counts are implementation-sensitive. Disk buffering is chosen for scalability and may behave differently from array/bytebuffer buffering.

Test signals: integration coverage for DistCp direct-write/no-rename and non-direct-write rename behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractDistCp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractEtag.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractEtag.java

Purpose: binds the generic ETag contract suite to S3A.

Important APIs/types/functions: extends `AbstractContractEtagTest` and returns `S3AContract`.

Control flow: inherited tests verify ETag availability/behavior through file status and metadata paths defined by the contract layer.

State and persistence: inherited tests create S3 test objects.

Dependencies and integration: Hadoop ETag contract and S3A metadata implementation.

Risks: ETag semantics vary with multipart uploads and encryption; this class has no local skips for those modes.

Test signals: integration coverage for S3A ETag support through contract expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractEtag.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractGetFileStatus.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractGetFileStatus.java

Purpose: S3A binding for get-file-status contract tests, tuned to exercise multipage listings.

Important APIs/types/functions: extends `AbstractContractGetFileStatusTest`. `createConfiguration()` disables FS caching and sets `MAX_PAGING_KEYS=2`. `teardown()` logs filesystem details before superclass cleanup. Timeout returns `S3A_TEST_TIMEOUT`.

Control flow: inherited tests trigger status lookups under constrained list pagination so directory probes cover multi-page behavior.

State and persistence: inherited status tests create files/directories; test configuration uses uncached filesystems.

Dependencies and integration: S3A paging constants, S3A test utilities, and contract status suite.

Risks: low page size increases request count and can amplify failures under fault injection; timeout is extended accordingly.

Test signals: integration coverage for status resolution across paginated S3 listings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractGetFileStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractMkdir.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractMkdir.java

Purpose: S3A binding for generic mkdir contract tests in non-performance mode.

Important APIs/types/functions: extends `AbstractContractMkdirTest`; `createConfiguration()` calls `setPerformanceFlags(super.createConfiguration(), "")`; `createContract()` returns `S3AContract`.

Control flow: all test cases are inherited.

State and persistence: inherited tests create and delete directory marker objects.

Dependencies and integration: S3A contract and performance-flag utility.

Risks: no local S3A overrides; S3-specific mkdir edge cases are handled separately in the create-performance variant.

Test signals: integration coverage for standard mkdir semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractMkdir.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractMkdirWithCreatePerf.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractMkdirWithCreatePerf.java

Purpose: exercises mkdir behavior when S3A create/mkdir performance flags are enabled.

Important APIs/types/functions: extends `AbstractContractMkdirTest`; `createConfiguration()` disables FS caching and enables `"create,mkdir"` performance flags. `testMkdirOverParentFile()` asserts a child directory can be created under a path that is also a file in performance mode.

Control flow: the custom test creates a file at the method path, calls `fs.mkdirs(path/child-to-mkdir)`, verifies the parent file remains intact, validates child existence, then deletes the child.

State and persistence: writes one file and one child directory marker/object under the method path.

Dependencies and integration: uses `KEY_PERFORMANCE_TESTS_ENABLED`, `ContractTestUtils`, and S3A performance flags.

Risks: behavior intentionally violates strict hierarchical expectations; useful only when performance flags are enabled.

Test signals: integration coverage for performance-mode mkdir over file-prefix cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractMkdirWithCreatePerf.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractMultipartUploader.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractMultipartUploader.java

Purpose: S3A implementation of multipart uploader contract tests, gated as integration/scale tests.

Important APIs/types/functions: extends `AbstractContractMultipartUploaderTest`; `partSizeInBytes()` returns configured `partitionSize`; payload count is 3; concurrent uploads to the same path are supported; `finalizeConsumesUploadIdImmediately()` reflects `MULTIPART_COMMIT_CONSUMES_UPLOAD_ID`. Configuration disables checksum generation/algorithm and FS caching.

Control flow: setup requires scale tests, assumes multipart uploads, reads partition size and upload-ID consumption behavior, and logs checksum settings. Directory-in-way and reverse-order tests are skipped/assumed as S3-specific. Abort tolerates `FileNotFoundException` from third-party stores.

State and persistence: creates multipart uploads and objects in the test bucket; reads filesystem configuration for stateful behavior flags.

Dependencies and integration: multipart uploader contract, S3A checksum support, scale-test constants, and S3 Express assumptions.

Risks: scale tests are expensive and depend on store multipart support. Third-party stores may not expose aborted uploads consistently.

Test signals: scale integration coverage for multipart upload lifecycle, concurrency, finalize semantics, and abort tolerance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractMultipartUploader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractOpen.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractOpen.java

Purpose: S3A open-file contract coverage plus S3A-specific `openFile()` validation.

Important APIs/types/functions: extends `AbstractContractOpenTest`; `areZeroByteFilesEncrypted()` returns true because S3A reports zero-byte files as encrypted. Adds `testOpenFileApplyReadBadName()` and `testOpenFileDirectory()`.

Control flow: bad-name test creates a zero-byte file, constructs a mismatched `FileStatus` with a `gopher://` path, and expects `IllegalArgumentException` from `openFile(...).withFileStatus(st2).build()`. Directory test mutates a file status to directory and expects `FileNotFoundException`.

State and persistence: creates files under method paths.

Dependencies and integration: `FileSystem.openFile()` builder, Hadoop `FileStatus`, contract open suite, and S3A status validation.

Risks: synthetic `FileStatus` construction must match constructor semantics; path scheme mismatch is deliberately artificial.

Test signals: integration coverage for open builder status/path validation and directory rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractOpen.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractRename.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractRename.java

Purpose: S3A rename contract tests with object-store-specific expectations and copy-stat assertions.

Important APIs/types/functions: extends `AbstractContractRenameTest`; timeout is `S3A_TEST_TIMEOUT`. Overrides `testRenameDirIntoExistingDir()` to assert S3A returns false when renaming into a non-empty directory. Adds `testRenamePopulatesFileAncestors2()` and skips `testRenameFileUnderFileSubdir()`.

Control flow: the ancestor test creates nested source file data, captures `FILES_COPIED` and `FILES_COPIED_BYTES` metric diffs, renames `src` to `dest`, asserts one copied file and byte count, lists the tree, verifies contents, and validates ancestors moved.

State and persistence: creates source/destination directory trees and performs S3A rename, which is implemented as copy/delete.

Dependencies and integration: S3A metrics, contract rename utilities, and `S3ATestUtils.lsR`.

Risks: rename is non-atomic and copy-based; metrics are implementation-sensitive. Deep paths under files are allowed in S3A and skipped from strict contract expectations.

Test signals: integration coverage for rename rejection, ancestor materialization, data integrity, and copy counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractRename.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractRootDir.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractRootDir.java

Purpose: binds root-directory contract tests to S3A bucket roots.

Important APIs/types/functions: extends `AbstractContractRootDirectoryTest`; setup calls `maybeSkipRootTests(conf)` after superclass setup. `getFileSystem()` narrows to `S3AFileSystem`. `testRmNonEmptyRootDirNonRecursive()` is disabled because S3 returns false for non-recursive root removal.

Control flow: inherited tests run unless root tests are disabled by configuration; one incompatible inherited test is explicitly disabled.

State and persistence: root operations may touch bucket root and therefore are guarded.

Dependencies and integration: S3A root-test skip utility and contract root suite.

Risks: root tests can be destructive or expensive against real buckets, making skip configuration important.

Test signals: integration coverage for safe root-directory operations with one known S3 behavior disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractRootDir.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractSeek.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractSeek.java

Purpose: S3A seek contract tests across input policies and SSL channel modes, with explicit readahead-boundary regressions.

Important APIs/types/functions: extends `AbstractContractSeekTest`, parameterized with sequential/default/random policies and JSSE/OpenSSL modes. `createConfiguration()` removes bucket overrides for readahead, fadvise, and SSL mode, disables FS caching, sets readahead to 1024, input fadvise, and SSL channel mode. Adds tests around reads crossing exactly at readahead boundaries.

Control flow: constructor validates OpenSSL availability with JUnit assumptions. Test paths append the seek policy for uniqueness. Helper `readAtEndAndReturn()` forces stream policy transitions by seeking near EOF, reading, and seeking back. Boundary tests write a fixed 2048-byte dataset and assert bytes around readahead offsets using `readFully`, `read(byte[])`, and `readByte()`.

State and persistence: writes per-test datasets in S3; uncached FS is closed in teardown.

Dependencies and integration: S3A input policy, SSL socket factory modes, native OpenSSL loader, and contract seek utilities.

Risks: OpenSSL parameterization is environment-dependent. Boundary tests are sensitive to stream buffering and readahead implementation.

Test signals: integration coverage for seek correctness, policy propagation, SSL-mode compatibility, and HADOOP-16109-style readahead EOF regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractSeek.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractUnbuffer.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractUnbuffer.java

Purpose: binds generic unbuffer contract tests to S3A.

Important APIs/types/functions: extends `AbstractContractUnbufferTest`; returns `S3AContract`.

Control flow: inherited tests validate `FSDataInputStream.unbuffer()` behavior.

State and persistence: inherited tests create/read S3 objects.

Dependencies and integration: S3A contract and Hadoop stream unbuffer contract.

Risks: no local overrides; any S3A-specific stream cleanup semantics must be in the base contract or separate tests.

Test signals: integration coverage for S3A input stream unbuffer support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractUnbuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractVectoredRead.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractVectoredRead.java

Purpose: classic S3A input-stream contract and metrics tests for vectored reads, with Analytics Accelerator disabled.

Important APIs/types/functions: extends `AbstractContractVectoredReadTest`, parameterized by buffer type. `createConfiguration()` disables AAL. Tests cover 416/EOF handling, min-seek/max-merged-read configuration propagation/defaults, close/unbuffer cancellation, vectored-vs-normal read statistics, and multiple vectored reads. Helper `getTestFileSystemWithReadAheadDisabled()` creates an uncached FS with readahead 0 and small vector thresholds.

Control flow: EOF test opens with an artificially extended length and verifies futures fail with `EOFException`. Cancellation tests start vectored reads, close/unbuffer, expect `InterruptedIOException`, then verify subsequent reads can succeed. Statistics tests compare coalesced vectored reads against individual `readFully()` calls, checking input policy, object stream closure, HTTP GET counts, byte counters, and FS-level aggregation.

State and persistence: creates vector-read test files inherited from the contract suite; uses temporary uncached filesystems for config-specific checks.

Dependencies and integration: Hadoop `FileRange`, `FSDataInputStream.readVectored`, S3A input stream/policy, open-file options, IOStatistics, and contract vector helpers.

Risks: asynchronous future timing and cancellation can race. Exact counter values depend on range coalescing and stream implementation.

Test signals: extensive integration coverage for vectored read correctness, configuration propagation, cancellation, coalescing, and statistics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractVectoredRead.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AWrappedIO.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AWrappedIO.java

Purpose: validates S3A through Hadoop's wrapped IO operation helpers.

Important APIs/types/functions: extends `org.apache.hadoop.io.wrappedio.impl.TestWrappedIO`; returns `S3AContract`.

Control flow: all wrapped operation tests are inherited.

State and persistence: inherited tests create/read/delete S3 test paths.

Dependencies and integration: wrapped IO implementation layer and S3A contract.

Risks: local class has no S3A-specific assertions; failures indicate wrapped IO and S3A contract mismatch.

Test signals: integration coverage for generic wrapped IO APIs over S3A.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AWrappedIO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/S3AContract.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/S3AContract.java

Purpose: Hadoop filesystem contract binding for S3A tests.

Important APIs/types/functions: extends `AbstractBondedFSContract`. Constant `CONTRACT_XML` points to `contract/s3a.xml`. Constructors optionally add that resource after forcing S3A static initialization. `getScheme()` returns `s3a`; `getTestPath()` wraps the superclass path with `S3ATestUtils.createTestPath()`.

Control flow: construction calls `S3AFileSystem.initializeClass()` to load deprecated keys, then optionally adds contract XML. Test path generation is delegated to base contract and S3A test utility.

State and persistence: holds inherited contract configuration; no external persistence.

Dependencies and integration: central integration point between Hadoop contract-test framework and S3A configuration/test-path utilities.

Risks: adding `contract/s3a.xml` can reload configuration and interfere with tests that deliberately remove bucket overrides; the boolean constructor exists for those cases.

Test signals: not a test itself, but every S3A contract test depends on it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/S3AContract.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/AbstractS3AMockTest.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/AbstractS3AMockTest.java

Purpose: base class for S3A unit tests backed by a mock AWS SDK S3 client instead of a live bucket.

Important APIs/types/functions: defines `BUCKET`, reusable `NOT_FOUND` `AwsServiceException`, protected `fs`, `s3`, and `conf`. `createConfiguration()` installs `MockS3ClientFactory`, sets multipart size/probe/region, forces blocking stream drain, and tight retry settings. `setup()` initializes `S3AFileSystem` at `s3a://mock-bucket`, unsets encryption, and captures the mock S3 client. `teardown()` closes the FS.

Control flow: each test gets a fresh configuration and filesystem; mock client is retrieved from internals with a purpose string.

State and persistence: per-test in-memory/mock filesystem state; no real S3 persistence.

Dependencies and integration: AWS SDK `S3Client`, Hadoop `S3ClientFactory`, mock factory, S3A internals, and retry/multipart constants.

Risks: tests inheriting this base must account for mock behavior differing from real S3. Encryption is explicitly unset to avoid path IO errors.

Test signals: foundational setup for mock-based S3A tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/AbstractS3AMockTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/AbstractS3ATestBase.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/AbstractS3ATestBase.java

Purpose: main base class for S3A integration tests, extending Hadoop contract-test base with S3A setup, audit spans, IO statistics, and async error helpers.

Important APIs/types/functions: `FILESYSTEM_IOSTATS` aggregates FS statistics across tests. `setup()` loads local FS resources, initializes S3A class, calls superclass setup, sets span source, and resets thread IO statistics. `teardown()` aggregates FS stats and closes the FS. Helpers expose `S3AFileSystem`, `S3AInternals`, `getConfiguration()`, `span()`, `writeThenReadFile()`, and CSE skip logic. Static async holders provide `setFutureException`, `setFutureAse`, `maybeReThrowFutureException`, and `maybeReThrowFutureASE`.

Control flow: JUnit lifecycle wraps every test with setup/teardown and `@AfterAll` logs aggregate IO stats. Configuration is prepared by `S3ATestUtils.prepareTestConfiguration()`, and contract creation uses `new S3AContract(conf, false)` to avoid adding contract XML.

State and persistence: static IO stats and atomic error references persist across tests in the JVM; per-test filesystem state is closed after each test.

Dependencies and integration: contract test framework, S3A contract/internals, IOStatisticsContext, audit span APIs, and Hadoop test constants.

Risks: `maybeReThrowFutureException()` clears the assertion reference instead of the exception reference, which may be intentional legacy behavior or a bug-prone typo. Static state can leak between tests if not cleared. Closing FS in teardown assumes tests do not need it afterward.

Test signals: not a test itself; provides core integration-test lifecycle and diagnostics for many S3A tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/AbstractS3ATestBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/AbstractTestS3AEncryption.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/AbstractTestS3AEncryption.java

Purpose: abstract integration-test base for S3A server-side encryption methods.

Important APIs/types/functions: `createConfiguration()` skips when encryption tests are disabled, disables FS caching, and patches encryption settings. `patchConfigurationEncryptionSettings()` removes base/bucket encryption overrides and sets `S3_ENCRYPTION_ALGORITHM` from `getSSEAlgorithm()`. Tests cover setting propagation, file-size encryption, and encryption over rename. `assertEncrypted()` delegates to `EncryptionTestUtils.assertEncrypted()`.

Control flow: setup first requires encryption-enabled configuration, then calls superclass setup, but catches `AccessDeniedException` to skip buckets that enforce incompatible encryption. File-size validation writes, reads, asserts encryption, then removes the file.

State and persistence: writes encrypted objects in the test bucket and deletes file-size test objects.

Dependencies and integration: S3A encryption constants, `EncryptionSecrets`, `S3AUtils.getEncryptionAlgorithm/getS3EncryptionKey`, and metadata assertions.

Risks: depends on bucket policy and KMS/SSE configuration. The `SIZES` entry `2 ^ 12 - 1` is Java bitwise XOR, not exponentiation, producing a smaller value than the expression may suggest.

Test signals: abstract server-side encryption test suite used by concrete SSE variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/AbstractTestS3AEncryption.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/CustomKeyring.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/CustomKeyring.java

Purpose: test-only AWS S3 encryption client `Keyring` implementation for custom client-side encryption tests.

Important APIs/types/functions: implements `software.amazon.encryption.s3.materials.Keyring`. Constructor builds a `KmsClient` using configured CSE KMS region and temporary AWS credentials, then builds a `KmsKeyring` with the S3 encryption key. `onEncrypt()` and `onDecrypt()` delegate to the wrapped KMS keyring.

Control flow: construction resolves bucket name from config, creates KMS client, creates KMS keyring, then all encrypt/decrypt calls are direct delegation.

State and persistence: holds `KmsClient`, `Configuration`, and `KmsKeyring` fields; no explicit close method.

Dependencies and integration: AWS encryption SDK S3 materials, AWS KMS SDK, S3A temporary credentials provider, and encryption-key configuration.

Risks: `KmsClient` lifecycle is not closed here. Tests require valid KMS permissions and region/key configuration.

Test signals: used by `ITestS3AClientSideEncryptionCustom` to validate custom keyring wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/CustomKeyring.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/EncryptionTestUtils.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/EncryptionTestUtils.java

Purpose: static assertion helpers for S3A encryption tests.

Important APIs/types/functions: constants for AWS KMS, DSSE KMS, and SSE-C algorithm strings. `convertKeyToMd5(FileSystem)` decodes configured base64 customer key, MD5 hashes it, and base64 encodes the result. `assertEncrypted(S3AFileSystem, Path, S3AEncryptionMethods, String)` inspects `HeadObjectResponse` metadata for SSE-C, SSE-KMS, DSSE-KMS, or AES256. `validateEncryptionFileAttributes()` checks S3A xAttrs for encryption algorithm and optional KMS key id.

Control flow: `assertEncrypted()` switches on `S3AEncryptionMethods`, performing algorithm-specific metadata assertions.

State and persistence: stateless utility class.

Dependencies and integration: S3A internals metadata lookup, AWS SDK `HeadObjectResponse`, header-processing xAttr decoding, AssertJ, Commons Codec/Net Base64.

Risks: metadata expectations vary by store, encryption mode, and KMS key ARN form. SSE-C key MD5 requires the exact configured key.

Test signals: shared by server-side encryption tests and xAttr encryption checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/EncryptionTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestBlockingThreadPoolExecutorService.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestBlockingThreadPoolExecutorService.java

Purpose: validates Hadoop's blocking executor service behavior used by S3A-style bounded concurrency paths.

Important APIs/types/functions: static `BlockingThreadPoolExecutorService tpe`; `ensureCreated()` creates a pool with 4 active and 2 waiting tasks. `verifyQueueSize()` submits latched sleepers and asserts the next submit blocks. `ensureDestroyed()` shuts down gracefully, then forcefully if needed. Tests cover callable submission, runnable/queue behavior, shutdown/recreate, and `SemaphoredDelegatingExecutor`.

Control flow: blocking is measured using `StopWatch` against a 50 ms threshold while submitted tasks sleep for 100 ms. `@AfterAll` ensures cleanup.

State and persistence: static executor persists across tests until destroyed; no filesystem state.

Dependencies and integration: `BlockingThreadPoolExecutorService`, `SemaphoredDelegatingExecutor`, concurrency primitives, and JUnit timeout.

Risks: timing-based blocking assertion can be flaky on slow or oversubscribed machines. Static executor requires reliable cleanup.

Test signals: unit/integration-style concurrency coverage for executor capacity and shutdown semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestBlockingThreadPoolExecutorService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestDowngradeSyncable.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestDowngradeSyncable.java

Purpose: verifies `hflush()` and `hsync()` can be downgraded from unsupported failures to ignored operations while updating IO statistics.

Important APIs/types/functions: extends `AbstractS3ACostTest`; `createConfiguration()` removes bucket override for `DOWNGRADE_SYNCABLE_EXCEPTIONS` and sets it true. Tests use `FSDataOutputStream.hflush()`/`hsync()` and assert `OP_HFLUSH`/`OP_HSYNC` counters on stream and FS statistics.

Control flow: each test records initial FS counter, writes one byte, calls the sync method, checks stream counters, closes stream, then checks FS-level merged counter.

State and persistence: creates one output file per method path and updates IOStatistics.

Dependencies and integration: S3A output stream sync downgrade option, cost-test base, and statistics assertions.

Risks: relies on stats being merged only after close. If sync downgrade defaults change, configuration setup is critical.

Test signals: integration coverage for compatibility behavior with APIs expecting Syncable output streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestDowngradeSyncable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestEMRFSCompatibility.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestEMRFSCompatibility.java

Purpose: verifies S3A compatibility with legacy S3N/EMRFS folder marker objects.

Important APIs/types/functions: extends `AbstractS3ATestBase`; `testFileSystemOperationWithS3NFolderMarker()` creates a marker named with `S3N_FOLDER_SUFFIX`, lists the directory, renames the parent, and checks source/destination state.

Control flow: touches `src/subdir_$folder$` style marker, asserts listing `subdir` is empty, renames `src` to `dest`, then checks `dest/subdir` exists and `src` no longer exists.

State and persistence: creates a legacy folder marker and performs rename in the test bucket.

Dependencies and integration: S3A rename/list semantics and S3N folder marker constant.

Risks: marker compatibility is object-key-convention sensitive. Rename over markers depends on S3A marker filtering.

Test signals: integration coverage for legacy marker filtering and rename compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestEMRFSCompatibility.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestLocatedFileStatusFetcher.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestLocatedFileStatusFetcher.java

Purpose: validates `LocatedFileStatusFetcher` behavior and list-call statistics against S3A directory trees.

Important APIs/types/functions: extends `AbstractS3ATestBase`; defines path filters (`EVERYTHING`, `.txt`, hidden-file filter), expected exception text constants, and a shared `HELLO` payload. Setup creates an empty directory, empty file, nested directories, and three files. `assertListCount()` reads fetcher IOStatistics and asserts `OBJECT_LIST_REQUEST`.

Control flow: single-thread and four-thread tests configure `LIST_STATUS_NUM_THREADS`, run recursive fetcher scans, and assert returned file paths and expected four list calls. File scan test passes a file path directly and expects only that file with null fetcher IOStatistics.

State and persistence: builds a fixed tree under each method path.

Dependencies and integration: old MapReduce `LocatedFileStatusFetcher`, S3A statistics extraction, path filters, and S3A listStatus/listFiles.

Risks: exact list-call counts are implementation-sensitive. Parallel fetcher behavior depends on thread count and directory layout.

Test signals: integration coverage for successful recursive located-status scanning and statistics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestLocatedFileStatusFetcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AAWSCredentialsProvider.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AAWSCredentialsProvider.java

Purpose: integration tests for S3A AWS credentials provider class loading, constructor selection, remapping, anonymous access, and create-factory methods.

Important APIs/types/functions: `createConf(String/Class)` sets `AWS_CREDENTIALS_PROVIDER` and clears delegation token binding. `createFailingFS()` creates an S3A FS, lists root, and expects failure. Nested providers simulate unsupported constructor, bad credentials, and private constructor with static `create()`.

Control flow: tests intercept `InstantiationIOException` for missing/unsupported providers, `AccessDeniedException` for bad credentials, and successful anonymous access to a public test object. Remapping tests set `AWS_CREDENTIALS_PROVIDER_MAPPING` aliases.

State and persistence: instantiates short-lived S3A filesystems; anonymous test reads an external public dataset.

Dependencies and integration: AWS SDK credentials interfaces, S3A provider instantiation logic, delegation-token binding, public dataset utilities, and exception kinds.

Risks: bad-credential tests require predictable AWS rejection. Anonymous test depends on public dataset availability and endpoint configuration.

Test signals: integration coverage for credential provider reflection/remapping and runtime credential failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AAWSCredentialsProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AAnalyticsAcceleratorStreamReading.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AAnalyticsAcceleratorStreamReading.java

Purpose: integration suite for S3A's Analytics Accelerator input stream, including connector framework wiring, prefetch/cache behavior, parquet handling, invalid configuration, and request statistics.

Important APIs/types/functions: extends `AbstractS3ATestBase`; `createConfiguration()` enables AAL. Setup skips CSE and resolves an external test file. Tests cover whole-file policy, sequential prefetching, malformed parquet footer, multi-row-group parquet, invalid AAL config, random-seek cache behavior, and sequential streams sharing cache.

Control flow: tests open files with `openFile()` policies or normal `open()`, inspect wrapped `ObjectInputStream`, and assert stream type/policy plus IOStatistics counters for GET/HEAD, audit requests, bytes read, prefetched bytes, cache hits, and parquet footer failures. Some tests copy local parquet resources into S3 before reading.

State and persistence: reads public external data and writes local test resources or generated datasets to the test bucket. AAL cache behavior spans streams/factory lifetime until FS close.

Dependencies and integration: AWS Analytics Accelerator library, S3A connector stream framework, IOStatistics, audit statistics, local parquet resources, and public dataset utilities.

Risks: exact GET/prefetch/cache counters are highly sensitive to AAL version, file size, cache timeout, and public dataset contents. Tests skip CSE due to incompatibility.

Test signals: broad integration coverage for AAL stream selection, caching, prefetching, parquet optimizations, and stats propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AAnalyticsAcceleratorStreamReading.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ABlockOutputArray.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ABlockOutputArray.java

Purpose: tests S3A block output stream behavior when upload blocks are buffered in heap byte arrays.

Important APIs/types/functions: extends `AbstractS3ATestBase`; configures multipart threshold/size to minimum and `FAST_UPLOAD_BUFFER` to array. Static dataset is one 256 KiB block. Tests cover zero-byte/regular upload, write-after-close, block allocation cleanup, mark/reset on content providers, and abort behavior. `createFactory()` returns `ArrayBlockFactory`.

Control flow: setup skips if multipart uploads are disabled. `markAndResetDatablock()` creates a data block, writes the dataset, starts upload, opens provider stream, reads, marks, drains, resets, and checks bytes. Abort tests assert stream path capabilities, abort results, and absence of destination object.

State and persistence: creates small S3 objects or aborted streams; tracks block output statistics.

Dependencies and integration: `S3ABlockOutputStream`, `S3ADataBlocks`, upload content providers, stream capabilities, and abort assertion helpers.

Risks: abort semantics depend on stream state; multipart disabled stores skip tests. Mark/reset support is buffer-implementation-specific.

Test signals: integration coverage for array-buffered fast upload, block lifecycle, provider stream reset, and abort semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ABlockOutputArray.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ABlockOutputByteBuffer.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ABlockOutputByteBuffer.java

Purpose: reuses block output tests with byte-buffer-backed upload blocks.

Important APIs/types/functions: extends `ITestS3ABlockOutputArray`; overrides `getBlockOutputBufferName()` to `FAST_UPLOAD_BYTEBUFFER` and `createFactory()` to `ByteBufferBlockFactory`.

Control flow: inherits all upload, close, mark/reset, and abort tests from the array variant under bytebuffer configuration.

State and persistence: same as parent, with bytebuffer data block allocation.

Dependencies and integration: S3A bytebuffer block factory and inherited fast-upload tests.

Risks: inherited mark/reset expectations require bytebuffer content provider support.

Test signals: integration coverage for bytebuffer fast-upload buffer mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ABlockOutputByteBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ABlockOutputDisk.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ABlockOutputDisk.java

Purpose: reuses block output tests with disk-backed upload blocks.

Important APIs/types/functions: extends `ITestS3ABlockOutputArray`; overrides `getBlockOutputBufferName()` to `FAST_UPLOAD_BUFFER_DISK`. `createFactory()` uses an AssertJ assumption to skip mark/reset because disk streams do not support it.

Control flow: inherited tests run under disk buffering except mark/reset factory creation is skipped by assumption.

State and persistence: creates disk-buffered S3 upload test objects and local temporary block files through S3A internals.

Dependencies and integration: S3A disk fast-upload buffering and inherited block output suite.

Risks: local disk capacity/temp behavior can affect tests. Mark/reset is intentionally unsupported.

Test signals: integration coverage for disk-buffered fast upload and inherited abort/close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ABlockOutputDisk.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ABlocksize.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ABlocksize.java

Purpose: validates S3A block-size configuration as exposed through file status and listings.

Important APIs/types/functions: extends `AbstractS3ATestBase`; `testBlockSize()` checks default block size, updates `FS_S3A_BLOCK_SIZE`, creates a file, checks `getFileStatus()` and `listStatus()` block size. `testRootFileStatusHasBlocksize()` checks root status has nonnegative block size.

Control flow: after changing conf in the live FS, the test writes a file under a directory, then scans the listing to find and assert that file's block size.

State and persistence: writes one file and mutates FS configuration for the test.

Dependencies and integration: S3A block-size constant, `FileStatus`, and contract test utilities.

Risks: changing conf on an initialized FS assumes block-size lookup reads current config dynamically.

Test signals: integration coverage for block size propagation through status APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ABlocksize.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ABucketExistence.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ABucketExistence.java

Purpose: verifies S3A bucket existence probing modes and error behavior against a random non-existent bucket.

Important APIs/types/functions: extends `AbstractS3ATestBase`; creates `randomBucket` and `s3a://random-bucket-.../` URI. `createConfiguration()` skips unless the endpoint is AWS. `createConfigurationWithProbe(int)` disables FS caching, removes endpoint/region/probe overrides, sets probe value and region. `expectUnknownStore()` helpers intercept `UnknownStoreException`. Access-point tests configure ARN bucket options and `AWS_S3_ACCESSPOINT_REQUIRED`.

Control flow: probe 0 initializes FS without init-time failure, root exists/status succeeds, but object operations are expected to fail with unknown store except `isFile()` false. Probe 1/2 fail at FS creation; probe 3 allows root status. Negative probe expects `IllegalArgumentException`. Access point required path validates missing-ARN error then unknown store when ARN is present.

State and persistence: creates/uses a secondary `FileSystem fs` for nonexistent bucket and cleans it up after each test.

Dependencies and integration: S3A probing constants, network endpoint detection, access point ARN options, exception translation, and filesystem caching controls.

Risks: tests require AWS endpoint behavior and credentials sufficient to distinguish no-such-bucket from access denial; otherwise some paths skip.

Test signals: integration coverage for bucket probe modes, root special cases, access point validation, and unknown-store propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ABucketExistence.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ACannedACLs.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ACannedACLs.java

Purpose: validates S3A canned ACL configuration is applied to created and renamed objects.

Important APIs/types/functions: extends `AbstractS3ATestBase`; `createConfiguration()` skips unless ACL tests are enabled, disables FS caching, removes `CANNED_ACL`, sets it to `LOG_DELIVERY_WRITE`, and disables out-of-span audit rejection. `assertObjectHasLoggingGrant()` calls AWS SDK `getObjectAcl()` and checks for LogDelivery WRITE grant.

Control flow: test creates a directory, checks directory marker ACL, touches a file, checks file ACL, renames file, and checks renamed object ACL inside an audit span.

State and persistence: creates directory marker and file objects with canned ACLs, then renames a file.

Dependencies and integration: AWS SDK S3 ACL APIs, S3A store context/path-to-key mapping, audit spans, and ACL test enable flag.

Risks: requires ACL permissions and buckets that support ACLs. Directory marker key appends `/` manually, matching S3A marker conventions.

Test signals: integration coverage for canned ACL propagation on mkdir, create, and rename/copy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ACannedACLs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AChecksum.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AChecksum.java

Purpose: parameterized S3 checksum-generation/validation integration tests.

Important APIs/types/functions: extends `AbstractS3ATestBase`, parameterized for `SHA256`, `CRC32C`, `SHA1`, and `UNKNOWN_TO_SDK_VERSION`. `createConfiguration()` removes checksum/audit overrides, disables FS caching, sets `CHECKSUM_ALGORITHM`, enables `CHECKSUM_VALIDATION`, and derives SDK checksum algorithm. `assertChecksum()` issues a `HeadObject` with `ChecksumMode.ENABLED` and asserts algorithm-specific checksum fields.

Control flow: `testChecksum()` writes and reads files of several sizes, then checks object metadata checksum fields. Unknown algorithm expects checksum fields like SHA256 to be null.

State and persistence: writes S3 objects under method paths and reads HEAD metadata.

Dependencies and integration: AWS SDK checksum APIs, S3A checksum support, S3A request factory, bucket option propagation, and audit option.

Risks: requires IAM permission for checksum-enabled HEAD and store support for configured algorithms. `SIZES` includes `2 ^ 12 - 1`, a bitwise XOR expression rather than exponentiation.

Test signals: parameterized integration coverage for checksum generation and metadata visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AChecksum.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AClientSideEncryption.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AClientSideEncryption.java

Purpose: abstract integration suite for S3 client-side encryption (CSE) behaviors common to CSE-KMS and custom keyring variants.

Important APIs/types/functions: extends `AbstractS3ATestBase`; test sizes include 0, 1, 255, and 4095 bytes plus big/small file constants. Tests validate encrypted writes, rename, directory listing lengths, multipart CSE reads/writes, behavior when encrypted and unencrypted filesystems read opposite content, V1 compatibility reads, and size derivation from encrypted metadata headers. `createConfiguration()` forces multipart threshold/part size to `MULTIPART_MIN_SIZE`. Abstract hooks `maybeSkipTest()` and `assertEncrypted()` are implemented by subclasses.

Control flow: common tests call `maybeSkipTest()`, write files with CSE-enabled FS, validate content and subclass encryption markers, and compare file lengths through `listStatus`, `listFiles`, and `getFileStatus`. Compatibility tests create separate CSE-disabled/enabled filesystems and assert expected read failures or successes. Header-size test writes an object directly with `UNENCRYPTED_CONTENT_LENGTH` metadata and checks status length.

State and persistence: writes encrypted/unencrypted S3 objects, uses extra `S3AFileSystem` instances, and performs direct `putObjectDirect`.

Dependencies and integration: AWS S3 encryption client behavior, S3A request factory, CSE compatibility config, audit spans, IOStatistics gauge for CSE enabled, and contract utilities.

Risks: CSE tests require encryption configuration, KMS/keyring permissions, and scale-test enablement for big-file multipart. Mixed encrypted/unencrypted behavior is sensitive to SDK compatibility mode and instruction-file expectations.

Test signals: broad abstract integration coverage for CSE correctness, listings, multipart, compatibility, and metadata-derived lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AClientSideEncryption.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AClientSideEncryptionCustom.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AClientSideEncryptionCustom.java

Purpose: concrete CSE test suite for custom keyring encryption.

Important APIs/types/functions: extends `ITestS3AClientSideEncryption`; `createConfiguration()` disables FS caching and sets `S3_ENCRYPTION_CSE_CUSTOM_KEYRING_CLASS_NAME` to `CustomKeyring`. `maybeSkipTest()` requires encryption tests enabled and `CSE_CUSTOM` configured. `assertEncrypted()` inspects xAttrs for crypto key-wrap algorithm `kms+context`.

Control flow: inherits all CSE tests and validates encryption by decoding `header.x-amz-cek-alg` style xAttrs through `HeaderProcessing`.

State and persistence: same as parent; uses custom KMS keyring for encrypted writes.

Dependencies and integration: `CustomKeyring`, S3A CSE custom keyring config, AWS encryption headers, and xAttr decoding.

Risks: requires KMS permissions and correct custom keyring configuration. Encryption assertion only checks key-wrap algorithm, not every header.

Test signals: inherited CSE integration coverage with custom keyring-specific header validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AClientSideEncryptionCustom.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AClientSideEncryptionKms.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AClientSideEncryptionKms.java

Purpose: concrete CSE test suite for KMS-backed client-side encryption.

Important APIs/types/functions: extends `ITestS3AClientSideEncryption`; `maybeSkipTest()` requires encryption tests enabled and `CSE_KMS` configured. `assertEncrypted()` reads xAttrs and verifies key-wrap algorithm `kms+context` plus materials-description content algorithm `AES/GCM/NoPadding` while ensuring the KMS key ID is not exposed in the materials description.

Control flow: inherits common CSE tests and applies KMS-specific header checks after writes/renames.

State and persistence: same as parent; encrypted objects use configured KMS key.

Dependencies and integration: S3A CSE-KMS configuration, `S3AUtils.getS3EncryptionKey`, AWS encryption headers, and xAttr decoding.

Risks: requires KMS permissions and correctly configured encryption key. Header expectations can change with encryption SDK versions.

Test signals: inherited CSE integration coverage with KMS-specific header/materials assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AClientSideEncryptionKms.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AClosedFS.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AClosedFS.java

Purpose: validates operations against a closed S3A filesystem fail consistently and do not leak lifecycle threads.

Important APIs/types/functions: extends `AbstractS3ATestBase`; setup qualifies root and closes the FS immediately. Teardown is no-op because FS is already closed. Static `THREAD_SET` captures initial thread names and `@AfterAll` asserts final threads are a subset. Tests intercept `IOException` containing `E_FS_CLOSED` for status, listing, create, delete, and open operations; instrumentation test checks metric system absence and non-null IOStatistics.

Control flow: each test starts from a closed FS and invokes one operation expecting the closed-FS error.

State and persistence: closes the shared test FS; no S3 objects should be created after close.

Dependencies and integration: S3A closed-state checks, lifecycle thread utilities, instrumentation, and LambdaTestUtils.

Risks: thread subset assertion can be brittle when unrelated JVM threads appear. Teardown intentionally bypasses superclass cleanup.

Test signals: integration coverage for closed-filesystem guardrails and lifecycle cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AClosedFS.java -->
