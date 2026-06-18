# Research: subset-b-007576

This grouped report covers Hadoop S3A filesystem support classes under `sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AInstrumentation.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AInstrumentation.java

## Purpose
`S3AInstrumentation` is the central metrics and IOStatistics implementation for an `S3AFileSystem` instance. It registers the filesystem with Hadoop Metrics2, declares every `Statistic` counter/gauge/duration, exposes `IOStatisticsSource`, and creates per-stream/per-committer/per-token statistics adapters.

## Important APIs, Types, and Functions
Key APIs are `getIOStatistics()`, `getDurationTrackerFactory()`, `trackDuration()`, `createMetricsUpdatingStore()`, `newInputStreamStatistics()`, `newOutputStreamStatistics()`, `newCommitterStatistics()`, `newDelegationTokenStatistics()`, `incrementCounter()`, `incrementGauge()`, `recordDuration()`, `dump()`, `toMap()`, and `close()`. Internal types include `MetricUpdatingDurationTracker`, `MetricDurationTrackerFactory`, `InputStreamStatistics`, `OutputStreamStatistics`, `CommitterStatisticsImpl`, `DelegationTokenStatisticsImpl`, `MetricsToMap`, and `MetricsUpdatingIOStatisticsStore`.

## Control Flow and State
Construction tags the registry with filesystem id and bucket, creates counters/gauges/duration counters from the `Statistic` enum, registers a weak Metrics2 source, builds the instance `IOStatisticsStore`, then pairs IOStatistics duration tracking with Metrics2 counter updates. Stream statistics collect local atomic counters during reads/writes and merge them into filesystem-wide metrics on `close()`, `unbuffered()`, or stream leak handling. Output statistics track block upload queue/active gauges and merge upload counters on close. `close()` unregisters the metrics source, stops quantiles, decrements the active source count, and shuts down the shared metrics system when the last source closes.

## State and Persistence Behavior
State is in-memory only: a static metrics system and source counters, one Metrics2 registry per filesystem, a filesystem-level `IOStatisticsStore`, and per-stream stores. Atomic counters support cross-thread stream activity, but merge points are explicit and some filesystem thread-local `FileSystem.Statistics` updates happen only during close. Quantiles start background work and must be stopped.

## Dependencies and Integration Points
The class integrates with Hadoop Metrics2, `WeakRefMetricsSource`, `IOStatisticsBinding`, `Statistic`, `StoreStatisticNames`, `StreamStatisticNames`, `S3AInputStreamStatistics`, `BlockOutputStreamStatistics`, committer statistics, delegation token statistics, and filesystem `FileSystem.Statistics`. It is consumed by S3A filesystem/store/read/write code to report object, stream, audit, committer, throttle, and duration metrics.

## Risks and Test Signals
Risks include stale metrics if streams are not closed/merged, gauge imbalance on failed uploads/prefetches, static metrics-system lifecycle races, quantile scheduler leakage if `close()` is skipped, and incomplete synchronization between Metrics2 counters and IOStatistics for specialized stores. Tests should verify metrics source registration/unregistration, counter/gauge increments, duration success/failure counters, input stream merge on close/unbuffer/leak, output stream gauge cleanup, committer counter updates, and storage statistics visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AInstrumentation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AInternals.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AInternals.java

## Purpose
`S3AInternals` is an unstable, limited-private diagnostics/testing interface that exposes low-level S3A filesystem internals and direct S3 operations beyond the normal public `FileSystem` API.

## Important APIs, Types, and Functions
The interface exposes `getAmazonS3Client(String)`, `getStore()`, `getBucketLocation()`, `getBucketLocation(String)`, `getObjectMetadata(Path)`, `shareCredentials(String)`, `getBucketMetadata()`, `isMultipartCopyEnabled()`, and `abortMultipartUploads(Path)`.

## Control Flow and State
This file defines no implementation. Implementations are expected to route calls into `S3AFileSystem` and `S3AStore`, wrapping external entry points with audit spans and translated retry behavior where annotated. `shareCredentials()` increments a reference count in the returned provider list and transfers close responsibility to the caller.

## State and Persistence Behavior
There is no local state. The interface provides access to live filesystem state: the active `S3Client`, store, credentials, bucket metadata, and multipart upload state in S3.

## Dependencies and Integration Points
It depends on AWS SDK `S3Client`, `HeadBucketResponse`, `HeadObjectResponse`, Hadoop `Path`, audit annotations, S3A retry annotations, `AWSCredentialProviderList`, and `S3AStore`. Callers include tests, diagnostics, and advanced integrations that need direct client/store access.

## Risks and Test Signals
The largest risk is bypassing normal auditing, retry translation, and filesystem invariants when using the raw client. Tests should cover audit rejection behavior for out-of-span raw operations, reference-count closure for shared credentials, translated errors for bucket/object metadata, and abort-multipart behavior when paths or buckets are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AInternals.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ALocatedFileStatus.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ALocatedFileStatus.java

## Purpose
`S3ALocatedFileStatus` adapts an `S3AFileStatus` into a Hadoop `LocatedFileStatus` while preserving S3-specific metadata: ETag, version id, and empty-directory tristate.

## Important APIs, Types, and Functions
The constructor accepts an `S3AFileStatus` and block locations. Public APIs are deprecated `getETag()`, `getEtag()`, `getVersionId()`, `toS3AFileStatus()`, `equals()`, `hashCode()`, and `toString()`.

## Control Flow and State
Construction delegates base file metadata to `LocatedFileStatus`, copies S3 metadata from the input status, and stores empty-directory state. `toS3AFileStatus()` reconstructs an S3A status from the located status fields plus preserved S3 metadata. Equality/hash behavior intentionally delegates to the base path-based implementation.

## State and Persistence Behavior
Instances are immutable after construction aside from superclass behavior. They are serializable through `LocatedFileStatus` conventions and carry only copied metadata, not live S3 state.

## Dependencies and Integration Points
The class depends on Hadoop `LocatedFileStatus`, `BlockLocation`, `EtagSource`, `S3AFileStatus`, and `Tristate`. It is used by listing/open status paths that need both block-location API compatibility and object version/change-detection metadata.

## Risks and Test Signals
Risks include losing S3 metadata when converting between status types, callers using deprecated `getETag()`, and path-only equality surprising code that expects version-sensitive comparison. Tests should verify ETag/version preservation, directory tristate preservation, conversion back to `S3AFileStatus`, and compatibility with list located status APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ALocatedFileStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AOpContext.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AOpContext.java

## Purpose
`S3AOpContext` is a base operation context struct for S3A filesystem operations, carrying retry invocation, optional filesystem statistics, instrumentation context, and destination file status.

## Important APIs, Types, and Functions
The main API is the constructor plus `getInvoker()`, `getStats()`, and `getDstFileStatus()`. It extends `ActiveOperationContext`, which contributes an operation id and statistics context.

## Control Flow and State
Construction creates a new operation id, validates `Invoker`, `S3AStatisticsContext`, and destination status, then stores them for downstream operation code. There is no behavior beyond accessors; operation-specific context belongs in subclasses such as `S3AReadOpContext`.

## State and Persistence Behavior
State is per-operation and in-memory. It does not persist changes but carries references to shared retry/statistics infrastructure and the destination status captured during preflight checks.

## Dependencies and Integration Points
Dependencies include `Invoker`, `FileSystem.Statistics`, `FileStatus`, `S3AStatisticsContext`, and `ActiveOperationContext`. It integrates with filesystem operations that need a common bundle of retry, stats, and destination-state information.

## Risks and Test Signals
Risks are mostly null/incorrect context wiring and stale destination status if callers reuse a context across changing remote state. Tests should assert constructor validation, unique operation ids, correct stat/invoker propagation, and subclass behavior using `dstFileStatus`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AOpContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AReadOpContext.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AReadOpContext.java

## Purpose
`S3AReadOpContext` extends `S3AOpContext` with all read/open-specific configuration needed to create and operate an S3A input stream.

## Important APIs, Types, and Functions
It exposes builder-style setters `withInputPolicy()`, `withChangeDetectionPolicy()`, `withReadahead()`, `withAuditSpan()`, and `withAsyncDrainThreshold()`, validation via `build()`, and getters for path, read invoker, input policy, change detection, readahead, audit span, async drain threshold, `VectoredIOContext`, `IOStatisticsAggregator`, and `ExecutorServiceFuturePool`.

## Control Flow and State
The constructor stores immutable references for path, vectored IO, statistics aggregation, and future pool. Callers then set required mutable fields and call `build()`, which verifies required policies/spans and non-negative numeric thresholds. The resulting object is passed to read stream creation and async/vector read code.

## State and Persistence Behavior
The context is per-read and in-memory. It is mutable until build but not made immutable afterward; callers are expected to treat it as configured state. It holds references to audit and async execution state but persists no data.

## Dependencies and Integration Points
Dependencies include `S3AInputPolicy`, `ChangeDetectionPolicy`, `AuditSpan`, `VectoredIOContext`, `IOStatisticsAggregator`, `ExecutorServiceFuturePool`, `Invoker`, `FileStatus`, and `S3AStatisticsContext`. It integrates with `S3AInputStream` construction, vectored reads, async prefetch/drain behavior, and change tracking.

## Risks and Test Signals
Risks include forgotten `build()` validation, mutation after validation, null future/aggregator handling, negative readahead/drain thresholds, and losing audit span context for later reads. Tests should verify required field checks, threshold validation, propagation to stream constructors, and correct vectored/async settings in read behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AReadOpContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ARetryPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ARetryPolicy.java

## Purpose
`S3ARetryPolicy` defines how S3A retries translated Hadoop/AWS failures. It separates normal IO retry limits, throttling retry limits, connectivity failures, non-idempotent operation filtering, and fail-fast exceptions.

## Important APIs, Types, and Functions
The primary API is `shouldRetry(Exception, int, int, boolean)`. Constructor-created policies include `baseExponentialRetry`, `retryIdempotentCalls`, `throttlePolicy`, `connectivityFailure`, `retryAwsClientExceptions`, and `http5xxRetryPolicy`. Extension hooks are `createThrottleRetryPolicy()` and `createExceptionMap()`. Internal filters are `IdempotencyRetryFilter`, `FailNonIOEs`, and unused-ready `RetryFromAWSClientExceptionPolicy`.

## Control Flow and State
Construction reads retry counts/intervals from configuration, builds exponential policies, creates a class-exact exception map, and wraps it in `retryByException()`. `shouldRetry()` translates raw AWS SDK exceptions through `S3AUtils.translateException()` before policy lookup, logs the probe, then delegates to the composed policy.

## State and Persistence Behavior
State is immutable after construction and backed by configuration-derived values. It persists no retry history itself; Hadoop retry callers pass retry counters on each probe.

## Dependencies and Integration Points
Dependencies include Hadoop `RetryPolicy`, S3A exception classes, `S3AUtils`, AWS SDK `SdkException`, and configuration constants such as `RETRY_LIMIT`, `RETRY_INTERVAL`, `RETRY_THROTTLE_LIMIT`, and `RETRY_HTTP_5XX_ERRORS`. It is used by `Invoker` and store/filesystem operations annotated with retry semantics.

## Risks and Test Signals
Risks include exact-class mapping missing subclasses, unsafe retries for non-idempotent calls, under/over-retrying 5xx or throttled failures, and behavior changes when AWS SDK exception translation changes. Tests should cover translated status codes, throttling retry even for non-idempotent calls, fail-fast auth/not-found/unsupported cases, connectivity retries, HTTP 5xx configuration, and raw `SdkException` handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ARetryPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AStorageStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AStorageStatistics.java

## Purpose
`S3AStorageStatistics` adapts S3A `IOStatistics` into Hadoop `StorageStatistics` with the scheme/name expected by filesystem consumers.

## Important APIs, Types, and Functions
The class exposes constant `NAME = "S3AStorageStatistics"` and two constructors: one wrapping a provided `IOStatistics`, and one wrapping `emptyStatistics()`.

## Control Flow and State
Construction delegates to `StorageStatisticsFromIOStatistics` with name `S3AStorageStatistics` and scheme `s3a`. There is no additional logic.

## State and Persistence Behavior
State is whatever `IOStatistics` instance is supplied. The default constructor is an empty, non-updating statistics view.

## Dependencies and Integration Points
Dependencies are `IOStatistics`, `StorageStatisticsFromIOStatistics`, and `IOStatisticsBinding.emptyStatistics()`. `S3AFileSystem#getStorageStatistics()` can expose this adapter to Hadoop callers.

## Risks and Test Signals
Risks are low, but using the default constructor in live contexts would hide actual counters. Tests should verify the name/scheme, dynamic reflection of wrapped IOStatistics counters, and empty behavior for the no-arg constructor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AStorageStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AStore.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AStore.java

## Purpose
`S3AStore` is the low-level store contract for S3A. It centralizes AWS client management, capacity acquisition, request construction, object IO, upload completion, temporary-file allocation, stream capabilities, and statistics hooks behind a mockable service interface.

## Important APIs, Types, and Functions
The interface extends `ClientManager`, `IOStatisticsSource`, `ObjectInputStreamFactory`, `PathCapabilities`, and `Service`. Key APIs include capacity methods, `getStoreContext()`, `getDurationTrackerFactory()`, `getStatisticsContext()`, `getRequestFactory()`, stats increment methods, `deleteObjects()`, `deleteObject()`, `headObject()`, `getRangedS3Object()`, `uploadPart()`, `putObject()`, `waitForUploadCompletion()`, `completeMultipartUpload()`, `getDirectoryAllocator()`, `createTemporaryFileForWriting()`, `inputStreamHasCapability()`, and default `hasCapability()`.

## Control Flow and State
This file defines a contract, not an implementation. Implementations are expected to acquire read/write capacity inside retry loops, update stats around operations, perform raw or translated retry behavior according to annotations, delegate upload work to the AWS transfer manager, and expose service lifecycle through `init/start/stop`.

## State and Persistence Behavior
Implementations own persistent in-memory clients, transfer managers, rate limiters, statistics, request factories, and temporary-file allocator state. Remote persistence occurs in S3 objects, multipart uploads, and delete results.

## Dependencies and Integration Points
Dependencies include AWS SDK S3 request/response types, transfer manager upload types, Hadoop service and filesystem capability APIs, `StoreContext`, `RequestFactory`, `S3AFileSystemOperations`, `ChangeTracker`, `Invoker`, and statistics contexts. It is the main integration seam between `S3AFileSystem`, stream classes, and AWS clients.

## Risks and Test Signals
Risks include missing lifecycle initialization, incorrect retry annotation handling, request bodies being closed too early, capacity accounting drift, swallowed delete 404 semantics masking bucket errors, async upload source lifetime bugs, and stats inaccuracies. Tests should mock this interface for filesystem logic and integration-test delete, ranged GET, HEAD with change tracking, multipart part upload, transfer-manager PUT, completion error translation, and temporary file allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AUtils.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AUtils.java

## Purpose
`S3AUtils` is a broad static utility class for S3A exception translation, status construction, reflection-based plugin loading, credential/password lookup, configuration validation, per-bucket option propagation, iterator helpers, encryption secret resolution, cleanup helpers, path filters, byte-range formatting, and classloader isolation.

## Important APIs, Types, and Functions
Major APIs include `translateException()`, `extractException()`, `isThrottleException()`, `createFileStatus()`, `createUploadFileStatus()`, `objectRepresentsDirectory()`, `getInstanceFromReflection()`, `getAWSAccessKeys()`, `lookupPassword()`, `intOption()`, `longOption()`, `longBytesOption()`, `getMultipartSizeProperty()`, `validateOutputStreamConfiguration()`, `checkDiskBuffer()`, `propagateBucketOptions()`, listing helpers, `patchSecurityCredentialProviders()`, `lookupBucketSecret()`, `getS3EncryptionKey()`, `getEncryptionAlgorithm()`, `buildEncryptionSecrets()`, bucket option setters/getters, `maybeAddTrailingSlash()`, `formatRange()`, and `maybeIsolateClassloader()`.

## Control Flow and State
Exception translation first processes encryption-client wrappers, then distinguishes client-side SDK failures from service responses. Client-side failures are mapped through interrupt/EOF/audit/credential/inner-IO/timeout handling; service failures switch on HTTP status and S3 error code to produce precise Hadoop/S3A IOExceptions. Credential lookup applies per-bucket long and short keys before global keys and can read credential providers. Encryption setup resolves algorithm and key across new/deprecated bucket/global keys, validates key requirements, and returns `EncryptionSecrets`.

## State and Persistence Behavior
The class is stateless except for constants and static path filters. It mutates supplied `Configuration` instances in bucket option helpers, credential-provider patching, and classloader isolation. It never persists data directly but reads secrets from configuration and credential providers.

## Dependencies and Integration Points
Dependencies include AWS SDK exceptions and S3 models, S3A exception classes, audit and credential translation helpers, Hadoop `Configuration`, `FileSystem`, `Path`, `RemoteIterator`, credential provider utilities, `S3AEncryption`, `EncryptionSecrets`, and S3A constants. It is used across filesystem initialization, request execution, listing/status creation, credentials, encryption, and tests.

## Risks and Test Signals
Risks include brittle message-based EOF detection, accidental secret exposure in diagnostics, precedence mistakes in bucket/global/deprecated credential keys, reflection compatibility bugs, invalid encryption algorithm/key combinations, config mutation surprises, and status misclassification of directory markers. Tests should cover HTTP status translation, nested interruption/timeout extraction, per-bucket password precedence, JCEKS fallback, SSE-C/SSE-S3/KMS/CSE validation, multipart buffer validation, reflection constructor/factory order, bucket option propagation exclusions, and range/header formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ClientFactory.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ClientFactory.java

## Purpose
`S3ClientFactory` defines the pluggable factory contract for creating synchronous S3 clients, asynchronous S3 clients, and S3 transfer managers. It also defines a stable parameter object so external implementations can tolerate new settings.

## Important APIs, Types, and Functions
Factory APIs are `createS3Client()`, `createS3AsyncClient()`, and `createS3TransferManager()`. Nested `S3ClientCreationParameters` carries credentials, endpoint, headers, metrics, CSE flags/materials, path-style access, requester-pays, interceptors, user-agent suffix, path URI, multipart sizes, transfer executor, region, S3 Express flags, checksum validation/calculation, MD5 headers, FIPS, and analytics accelerator settings through builder-style `with...` methods and getters.

## Control Flow and State
The interface has no implementation. Callers build a mutable `S3ClientCreationParameters` object, chaining setters, then pass it to a factory implementation. The factory reads the flags to configure AWS SDK clients and transfer manager behavior.

## State and Persistence Behavior
The parameter object is mutable and exposes a mutable headers map. It persists no external state, but it may contain live credential providers, interceptors, executor references, metrics collectors, and encryption materials used by clients after creation.

## Dependencies and Integration Points
Dependencies include AWS SDK `S3Client`, `S3AsyncClient`, `S3TransferManager`, credentials providers, execution interceptors, `StatisticsFromAwsSdk`, `CSEMaterials`, and S3A constants. HBase HBoss tests implement this interface, so source/binary compatibility is an explicit integration concern.

## Risks and Test Signals
Risks include mutable parameters being changed after client creation, external factory breakage when method contracts change, missing sensitive fields in `toString()`, misconfigured S3 Express/FIPS/checksum combinations, and header map mutation races. Tests should cover parameter defaults, fluent setters/getters, factory compatibility, transfer-manager executor propagation, and client creation with requester-pays, interceptors, encryption, and region/endpoint options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ClientFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ListRequest.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ListRequest.java

## Purpose
`S3ListRequest` is a version-independent wrapper around AWS S3 ListObjects v1 and v2 request types.

## Important APIs, Types, and Functions
Static constructors `v1(ListObjectsRequest)` and `v2(ListObjectsV2Request)` create the wrapper. Accessors are `isV1()`, `getV1()`, `getV2()`, and `toString()`.

## Control Flow and State
The private constructor stores exactly one request slot by convention. `isV1()` dispatches all behavior. `toString()` formats bucket, prefix, delimiter, max keys, and requester-pays value from the active request.

## State and Persistence Behavior
State is immutable references to AWS SDK request objects. The wrapper persists no remote state and performs no validation that the active request is non-null beyond factory discipline.

## Dependencies and Integration Points
Dependencies are AWS SDK `ListObjectsRequest` and `ListObjectsV2Request`. It is used by S3A listing code to abstract over list API versions while preserving useful debug logging.

## Risks and Test Signals
Risks include null requests accepted by static factories, misuse of the inactive getter, and behavior drift between v1/v2 request fields. Tests should cover v1/v2 dispatch, string formatting, requester-pays propagation, and null-request handling expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ListRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ListResult.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ListResult.java

## Purpose
`S3ListResult` is a version-independent wrapper around AWS S3 ListObjects v1 and v2 responses.

## Important APIs, Types, and Functions
Static constructors `v1()` and `v2()` require non-null responses. Public APIs are `isV1()`, `getV1()`, `getV2()`, `getS3Objects()`, `isTruncated()`, `getCommonPrefixes()`, `hasPrefixesOrObjects()`, `representsEmptyDirectory()`, and `logAtDebug()`.

## Control Flow and State
The wrapper dispatches to the active response based on whether the v1 field is set. `representsEmptyDirectory()` treats a listing as an empty directory only when exactly one object key equals the directory marker and there are no common prefixes. Debug logging enumerates object summaries and prefixes.

## State and Persistence Behavior
State is a pair of response references with exactly one intended to be non-null. It is otherwise read-only and does not retain pagination cursor state beyond the AWS response.

## Dependencies and Integration Points
Dependencies are AWS SDK `ListObjectsResponse`, `ListObjectsV2Response`, `S3Object`, `CommonPrefix`, Java streams, and SLF4J. It integrates with S3A listing/status logic that must support both list API versions and directory marker detection.

## Risks and Test Signals
Risks include null collections from unexpected SDK behavior, incorrect empty-directory classification under versioned or third-party stores, and inactive getter misuse. Tests should cover object/prefix extraction for both versions, truncated flags, directory-marker-only listings, non-empty listings with prefixes, and debug logging not failing on empty results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ListResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ObjectAttributes.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ObjectAttributes.java

## Purpose
`S3ObjectAttributes` is an immutable value holder for object metadata needed by streams and other S3A code without requiring a full file status object.

## Important APIs, Types, and Functions
The constructor captures bucket, Hadoop path, S3 key, server-side encryption algorithm/key, ETag, version id, and length. Getters expose each field.

## Control Flow and State
There is no control flow beyond construction and access. The class reduces constructor parameter sprawl in consumers such as `S3AInputStream`.

## State and Persistence Behavior
Instances are immutable references/values and persist no remote state. Encryption key material may be held in memory as a string.

## Dependencies and Integration Points
Dependencies include Hadoop `Path` and `S3AEncryptionMethods`. It integrates with stream setup, change detection, and file-status-derived paths that need bucket/key/length/encryption metadata.

## Risks and Test Signals
Risks include retaining sensitive SSE-C key strings, passing stale length/version metadata after object replacement, and no validation of required fields. Tests should verify field preservation, null-tolerant optional metadata behavior, and consumers' handling of version/ETag and encryption attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ObjectAttributes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/SharedInstanceCredentialProvider.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/SharedInstanceCredentialProvider.java

## Purpose
`SharedInstanceCredentialProvider` restores a documented public credential provider name by subclassing `IAMInstanceCredentialsProvider` for IAM instance/container credentials.

## Important APIs, Types, and Functions
The class declares no methods or fields; its behavior is inherited entirely from `IAMInstanceCredentialsProvider`.

## Control Flow and State
Construction and credential resolution follow the superclass. Authentication failures should surface as `NoAwsCredentialsException`, allowing retry handlers to treat them as non-recoverable.

## State and Persistence Behavior
All state is inherited from the IAM provider. This wrapper persists no additional data.

## Dependencies and Integration Points
Dependencies are `IAMInstanceCredentialsProvider` and `NoAwsCredentialsException`. The class name is a configuration-facing compatibility point for `fs.s3a.aws.credentials.provider` and documentation.

## Risks and Test Signals
Risks include accidental removal/renaming breaking configured deployments, superclass semantic changes altering this provider, and public evolving API expectations. Tests should verify class instantiation through configured provider lists and failure translation when instance/container credentials are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/SharedInstanceCredentialProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/SimpleAWSCredentialsProvider.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/SimpleAWSCredentialsProvider.java

## Purpose
`SimpleAWSCredentialsProvider` supplies AWS basic credentials from Hadoop S3A configuration or credential providers.

## Important APIs, Types, and Functions
Public API includes constant `NAME`, constructor `(URI, Configuration)`, package-visible test constructor from `S3xLoginHelper.Login`, `resolveCredentials()`, and `toString()`.

## Control Flow and State
Construction calls `S3AUtils.getAWSAccessKeys()` and stores access/secret strings. `resolveCredentials()` returns `AwsBasicCredentials` only when both strings are non-empty; otherwise it raises `NoAwsCredentialsException`. `toString()` reports only emptiness flags, not secrets.

## State and Persistence Behavior
The provider keeps credentials in memory as strings for its lifetime and does not refresh them. It persists no data externally.

## Dependencies and Integration Points
Dependencies include AWS SDK credentials types, Hadoop `Configuration`, `S3AUtils`, `S3xLoginHelper`, Apache `StringUtils`, and `NoAwsCredentialsException`. It is referenced by configured credential provider chains and must keep its class name stable.

## Risks and Test Signals
Risks include long-lived string secrets, no refresh support, empty access/secret handling, and compatibility breakage if constructors/class name change. Tests should verify config/JCEKS lookup, missing credential exception behavior, no secret leakage in `toString()`, and provider-chain instantiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/SimpleAWSCredentialsProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/Statistic.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/Statistic.java

## Purpose
`Statistic` is the enum vocabulary for S3A counters, gauges, durations, and quantiles. It drives metric declaration in `S3AInstrumentation` and storage statistics exported by the filesystem.

## Important APIs, Types, and Functions
Each enum value stores a symbol, description, and `StatisticTypeEnum`. Categories cover low-level HTTP/action durations, HTTP responses, filesystem invocations, object IO, stream read/write/prefetch/cache metrics, committer metrics, store retry/throttle/client creation metrics, delegation token metrics, multipart uploader metrics, audit metrics, and client-side encryption gauge. APIs are `getSymbol()`, `fromSymbol()`, `getDescription()`, `getType()`, and `toString()`.

## Control Flow and State
Static initialization builds `SYMBOL_MAP` from all enum values for reverse lookup. `S3AInstrumentation` iterates all values by type to create metrics and IOStatistics declarations.

## State and Persistence Behavior
Enum values and the symbol map are static immutable runtime state. The enum does not store metric values; it names and classifies them.

## Dependencies and Integration Points
Dependencies include `StatisticTypeEnum`, Hadoop `StoreStatisticNames`, `StreamStatisticNames`, `FileSystemStatisticNames`, and `AuditStatisticNames`. It integrates with instrumentation, stream stats, store stats, audit tests, committers, retry/throttle reporting, and external monitoring expecting stable symbols.

## Risks and Test Signals
Risks include symbol collisions silently overwriting `SYMBOL_MAP`, type misclassification causing missing counters/gauges/durations, changing symbols breaking metrics consumers, and new audit values requiring test support updates. Tests should verify unique symbols, reverse lookup, type-driven metric registration, expected metric publication, and compatibility of important symbol names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/Statistic.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/TemporaryAWSCredentialsProvider.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/TemporaryAWSCredentialsProvider.java

## Purpose
`TemporaryAWSCredentialsProvider` supplies AWS session credentials from S3A/Hadoop configuration. It is intended for credential chains where construction must not fail merely because credentials are absent.

## Important APIs, Types, and Functions
Public constants are `NAME` and `COMPONENT`. Constructors accept `Configuration` alone or `(URI, Configuration)`. The core override is `createCredentials(Configuration)`.

## Control Flow and State
The provider delegates common session-provider behavior to `AbstractSessionCredentialsProvider`. `createCredentials()` loads `MarshalledCredentials` from filesystem configuration, requires `SessionOnly`, raises `NoAwsCredentialsException` if session credentials are absent, and converts valid credentials to AWS SDK credentials.

## State and Persistence Behavior
State is inherited and represents loaded session credentials. Credentials are read from configuration/credential providers and kept in memory; there is no automatic remote refresh in this class.

## Dependencies and Integration Points
Dependencies include AWS SDK `AwsCredentials`, `AbstractSessionCredentialsProvider`, `MarshalledCredentialBinding`, `MarshalledCredentials`, `NoAuthWithAWSException`, and `NoAwsCredentialsException`. The class name is stable for `fs.s3a.aws.credentials.provider`.

## Risks and Test Signals
Risks include treating long-lived basic credentials as empty, missing/expired session token behavior, construction compatibility in provider chains, and URI-specific lookup precedence. Tests should verify session-only validation, empty/basic-only failure, conversion to AWS credentials, provider-chain behavior, and bucket-specific credential loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/TemporaryAWSCredentialsProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/Tristate.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/Tristate.java

## Purpose
`Tristate` represents true, false, and unknown values, mainly for S3A metadata where a boolean property may not be known without extra remote calls.

## Important APIs, Types, and Functions
Enum values are `TRUE`, `FALSE`, and `UNKNOWN`. APIs are `getMapping()`, `isBoolean()`, `fromBool(boolean)`, and `from(Optional<Boolean>)`.

## Control Flow and State
Each enum value stores an `Optional<Boolean>`. Conversion from boolean maps directly; conversion from optional maps empty to `UNKNOWN`.

## State and Persistence Behavior
State is static enum data only. The optional mapping is immutable by convention.

## Dependencies and Integration Points
Dependencies are Java `Optional`. S3A file status classes use it for empty-directory knowledge and conversions between S3 status and located status.

## Risks and Test Signals
Risks are low, but code comments warn logic assumes exactly three values. Tests should cover optional mapping, boolean detection, conversions, and status classes preserving `UNKNOWN` distinctly from false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/Tristate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/UnknownStoreException.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/UnknownStoreException.java

## Purpose
`UnknownStoreException` represents an absent bucket or AWS store resource. It intentionally does not extend `FileNotFoundException` so missing stores are not cached or ignored as missing files.

## Important APIs, Types, and Functions
It extends `PathIOException` and provides constructors `(String path, String message)` and `(String path, String message, Throwable cause)`.

## Control Flow and State
Construction delegates path/message to `PathIOException` and conditionally installs a cause. There is no additional behavior.

## State and Persistence Behavior
The exception carries path, message, and optional cause. It persists no external state.

## Dependencies and Integration Points
Dependencies include Hadoop `PathIOException`. `S3AUtils.translateException()` maps unknown-bucket 404 responses to this type, and `S3ARetryPolicy` fails it fast.

## Risks and Test Signals
Risks include misclassifying missing objects as missing stores or vice versa, and callers catching only `FileNotFoundException`. Tests should verify unknown bucket translation, retry fail-fast behavior, cause preservation, and user-visible path/message formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/UnknownStoreException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/UploadInfo.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/UploadInfo.java

## Purpose
`UploadInfo` is a small struct pairing an AWS transfer-manager `FileUpload` with the expected upload length.

## Important APIs, Types, and Functions
The constructor stores `FileUpload` and length. Getters are `getFileUpload()` and `getLength()`.

## Control Flow and State
There is no control flow beyond storing the upload handle. `S3AStore.putObject()` returns this object and `waitForUploadCompletion()` consumes it to wait and update completion statistics.

## State and Persistence Behavior
State is an in-memory handle to an active asynchronous upload plus a byte length. Remote persistence is the eventual S3 object created by the upload, managed by AWS transfer manager code.

## Dependencies and Integration Points
Dependency is AWS SDK transfer manager `FileUpload`. It integrates with S3A put/upload completion paths and statistics accounting.

## Risks and Test Signals
Risks include null upload handles, incorrect length causing wrong statistics, and lifetime mismatch where source files/buffers disappear before async upload completion. Tests should verify length propagation, completion stats using length, failed/cancelled upload handling, and null expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/UploadInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/VectoredIOContext.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/VectoredIOContext.java

## Purpose
`VectoredIOContext` holds configuration for S3A vectored read behavior: range merge thresholds and maximum active range reads.

## Important APIs, Types, and Functions
APIs are `setMinSeekForVectoredReads()`, `getMinSeekForVectorReads()`, `setMaxReadSizeForVectoredReads()`, `getMaxReadSizeForVectorReads()`, `setVectoredActiveRangeReads()`, `getVectoredActiveRangeReads()`, `build()`, and `toString()`.

## Control Flow and State
Setters validate the instance is still mutable and values are non-negative, then return `this`. `build()` marks the object immutable. Later setter calls fail through `checkMutable()`.

## State and Persistence Behavior
State is in-memory configuration. It becomes immutable after `build()` but is not deeply copied by this class. Zero values can intentionally disable range merging or extra active reads.

## Dependencies and Integration Points
Dependency is Hadoop `Preconditions.checkState`. `S3AReadOpContext` carries this object into `S3AInputStream#readVectored(...)` behavior.

## Risks and Test Signals
Risks include forgetting to call `build()`, sharing a mutable instance across streams, invalid zero/threshold interpretation, and naming inconsistency between `Vector` and `Vectored` getter/setter names. Tests should cover non-negative validation, immutability after build, toString content, and read-vector range-combination behavior using the configured thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/VectoredIOContext.java -->
