# subset-b-007591 grouped research

This grouped report was produced from the listed source files. Each section preserves the source path and is delimited for deterministic reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ABlockOutputStreamInterruption.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ABlockOutputStreamInterruption.java


## Purpose
JUnit 5 parameterized S3A scale test that validates close(), abort(), and retry behavior when block output stream uploads are interrupted across disk, array, and bytebuffer upload buffers.


## Important APIs, Types, and Functions
ITestS3ABlockOutputStreamInterruption, params(), createScaleConfiguration(), setup()/teardown(), interruptMultipartUpload(), createFile(), expectCloseInterrupted(), and the nested InterruptingProgressListener. It configures FAST_UPLOAD_BUFFER, MULTIPART_SIZE, FAST_UPLOAD_ACTIVE_BLOCKS, retry limits, directory-upload purge, and SdkFaultInjector auditing.


## Control Flow
Each test creates an S3A output stream with a progress listener, writes enough data to drive either multipart upload, magic commit upload, or simple PUT, then triggers thread interruption, abort(), or injected failures from progress callbacks. The assertions check listener event counts, InterruptedIOException propagation, multipart abort statistics, bytes transferred bounds, and idempotent second close/abort behavior.


## State and Persistence Behavior
Persistent state is S3 object and multipart-upload state: partial uploads must be aborted and completed objects must not appear after abort. Test instance state is limited to buffer type and active-block count, while SdkFaultInjector uses static evaluator/action counters reset before and after each test.


## Dependencies and Integration Points
Depends on S3AFileSystem create builders, FSDataOutputStream Abortable support, ProgressListenerEvent callbacks, magic commit path naming, IOStatistics counters, and AWS SDK execution interception through SdkFaultInjector.


## Risks and Test Signals
Racy by design because progress callbacks fire from upload/control paths; strict assertions around failed part counts are deliberately relaxed. Cleanup relies on fault injector reset and directory purge to avoid leaked multipart uploads. Failures signal regressions in interruption translation, multipart abort cleanup, or stream idempotency.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ABlockOutputStreamInterruption.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AConcurrentOps.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AConcurrentOps.java


## Purpose
Scale test for concurrent rename/copy/delete operations sharing one S3AFileSystem and for transfer-thread pool cooldown after active work.


## Important APIs, Types, and Functions
ITestS3AConcurrentOps, createScaleConfiguration(), setup(), getNormalFileSystem(), parallelRenames(), testParallelRename(), and testThreadPoolCoolDown(). It tunes MULTIPART_SIZE to the minimum and uses MAX_THREADS/MAX_TOTAL_TASKS to force tiny executor resources.


## Control Flow
The test creates 10 source files through an auxiliary FS, each with repeated 1 MiB blocks, then submits concurrent fs.rename() tasks on another S3AFileSystem. It waits for all futures, validates target existence and source absence, and separately counts live s3a-transfer threads before and after keepalive expiry.


## State and Persistence Behavior
State lives in S3 paths under methodPath(); teardown deletes the test root through the auxiliary FS. The tiny-thread-pool variant intentionally stresses bounded task queues and transfer pools to catch deadlock-prone scheduling.


## Dependencies and Integration Points
Depends on S3AFileSystem, SubjectInheritingThread, ContractTestUtils datasets/timers, executor services, multipart copy support, and default transfer keepalive configuration.


## Risks and Test Signals
The test is sensitive to S3 latency, configured multipart support, and JVM thread naming. It is a strong signal for deadlocks, copy executor starvation, and transfer-pool resource leaks after rename workloads.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AConcurrentOps.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ACreatePerformance.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ACreatePerformance.java


## Purpose
Single-thread create() scale/performance test for deeply nested S3A paths.


## Important APIs, Types, and Functions
ITestS3ACreatePerformance with setup(), testDeepSequentialCreate(), and getPathIteration(). It uses S3AScaleTestBase operation counts and a fixed PATH_DEPTH of 10.


## Control Flow
Before each run it records the base path and depth, then creates getOperationCount() one-byte files below uniquely generated nested directories. A NanoTimer reports total and per-create timing.


## State and Persistence Behavior
The test persists many small objects under getTestPath(); each object name embeds the iteration number to avoid overwrite collisions. No custom cleanup state is held beyond basePath/basePathDepth.


## Dependencies and Integration Points
Depends on S3AFileSystem.create(), Path depth semantics, ContractTestUtils.NanoTimer, and scale-test configuration keys.


## Risks and Test Signals
Risks are cost and runtime from many small PUTs and directory marker side effects. Test signals are performance timing plus assertion that the requested path depth is actually deeper than the configured base path.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ACreatePerformance.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ADeleteFilesOneByOne.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ADeleteFilesOneByOne.java


## Purpose
Variant of the bulk rename/delete scale test that disables S3A multi-object delete.


## Important APIs, Types, and Functions
ITestS3ADeleteFilesOneByOne overrides createScaleConfiguration() and sets Constants.ENABLE_MULTI_DELETE to false after inheriting ITestS3ADeleteManyFiles configuration.


## Control Flow
Control flow is entirely inherited: create many files, rename a directory tree, audit destination/source, then delete recursively. This subclass forces deletion to proceed object-by-object rather than via multi-delete pages.


## State and Persistence Behavior
Persistent state is the same S3 test tree as the parent class, but delete behavior changes from batched DeleteObjects calls to individual object deletes.


## Dependencies and Integration Points
Depends on ITestS3ADeleteManyFiles, S3A Constants.ENABLE_MULTI_DELETE, and the parent’s S3ATestUtils setup.


## Risks and Test Signals
Useful for detecting regressions hidden by bulk delete. It is slower and more request-heavy than the parent, so timeout/cost sensitivity is higher.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ADeleteFilesOneByOne.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ADeleteManyFiles.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ADeleteManyFiles.java


## Purpose
Scale test for renaming and recursively deleting a directory containing many files with a deliberately small bulk-delete page size.


## Important APIs, Types, and Functions
ITestS3ADeleteManyFiles, DELETE_PAGE_SIZE, createScaleConfiguration(), and testBulkRenameAndDelete(). It disables filesystem caching, removes bucket overrides, disables experimental AWS throttling, and sets BULK_DELETE_PAGE_SIZE to 50.


## Control Flow
The test creates count files under src, measures rename(srcDir, finalDir), verifies recursive source emptiness and destination file count, then measures delete(finalDir, recursive=true) and verifies the final parent is empty.


## State and Persistence Behavior
S3 object state moves from srcParent/src to finalParent/final and then to deleted. The test audits listStatus/listFiles counts and specific first/middle/last filenames to catch partial operations.


## Dependencies and Integration Points
Depends on S3AFileSystem, S3ATestUtils.createFiles/lsR, ContractTestUtils rm/timers, filenameOfIndex(), and AssertJ assertions.


## Risks and Test Signals
Primary risks are scale configuration too high for MAX_THREADS, S3 throttling, and delete pagination regressions. Strong test signals include exact object counts, path existence checks, and rename/delete throughput logs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ADeleteManyFiles.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ADirectoryPerformance.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ADirectoryPerformance.java


## Purpose
Scale/performance coverage for S3A directory listing, recursive scans, content summaries, paged listings, and repeated getFileStatus calls.


## Important APIs, Types, and Functions
ITestS3ADirectoryPerformance exposes testListOperations(), testMultiPagesListingPerformanceAndCorrectness(), getConfigurationWithConfiguredBatchSize(), sleep(), stat timing tests, and timeToStatPath(). It uses MetricDiff counters and WriteOperationHelper for direct PUTs.


## Control Flow
The first test creates a synthetic directory tree and compares explicit treewalk, listFiles(recursive=true), and getContentSummary results while validating expected object-list request counts. The paged-listing test uploads 1000 zero-byte objects in parallel, exercises listFiles/listStatus/listStatusIterator/listLocatedStatus with MAX_PAGING_KEYS=10, and checks continuation counters. Stat tests repeat getFileStatus over file, empty/non-empty directory, and root paths.


## State and Persistence Behavior
Persistent S3 state consists of generated directories/files under method paths and is deleted in finally blocks. Per-iterator IOStatistics are inspected after traversal; filesystem statistics are logged before closing the uncached FS.


## Dependencies and Integration Points
Depends on S3A internals including RequestFactory, WriteOperationHelper, S3ADataBlocks, audit spans, RemoteIterators, IOStatistics retrieval, object list/continue counters, and ContractTestUtils tree builders.


## Risks and Test Signals
Expensive and latency-sensitive due to 1000 PUTs and intentional per-file sleeps. It detects listing pagination bugs, incorrect directory marker/content-summary semantics, missing iterator statistics, and inefficient extra LIST/HEAD requests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ADirectoryPerformance.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesArrayBlocks.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesArrayBlocks.java


## Purpose
Concrete huge-file scale-test variant using in-memory array blocks for fast upload buffering.


## Important APIs, Types, and Functions
ITestS3AHugeFilesArrayBlocks overrides getBlockOutputBufferName() to return FAST_UPLOAD_BUFFER_ARRAY and requireMultipartUploads() to require MPU availability.


## Control Flow
All create/read/rename/delete control flow is inherited from AbstractSTestS3AHugeFiles; this class supplies the buffering mode and skip condition.


## State and Persistence Behavior
State is the inherited huge S3 object lifecycle plus array-backed upload block memory state. No additional fields are introduced.


## Dependencies and Integration Points
Depends on AbstractSTestS3AHugeFiles and S3A Constants.FAST_UPLOAD_BUFFER_ARRAY.


## Risks and Test Signals
Risk is high heap pressure for huge files; test signal isolates array-buffer multipart behavior from disk and bytebuffer variants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesArrayBlocks.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesByteBufferBlocks.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesByteBufferBlocks.java


## Purpose
Concrete huge-file scale-test variant using bytebuffer upload blocks and directory-level rename.


## Important APIs, Types, and Functions
ITestS3AHugeFilesByteBufferBlocks overrides getBlockOutputBufferName(), requireMultipartUploads(), and renameFile(Path, Path).


## Control Flow
Inherited huge-file tests use bytebuffer buffering. The rename hook deletes/mkdirs the destination parent, then renames the source parent directory to the destination parent and asserts success.


## State and Persistence Behavior
Persistent state is the huge-file object plus its parent directory marker/tree; renaming at parent level verifies directory rename semantics, not only single-object copy/delete.


## Dependencies and Integration Points
Depends on AbstractSTestS3AHugeFiles, S3AFileSystem.rename/delete/mkdirs, FAST_UPLOAD_BYTEBUFFER, and AssertJ.


## Risks and Test Signals
Risks include direct/off-heap memory pressure and parent-directory rename side effects. Test signals catch directory rename regressions for huge multipart objects.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesByteBufferBlocks.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesDiskBlocks.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesDiskBlocks.java


## Purpose
Concrete huge-file scale-test variant using disk-backed upload blocks and direct buffers for vector IO.


## Important APIs, Types, and Functions
ITestS3AHugeFilesDiskBlocks overrides getBlockOutputBufferName() to FAST_UPLOAD_BUFFER_DISK and isDirectVectorBuffer() to true.


## Control Flow
The inherited huge-file workflow creates, verifies, reads, renames, and deletes a large object while this subclass changes upload buffering and vector-read buffer allocation.


## State and Persistence Behavior
State includes temporary disk block files managed by S3A upload buffering and persisted S3 huge-file objects. The class itself has no mutable fields.


## Dependencies and Integration Points
Depends on AbstractSTestS3AHugeFiles and S3A Constants.FAST_UPLOAD_BUFFER_DISK.


## Risks and Test Signals
Risks are local disk pressure and cleanup of temporary upload blocks. Test signals isolate disk-buffer behavior and direct vector buffer compatibility.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesDiskBlocks.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesEncryption.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesEncryption.java


## Purpose
Huge-file scale test for SSE-KMS or DSSE-KMS encryption settings.


## Important APIs, Types, and Functions
ITestS3AHugeFilesEncryption overrides setup(), getBlockOutputBufferName(), isEncrypted(), and assertEncrypted(). It uses EncryptionTestUtils, getEncryptionAlgorithm(), and getS3EncryptionKey().


## Control Flow
setup() skips unless configured for SSE_KMS or DSSE_KMS. Inherited huge-file operations run with array buffering, then encryption assertions fetch the configured bucket key/algorithm and validate object metadata.


## State and Persistence Behavior
State is S3 encrypted object metadata and configured KMS key binding. The class reads fresh Configuration instances to inspect bucket encryption settings rather than storing them.


## Dependencies and Integration Points
Depends on AbstractSTestS3AHugeFiles, S3A encryption utilities, bucket-specific config, and EncryptionTestUtils metadata checks.


## Risks and Test Signals
Risks include mismatched bucket KMS policy, missing encryption key, or incompatible mandatory bucket encryption. Test signals validate that large multipart objects preserve expected encryption metadata.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesEncryption.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesNoMultipart.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesNoMultipart.java


## Purpose
Huge-file variant that disables multipart uploads and verifies single-PUT behavior and disabled multipart copy.


## Important APIs, Types, and Functions
ITestS3AHugeFilesNoMultipart overrides getBlockOutputBufferName(), expectMultipartUpload(), createScaleConfiguration(), and test_030_postCreationAssertions(). It configures CONNECTION_EXPECT_CONTINUE, IO_CHUNK_BUFFER_SIZE, MIN_MULTIPART_THRESHOLD, MULTIPART_SIZE, MULTIPART_UPLOADS_ENABLED, PART_UPLOAD_TIMEOUT, and REQUEST_TIMEOUT.


## Control Flow
Inherited huge-file workflow runs with disk buffering but no multipart upload. Post-creation assertions additionally confirm S3A internals report multipart copy disabled.


## State and Persistence Behavior
Persistent state is a single PUT-created large object, not MPU parts. Configuration state is deliberately stripped of base/bucket overrides to prevent accidental multipart behavior.


## Dependencies and Integration Points
Depends on AbstractSTestS3AHugeFiles, S3A internals, and S3AConstants around multipart and request timeouts.


## Risks and Test Signals
Risk is very long single PUT runtime and provider limits. The class is important for fail-fast validation when transfer manager would otherwise assume multipart thresholds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesNoMultipart.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesSSECDiskBlocks.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesSSECDiskBlocks.java


## Purpose
Huge-file disk-buffer variant with SSE-C client-provided encryption enabled.


## Important APIs, Types, and Functions
ITestS3AHugeFilesSSECDiskBlocks overrides setup() and createScaleConfiguration(), sets S3_ENCRYPTION_ALGORITHM to SSE_C, and sets a fixed base64 SSE-C key.


## Control Flow
setup() runs the parent setup but skips if the bucket rejects SSE-C or encryption tests are disabled. The inherited disk-buffer huge-file suite then runs under SSE-C configuration.


## State and Persistence Behavior
State is encrypted S3 object metadata and local disk upload buffering. The fixed test key is configuration-only and not persisted by this class.


## Dependencies and Integration Points
Depends on ITestS3AHugeFilesDiskBlocks, S3AEncryptionMethods.SSE_C, skipIfEncryptionTestsDisabled(), and bucket encryption policies.


## Risks and Test Signals
Risks include 403 AccessDenied on mandatory-encryption buckets and provider support gaps. Test signals validate huge multipart operations with SSE-C and direct vector buffers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesSSECDiskBlocks.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesStorageClass.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesStorageClass.java


## Purpose
Huge-file test that verifies configured S3 storage class is applied on create and rename/copy.


## Important APIs, Types, and Functions
ITestS3AHugeFilesStorageClass overrides createScaleConfiguration(), getBlockOutputBufferName(), selected inherited tests, assertStorageClass(), and skipQuietly(). It configures STORAGE_CLASS_REDUCED_REDUNDANCY.


## Control Flow
The class runs create/post-create storage-class assertions, skips read/encryption-only inherited checks, and overrides rename to copy the huge object then validate size and storage class at destination.


## State and Persistence Behavior
Persistent state is object metadata storageClassAsString() on the huge file and renamed destination. Filesystem caching is disabled so configuration changes are respected.


## Dependencies and Integration Points
Depends on AbstractSTestS3AHugeFiles, S3AInternals.getObjectMetadata(), ContractTestUtils timers/bandwidth, and storage-class test skip helpers.


## Risks and Test Signals
Risks include provider support for Reduced Redundancy and metadata differences after copy. Signals catch storage-class loss across multipart upload and rename/copy.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesStorageClass.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AInputStreamPerformance.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AInputStreamPerformance.java


## Purpose
Comprehensive scale/performance test for classic S3A input stream read policies, seeking, readahead, decompression, random IO, and stream statistics.


## Important APIs, Types, and Functions
ITestS3AInputStreamPerformance defines openFS(), cleanup(), openTestFile()/openDataFile(), assertOpenOperationCount(), testTimeToOpenAndReadWholeFileBlocks(), bandwidth(), lazy seek/readahead tests, decompression, executeSeekReadSequence(), executeRandomIO(), getS3aStream(), and testRandomReadOverBuffer().


## Control Flow
Setup binds a new S3AFileSystem to a configured public gzipped test object, using classic streams and disabled prefetch. Tests read full files in 1 MiB blocks, verify lazy seeks do not open streams, reject negative readahead, exercise normal/sequential/random policies, decompress through LineReader, and perform positioned reads spanning readahead ranges. IOStatistics are logged and aggregated after each test.


## State and Persistence Behavior
State includes the external test object status, a per-test FSDataInputStream, S3AInputStreamStatistics, aggregate static IOStatisticsSnapshot, and one local test object for buffer-boundary reads. No production state is persisted except temporary test paths.


## Dependencies and Integration Points
Depends on PublicDatasetTestUtils, S3AInputStream internals, FutureDataInputStreamBuilder options, CompressionCodecFactory, LineReader, stream statistic names, IOStatistics assertions, and public S3 datasets.


## Risks and Test Signals
Risks are external dataset availability, client-side encryption incompatibility, network variability, and exact statistics changes. Strong signals include open-operation counts, abort/policy-change counters, HTTP GET timing samples, and byte-for-byte buffer checks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AInputStreamPerformance.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AMultipartUploadSizeLimits.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AMultipartUploadSizeLimits.java


## Purpose
Scale test for multipart upload part-count limits, commit upload failure cleanup, and Abortable output-stream behavior.


## Important APIs, Types, and Functions
ITestS3AMultipartUploadSizeLimits overrides createScaleConfiguration() to set MULTIPART_SIZE=5 MiB and UPLOAD_PART_COUNT_LIMIT=2, then defines tests for two-part upload, over-limit failure, commit-limit failure, abort after upload, abort while overwriting, and verifyStreamWasAborted().


## Control Flow
Valid two-part uploads should complete. Larger writes and committer uploads are expected to raise PathIOException and leave no destination. Abort tests write multipart data then call stream.abort(), assert no object materializes or previous contents survive, and verify stream/filesystem IOStatistics counters.


## State and Persistence Behavior
Persistent S3 state is the target object path, which must either not exist after failed/aborted uploads or retain original contents after overwrite abort. Temporary local commit files are created for CommitOperations upload tests.


## Dependencies and Integration Points
Depends on S3A commit operations, FSDataOutputStream Abortable, ExtraAssertions abort helpers, S3AInstrumentation counters, IOStatistics assertions, and multipart support assumptions.


## Risks and Test Signals
Risks include leaked MPU parts or overwriting existing data after abort. Test signals include PathIOException interception, path absence/content verification, committer abort counters, and stream abort/multipart abort statistics.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AMultipartUploadSizeLimits.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/NanoTimerStats.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/NanoTimerStats.java


## Purpose
Small mutable utility that aggregates ContractTestUtils.NanoTimer durations using Welford's online variance algorithm.


## Important APIs, Types, and Functions
NanoTimerStats constructors, add(NanoTimer), add(long), reset(), getters, getVariance(), getDeviation(), toSeconds(), and toString(). It tracks operation, count, sum, min, max, mean, and m2.


## Control Flow
Callers add elapsed nanosecond values; each sample updates count/sum/mean/variance state online. reset() clears all values and toString() formats totals and descriptive statistics in seconds.


## State and Persistence Behavior
All state is in instance fields and is explicitly not synchronized. The copy constructor snapshots values from another instance.


## Dependencies and Integration Points
Depends only on ContractTestUtils.NanoTimer and standard math/formatting.


## Risks and Test Signals
Risks are non-thread-safe use and edge cases: getVariance() returns NaN for zero samples but divides by count-1 for count=1, yielding NaN through IEEE arithmetic. Test signal is primarily consumers' timing output, not direct assertions here.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/NanoTimerStats.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/S3AScaleTestBase.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/S3AScaleTestBase.java


## Purpose
Common base class for S3A scale tests that centralizes configuration creation, scale enablement, operation counts, timeouts, and gauge lookup.


## Important APIs, Types, and Functions
S3AScaleTestBase defines _1KB/_1MB, setup(), demandCreateConfiguration(), final createConfiguration(), overridable createScaleConfiguration(), getTestPath(), getOperationCount(), getTestTimeoutSeconds(), getTestTimeoutMillis(), gaugeValue(), isEnabled(), and isParallelExecution().


## Control Flow
Configuration is lazily created before normal JUnit setup so timeout calculation can read scale properties early. setup() initializes a shared test path, logs operation count, and skips unless scale tests are enabled. Subclasses customize only createScaleConfiguration().


## State and Persistence Behavior
Instance state is the cached Configuration, enabled flag, and testPath. The design intentionally guards against subclasses overriding createConfiguration() and breaking early timeout/config initialization.


## Dependencies and Integration Points
Depends on AbstractS3ATestBase, S3ATestUtils property helpers/assume(), IOStatistics gauge lookup, S3ATestConstants, and ScaleTest tagging.


## Risks and Test Signals
Risks are Java constructor/override ordering and stale configuration if subclasses expect repeated creation. Test signals are indirect: all scale tests rely on correct enablement, timeout, and operation-count behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/S3AScaleTestBase.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/select/ITestSelectUnsupported.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/select/ITestSelectUnsupported.java


## Purpose
Integration test proving removed S3 Select functionality is consistently reported unsupported.


## Important APIs, Types, and Functions
ITestSelectUnsupported defines STATEMENT and tests openFile .must/.opt behavior, path capability absence, and S3GuardTool select command failure.


## Control Flow
The .must(SELECT_SQL) path must raise UnsupportedOperationException with SELECT_UNSUPPORTED; .opt(SELECT_SQL) is ignored after touching a file. hasPathCapability must return false, and the CLI path is invoked with system exits disabled to inspect exit code.


## State and Persistence Behavior
Persistent state is a touched methodPath object for the optional-open test. CLI state is limited to ExitUtil system-exit interception.


## Dependencies and Integration Points
Depends on AbstractS3ATestBase, SelectConstants, ContractTestUtils.touch, S3GuardTool.main(), ExitUtil, and launcher exit codes.


## Risks and Test Signals
Risks are accidental re-advertisement of removed capability or inconsistent optional/must semantics. Signals cover API-level, capability-level, and command-line behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/select/ITestSelectUnsupported.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/ITestAWSStatisticCollection.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/ITestAWSStatisticCollection.java


## Purpose
Cost/statistics integration test that verifies AWS SDK request metrics are wired into S3A IO statistics.


## Important APIs, Types, and Functions
ITestAWSStatisticCollection overrides createConfiguration() to disable S3 Express create sessions and set create performance flags, and testSDKMetricsCostOfGetFileStatusOnFile().


## Control Flow
The test creates a simple file via AbstractS3ACostTest.file(), calls getFileStatus(), and verifies STORE_IO_REQUEST increased by one using the cost-test metric harness.


## State and Persistence Behavior
Persistent state is a single test file; statistics state is captured around the operation by verifyMetrics().


## Dependencies and Integration Points
Depends on AbstractS3ACostTest, S3AFileSystem, S3A performance flags, S3EXPRESS_CREATE_SESSION, and Statistic.STORE_IO_REQUEST.


## Risks and Test Signals
Risk is metric name/wiring drift between AWS SDK and S3A counters. The signal is intentionally narrow: one getFileStatus should produce one SDK IO request.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/ITestAWSStatisticCollection.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/ITestAggregateIOStatistics.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/ITestAggregateIOStatistics.java


## Purpose
Integration test for serializing aggregate IOStatistics snapshots to local disk and to S3.


## Important APIs, Types, and Functions
ITestAggregateIOStatistics defines testSaveStatisticsLocal(), testSaveStatisticsS3(), createOutputDir(), and outputFilename(). It uses IOStatisticsSnapshot.serializer().


## Control Flow
Local test aggregates filesystem statistics, writes JSON under test.build.dir/classname with a timestamped filename, reloads it, and logs the deserialized string. S3 test writes the same snapshot to methodPath and reloads from the filesystem.


## State and Persistence Behavior
State persists as a local JSON file and an S3 object. It also reads/writes the static FILESYSTEM_IOSTATS aggregate inherited from the base test class.


## Dependencies and Integration Points
Depends on AbstractS3ATestBase, JsonSerialization, IOStatisticsSnapshot, local filesystem, and S3A filesystem serializer overloads.


## Risks and Test Signals
Risks include timestamp collision only at extreme speed, permissions on target build dir, and serializer compatibility. Signals validate round-trip persistence in both local and S3-backed stores.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/ITestAggregateIOStatistics.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/ITestS3AContractStreamIOStatistics.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/ITestS3AContractStreamIOStatistics.java


## Purpose
Contract-level integration test declaring the input and output stream IOStatistics keys S3A streams must expose.


## Important APIs, Types, and Functions
ITestS3AContractStreamIOStatistics extends AbstractContractStreamIOStatisticsTest, overrides createContract(), inputStreamStatisticKeys(), outputStreamStatisticKeys(), and re-enables testInputStreamStatisticRead().


## Control Flow
The parent contract test performs stream reads/writes against an S3AContract; this subclass supplies the required statistic key lists for read aborts, close/open/read/seek operations, bytes, version mismatches, and write bytes/block uploads/exceptions.


## State and Persistence Behavior
State is contract test filesystem data and stream IOStatistics collected by the parent class. This class stores no mutable state.


## Dependencies and Integration Points
Depends on S3AContract, AbstractContractStreamIOStatisticsTest, StreamStatisticNames, and IntegrationTest tagging.


## Risks and Test Signals
Risks are missing or renamed statistic keys after stream implementation changes. Signals ensure S3A streams stay compatible with the filesystem contract's statistics expectations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/ITestS3AContractStreamIOStatistics.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/ITestS3AFileSystemStatistic.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/ITestS3AFileSystemStatistic.java


## Purpose
Integration test that filesystem-level bytesRead aggregates reads from multiple S3A input streams.


## Important APIs, Types, and Functions
ITestS3AFileSystemStatistic defines constants ONE_KB/TWO_KB and testBytesReadWithStream().


## Control Flow
The test writes 1 KiB, asserts the output stream counted STREAM_WRITE_BYTES, reads the file fully through two separate input streams, then asserts FileSystem.Statistics.getBytesRead() equals 2 KiB.


## State and Persistence Behavior
Persistent state is one S3 test file. Statistics state is the S3AFileSystem instance's shared FileSystem.Statistics object.


## Dependencies and Integration Points
Depends on AbstractS3ATestBase, FSDataInputStream/OutputStream, S3AFileSystem, IOStatisticAssertions, and StreamStatisticNames.


## Risks and Test Signals
Risks are global statistics contamination if filesystem reuse changes and exact byte-count assumptions if reads overfetch. Signal verifies user-visible FS statistics, not only per-stream IOStatistics.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/ITestS3AFileSystemStatistic.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/TestErrorCodeMapping.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/TestErrorCodeMapping.java


## Purpose
Parameterized unit test for mapping HTTP status codes from AWS SDK failures to S3A statistic names.


## Important APIs, Types, and Functions
TestErrorCodeMapping defines params(), constructor fields code/name, and testMapping(). It targets StatisticsFromAwsSdkImpl.mapErrorStatusCodeToStatisticName().


## Control Flow
JUnit parameterization feeds representative 2xx/3xx/4xx/5xx codes. The test asserts only selected errors map to specific HTTP_RESPONSE_* counters; 404 and non-error statuses map to null, while GCS 429 maps to HTTP_RESPONSE_503.


## State and Persistence Behavior
No external state; all state is constructor parameters for the current test instance.


## Dependencies and Integration Points
Depends on StatisticsFromAwsSdkImpl, InternalConstants status code constants, StoreStatisticNames, AssertJ, and JUnit parameterized class support.


## Risks and Test Signals
Risks are provider-specific status mapping changes. Signals protect cost/statistic categorization for error counters.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/TestErrorCodeMapping.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/ExtraAssertions.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/ExtraAssertions.java


## Purpose
Private test assertion utility for file counts, text containment, nested causes, status codes, and Abortable results.


## Important APIs, Types, and Functions
ExtraAssertions contains assertFileCount(), assertTextContains(), failIf(), failUnless(), extractCause(), assertStatusCode(), assertCompleteAbort(), and assertNoopAbort().


## Control Flow
assertFileCount recursively lists files and fails with a joined listing on mismatch. Cause helpers unwrap and validate exception causes. Abort helpers assert whether AbortableResult represented a real cleanup or already-closed no-op.


## State and Persistence Behavior
No persistent state; only a static logger. Methods operate on supplied filesystems, paths, strings, exceptions, and abort results.


## Dependencies and Integration Points
Depends on S3AUtils.applyLocatedFiles, ContractTestUtils.fail, AssertJ, JUnit assertions, DurationInfo, AWSServiceIOException, and Abortable.


## Risks and Test Signals
Risks are test-only visibility: assertStatusCode is protected in a final utility, so it is not generally usable. Signals improve diagnostics for file-count and abort-cleanup tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/ExtraAssertions.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/MinimalListingOperationCallbacks.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/MinimalListingOperationCallbacks.java


## Purpose
Minimal stub implementation of ListingOperationCallbacks for tests that need an object satisfying the interface without real S3/listing behavior.


## Important APIs, Types, and Functions
Implements listObjectsAsync(), continueListObjectsAsync(), toLocatedFileStatus(), createListObjectsRequest(), getDefaultBlockSize(), getObjectSize(), and getMaxKeys().


## Control Flow
All methods return null or zero; no control flow performs IO. It is intended as a base for subclassing or for tests where only construction/type compatibility matters.


## State and Persistence Behavior
No state is stored. Returning null futures/statuses will fail fast if a test accidentally exercises real listing behavior.


## Dependencies and Integration Points
Depends on S3A listing model types, AWS S3Object, DurationTrackerFactory, and AuditSpan.


## Risks and Test Signals
Risk is misuse in tests expecting functional callbacks. Signal is mostly compile-time interface coverage when ListingOperationCallbacks evolves.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/MinimalListingOperationCallbacks.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/MinimalOperationCallbacks.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/MinimalOperationCallbacks.java


## Purpose
Minimal stub for OperationCallbacks used by S3A operation helper unit tests.


## Important APIs, Types, and Functions
Implements createObjectAttributes overloads, createReadContext(), finishRename(), deleteObjectAtPath(), listFilesAndDirectoryMarkers(), copyFile(), removeKeys(), and listObjects().


## Control Flow
Most methods return null and mutating callbacks are no-ops. Tests can subclass or inject it where only selected callbacks are expected to be called.


## State and Persistence Behavior
No persistent or mutable state. Null returns are intentional tripwires for unimplemented paths.


## Dependencies and Integration Points
Depends on S3A status/read/object attribute types, AWS SDK copy/delete types, RemoteIterator, and MultiObjectDeleteException.


## Risks and Test Signals
Risk is silent no-op mutation callbacks masking a missing assertion if a test does not verify side effects. Interface implementation also acts as a signal for callback API drift.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/MinimalOperationCallbacks.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/MinimalWriteOperationHelperCallbacks.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/MinimalWriteOperationHelperCallbacks.java


## Purpose
Minimal WriteOperationHelper callback implementation that delegates actual multipart calls to a supplied S3Client.


## Important APIs, Types, and Functions
Defines a Supplier<S3Client> field, constructor, completeMultipartUpload(), and uploadPart().


## Control Flow
On each callback it resolves the S3Client supplier and invokes completeMultipartUpload or uploadPart. A null supplier result intentionally causes NullPointerException for tests expecting failure.


## State and Persistence Behavior
State is only the supplier reference. S3 service state is affected only when delegated client calls are real rather than mocked.


## Dependencies and Integration Points
Depends on WriteOperationHelper.WriteOperationHelperCallbacks, AWS SDK S3Client, multipart request/response types, RequestBody, and DurationTrackerFactory.


## Risks and Test Signals
Risks are on-demand supplier side effects and missing duration tracking in uploadPart. Test signal is controlled delegation into mocked or instrumented S3 clients.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/MinimalWriteOperationHelperCallbacks.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/PublicDatasetTestUtils.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/PublicDatasetTestUtils.java


## Purpose
Utility centralizing public S3 dataset paths and configuration keys used by S3A tests.


## Important APIs, Types, and Functions
PublicDatasetTestUtils defines defaults for requester-pays, many-objects, ORC, and external gzipped data; methods include getOrcData(), getExternalData(), requireAnonymousDataPath(), requireDefaultExternalDataFile(), isUsingDefaultExternalDataFile(), requireDefaultExternalData(), getBucketPrefixWithManyObjects(), getRequesterPaysObject(), and fetchFromConfig().


## Control Flow
Callers obtain Paths or URI strings from configuration with defaults. require* methods use assumptions to skip tests when configured values are empty or not the expected default.


## State and Persistence Behavior
No persistent state beyond constants. Methods may use and semantically depend on mutable Configuration, but only read from it here.


## Dependencies and Integration Points
Depends on Hadoop Configuration/Path, S3ATestConstants, S3ATestUtils.assume(), and AssertJ assumptions.


## Risks and Test Signals
Risks are public dataset movement, requester-pays costs, or endpoint changes. Signals standardize external data contracts so tests fail/skip consistently rather than embedding stale paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/PublicDatasetTestUtils.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/SdkFaultInjector.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/SdkFaultInjector.java


## Purpose
AWS SDK v2 ExecutionInterceptor used by tests to inject post-success HTTP failures into selected S3 requests.


## Important APIs, Types, and Functions
SdkFaultInjector exposes static evaluators/actions/counters, request predicates such as isGetRequest/isPutRequest/isPartUpload/isMultipartAbort, reset/set methods, modifyHttpResponse(), patchStatusCode(), shouldFail(), and addFaultInjection().


## Control Flow
modifyHttpResponse inspects the SDK context after S3 has responded. If the evaluator matches and the failure count still demands failure, it applies the configured action, normally copying the HTTP response with a configured error status. addFaultInjection wires the interceptor through S3A audit execution interceptors.


## State and Persistence Behavior
State is global static and mutable: failure status, failure count, evaluator, and action. Tests must reset before/after use to avoid cross-test contamination.


## Dependencies and Integration Points
Depends on AWS SDK ExecutionInterceptor/Context/SdkHttpResponse, S3 request classes, S3A audit test support, Configuration, and InternalConstants status codes.


## Risks and Test Signals
Risks are race/cross-test interference from static state and the fact that failures happen after the backend operation succeeded. Signals are powerful for retry, abort, and cleanup tests that need deterministic SDK-layer errors.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/SdkFaultInjector.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/StubS3ClientFactory.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/StubS3ClientFactory.java


## Purpose
Stub S3ClientFactory returning preconfigured sync, async, and transfer-manager clients while counting creations.


## Important APIs, Types, and Functions
StubS3ClientFactory defines STUB_FACTORY, constructor-injected S3Client/S3AsyncClient/S3TransferManager/launcher, createS3Client(), createS3AsyncClient(), createS3TransferManager(), creation-count getters, and toString().


## Control Flow
Sync and async client creation increment counters, invoke the launcher hook for injected delay/failure, then return supplied clients. Transfer manager creation only increments and returns the supplied manager.


## State and Persistence Behavior
State is injected clients, launcher, and AtomicInteger counters. No null checks are performed, so null clients are deliberate failure hooks.


## Dependencies and Integration Points
Depends on S3ClientFactory, AWS SDK S3 sync/async clients, S3TransferManager, URI, and InvocationRaisingIOE.


## Risks and Test Signals
Risks are launcher side effects and test fragility if factory API changes. Signals support tests for lazy client construction, retry on factory failures, and creation-count assertions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/StubS3ClientFactory.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/AbstractMarkerToolTest.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/AbstractMarkerToolTest.java


## Purpose
Base class for S3A directory-marker CLI/tool tests with shared configuration, execution, output-reading, and assertion helpers.


## Important APIs, Types, and Functions
AbstractMarkerToolTest overrides createConfiguration() and teardown(), and defines tempAuditFile(), expectMarkersInOutput(), readOutput(), markerTool() overloads, run(), uncachedFSConfig(), runToFailure(), toPath(), and m().


## Control Flow
Configuration disables create-performance flags, authoritative path overrides, bucket probes, and FS caching for tool invocations. Helpers run S3Guard/MarkerTool commands, assert exit codes, read audit output files, and delete test dirs before superclass teardown to avoid audit failures from intentional markers.


## State and Persistence Behavior
State is inherited filesystem/test-directory state plus temporary audit files. Tool execution may create/delete S3 directory markers under test paths.


## Dependencies and Integration Points
Depends on AbstractS3ATestBase, S3GuardToolTestHelper, MarkerTool.ScanArgsBuilder/ScanResult, S3A constants, FileSystem, and AssertJ.


## Risks and Test Signals
Risks include teardown order and caching hiding config changes. Signals centralize marker count and exit-code checks used by concrete marker-tool tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/AbstractMarkerToolTest.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/CsvFile.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/CsvFile.java


## Purpose
Package-private helper for writing small CSV test files to a Hadoop FileSystem.


## Important APIs, Types, and Functions
CsvFile defines ALL_QUOTES/NO_QUOTES, constructor, close(), getPath(), getSeparator(), getEol(), row(), line(), and getOut().


## Control Flow
The constructor opens fs.create(path, overwrite) as a PrintWriter. row() writes separator-delimited columns, quoting columns according to bits in a long mask, and line() writes raw lines followed by configured EOL.


## State and Persistence Behavior
State is path, PrintWriter, separator, EOL, and quote string. close() closes the writer but does not null it or check writer errors.


## Dependencies and Integration Points
Depends on FileSystem, Path, PrintWriter, and Hadoop Preconditions.


## Risks and Test Signals
Risks include unescaped quote characters and PrintWriter swallowing IO errors until checked. Test signal is deterministic generation of CSV fixtures for select/CSV-related tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/CsvFile.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/ITestBucketTool.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/ITestBucketTool.java


## Purpose
Integration tests for BucketTool bucket creation validation, especially S3 Express constraints, without intentionally creating new buckets.


## Important APIs, Types, and Functions
ITestBucketTool defines setup(), tests for recreating existing S3 Express/non-S3 Express buckets, zone argument validation, missing S3 Express zone, non-AWS endpoint rejection, and d().


## Control Flow
setup captures the active FS, bucket URI, region, S3 Express capability, and BucketTool. Tests invoke bucketTool.exec() with create/region/zone/endpoint arguments and assert AWS or launcher error codes/messages according to store type.


## State and Persistence Behavior
No intended persistent bucket creation; operations target existing test bucket or invalid sample names. State is per-test fields derived from current filesystem configuration.


## Dependencies and Integration Points
Depends on AbstractS3ATestBase, BucketTool constants, S3ATestUtils assumptions/error helpers, S3 Express capability, ExitUtil, and launcher exit codes.


## Risks and Test Signals
Risks are endpoint/region-specific errors and third-party stores behaving differently. Signals protect CLI validation around S3 Express zone requirements and provider safety checks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/ITestBucketTool.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/ITestMarkerTool.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/ITestMarkerTool.java


## Purpose
Integration tests for MarkerTool auditing, cleaning, limits, rename behavior, and directory-marker expectations.


## Important APIs, Types, and Functions
ITestMarkerTool defines marker CLI tests, assertMarkersDeleted(), nested CreatedPaths, createPaths(), and verifyRenamed(). It tracks expected file/marker counts as fields.


## Control Flow
Tests create a standard tree with base marker, empty dirs, non-empty dirs, and files; then run marker scans/CLI commands with limits, expected min/max, audit output files, clean/audit modes, and public many-object bucket scans. Rename test verifies markers are not copied to destination while files and directories remain visible.


## State and Persistence Behavior
Persistent state is S3 test trees and intentional directory markers. Temporary audit files capture scan output. Expected counts are instance fields populated during createPaths().


## Dependencies and Integration Points
Depends on AbstractMarkerToolTest, MarkerTool constants, S3GuardTool bucket-info command, PublicDatasetTestUtils, ContractTestUtils.touch, and S3A directory marker policy.


## Risks and Test Signals
Risks include directory-marker policy changes, root/base marker semantics, and public bucket availability. Signals validate CLI exit codes, audit output counts, marker purge behavior, and rename marker cleanup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/ITestMarkerTool.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/ITestMarkerToolRootOperations.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/ITestMarkerToolRootOperations.java


## Purpose
Sequential root-filesystem tests for auditing and cleaning directory markers at bucket root.


## Important APIs, Types, and Functions
ITestMarkerToolRootOperations overrides setup() and defines ordered tests test_100_audit_root_noauth() and test_200_clean_root().


## Control Flow
setup skips unless root tests are enabled and stores the qualified root path. Tests run MarkerTool audit and clean with verbose output and write scan output to temporary files for logging.


## State and Persistence Behavior
Persistent state can include root-level marker cleanup across the whole test bucket, so the class is root-test tagged and ordered. rootPath is per-test state.


## Dependencies and Integration Points
Depends on AbstractMarkerToolTest, maybeSkipRootTests(), RootFilesystemTest, MethodOrderer, and MarkerTool CLI constants.


## Risks and Test Signals
High blast radius because it scans/cleans root. Signals are mostly smoke/integration checks for root path handling rather than exact marker counts.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/ITestMarkerToolRootOperations.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/yarn/ITestS3A.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/yarn/ITestS3A.java


## Purpose
Basic FileContext API integration tests over S3A.


## Important APIs, Types, and Functions
ITestS3A extends AbstractS3ATestBase, sets up FileContext via S3ATestUtils.createTestFileContext(), and tests getFsStatus() plus file creation in a subdirectory.


## Control Flow
setup creates a FileContext from the test configuration. One test asserts capacity/used/remaining are non-negative; the other mkdirs a method path and creates a file with CreateFlag.CREATE.


## State and Persistence Behavior
Persistent state is one test directory and file under methodPath. FileContext is per-test instance state.


## Dependencies and Integration Points
Depends on FileContext, FsStatus, CreateFlag, FSDataOutputStream, S3ATestUtils, and JUnit Timeout.


## Risks and Test Signals
Risks are differences between FileSystem and FileContext behavior over S3A. Signals cover basic status reporting and create semantics through the FileContext abstraction.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/yarn/ITestS3A.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/yarn/ITestS3AMiniYarnCluster.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/yarn/ITestS3AMiniYarnCluster.java


## Purpose
End-to-end integration test running Hadoop WordCount on a MiniYARNCluster with S3A input/output and staging committer.


## Important APIs, Types, and Functions
ITestS3AMiniYarnCluster overrides createConfiguration(), setup(), teardown(), testWithMiniCluster(), getResultAsMap(), writeStringToFile(), and readStringFromFile().


## Control Flow
Configuration selects the S3A staging committer and disables unique filenames. setup requires multipart uploads, creates input dirs, sets working directory, and starts a one-node MiniYARNCluster. The test writes input text, configures WordCount job, waits for completion, validates non-empty _SUCCESS committer metadata, loads SuccessData, reads reducer output, and checks word counts.


## State and Persistence Behavior
Persistent state is S3 input/output/working directories and committer _SUCCESS/part files. Runtime state includes MiniYARNCluster lifecycle and job credentials/configuration.


## Dependencies and Integration Points
Depends on MiniYARNCluster, MapReduce Job APIs, WordCount example classes, S3A staging committer, SuccessData, FileContext, and S3A filesystem reads/writes.


## Risks and Test Signals
Risks are high runtime/environment sensitivity, multipart availability, and committer configuration drift. Signals validate S3A usability from YARN containers and committer output correctness.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/yarn/ITestS3AMiniYarnCluster.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/sdk/TestAWSV2SDK.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/sdk/TestAWSV2SDK.java


## Purpose
Classpath inspection test for AWS SDK v2 bundle contents and shaded-class expectations.


## Important APIs, Types, and Functions
TestAWSV2SDK defines testShadedClasses() and private getClassNamesFromJarFile().


## Control Flow
The test scans java.class.path for a path containing awssdk/bundle/2, asserts it exists, reads all .class entries from the jar, and logs any classes not under software/amazon/.


## State and Persistence Behavior
State is local JVM classpath and jar file contents; no repository or S3 state is changed.


## Dependencies and Integration Points
Depends on JarFile/JarEntry, java.class.path, AssertJ, and Hadoop test base logging.


## Risks and Test Signals
Risk is path-pattern fragility if dependency layout changes. The current test logs unshaded classes instead of failing on them, so its strongest signal is SDK bundle presence.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/sdk/TestAWSV2SDK.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/mapreduce/MockJob.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/mapreduce/MockJob.java


## Purpose
MapReduce Job subclass that replaces YARN/client submission with a Mockito ClientProtocol for unit tests needing JobSubmitter behavior.


## Important APIs, Types, and Functions
MockJob defines constructor, init(), isSuccessful(), package-private getJobSubmitter(), connect(), getSubmittedCredentials(), and updateStatus(). It stores mockClient, jobIdCounter/trackerId, and submittedCredentials.


## Control Flow
init() stubs submitJob to capture submitted credentials and return a RUNNING JobStatus, getNewJobID to return incrementing IDs, and getQueueAdmins to allow all. getJobSubmitter ignores the supplied submitClient and constructs a JobSubmitter with the mock client.


## State and Persistence Behavior
State includes static job ID/tracker counters and per-instance submitted credentials. No YARN cluster or real job execution occurs.


## Dependencies and Integration Points
Depends on Job, JobSubmitter package-private access, ClientProtocol, Mockito, Credentials, JobConf, and AccessControlList.


## Risks and Test Signals
Risks are package-private coupling to Hadoop MapReduce internals and static counter sharing. Signals let tests inspect submitted credentials/resources without contacting YARN.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/mapreduce/MockJob.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/mapreduce/filecache/TestS3AResourceScope.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/mapreduce/filecache/TestS3AResourceScope.java


## Purpose
Unit test proving S3A resources are treated as private/non-executable by distributed cache permission checks.


## Important APIs, Types, and Functions
TestS3AResourceScope defines PATH, tests two S3AFileStatus constructors, and assertNotExecutable().


## Control Flow
Each test constructs an encrypted S3AFileStatus, asserts isEncrypted(), places it in an ancestor cache map, and asserts ClientDistributedCacheManager.ancestorsHaveExecutePermissions() returns false.


## State and Persistence Behavior
No external state. The cache map is local to assertion helper.


## Dependencies and Integration Points
Depends on S3AFileStatus, ClientDistributedCacheManager package-private permission method, FileStatus, URI maps, and HadoopTestBase assertions.


## Risks and Test Signals
Risks are constructor semantic changes around encryption/private resources. Signals ensure YARN distributed cache does not treat S3A paths as public executable resources.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/mapreduce/filecache/TestS3AResourceScope.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/resources/contract/s3a.xml -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/resources/contract/s3a.xml


## Purpose
Contract-test capability declaration for S3A filesystem behavior.


## Important APIs, Types, and Functions
The XML defines fs.contract.* properties covering root tests, random seek count, blobstore identity, visibility delay, case sensitivity, rename semantics, unsupported append/concat/atomic operations, seek/unbuffer/vector IO, multipart uploader support, permissions, and create-under-file behavior.


## Control Flow
Contract tests load these properties to decide expected behavior and which assertions to run. Duplicate rename-overwrites-dest entries both set false.


## State and Persistence Behavior
State is configuration data only; it does not execute code or persist runtime state. It shapes downstream contract-test expectations.


## Dependencies and Integration Points
Depends on Hadoop contract test framework property names and S3A's documented blobstore semantics.


## Risks and Test Signals
Risks are stale properties causing false contract failures or masking regressions. Signals encode S3A's non-POSIX semantics, especially non-atomic rename/delete and delayed create visibility.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/resources/contract/s3a.xml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/resources/core-site.xml -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/resources/core-site.xml


## Purpose
Test-time Hadoop configuration defaults for hadoop-aws integration tests.


## Important APIs, Types, and Functions
The XML sets hadoop.tmp.dir, bucket-specific endpoint/requester-pays/audit/prefetch properties for public datasets, named regional endpoint aliases, simple security, audit rejection of out-of-span operations, thread-level IOStatistics, low retry counts, and optional auth-keys.xml inclusion.


## Control Flow
Tests load this file as a baseline; per-test code may remove or override properties. The XInclude fallback allows private credentials/bucket bindings outside version control.


## State and Persistence Behavior
State is configuration only, but it controls external S3 endpoints, public buckets, retry behavior, audit behavior, and local temp directories used by many tests.


## Dependencies and Integration Points
Depends on Hadoop Configuration XML parsing, XInclude support, S3A bucket-specific property naming, and PublicDatasetTestUtils defaults.


## Risks and Test Signals
Risks include stale public bucket endpoints, too-low retry counts increasing flakiness, and missing auth-keys.xml for private tests. Signals centralize reproducible integration-test defaults.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/resources/core-site.xml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.codeclimate.yml -->

# sources/distributed-fs/ipfs-kubo/.codeclimate.yml


## Purpose
Code Climate configuration for Kubo Go code quality checks.


## Important APIs, Types, and Functions
Defines ratings paths for **/*.go, exclude_paths for tests/vendor/generated protobufs, engines fixme/golint/govet/gofmt, version 2, and disables several complexity/size/style checks.


## Control Flow
Code Climate consumes this YAML to choose analyzers and thresholds; FIXME strings include FIXME/HACK/XXX/BUG while many maintainability checks are disabled.


## State and Persistence Behavior
No runtime state; repository metadata only. It affects external quality-report persistence in Code Climate.


## Dependencies and Integration Points
Depends on Code Climate engine names and path glob semantics.


## Risks and Test Signals
Risks include obsolete engines such as golint and broad disabled checks reducing signal. Test signal is static-analysis configuration rather than executable tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.codeclimate.yml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.cspell.yml -->

# sources/distributed-fs/ipfs-kubo/.cspell.yml


## Purpose
cspell spelling configuration for Kubo-specific accepted words.


## Important APIs, Types, and Functions
Contains ignoreWords entries for known names or intentional spellings: childs, NodeCreater, Boddy, Botto, cose.


## Control Flow
Spell-check tooling reads the list and suppresses matching findings.


## State and Persistence Behavior
No state beyond YAML config.


## Dependencies and Integration Points
Depends on cspell configuration schema.


## Risks and Test Signals
Risks are hiding real typos if ignored terms are over-broad, but the list is small and annotated.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.cspell.yml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/FUNDING.yml -->

# sources/distributed-fs/ipfs-kubo/.github/FUNDING.yml


## Purpose
GitHub Sponsors funding metadata for the Kubo repository.


## Important APIs, Types, and Functions
Defines github funding account ipshipyard.


## Control Flow
GitHub reads this file to show sponsorship links in repository UI.


## State and Persistence Behavior
No runtime or CI state.


## Dependencies and Integration Points
Depends on GitHub FUNDING.yml schema.


## Risks and Test Signals
Risk is only stale sponsorship metadata; no test signal.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/FUNDING.yml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/ISSUE_TEMPLATE/bug-report.yml -->

# sources/distributed-fs/ipfs-kubo/.github/ISSUE_TEMPLATE/bug-report.yml


## Purpose
GitHub issue form for Kubo bug reports.


## Important APIs, Types, and Functions
Defines name/description/labels, markdown guidance, required checklist, installation-method dropdown, version textarea, config textarea, and description textarea.


## Control Flow
GitHub renders the form and enforces required checklist/dropdown fields. The template directs support/security/enhancement traffic elsewhere and asks for ipfs version/config output.


## State and Persistence Behavior
State becomes issue metadata and body content when submitted; the template itself has no runtime state.


## Dependencies and Integration Points
Depends on GitHub issue forms YAML schema and Kubo support/release links.


## Risks and Test Signals
Risks include outdated links or requiring config output that may contain sensitive values. Signal improves triage quality for bug reports.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/ISSUE_TEMPLATE/bug-report.yml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/ISSUE_TEMPLATE/config.yml -->

# sources/distributed-fs/ipfs-kubo/.github/ISSUE_TEMPLATE/config.yml


## Purpose
GitHub issue-template configuration controlling blank issues and contact links.


## Important APIs, Types, and Functions
Sets blank_issues_enabled=false and declares help/config/experimental/RPC/discussion contact links.


## Control Flow
GitHub uses it on the new-issue chooser to block blank issues and redirect support/documentation traffic.


## State and Persistence Behavior
No runtime state; submitted user navigation is external.


## Dependencies and Integration Points
Depends on GitHub issue template config schema and linked documentation URLs.


## Risks and Test Signals
Risks are stale URLs or over-constraining ad hoc reports. Signal reduces low-quality issues by routing support elsewhere.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/ISSUE_TEMPLATE/config.yml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/ISSUE_TEMPLATE/doc.yml -->

# sources/distributed-fs/ipfs-kubo/.github/ISSUE_TEMPLATE/doc.yml


## Purpose
GitHub issue form for documentation issues in the Kubo repository.


## Important APIs, Types, and Functions
Defines documentation issue name/description/labels, markdown note about docs.ipfs.tech, required checklist, Location input, and Description textarea.


## Control Flow
GitHub renders a docs-specific form and requires users to confirm the issue belongs in this repository and was searched first.


## State and Persistence Behavior
State becomes issue labels and submitted body fields.


## Dependencies and Integration Points
Depends on GitHub issue form schema and Kubo/IPFS docs split.


## Risks and Test Signals
Risks are misrouting docs.ipfs.tech issues if guidance becomes stale. Signal improves docs triage metadata.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/ISSUE_TEMPLATE/doc.yml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/ISSUE_TEMPLATE/enhancement.yml -->

# sources/distributed-fs/ipfs-kubo/.github/ISSUE_TEMPLATE/enhancement.yml


## Purpose
GitHub issue form for improvements to existing Kubo features.


## Important APIs, Types, and Functions
Defines enhancement name/description/labels, markdown guidance, required specificity/protocol/search checklist, and description textarea.


## Control Flow
The form distinguishes product enhancements from protocol brainstorming and requires actionable motivation before submission.


## State and Persistence Behavior
State becomes issue labels/body; no runtime state.


## Dependencies and Integration Points
Depends on GitHub issue forms and discussion forum links.


## Risks and Test Signals
Risks are process friction and stale forum guidance. Signal helps maintainers triage actionable enhancement requests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/ISSUE_TEMPLATE/enhancement.yml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/ISSUE_TEMPLATE/feature.yml -->

# sources/distributed-fs/ipfs-kubo/.github/ISSUE_TEMPLATE/feature.yml


## Purpose
GitHub issue form for new Kubo feature requests.


## Important APIs, Types, and Functions
Defines feature name/description/labels, guidance, required checklist, and description textarea.


## Control Flow
The form routes protocol ideas to the forum and asks for specific, motivated feature descriptions with examples.


## State and Persistence Behavior
State becomes labeled issue content.


## Dependencies and Integration Points
Depends on GitHub issue forms and IPFS discussion links.


## Risks and Test Signals
Risks are duplicated wording typo ('and and') and process friction. Signal improves feature-request quality.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/ISSUE_TEMPLATE/feature.yml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/auto-comment.yml -->

# sources/distributed-fs/ipfs-kubo/.github/auto-comment.yml


## Purpose
Disabled auto-comment configuration placeholder.


## Important APIs, Types, and Functions
Contains commented issueOpened and pullRequestOpened entries marked disabled.


## Control Flow
No actions run while entries are commented/empty; it documents where auto-comment text would be configured.


## State and Persistence Behavior
No state or integration unless an external action is configured to read it.


## Dependencies and Integration Points
Depends on the unspecified auto-comment tool's expected keys.


## Risks and Test Signals
Risk is confusion from dead configuration. Test signal is absent because automation is disabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/auto-comment.yml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/build-platforms.yml -->

# sources/distributed-fs/ipfs-kubo/.github/build-platforms.yml


## Purpose
Distribution build matrix metadata listing Kubo target platforms.


## Important APIs, Types, and Functions
Defines platforms for darwin/freebsd/linux/openbsd/windows across amd64/arm64 plus linux-riscv64.


## Control Flow
Release or distribution scripts can read the list to drive builds; comments state FUSE support is handled by Go build tags.


## State and Persistence Behavior
No runtime state; it shapes artifact generation.


## Dependencies and Integration Points
Depends on downstream distribution tooling and platform string conventions.


## Risks and Test Signals
Risks are omissions or unsupported platform strings causing release drift. Signal centralizes supported build target intent.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/build-platforms.yml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/dependabot.yml -->

# sources/distributed-fs/ipfs-kubo/.github/dependabot.yml


## Purpose
Dependabot configuration for GitHub Actions and Go modules in Kubo.


## Important APIs, Types, and Functions
Defines weekly github-actions updates, monthly gomod updates at root, PR limit, dependency label, ignored datastore wrapper dependencies, and grouped update families for IPFS, libp2p, golang-x, OpenTelemetry, Prometheus, and Uber packages.


## Control Flow
Dependabot reads this schedule/grouping to open dependency PRs; companion workflow dependabot-tidy handles multi-module tidy.


## State and Persistence Behavior
State persists as Dependabot PRs and labels, not runtime application state.


## Dependencies and Integration Points
Depends on Dependabot v2 schema, Go module dependency names, and repo label conventions.


## Risks and Test Signals
Risks include ignored dependencies going stale and groups becoming too broad. Signal controls dependency maintenance cadence and PR shape.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/dependabot.yml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/changelog.yml -->

# sources/distributed-fs/ipfs-kubo/.github/workflows/changelog.yml


## Purpose
GitHub Actions workflow enforcing changelog entries on relevant Go dependency/source PRs.


## Important APIs, Types, and Functions
Workflow Changelog triggers on pull_request opened/edited/synchronize/reopened/labeled/unlabeled for Go files/go.mod/go.sum. Job uses gh api to count files under docs/changelogs/ and fails unless modified or PR opts out by title/label.


## Control Flow
The job writes a modified count to GITHUB_OUTPUT, then emits a GitHub error and exits nonzero when no changelog entry is present.


## State and Persistence Behavior
State is workflow run status and PR check result. It reads PR labels/title/files through the GitHub API.


## Dependencies and Integration Points
Depends on GitHub Actions, gh CLI, github.token, PR file API, and shell jq selector support in gh.


## Risks and Test Signals
Risks are false positives for internal-only changes and reliance on title/label skip conventions. Signal enforces release-note hygiene.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/changelog.yml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/codeql-analysis.yml -->

# sources/distributed-fs/ipfs-kubo/.github/workflows/codeql-analysis.yml


## Purpose
GitHub Actions CodeQL workflow for Go security/static analysis.


## Important APIs, Types, and Functions
Triggers on workflow_dispatch, pushes to master, pull requests to master excluding markdown-only changes, and a weekly Tuesday cron. It grants contents read and security-events write permissions, uses concurrency cancellation, checkout, setup-go, CodeQL init/autobuild/analyze.


## Control Flow
Runs only in ipfs/kubo unless manually dispatched. CodeQL analyzes Go and uploads security events.


## State and Persistence Behavior
State is CodeQL analysis results and GitHub code scanning alerts. No repository writes.


## Dependencies and Integration Points
Depends on actions/checkout@v6, actions/setup-go@v6, github/codeql-action v4, go.mod toolchain metadata, and GitHub code scanning permissions.


## Risks and Test Signals
Risks include 20-minute timeout and autobuild assumptions. Signal provides scheduled and PR security analysis for Go code.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/codeql-analysis.yml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/dependabot-tidy.yml -->

# sources/distributed-fs/ipfs-kubo/.github/workflows/dependabot-tidy.yml


## Purpose
GitHub Actions workflow that tidies all Go modules on Dependabot PRs.


## Important APIs, Types, and Functions
Triggers on pull_request_target opened/synchronize and manual dispatch with pr_number. It discovers PR branch with gh, checks it out with write token, sets up Go, runs make mod_tidy, commits and pushes changes if git status is dirty.


## Control Flow
The workflow mutates Dependabot branches to keep secondary go.sum files in sync. It only runs for dependabot[bot] or manual dispatch.


## State and Persistence Behavior
State is committed tidy changes on PR branches and workflow outputs for PR number/branch/modified.


## Dependencies and Integration Points
Depends on pull_request_target permissions, secrets.GITHUB_TOKEN, gh CLI, actions/checkout/setup-go, make mod_tidy, and git identity config.


## Risks and Test Signals
Risks include elevated pull_request_target context and branch trust assumptions, though actor gating reduces exposure. Signal prevents CI failures from multi-module dependency drift.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/dependabot-tidy.yml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/docker-check.yml -->

# sources/distributed-fs/ipfs-kubo/.github/workflows/docker-check.yml


## Purpose
Pull-request/push Docker validation workflow for Kubo.


## Important APIs, Types, and Functions
Triggers on workflow_dispatch, pull_request excluding markdown-only changes, and pushes to master. It has lint and build jobs: hadolint, Dockerfile GO_VERSION guard, Buildx build using go.mod version, cache configuration, and docker run --version smoke test.


## Control Flow
The lint job validates Dockerfile quality and checks the default GO_VERSION ARG matches go.mod. The build job builds a local ipfs/kubo:wip image with BuildKit and runs a basic version command.


## State and Persistence Behavior
State is workflow check status and BuildKit/GHA cache entries; no image is pushed.


## Dependencies and Integration Points
Depends on Docker, setup-buildx, hadolint action, docker/build-push-action@v7, go.mod, Dockerfile ARG format, and repository guard conditions.


## Risks and Test Signals
Risks include cache flakiness and Docker daemon availability. Signals catch Dockerfile/toolchain drift and basic image breakage early.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/docker-check.yml -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/docker-image.yml -->

# sources/distributed-fs/ipfs-kubo/.github/workflows/docker-image.yml


## Purpose
Official Docker image build and publish workflow for Kubo releases/branches/manual dispatch.


## Important APIs, Types, and Functions
Triggers on workflow_dispatch with push/tags inputs and pushes to master/staging/bifrost-* branches or v* tags. Job docker-hub checks out, sets QEMU/Buildx, logs into Docker Hub, computes tags, reads Go version, builds amd64/armv7/arm64 images separately, smoke-tests them, then conditionally publishes multi-arch images and cache.


## Control Flow
The workflow builds each architecture with GO_VERSION from go.mod, uses registry/GHA cache, tests images with timeout/retry under QEMU where needed, and only pushes on non-manual or manual push=true.


## State and Persistence Behavior
State is Docker Hub images/tags, build cache, and workflow outputs. Secrets/vars provide Docker credentials.


## Dependencies and Integration Points
Depends on Docker Hub credentials, bin/get-docker-tags.sh, Dockerfile, docker/build-push-action@v7, QEMU emulation, Buildx, and GitHub event inputs.


## Risks and Test Signals
Risks include credential exposure scope, QEMU flakiness, tag-generation mistakes, and publish conditions. Signals validate all release image platforms before publication.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/docker-image.yml -->
