# Research group subset-b-007585

Work item: `subset-b-007585`

Scope: S3A unit and integration test support files under `sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AUnbuffer.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AUnbuffer.java

## Purpose

Integration coverage for `CanUnbuffer.unbuffer()` on `S3AInputStream`. It writes a small real S3A test object, opens it through `FSDataInputStream`, verifies the wrapped stream is an `S3AInputStream`, and proves that `unbuffer()` closes the underlying object stream while preserving readable stream state.

## Important APIs, Types, and Functions

Key APIs are `FSDataInputStream.open/read/unbuffer/getIOStatistics`, `StreamCapabilities.UNBUFFER`, `S3AInputStream.isObjectStreamOpen()`, `S3AInputStreamStatistics`, `IOStatisticsSnapshot`, and `S3ATestUtils.MetricDiff`. The helpers `isObjectStreamOpen()`, `skipIfCannotUnbuffer()`, and `readAndAssertBytesRead()` keep assertions focused on stream support and exact byte counts.

## Control Flow

`setup()` creates `ITestS3AUnbuffer` with 16 bytes. `testUnbuffer()` reads 8 bytes, snapshots IO statistics, calls `unbuffer()`, then checks `STREAM_READ_UNBUFFERED`, `STREAM_READ_BYTES`, and HTTP GET counts without a second GET. `testUnbufferStreamStatistics()` performs two read/unbuffer cycles, compares filesystem metric deltas for bytes read and close-drained bytes, closes the stream, and asserts close does not double-count.

## State, Dependencies, and Integration Points

State is held in the S3 object, the live wrapped AWS object stream, per-stream IO statistics, and filesystem instrumentation counters. It depends on `AbstractS3ATestBase`, contract dataset helpers, S3A stream capabilities, and Hadoop IOStatistics.

## Risks and Test Signals

The suite is sensitive to alternative stream implementations and skips if unbuffer capability is absent. It catches regressions where unbuffer fails to close the HTTP stream, loses IO statistics, double-counts close bytes, or leaves filesystem counters inconsistent after repeated unbuffer calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AUnbuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AUrlScheme.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AUrlScheme.java

## Purpose

Small integration test proving the S3A implementation can be registered as the implementation for the legacy `s3://` scheme and still preserve that scheme in filesystem and qualified path APIs.

## Important APIs, Types, and Functions

The test overrides `createConfiguration()` to set `fs.s3.impl` to `org.apache.hadoop.fs.s3a.S3AFileSystem`. `testFSScheme()` uses `FileSystem.get(new URI("s3://mybucket/path"), conf)`, `FileSystem.getScheme()`, and `FileSystem.makeQualified(Path)`.

## Control Flow

The test constructs a `s3://` filesystem using the S3A class binding, asserts the returned filesystem reports scheme `s3`, qualifies a relative path, and checks the resulting URI remains `s3://...`. The filesystem is closed in a `finally` block.

## State, Dependencies, and Integration Points

The only mutable state is the Hadoop `Configuration` mapping and the cached filesystem instance opened by `FileSystem.get`. It integrates the Hadoop filesystem registry, URI qualification, and S3A initialization path.

## Risks and Test Signals

This is a compatibility sentinel for applications still using `s3://` aliases. It will fail if scheme alias registration changes, if S3A canonicalizes qualified paths back to `s3a`, or if cache behavior returns an implementation with a different scheme.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AUrlScheme.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/MockS3AFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/MockS3AFileSystem.java

## Purpose

Test double for `S3AFileSystem` that relays most filesystem calls to an injected mocked `S3AFileSystem`, while stubbing S3A internals enough for committer and write-operation unit tests. It provides predictable URI/bucket identity, request construction, logging hooks, empty listing behavior, and no-op statistics.

## Important APIs, Types, and Functions

The class extends `S3AFileSystem` and exposes constants `BUCKET`, `FS_URI`, logging levels, and `REQUEST_FACTORY`. It overrides initialization, URI/path qualification, `getWriteOperationHelper()`, `createWriteOperationHelper()`, committer statistics, counters/gauges, `deleteObjectAtPath()`, and `createStoreContext()`. Delegated methods include `exists`, `open`, `create`, `append`, `rename`, `delete`, `listStatus`, `mkdirs`, and `getFileStatus`.

## Control Flow

Construction records the delegate filesystem and a pair of staging committer client outcomes, sets the URI, bucket, encryption secrets, and root. `initialize()` stores the configuration and creates a `WriteOperationHelper` with empty statistics, a noop auditor, and minimal callbacks. Public filesystem operations call `event()` for optional name/stack logging, then forward to the delegate. Methods that would create fake parents, update counters, or close resources are deliberately inert.

## State, Dependencies, and Integration Points

State includes the delegate mock, outcome pair, log level, configuration, write helper, and synthetic root path. It integrates with `RequestFactoryImpl`, `WriteOperationHelper`, `EmptyS3AStatisticsContext`, audit test support, committer tests, and `StoreContextBuilder`.

## Risks and Test Signals

Because it subclasses a complex filesystem and selectively overrides internals, it can drift when S3A initialization contracts change. The no-op statistics and empty `listFiles()` are intentional but can hide behavior if used outside narrow unit tests. Its value is high for verifying call paths and request construction without live S3 side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/MockS3AFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/MockS3ClientFactory.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/MockS3ClientFactory.java

## Purpose

Mockito-backed `S3ClientFactory` for unit tests that need an S3A filesystem to initialize without talking to AWS. It supplies mocked sync, async, and transfer-manager clients with enough default behavior for startup.

## Important APIs, Types, and Functions

Implements `S3ClientFactory.createS3Client()`, `createS3AsyncClient()`, and `createS3TransferManager()`. The sync client stubs `listMultipartUploads()` to return an empty non-truncated response and `getBucketLocation()` to return `us-west-2`.

## Control Flow

Each factory method creates a Mockito mock and returns it. The sync client has fixed stubs for multipart purge checks and bucket-region discovery; async client and transfer manager have no behavior beyond mock identity.

## State, Dependencies, and Integration Points

There is no persistent state. The class depends on AWS SDK v2 S3 model builders, `Region.US_WEST_2`, Mockito, and S3A client creation parameters. It integrates with tests that configure S3A to use a custom client factory during initialization.

## Risks and Test Signals

The stubbed region and empty MPU list can mask tests that need other startup behavior. It should be extended only with targeted stubs so it remains a low-friction initialization mock. Failures usually signal changed S3A startup calls or AWS SDK method signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/MockS3ClientFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/MultipartTestUtils.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/MultipartTestUtils.java

## Purpose

Shared utilities for S3A multipart-upload and magic-commit tests. The file creates test multipart uploads, lists and counts pending uploads, aborts known upload IDs, clears uploads under a path, and creates magic commit marker paths.

## Important APIs, Types, and Functions

Important functions are `cleanupParts()`, `createPartUpload()`, `clearAnyUploads()`, `assertNoUploadsAt()`, `countUploadsAt()`, `listMultipartUploads()`, `magicPath()`, and `createMagicFile()`. The nested `IdKey` value class pairs object key and upload ID and implements equality/hash/toString.

## Control Flow

`createPartUpload()` opens an audit span, obtains the filesystem `WriteOperationHelper`, initiates an MPU, builds an upload-part request, uploads an in-memory dataset as one part, and returns the upload identity. Cleanup iterates IDs, aborts each upload in its own audit span, logs failures, and fails at the end if any abort failed. Listing helpers traverse `RemoteIterator<MultipartUpload>` from the filesystem.

## State, Dependencies, and Integration Points

State lives in S3 pending multipart uploads and in `IdKey` sets passed by tests. The utilities depend on S3A audit spans, write helpers, AWS SDK `UploadPartRequest/Response`, commit magic path constants, contract file helpers, and `S3ATestUtils.LISTING_FORMAT`.

## Risks and Test Signals

These helpers touch live MPU state and must reliably clean up to avoid leaked uploads and cost. Assertions detect unexpected uploads, zero-byte magic marker behavior, and abort failures. Third-party object stores with different MPU visibility semantics may need tests to account for `S3ATestConstants.MULTIPART_COMMIT_CONSUMES_UPLOAD_ID`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/MultipartTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/S3ATestConstants.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/S3ATestConstants.java

## Purpose

Central interface of test-only configuration keys, defaults, timeouts, scale-test controls, and feature flags used across Hadoop S3A tests.

## Important APIs, Types, and Functions

Constants cover test filesystem naming (`test.fs.s3a.name`), feature gates for encryption, storage class, ACL, list-v1, content encoding, performance, scale tests, STS/session settings, requester-pays/public data inputs, huge-file sizes, root tests, multipart compatibility, and analytics accelerator settings. It also defines default operation counts, directory/file counts, read buffer size, session duration, timeouts, and common regions.

## Control Flow

There is no executable control flow. Consumers read keys from `Configuration` and system properties through utilities such as `S3ATestUtils.getTestProperty*()` and use defaults when not explicitly enabled.

## State, Dependencies, and Integration Points

The interface has no runtime state, but it encodes cross-suite configuration contracts. It depends on `PublicDatasetTestUtils` for deprecated public dataset defaults and `Duration` for test session duration.

## Risks and Test Signals

Changing names or defaults can silently skip or enable expensive/live tests. Deprecated constants remain to ease cherry-picks and compatibility. These constants are also risk points for third-party store test behavior, especially root tests, MPU semantics, and analytics accelerator tuning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/S3ATestConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/S3ATestUtils.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/S3ATestUtils.java

## Purpose

Large private test helper for S3A suites. It centralizes live filesystem creation, test property resolution, feature-skipping assumptions, credential/session helpers, configuration cleanup, metrics diffs, file tree generation, stream introspection, encryption checks, status assertions, and small exception/range utilities.

## Important APIs, Types, and Functions

Major APIs include `createTestFileSystem()`, `createTestFileContext()`, `prepareTestConfiguration()`, `getTestProperty*()`, `skipIf*()`/`assume*()` feature gates, `requestSessionCredentials()`, `removeBucketOverrides()`, `removeBaseAndBucketOverrides()`, `createMockStoreContext()`, `createFiles()`/`createDirsAndFiles()`, `MetricDiff`, `verifyFileStatus()`, `verifyDirStatus()`, `getInputStreamStatistics()`, `getS3AInputStream()`, checksum stream assertions, stream type toggles, `etag()`, `sdkClientException()`, and `requestRange()`.

## Control Flow

Static initialization registers deprecated STS keys. Live filesystem creation validates `test.fs.s3a.name`, optionally enables MPU purge, and initializes S3A or FileContext. Property helpers merge configuration defaults with Maven/system-property overrides, ignoring the special `unset` value. File tree helpers build path sets, create directories and files asynchronously on a bounded executor, and wait for completion. Metric helpers snapshot instrumentation counters and compute deltas. Stream helpers unwrap S3A/prefetch streams and use reflection to inspect nested SDK filter streams.

## State, Dependencies, and Integration Points

State includes a static executor, deprecated-key registration, and mutable `MetricDiff` baselines. It integrates with almost every S3A test layer: configuration keys, credentials, STS, S3 Express, analytics accelerator, S3A storage statistics, audit/noop contexts, IOStatistics, Hadoop services, contract utilities, AWS SDK stream wrappers, and object-store feature capabilities.

## Risks and Test Signals

Because this is shared test infrastructure, small semantic changes can broadly alter which tests run or how failures are interpreted. `getCurrentThreadNames()` currently filters for names starting with both `JUnit` and `surefire`, so it appears to drop all normal thread names; lifecycle checks relying on it may miss leaks. Reflection into `FilterInputStream` can break under module-access restrictions. The strongest signals are assumption gating, exact metric deltas, filesystem capability probes, stream type detection, and encryption/status assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/S3ATestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/StorageStatisticsTracker.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/StorageStatisticsTracker.java

## Purpose

Small helper that snapshots a filesystem's `StorageStatistics` long counters and reports differences against later snapshots.

## Important APIs, Types, and Functions

The public API is `mark()`, `compare(Map<String, Long>)`, `compareToCurrent()`, `toString(Map)`, `snapshot()`, and `latestValues()`. `StatsIterator` adapts `StorageStatistics.getLongStatistics()` to an `Iterable`.

## Control Flow

Construction stores the filesystem and immediately captures a baseline snapshot. `mark()` refreshes the baseline. `snapshot()` iterates current long statistics into a map. `compare()` walks baseline entries and records keys whose current values differ.

## State, Dependencies, and Integration Points

State is the tracked `FileSystem` and the current baseline map. It depends on Hadoop `StorageStatistics` and shaded Guava `Joiner`. It is useful in tests that want operation-count deltas without directly reading S3A instrumentation.

## Risks and Test Signals

The diff direction is baseline minus current, which can surprise readers expecting current minus baseline. New counters that appear after the baseline are ignored. Test signal is strongest when the caller knows exact counter names and understands this signed-difference convention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/StorageStatisticsTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestArnResource.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestArnResource.java

## Purpose

Unit tests for parsing S3 access point ARNs and deriving access point endpoints across AWS partitions and services.

## Important APIs, Types, and Functions

Tests call `ArnResource.accessPointFromArn()`, then assert `getName()`, `getOwnerAccountId()`, `getRegion()`, and `getEndpoint()`. The helper `getArnResourceFrom()` builds `arn:partition:service:region:account:accesspoint/name` strings.

## Control Flow

`parseAccessPointFromArn()` loops through standard, GovCloud, and China region/partition pairs and checks parsed fields. Endpoint tests separately validate `s3-accesspoint.<region>.amazonaws.com` and `s3-outposts.<region>.amazonaws.com`. Invalid input is expected to throw `IllegalArgumentException`.

## State, Dependencies, and Integration Points

No persistent state. It depends on AWS SDK `Region`, AssertJ, Hadoop test base logging, and S3A `ArnResource` endpoint construction used by access point client setup.

## Risks and Test Signals

Endpoint expectations are intentionally partial and stable around AWS SDK changes. The tests catch ARN grammar regressions, partition/region field loss, invalid ARN acceptance, and wrong S3 versus S3 Outposts endpoint prefixes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestArnResource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestBucketConfiguration.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestBucketConfiguration.java

## Purpose

Unit tests for per-bucket S3A configuration propagation, credential-provider path patching, and deprecated encryption option resolution.

## Important APIs, Types, and Functions

Tests exercise `S3AUtils.setBucketOption()`, `clearBucketOption()`, `propagateBucketOptions()`, `patchSecurityCredentialProviders()`, `getEncryptionAlgorithm()`, and `buildEncryptionSecrets()`. They also use Hadoop credential-provider APIs to store JCEKS-backed encryption keys.

## Control Flow

`setup()` forces S3A deprecation wiring. Propagation tests build minimal configurations, set bucket-specific values, propagate for a target bucket, and assert base keys, property sources, resolution of `${fs.s3a.base}`, multiple bucket isolation, and skipped unmodifiable keys. Credential tests combine base and S3A-specific provider paths. Encryption tests verify older per-bucket server-side encryption keys override newer global keys, including through a local Java keystore provider.

## State, Dependencies, and Integration Points

State is confined to `Configuration` instances and a temporary JCEKS file. It integrates S3A bucket-option mapping, Hadoop configuration interpolation, credential provider path merging, deprecation mappings, and encryption-secret construction.

## Risks and Test Signals

Bucket option rewriting is fragile because it must avoid loops and must not alter unmodifiable filesystem implementation keys. The strongest signals are exact option values, property source traces, merged credential provider path order, and encryption algorithm/key resolution from both XML-style config and JCEKS secrets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestBucketConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestDataBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestDataBlocks.java

## Purpose

Parameterized unit test for `S3ADataBlocks` upload buffer implementations: disk, byte array, and direct byte buffer. It validates block writes, upload content providers, stream mark/reset behavior, and buffer lifecycle.

## Important APIs, Types, and Functions

The test creates `DiskBlockFactory`, `ArrayBlockFactory`, or `ByteBufferBlockFactory`, then uses `DataBlock.write()`, `dataSize()`, `remainingCapacity()`, `hasCapacity()`, `startUpload()`, `BlockUploadData.getContentProvider()`, and `UploadContentProviders.BaseContentProvider.newStream()`.

## Control Flow

For each buffer type, a 128-byte block is created and loaded with `"test data"`. The content stream is read by single-byte and array reads, `available()` is checked throughout, mark/reset is exercised, a second stream is requested to ensure the first byte-buffer stream closes, and closing the block returns pooled buffers. After block close, creating another stream must fail.

## State, Dependencies, and Integration Points

State includes temporary disk files for disk buffering, in-memory arrays/byte buffers, content provider stream creation counts, and byte-buffer outstanding counts. It depends on contract byte helpers, `ByteBufferInputStream`, temporary directories, and AssertJ.

## Risks and Test Signals

This catches regressions in upload-body replayability, mark/reset support required by AWS request bodies, stream closure, byte-buffer pool leaks, and capacity accounting. Disk behavior is less deeply inspected than byte-buffer outstanding counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestDataBlocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestInstrumentationLifecycle.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestInstrumentationLifecycle.java

## Purpose

Unit test for `S3AInstrumentation` lifecycle with Hadoop metrics registration through `WeakRefMetricsSource`, especially close and double-close behavior.

## Important APIs, Types, and Functions

The test uses `S3AInstrumentation`, `S3AInstrumentation.getMetricsSystem()`, `hasMetricSystem()`, `lookupMetric()`, `getMetricSourceName()`, `close()`, `getIOStatistics()`, Hadoop `MetricsSystem`, and `WeakRefMetricsSource`.

## Control Flow

It creates instrumentation for a sample S3A URI, verifies a metrics system is active and a counter metric can be looked up, checks the registered source is a weak reference pointing to the instrumentation instance, closes it, verifies IO statistics and metric lookup still work, forces a new metrics system on demand, then closes the instrumentation a second time and asserts the new metrics system is not closed.

## State, Dependencies, and Integration Points

State is global metrics-system state plus the instrumentation instance's metrics source registration. It integrates S3A instrumentation with Hadoop metrics2 weak-reference lifecycle semantics.

## Risks and Test Signals

Global metrics state makes the test sensitive to ordering and leftover metrics from other tests. It catches leaks, double-close side effects, and regressions where closed instrumentation cannot tolerate later metric updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestInstrumentationLifecycle.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestInvoker.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestInvoker.java

## Purpose

Unit test suite for `Invoker`, `S3ARetryPolicy`, and S3A exception translation/retry behavior. It focuses on 5xx handling, throttling, connectivity failures, shaded timeout class matching, EOF-like SDK errors, non-idempotent operations, and quiet evaluation helpers.

## Important APIs, Types, and Functions

Key APIs are `Invoker.retry()`, `Invoker.quietlyEval()`, `S3ARetryPolicy.shouldRetry()`, `S3AUtils.translateException()`, `extractException()`, and AWS SDK exception builders. Constants configure fast retry intervals, active retry limits, and retrying HTTP 5xx errors.

## Control Flow

Tests translate S3 status codes to specific S3A IO exceptions, assert retry decisions for 500/501/503/504 and generic 5xx responses under enabled/disabled policies, repeatedly retry operations that fail until a counter threshold, and verify non-idempotent bad requests are not retried. Timeout tests wrap local, Hadoop, Apache HTTP, execution, and completion exceptions to ensure extraction and classname-based matching. Quiet helpers are tested for void and return-value behavior.

## State, Dependencies, and Integration Points

State includes retry count, retry policies built from `Configuration`, and synthetic AWS exceptions. It integrates Hadoop retry policy contracts, AWS SDK v2 exception hierarchy, shaded Apache HTTP classes, and S3A's IO exception taxonomy.

## Risks and Test Signals

These tests encode precise retry policy semantics. They are sensitive to AWS SDK exception text/class changes and configuration defaults for 5xx retries. Strong signals include exact translated exception classes, retry/fail decisions, retry counters, and no retry of NPEs or interrupted IO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestInvoker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestListing.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestListing.java

## Purpose

Narrow unit test for the listing helper that converts provided `S3AFileStatus` arrays into `RemoteIterator` instances.

## Important APIs, Types, and Functions

The file constructs an `S3AFileStatus` and calls `Listing.toProvidedFileStatusIterator()`, then uses `RemoteIterator.hasNext()` and `next()`.

## Control Flow

The test creates a one-element status array, obtains the iterator, verifies `hasNext()` before reading, checks the first returned element is the original status, verifies the iterator is exhausted, and asserts another `next()` raises `NoSuchElementException`.

## State, Dependencies, and Integration Points

State is only the in-memory iterator cursor. The test depends on `AbstractS3AMockTest`, `S3AFileStatus`, `Path`, and LambdaTestUtils exception interception.

## Risks and Test Signals

This protects iterator contract behavior for list implementations. It is small but catches off-by-one or invalid exhausted-iterator behavior that can affect callers consuming S3A listings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestListing.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AAWSCredentialsProvider.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AAWSCredentialsProvider.java

## Purpose

Comprehensive unit suite for S3A AWS credentials provider configuration, instantiation, remapping, resolution, exception handling, reference counting, and concurrent lazy initialization.

## Important APIs, Types, and Functions

The suite exercises `createAWSCredentialProviderList()`, `buildAWSProviderList()`, `AWSCredentialProviderList.resolveCredentials()/share()/close()`, `CredentialProviderListFactory` mappings, profile credentials, IAM instance credentials, `AbstractSessionCredentialsProvider`, `S3AUtils.getTrimmedStringCollectionSplitByEquals()`, and `S3ATestUtils.authenticationContains()`.

## Control Flow

Early tests assert failures for wrong provider classes, abstract classes, missing classes, bad constructors, constructor exceptions, and invalid factory return types. Chain tests validate configured, default, profile, anonymous, simple, temporary, IAM, environment, and remapped providers. Provider-list tests validate credential resolution, no-auth retry behavior, close/ref-count semantics, IOE propagation, and non-SDK exception wrapping. Concurrency tests run four threads against slow and failing session providers, checking cached success or cached initialization error. String-splitting tests cover whitespace, duplicates, empty entries, and invalid `key=value` forms.

## State, Dependencies, and Integration Points

State includes Hadoop `Configuration`, temp profile files, credential provider lists with reference counts, cached session-provider credentials/errors, and thread pools. It integrates AWS SDK v2 credential providers, legacy provider-name remapping, S3A auth classes, public dataset URI helpers, Hadoop retry policy, and configuration parsing.

## Risks and Test Signals

Provider instantiation is reflection-heavy and sensitive to constructor/factory signatures. Concurrency tests are important for race conditions in lazy credentials. Strong signals include exact provider class order, exception text/classes, no retry on auth failures, ref-count transitions to closed state, and deterministic split-map validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AAWSCredentialsProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3ABlockOutputStream.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3ABlockOutputStream.java

## Purpose

Unit tests for `S3ABlockOutputStream` edge behavior around closed streams, abort semantics, multipart part-number validation, and `Syncable` downgrade behavior.

## Important APIs, Types, and Functions

The test builds `S3ABlockOutputStream.BlockOutputStreamBuilder` with mocked executor, progress callback, block factory, write helper, put tracker, put options, and IOStatistics aggregator. It uses `flush()`, `abort()`, `checkOpen()`, `write()`, `close()`, `hflush()`, `hsync()`, and `WriteOperationHelper.newUploadPartRequestBuilder()`.

## Control Flow

`setUp()` creates a spied stream from the mock builder. One test forces `checkOpen()` to throw and verifies `flush()` becomes a no-op when closed. Multipart limits are tested by building part 1 successfully and intercepting `PathIOException` for part 50000. Abort tests ensure abort closes the stream, write checks open state, and close after abort is harmless. Sync tests distinguish unsupported `hsync()` from configured downgrade.

## State, Dependencies, and Integration Points

State is local mock/spied stream state and a mocked `S3AFileSystem` request factory. It integrates output stream builder wiring, multipart request validation, audit noop support, write operation callbacks, and Hadoop `ClosedIOException`.

## Risks and Test Signals

Mocked builder pieces mean this tests stream contract edges rather than upload success. It catches part-limit regressions, abort/close idempotency issues, and accidental reintroduction of unsupported `hsync()` failures when downgrade is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3ABlockOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3ADeleteOnExit.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3ADeleteOnExit.java

## Purpose

Unit tests for S3A delete-on-exit close processing and request-factory initialization failure for invalid checksum algorithm configuration.

## Important APIs, Types, and Functions

Nested `TestS3AFileSystem` extends `S3AFileSystem`, counts `deleteOnExit()` calls, and decrements count in `deleteWithoutCloseCheck()`. Tests use S3 mock `headObject()`, `deleteOnExit()`, `close()`, and `S3AFileSystem.initialize()`.

## Control Flow

`testDeleteOnExit()` initializes a test filesystem against the mock bucket, stubs `headObject()` for `/file`, registers delete-on-exit, closes the filesystem, and asserts the counter returns to zero through close-time deletion. `testCreateRequestFactoryWithInvalidChecksumAlgorithm()` sets `fs.s3a.checksum.algorithm` to `INVALID` and expects initialization to throw a clear `IllegalArgumentException`.

## State, Dependencies, and Integration Points

State includes filesystem delete-on-exit tracking, mocked S3 object metadata, and configuration. It integrates S3A close processing, delete without close checks, request factory creation, checksum algorithm parsing, and Mockito request matching.

## Risks and Test Signals

The counter-based subclass directly observes internal close path behavior. It catches regressions where delete-on-exit entries are skipped on close, close checks prevent cleanup, or invalid checksum configuration fails later with less useful errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3ADeleteOnExit.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AEndpointParsing.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AEndpointParsing.java

## Purpose

Focused unit tests for deriving AWS regions from standard S3 and VPC endpoint hostnames.

## Important APIs, Types, and Functions

Both tests call `DefaultS3ClientFactory.getS3RegionFromEndpoint(endpoint, false)` and compare the result with AWS SDK `Region.of(...)`.

## Control Flow

`testVPCEndpoint()` parses `vpce-...s3.us-west-2.vpce.amazonaws.com` and expects `us-west-2`. `testNonVPCEndpoint()` parses `s3.eu-west-1.amazonaws.com` and expects `eu-west-1`.

## State, Dependencies, and Integration Points

There is no state. It depends on `AbstractS3AMockTest`, AssertJ, AWS SDK `Region`, and endpoint parsing in the default S3 client factory.

## Risks and Test Signals

Endpoint parsing is easy to break with VPC endpoint hostname shapes. These tests catch incorrect token selection for both VPC and classic endpoints, but do not cover dualstack, FIPS, China, GovCloud, or custom endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AEndpointParsing.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AExceptionTranslation.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AExceptionTranslation.java

## Purpose

Unit suite for translating AWS SDK, S3 service, credential, audit, timeout, and HTTP channel exceptions into Hadoop/S3A exception classes, and for verifying retry policy decisions on translated channel/timeouts.

## Important APIs, Types, and Functions

It exercises `S3AUtils.translateException()`, `extractException()`, `containsInterruptedException()`, `AWSCredentialProviderList.maybeTranslateCredentialException()`, `AuditIntegration.maybeTranslateAuditException()`, `ErrorTranslation.maybeExtractChannelException()`, and `S3ARetryPolicy.shouldRetry()`.

## Control Flow

Tests map HTTP statuses: 301 with bucket-region header to `AWSRedirectException`, 400 to bad request, 401/403 to access denied, 404/410 to not found, NoSuchBucket to `UnknownStoreException`, 416 to `RangeNotSatisfiableEOFException`, generic S3/service/client errors to S3A IO wrappers, and 504/API call timeouts to `AWSApiCallTimeoutException`. Additional tests unwrap interrupted exceptions, translate nested credential/audit failures, extract shaded and unshaded no-response channel errors, recognize OpenSSL stream-closed text, and map S3 Express precondition failure to `RemoteFileChangedException`.

## State, Dependencies, and Integration Points

State is limited to a retry policy initialized per test and synthetic AWS SDK exception objects. It integrates AWS SDK v2 error details and HTTP response headers, S3A audit and credential layers, shaded/unshaded Apache HTTP exceptions, and Hadoop IO/retry contracts.

## Risks and Test Signals

The suite is sensitive to exact AWS SDK exception hierarchies, error-code strings, and message content. Strong signals include translated class, preserved status code, region text in redirect messages, unwrapped causes for credential/audit errors, and retry decisions for timeout/channel EOF exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AExceptionTranslation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AGetFileStatus.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AGetFileStatus.java

## Purpose

Mock-S3 unit tests for `S3AFileSystem.getFileStatus()` classification of files, fake directory markers, implicit directories, root, and missing paths.

## Important APIs, Types, and Functions

Tests mock `S3Client.headObject()`, `listObjects()`, and `listObjectsV2()`, then call `fs.getFileStatus(Path)`. Helpers match `HeadObjectRequest` and set up V1/V2 list responses with `CommonPrefix` and `S3Object`.

## Control Flow

`testFile()` stubs object metadata and verifies file status path, length, mod time, and no erasure coding. `testFakeDirectory()` makes the object key miss but `key/` list contain a zero-size marker and expects a directory. `testImplicitDirectory()` makes metadata miss and list return a common prefix. `testRoot()` treats `/` as an existing directory despite misses. `testNotFound()` makes all probes empty and expects `FileNotFoundException`.

## State, Dependencies, and Integration Points

State is the mocked S3 client behavior inherited from `AbstractS3AMockTest`. It integrates S3A status probing, directory-marker interpretation, V1/V2 listing fallbacks, erasure-coding status expectations, and path qualification.

## Risks and Test Signals

These tests encode S3A's object-store directory model. They catch probe-order or request-key regressions, root handling mistakes, and accidental erasure-coding metadata changes. They do not exercise live object store consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AGetFileStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AInputPolicies.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AInputPolicies.java

## Purpose

Parameterized unit test for `S3AInputStream.calculateRequestLimit()` under normal, sequential, and random input policies.

## Important APIs, Types, and Functions

The test uses `S3AInputPolicy` enum values and feeds target position, requested length, content length, readahead, and expected request limit into `calculateRequestLimit()`.

## Control Flow

`data()` enumerates cases for unknown length, zero content length, full-file reads, explicit read lengths, readahead-limited random reads, zero/one-byte reads under random policy, and target positions past object length. The parameterized test initializes fields and asserts the calculated limit equals the expected value with a detailed argument string.

## State, Dependencies, and Integration Points

No external state or S3 calls. It integrates directly with S3A input stream range-planning logic and JUnit parameterized tests.

## Risks and Test Signals

The matrix documents range-request semantics. It catches regressions where random policy over-fetches or under-fetches, normal/sequential policy fails to read to object end, or out-of-range positions are not capped at content length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AInputPolicies.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AInputStreamRetry.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AInputStreamRetry.java

## Purpose

Unit tests for `S3AInputStream` recovery when reads or reopen GET requests fail. The suite validates retry behavior for single-byte reads, buffer reads, `readFully()`, repeated seek/read operations, range parsing, and out-of-range responses.

## Important APIs, Types, and Functions

The file constructs `S3AInputStream` directly using `ObjectReadParameters`, `ObjectInputStreamCallbacks`, `S3ObjectAttributes`, and `S3AReadOpContext`. Helpers include `failingInputStreamCallbacks()`, `maybeFailInGetCallback()`, `mockInputStreamCallback()`, `awsServiceException()`, and `mockedInputStream()`.

## Control Flow

Basic tests inject streams that fail during early reads and one GET attempt, then eventually return the test string `012345678ABCDEF`; reads must return correct bytes after retries. Repeated seek tests fail every second GET with a no-response SDK exception and verify ten seek/read cycles still read offset zero. Callback logic increments attempt count, optionally throws, parses the Range header, rejects invalid ranges with 416, skips to the requested start, and returns an AWS `ResponseInputStream`.

## State, Dependencies, and Integration Points

State includes callback attempt counters, mock filesystem read context, S3 object metadata such as eTag/version ID, and synthetic response streams. It integrates S3A read contexts, object attributes, AWS SDK response streams, audit noop spans, future submission callbacks, and `S3ATestUtils.requestRange()`.

## Risks and Test Signals

The two repeated seek tests currently have identical failure setup despite different names, so they may not distinguish stream-closed failures from no-response failures. Strong signals include correct bytes after retries, retry of GET failures during reopen, 416 handling for invalid ranges, and preservation of position semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AInputStreamRetry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AProxy.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AProxy.java

## Purpose

Unit tests verifying S3A proxy configuration is translated into AWS SDK Apache HTTP proxy configuration with the correct scheme.

## Important APIs, Types, and Functions

Tests set `Constants.PROXY_HOST`, `PROXY_PORT`, and `PROXY_SECURED`, then call `AWSClientConfig.createProxyConfiguration(conf, "testBucket")` and inspect `ProxyConfiguration.scheme()`.

## Control Flow

`testProxyHttp()` creates an unsecured proxy config and expects `http`. `testProxyHttps()` creates a secured proxy config and expects `https`. `testProxyDefault()` sets only a proxy host and expects the default scheme `http`. `verifyProxy()` builds the proxy configuration and asserts the scheme.

## State, Dependencies, and Integration Points

State is limited to Hadoop `Configuration`. It integrates S3A proxy options, per-bucket-aware AWS client config creation, and AWS SDK Apache proxy configuration.

## Risks and Test Signals

The test only checks scheme, not host, port, credentials, or no-proxy lists. It catches regressions where `fs.s3a.proxy.secured` is ignored or defaults change unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AProxy.java -->
