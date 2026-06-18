# subset-b-000497 research

Grouped research report for Alluxio underfs OBS, OSS, Ozone, S3A, and Swift adapter files. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/obs/src/main/java/alluxio/underfs/obs/OBSUnderFileSystemFactory.java -->
# sources/distributed-fs/alluxio/underfs/obs/src/main/java/alluxio/underfs/obs/OBSUnderFileSystemFactory.java

## Purpose
`OBSUnderFileSystemFactory` is the service-provider factory that lets Alluxio create Huawei OBS under file systems for `obs://` URIs.

## Important APIs, Types, And Functions
The class implements `UnderFileSystemFactory`. `create(String, UnderFileSystemConfiguration)` validates the path, checks required OBS credential properties, and delegates to `OBSUnderFileSystem.createInstance`. `supportsPath(String)` accepts only paths with `Constants.HEADER_OBS`. `checkOBSCredentials` requires `OBS_ACCESS_KEY`, `OBS_SECRET_KEY`, `OBS_ENDPOINT`, and `OBS_BUCKET_TYPE`.

## Control Flow
Creation is fail-fast: null paths are rejected, missing credentials produce an `IOException` wrapped through Guava `Throwables.propagate`, and factory construction errors from the concrete UFS are propagated the same way.

## State And Persistence
The factory has no mutable state. It only reads the supplied configuration and returns a new UFS instance.

## Dependencies And Integration Points
It integrates with Alluxio's UFS registry through the factory interface and depends on `AlluxioURI`, `PropertyKey`, and `OBSUnderFileSystem`.

## Risks
The credential check is stricter than simple path support, so registry discovery can succeed while actual creation fails. Exception wrapping uses older Guava propagation style, which can obscure checked failure types.

## Test Signals
`OBSUnderFileSystemFactoryTest` verifies registry discovery for `obs://` paths. Credential-negative and creation-error cases are not directly covered in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/obs/src/main/java/alluxio/underfs/obs/OBSUnderFileSystemFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/obs/src/main/java/alluxio/underfs/obs/ObsClientExt.java -->
# sources/distributed-fs/alluxio/underfs/obs/src/main/java/alluxio/underfs/obs/ObsClientExt.java

## Purpose
`ObsClientExt` extends Huawei's `ObsClient` to inject additional OBS client properties after construction.

## Important APIs, Types, And Functions
The only API is the constructor accepting access key, secret key, endpoint, and a `Map<String,Object>` of OBS configuration values. It calls the parent `ObsClient` constructor and writes every map entry into the inherited `obsProperties`.

## Control Flow
Construction loops through configuration entries, stringifies non-null values, stores them in `obsProperties`, and logs each key/value at debug level.

## State And Persistence
State is persisted in the underlying client property bag for the lifetime of the OBS client. The class adds no separate fields.

## Dependencies And Integration Points
It depends on Huawei OBS SDK internals exposing `obsProperties`. It is used by the OBS UFS construction path to apply Alluxio-provided client settings that the base constructor does not take directly.

## Risks
Because it reaches into inherited mutable properties, compatibility depends on OBS SDK implementation details. Null values are passed to `setProperty` as null, which may be provider-sensitive. Debug logging can reveal configuration keys and values.

## Test Signals
No direct unit test appears in this subset. Coverage is indirect through OBS UFS construction and stream tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/obs/src/main/java/alluxio/underfs/obs/ObsClientExt.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/obs/src/test/java/alluxio/underfs/obs/OBSInputStreamTest.java -->
# sources/distributed-fs/alluxio/underfs/obs/src/test/java/alluxio/underfs/obs/OBSInputStreamTest.java

## Purpose
This test validates `OBSInputStream` range-read behavior against a mocked `ObsClient`.

## Important APIs, Types, And Functions
The fixture creates mocked `ObsObject` instances and range-sensitive `getObject(GetObjectRequest)` answers. Test methods cover `close`, `readInt`, `readByteArray`, and `skip`.

## Control Flow
Setup prepares three byte positions, each returning a stream over the remaining bytes. Reads should open the correct range lazily, skip should advance position, and close should make later reads fail with `IOException("Stream closed")`.

## State And Persistence
All state is in mocks, byte arrays, and the tested stream's in-memory cursor. No external OBS state is used.

## Dependencies And Integration Points
It depends on JUnit, Mockito, Hamcrest, `CountingRetry`, global Alluxio configuration, and OBS SDK request/object types. It exercises the same `MultiRangeObjectInputStream` pattern used by OSS and Swift.

## Risks
The mock only checks range starts and does not validate range end, retry, or provider exceptions. It gives a good signal for cursor handling but not real OBS protocol behavior.

## Test Signals
Passing tests indicate that basic single-byte, buffer, skip, and closed-stream semantics remain stable for OBS reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/obs/src/test/java/alluxio/underfs/obs/OBSInputStreamTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/obs/src/test/java/alluxio/underfs/obs/OBSLowLevelOutputStreamTest.java -->
# sources/distributed-fs/alluxio/underfs/obs/src/test/java/alluxio/underfs/obs/OBSLowLevelOutputStreamTest.java

## Purpose
This test covers OBS streaming-upload output behavior implemented through the low-level multipart stream.

## Important APIs, Types, And Functions
The fixture mocks `IObsClient`, `ListeningExecutorService`, local temp `File`, `BufferedOutputStream`, and multipart result types. Tests cover single-byte writes, small-file writes, multipart transition for large files, empty file close, flush, and close.

## Control Flow
Small writes remain local and complete through `putObject`. When data exceeds the configured partition size, the stream initiates multipart upload, submits part uploads to the executor, tracks part numbers, waits on futures during flush/close, and completes multipart upload.

## State And Persistence
State under test includes part number, upload id, submitted futures, temporary output buffering, and returned content hash. No real files or OBS objects are created because constructors are PowerMockito-mocked.

## Dependencies And Integration Points
It depends on PowerMock because the production stream creates local files and output streams internally. It validates behavior inherited from `ObjectLowLevelOutputStream` as adapted to OBS SDK request/result types.

## Risks
Constructor mocking makes the test brittle to implementation refactors. It does not cover abort-on-error paths, concurrent part ordering, or real SDK ETag semantics.

## Test Signals
The suite confirms the key lifecycle split: small files use `putObject`, larger files use initiate/upload/complete multipart, and content hash is populated after completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/obs/src/test/java/alluxio/underfs/obs/OBSLowLevelOutputStreamTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/obs/src/test/java/alluxio/underfs/obs/OBSOutputStreamTest.java -->
# sources/distributed-fs/alluxio/underfs/obs/src/test/java/alluxio/underfs/obs/OBSOutputStreamTest.java

## Purpose
This unit test validates the non-streaming OBS output stream that buffers to a local temporary file and uploads on close.

## Important APIs, Types, And Functions
The fixture mocks `ObsClient`, `File`, `BufferedOutputStream`, and `PutObjectResult`. Tests cover constructor preconditions, `write(int)`, full-array write, ranged write, failed close, successful close, and flush forwarding.

## Control Flow
Writes are expected to pass through to the local buffered stream. `close` closes the local stream, uploads the file through `putObject`, records the returned ETag/content hash, and deletes the temp file. Error tests force OBS exceptions and expect I/O failure.

## State And Persistence
The production stream persists bytes temporarily on local disk until close. In this test, disk objects are mocked; state assertions focus on calls, deletion, closed status, and optional content hash.

## Dependencies And Integration Points
It depends on PowerMock to intercept file and stream construction and on OBS SDK model classes. It complements the low-level streaming output tests.

## Risks
The test is implementation-sensitive because constructor calls are mocked. It does not cover actual filesystem cleanup failures or large-object behavior.

## Test Signals
Passing tests verify local buffering semantics, upload-on-close, flush delegation, and basic failure propagation for OBS non-streaming writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/obs/src/test/java/alluxio/underfs/obs/OBSOutputStreamTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/obs/src/test/java/alluxio/underfs/obs/OBSUnderFileSystemFactoryTest.java -->
# sources/distributed-fs/alluxio/underfs/obs/src/test/java/alluxio/underfs/obs/OBSUnderFileSystemFactoryTest.java

## Purpose
This is a registry smoke test for the OBS UFS module.

## Important APIs, Types, And Functions
The single `factory` test calls `UnderFileSystemFactoryRegistry.find("obs://bucket/key", Configuration.global())` and asserts a non-null factory.

## Control Flow
The test relies on service loader metadata for the module being present on the test classpath. It does not instantiate a UFS or exercise credentials.

## State And Persistence
No persistent state is used. The registry and global configuration are read only.

## Dependencies And Integration Points
It exercises Alluxio's UFS factory registry integration and the OBS module service-provider packaging.

## Risks
This catches packaging/registration regressions but not creation behavior, credential validation, or path rejection.

## Test Signals
Passing means the OBS module can advertise support for `obs://` URIs when included in the runtime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/obs/src/test/java/alluxio/underfs/obs/OBSUnderFileSystemFactoryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/obs/src/test/java/alluxio/underfs/obs/OBSUnderFileSystemTest.java -->
# sources/distributed-fs/alluxio/underfs/obs/src/test/java/alluxio/underfs/obs/OBSUnderFileSystemTest.java

## Purpose
This test covers selected failure and directory-detection behavior of the OBS UFS adapter.

## Important APIs, Types, And Functions
The fixture constructs `OBSUnderFileSystem` with a mocked `ObsClient`. Tests cover `deleteDirectory` non-recursive/recursive failures, `renameFile` failures, `judgeDirectoryInBucket`, and null object metadata handling.

## Control Flow
Mocked OBS listing or metadata calls throw `ObsException` or return controlled listing results. The UFS should convert these into false outcomes for delete/rename paths, classify directory markers from object summaries, and tolerate missing metadata.

## State And Persistence
Only mocked OBS client responses are used. The test drives `ObjectUnderFileSystem` inherited operations through the OBS-specific listing/status hooks.

## Dependencies And Integration Points
It integrates OBS adapter logic with Alluxio delete/rename/listing semantics and OBS SDK object summary/metadata types.

## Risks
The test is focused on negative and classification cases. It does not cover successful copy/delete, bulk listing pagination, credentials, or real OBS consistency behavior.

## Test Signals
Passing tests indicate that common OBS provider exceptions are contained as expected and that directory-marker edge cases do not crash metadata paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/obs/src/test/java/alluxio/underfs/obs/OBSUnderFileSystemTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/oss/pom.xml -->
# sources/distributed-fs/alluxio/underfs/oss/pom.xml

## Purpose
This Maven module descriptor builds the Aliyun OSS under file system implementation.

## Important APIs, Types, And Functions
The artifact is `alluxio-underfs-oss` under parent `alluxio-underfs`. It declares external dependencies on `aliyun-sdk-oss` and `commons-codec`, provided dependency on `alluxio-core-common`, a test-jar dependency for common tests, and `mockito-inline` for tests.

## Control Flow
Maven inherits most build behavior from the parent. The module configures shade and copy-rename plugins without local execution details, leaving dependency packaging and renamed artifacts to shared plugin configuration.

## State And Persistence
The POM has no runtime state. It controls dependency resolution, test classpath, and build output.

## Dependencies And Integration Points
It is listed by the parent `underfs/pom.xml` and contributes OSS classes and service-provider resources to Alluxio UFS packaging.

## Risks
OSS SDK compatibility and shaded dependency boundaries are the key risk. `mockito-inline` is needed for tests that mock final/static-adjacent SDK behavior.

## Test Signals
Successful module build compiles OSS adapter classes and the mock-heavy stream/UFS/STS tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/oss/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/oss/src/main/java/alluxio/underfs/oss/OSSInputStream.java -->
# sources/distributed-fs/alluxio/underfs/oss/src/main/java/alluxio/underfs/oss/OSSInputStream.java

## Purpose
`OSSInputStream` reads Aliyun OSS objects through ranged requests and plugs into Alluxio's multi-range object stream abstraction.

## Important APIs, Types, And Functions
It extends `MultiRangeObjectInputStream`. Constructors accept bucket, key, `OSS` client, optional start position, retry policy, and range chunk size. `createStream(long startPos, long endPos)` builds `GetObjectRequest`, sets an inclusive OSS range, retries `NoSuchKey`, and returns a buffered object content stream.

## Control Flow
Construction fetches object metadata to cache content length. Range reads clamp the requested end to `contentLength - 1` because OSS may return the whole object when reading past the end. Non-`NoSuchKey` OSS errors fail immediately as `IOException`; missing keys retry according to a copied retry policy.

## State And Persistence
The stream keeps bucket, key, client, current `mPos` from the parent, cached object length, and retry policy. No data is persisted outside the remote read stream.

## Dependencies And Integration Points
It depends on Aliyun OSS SDK request/object/metadata types and Alluxio retry/multi-range infrastructure. `OSSUnderFileSystem.openObject` constructs it.

## Risks
Metadata lookup during construction can fail before retry handling. Zero-length objects need careful range boundaries. Eventual consistency is only retried for `NoSuchKey`.

## Test Signals
`OSSInputStreamTest` validates close, byte reads, buffer reads, and skip by mocking range-start-specific OSS responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/oss/src/main/java/alluxio/underfs/oss/OSSInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/oss/src/main/java/alluxio/underfs/oss/OSSLowLevelOutputStream.java -->
# sources/distributed-fs/alluxio/underfs/oss/src/main/java/alluxio/underfs/oss/OSSLowLevelOutputStream.java

## Purpose
`OSSLowLevelOutputStream` implements streaming multipart uploads to Aliyun OSS for Alluxio object writes.

## Important APIs, Types, And Functions
It extends `ObjectLowLevelOutputStream` and implements provider-specific hooks: `initMultiPartUploadInternal`, `uploadPartInternal`, `completeMultiPartUploadInternal`, `abortMultiPartUploadInternal`, `createEmptyObject`, `putObject`, and `getContentHash`.

## Control Flow
The parent buffers data into partition-sized temp files. This subclass starts an OSS multipart upload, uploads each part with optional MD5, stores `PartETag`s, completes with all tags, or aborts on failure. Small or empty writes use `putObject`.

## State And Persistence
State includes the OSS client, synchronized part tag list, volatile upload id, and final ETag content hash. Temporary file state is managed by the parent stream.

## Dependencies And Integration Points
It depends on `ObjectLowLevelOutputStream`, Aliyun OSS multipart requests/results, Alluxio configuration partition size, and a `ListeningExecutorService` supplied by `OSSUnderFileSystem`.

## Risks
Part ordering relies on the collected tag list matching OSS expectations under concurrent uploads. Error paths translate SDK exceptions to `IOException`, but cleanup/abort reliability depends on the parent lifecycle.

## Test Signals
`OSSLowLevelOutputStreamTest` verifies small-file put, large-file multipart initiation/upload/completion, empty file creation, flush waiting, and content hash propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/oss/src/main/java/alluxio/underfs/oss/OSSLowLevelOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/oss/src/main/java/alluxio/underfs/oss/OSSOutputStream.java -->
# sources/distributed-fs/alluxio/underfs/oss/src/main/java/alluxio/underfs/oss/OSSOutputStream.java

## Purpose
`OSSOutputStream` is the non-streaming OSS write path: it buffers all bytes to a local temporary file and uploads the completed file on close.

## Important APIs, Types, And Functions
The constructor validates bucket/key/client, chooses a temp path from configured tmp dirs, and wraps a local file stream in an MD5 `DigestOutputStream` when possible. `write`, `flush`, `close`, and `getContentHash` form the public behavior.

## Control Flow
Writes go to local disk. `close` is guarded by an `AtomicBoolean`; it closes the local stream, builds metadata including Base64 MD5 if available, calls `putObject`, stores the returned ETag, and deletes the temp file.

## State And Persistence
State includes bucket, key, temp file, OSS client, local stream, MD5 digest, closed flag, and content hash. Persistence is local until close, then remote in OSS.

## Dependencies And Integration Points
It depends on Aliyun OSS `putObject`, Alluxio temp-dir selection, Commons Codec Base64, and `ContentHashable`. `OSSUnderFileSystem.createObject` uses it when streaming upload is disabled.

## Risks
Large writes require local disk space. Failure during close may leave temp files or partial remote state. Content hash is only available after successful upload.

## Test Signals
`OSSOutputStreamTest` verifies constructor guards, write forwarding, close failure/success, flush forwarding, upload call, deletion, and content hash behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/oss/src/main/java/alluxio/underfs/oss/OSSOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/oss/src/main/java/alluxio/underfs/oss/OSSUnderFileSystem.java -->
# sources/distributed-fs/alluxio/underfs/oss/src/main/java/alluxio/underfs/oss/OSSUnderFileSystem.java

## Purpose
`OSSUnderFileSystem` adapts Aliyun OSS buckets to Alluxio's `ObjectUnderFileSystem` contract.

## Important APIs, Types, And Functions
Important methods include `createInstance`, the protected constructor, `cleanup`, `copyObject`, `createEmptyObject`, `createObject`, `deleteObject`, `deleteObjects`, `getObjectListingChunk`, `getObjectStatus`, `getPermissions`, `initializeOSSClientConfig`, `openObject`, and `close`.

## Control Flow
Construction either creates an STS-backed client, uses an injected client, or builds a static-credential client from required OSS properties. Object operations call OSS SDK copy/put/delete/list/metadata APIs. Listing normalizes prefixes, chooses delimiter by recursive flag, and wraps paginated `ObjectListing` in `OSSObjectListingChunk`. Writes choose streaming multipart or temp-file output from configuration.

## State And Persistence
The UFS holds an OSS client, bucket name, optional STS provider, memoized streaming upload executor, and memoized permissions. Persistent data lives in OSS objects and multipart uploads; cleanup aborts old multipart uploads.

## Dependencies And Integration Points
It depends on Alluxio object-UFS base behavior, Aliyun OSS SDK, STS provider, `PathUtils`, `ModeUtils`, and `UnderFileSystemUtils`.

## Risks
`close` calls `mClientProvider.close()` without a null guard even though `mClientProvider` is only initialized in STS mode. Metadata exceptions in `getObjectStatus` return null for all `ServiceException`s, potentially hiding authorization or service failures.

## Test Signals
`OSSUnderFileSystemTest` covers delete/rename failure handling and folder suffix. Stream tests cover read/write paths; STS behavior is tested separately.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/oss/src/main/java/alluxio/underfs/oss/OSSUnderFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/oss/src/main/java/alluxio/underfs/oss/OSSUnderFileSystemFactory.java -->
# sources/distributed-fs/alluxio/underfs/oss/src/main/java/alluxio/underfs/oss/OSSUnderFileSystemFactory.java

## Purpose
This factory registers Aliyun OSS support with Alluxio's UFS factory mechanism.

## Important APIs, Types, And Functions
It implements `UnderFileSystemFactory`. `create` validates path and required credentials through `checkOSSCredentials`, then calls `OSSUnderFileSystem.createInstance`. `supportsPath` checks `Constants.HEADER_OSS`. Credential checks require access key, secret key, and endpoint properties.

## Control Flow
The factory reports support based on URI prefix but only creates a UFS when configuration contains the required OSS connection keys. Exceptions are wrapped with Guava `Throwables.propagate`.

## State And Persistence
The factory is stateless.

## Dependencies And Integration Points
It integrates the OSS module with `UnderFileSystemFactoryRegistry` and delegates actual client construction to `OSSUnderFileSystem`.

## Risks
STS mode may not need the same static credentials, but the factory-level credential check can reject creation before STS construction logic runs if the required static keys are absent.

## Test Signals
`OSSUnderFileSystemFactoryTest` verifies registry discovery for `oss://` paths but does not test credential gating or STS mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/oss/src/main/java/alluxio/underfs/oss/OSSUnderFileSystemFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/oss/src/main/java/alluxio/underfs/oss/StsOssClientProvider.java -->
# sources/distributed-fs/alluxio/underfs/oss/src/main/java/alluxio/underfs/oss/StsOssClientProvider.java

## Purpose
`StsOssClientProvider` manages an Aliyun OSS client backed by temporary STS credentials fetched from ECS RAM role metadata.

## Important APIs, Types, And Functions
The public APIs are constructor, `init`, `createOrRefreshOssStsClient`, `getOSSClient`, and `close`. Internals include `tokenWillExpiredAfter`, `doCreateOrRefreshStsOssClient`, `convertStringToDate`, and `setOssClientBuilder` for tests.

## Control Flow
Construction stores configuration and schedules a refresh task every 60 seconds. `init` retries client creation with exponential backoff. Refresh fetches metadata JSON from the ECS metadata service plus role name, parses access key, secret, token, and expiration, then either builds the OSS client or switches credentials on the existing client.

## State And Persistence
State includes a volatile OSS client, token expiration timestamp, metadata URL, token refresh interval, scheduled executor, and client builder. No credentials are persisted to disk.

## Dependencies And Integration Points
It depends on `HttpUtils`, Gson, OSS SDK credential switching, Alluxio retry utilities, and `OSSUnderFileSystem.initializeOSSClientConfig`.

## Risks
Metadata response parsing assumes all fields are present and valid. Scheduled refresh starts in the constructor, so lifecycle must call `close`. Time-based refresh can serve expired credentials if metadata fetch repeatedly fails.

## Test Signals
`StsOssClientProviderTest` mocks metadata HTTP responses and `OSSClientBuilder` to validate initial client creation and refresh when token expiration approaches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/oss/src/main/java/alluxio/underfs/oss/StsOssClientProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/oss/src/test/java/alluxio/underfs/oss/OSSInputStreamTest.java -->
# sources/distributed-fs/alluxio/underfs/oss/src/test/java/alluxio/underfs/oss/OSSInputStreamTest.java

## Purpose
This test validates `OSSInputStream` basic cursor and range-read behavior.

## Important APIs, Types, And Functions
Setup creates an `OSS` mock and one `OSSObject` per starting position. Tests cover closing, single-byte reads, byte-array reads, and skipping.

## Control Flow
Each mocked `getObject` answer is keyed by request range start and returns a stream over the remaining bytes. The stream should lazily issue ranged reads as its cursor advances and throw `IOException("Stream closed")` after close.

## State And Persistence
Only in-memory byte arrays and mocks are used. No real OSS object or local file is created.

## Dependencies And Integration Points
It uses Mockito, JUnit, Hamcrest, `CountingRetry`, and Alluxio configuration for multi-range chunk size.

## Risks
The test does not cover range end clamping, metadata lookup behavior, retry on `NoSuchKey`, or non-missing OSS errors.

## Test Signals
Passing tests confirm that the OSS input stream preserves ordinary Java `InputStream` semantics for read, skip, and close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/oss/src/test/java/alluxio/underfs/oss/OSSInputStreamTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/oss/src/test/java/alluxio/underfs/oss/OSSLowLevelOutputStreamTest.java -->
# sources/distributed-fs/alluxio/underfs/oss/src/test/java/alluxio/underfs/oss/OSSLowLevelOutputStreamTest.java

## Purpose
This test verifies Aliyun OSS low-level streaming upload behavior.

## Important APIs, Types, And Functions
It uses PowerMock to intercept file and stream construction and Mockito to mock `OSS`, executor futures, and multipart result objects. Tests cover byte writes, small file writes, large multipart writes, empty file close, flush, and close.

## Control Flow
The tested stream should keep small writes local until close and use `putObject`. When data crosses the partition threshold, it should initiate multipart upload, submit part uploads, increment part numbers, wait on futures during flush, and complete multipart upload on close.

## State And Persistence
State under assertion includes mocked temp buffering, part number, upload id, executor submissions, and content hash. Real filesystem and OSS persistence are avoided.

## Dependencies And Integration Points
It validates the `ObjectLowLevelOutputStream` subclass hooks implemented by `OSSLowLevelOutputStream`.

## Risks
The test does not exercise abort or exception paths. PowerMock constructor interception can break when implementation details change.

## Test Signals
Passing tests give high confidence that the threshold split between single put and multipart upload remains intact.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/oss/src/test/java/alluxio/underfs/oss/OSSLowLevelOutputStreamTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/oss/src/test/java/alluxio/underfs/oss/OSSOutputStreamTest.java -->
# sources/distributed-fs/alluxio/underfs/oss/src/test/java/alluxio/underfs/oss/OSSOutputStreamTest.java

## Purpose
This test covers the local-buffered OSS output stream.

## Important APIs, Types, And Functions
The fixture mocks `OSS`, temp `File`, local `BufferedOutputStream`, and `PutObjectResult`. Tests cover constructor validation, `write(int)`, full-array write, ranged write, close failure, close success, and flush.

## Control Flow
Writes should delegate directly to the local stream. Successful close closes local output, uploads with `putObject`, stores ETag as content hash, and deletes the temporary file. Failure close paths are expected to raise an exception.

## State And Persistence
The production class persists to local disk until close; the test replaces that with mocks and verifies interactions.

## Dependencies And Integration Points
It uses PowerMock/Mockito and Aliyun OSS SDK request/result types. It complements streaming upload tests by covering the non-streaming path.

## Risks
The test does not validate real MD5 metadata, actual temp directory selection, or deletion failure handling.

## Test Signals
Passing tests show correct write delegation, flush behavior, close idempotence basics, and upload-on-close semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/oss/src/test/java/alluxio/underfs/oss/OSSOutputStreamTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/oss/src/test/java/alluxio/underfs/oss/OSSUnderFileSystemFactoryTest.java -->
# sources/distributed-fs/alluxio/underfs/oss/src/test/java/alluxio/underfs/oss/OSSUnderFileSystemFactoryTest.java

## Purpose
This is a factory registration smoke test for Aliyun OSS.

## Important APIs, Types, And Functions
The `factory` test calls `UnderFileSystemFactoryRegistry.find("oss://test-bucket/path", Configuration.global())` and asserts that a factory is present.

## Control Flow
The registry scans available UFS factory providers and should select the OSS factory for the `oss://` scheme.

## State And Persistence
No external state is used.

## Dependencies And Integration Points
It checks module service registration rather than OSS client behavior.

## Risks
It does not validate `create`, credentials, STS mode, or negative scheme matching.

## Test Signals
Passing confirms that the OSS module is discoverable by Alluxio when present on the classpath.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/oss/src/test/java/alluxio/underfs/oss/OSSUnderFileSystemFactoryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/oss/src/test/java/alluxio/underfs/oss/OSSUnderFileSystemTest.java -->
# sources/distributed-fs/alluxio/underfs/oss/src/test/java/alluxio/underfs/oss/OSSUnderFileSystemTest.java

## Purpose
This test covers selected OSS UFS failure handling and folder suffix behavior.

## Important APIs, Types, And Functions
The fixture builds `OSSUnderFileSystem` with a mocked `OSSClient`. Tests cover non-recursive delete, recursive delete, rename when listing throws `ServiceException`, and `getFolderSuffix`.

## Control Flow
Mocked listing failures flow through inherited `ObjectUnderFileSystem` delete/rename operations. The expected result is `false`, not an uncaught exception. Folder suffix is expected to be `/`.

## State And Persistence
Only mocked client behavior is used; no objects are created.

## Dependencies And Integration Points
It validates interactions between OSS-specific listing hooks and Alluxio's generic object UFS operations.

## Risks
Success paths, pagination, copy/delete calls, permissions, and `close` lifecycle are not covered here.

## Test Signals
Passing tests confirm that common `ServiceException` listing failures are contained for delete and rename operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/oss/src/test/java/alluxio/underfs/oss/OSSUnderFileSystemTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/oss/src/test/java/alluxio/underfs/oss/StsOssClientProviderTest.java -->
# sources/distributed-fs/alluxio/underfs/oss/src/test/java/alluxio/underfs/oss/StsOssClientProviderTest.java

## Purpose
This test verifies STS-backed OSS client initialization and credential refresh.

## Important APIs, Types, And Functions
The test sets OSS endpoint and ECS RAM role configuration, mocks `HttpUtils.get`, injects a mocked `OSSClientBuilder`, calls `init`, manipulates metadata response expiration, and calls `createOrRefreshOssStsClient`.

## Control Flow
Initial metadata returns temporary credentials and should build an OSS client. A later response with a future expiration should refresh credentials, after which `tokenWillExpiredAfter(0)` should be false.

## State And Persistence
State is the provider's in-memory OSS client and expiration timestamp. HTTP responses and client builder are mocked.

## Dependencies And Integration Points
It uses Mockito static mocking for `HttpUtils`, Aliyun OSS client builder, and Alluxio configuration. The provider is used by `OSSUnderFileSystem` when STS mode is enabled.

## Risks
The test uses JSON-like strings with single quotes accepted by Gson leniency; real metadata strictness is not validated. Scheduled background refresh is created by the provider and closed by try-with-resources.

## Test Signals
Passing confirms the provider can parse metadata, build a token client, detect expiring tokens, and refresh credentials.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/oss/src/test/java/alluxio/underfs/oss/StsOssClientProviderTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/ozone/pom.xml -->
# sources/distributed-fs/alluxio/underfs/ozone/pom.xml

## Purpose
This Maven descriptor builds the Apache Ozone under file system module.

## Important APIs, Types, And Functions
The artifact is `alluxio-underfs-ozone`. It pins `ufs.ozone.version` to `1.2.1`, declares Ozone client/filesystem dependencies, metrics, provided logging dependencies, `alluxio-core-common`, and `alluxio-underfs-hdfs`.

## Control Flow
Profiles choose `ozone-filesystem-hadoop2` or the default active `ozone-filesystem-hadoop3`. The build shades dependencies, relocates `com.google` to `alluxio.shaded.hdfs.com.google`, filters metadata/license artifacts, excludes the HDFS UFS service file, and runs templating for generated constants.

## State And Persistence
The POM controls build artifacts and generated source constants; it has no runtime state.

## Dependencies And Integration Points
Ozone implementation extends the HDFS UFS, so this module depends directly on the HDFS underfs module and Ozone's Hadoop filesystem artifacts.

## Risks
Dependency conflicts are likely around Hadoop/Ozone/Guava/metrics, making shading and service-resource filtering important. Hadoop profile selection affects runtime compatibility.

## Test Signals
Build success checks dependency resolution, shade configuration, and generated `OzoneUfsConstants`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/ozone/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/ozone/src/main/java-templates/alluxio/OzoneUfsConstants.java -->
# sources/distributed-fs/alluxio/underfs/ozone/src/main/java-templates/alluxio/OzoneUfsConstants.java

## Purpose
This template generates a compile-time constant exposing the Ozone UFS dependency version.

## Important APIs, Types, And Functions
It defines final class `OzoneUfsConstants` with public static `UFS_OZONE_VERSION = "${ufs.ozone.version}"` and a private constructor.

## Control Flow
There is no runtime control flow. The Maven templating plugin replaces the property placeholder into generated Java sources.

## State And Persistence
The generated class holds a single immutable string constant.

## Dependencies And Integration Points
It is consumed by `OzoneUnderFileSystemFactory.getVersion` to report the module's Ozone version.

## Risks
If templating is skipped or the property is missing, the literal placeholder may leak into runtime version reporting.

## Test Signals
The main signal is successful Maven templating and compilation of the Ozone module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/ozone/src/main/java-templates/alluxio/OzoneUfsConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/ozone/src/main/java/alluxio/underfs/ozone/OzoneUnderFileSystem.java -->
# sources/distributed-fs/alluxio/underfs/ozone/src/main/java/alluxio/underfs/ozone/OzoneUnderFileSystem.java

## Purpose
`OzoneUnderFileSystem` adapts Apache Ozone through Alluxio's HDFS UFS implementation.

## Important APIs, Types, And Functions
It extends `HdfsUnderFileSystem`. `createInstance` builds Hadoop configuration with inherited `createConfiguration` and constructs the Ozone subclass. The constructor passes URI, Alluxio UFS conf, and Hadoop conf to the parent. `getUnderFSType` returns `ozone`.

## Control Flow
All filesystem operations are inherited from HDFS UFS. This class only supplies construction and type identity.

## State And Persistence
Runtime state is inherited from `HdfsUnderFileSystem`, including Hadoop filesystem handles and configuration. This subclass adds no fields.

## Dependencies And Integration Points
It depends on Ozone Hadoop filesystem wiring being available through the module POM and on HDFS UFS behavior for actual operations.

## Risks
Most correctness risk lies in URI support and Hadoop/Ozone configuration compatibility rather than local code. Because operations are inherited, Ozone-specific edge cases may not have specialized handling.

## Test Signals
No direct test is listed in this subset. Build and factory behavior are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/ozone/src/main/java/alluxio/underfs/ozone/OzoneUnderFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/ozone/src/main/java/alluxio/underfs/ozone/OzoneUnderFileSystemFactory.java -->
# sources/distributed-fs/alluxio/underfs/ozone/src/main/java/alluxio/underfs/ozone/OzoneUnderFileSystemFactory.java

## Purpose
This factory exposes Apache Ozone as an Alluxio UFS while reusing HDFS factory behavior.

## Important APIs, Types, And Functions
It extends `HdfsUnderFileSystemFactory`. `create` delegates to `OzoneUnderFileSystem.createInstance`, `supportsPath(String)` accepts `o3fs://`, `ofs://`, and `o3fs:` paths, `supportsPath(String, UnderFileSystemConfiguration)` adds availability checks through `UnderFileSystemUtils.isHdfsUnderFSSupported`, and `getVersion` returns `OzoneUfsConstants.UFS_OZONE_VERSION`.

## Control Flow
Path support first checks scheme/prefix. Configuration-aware support then ensures the Hadoop/Ozone filesystem can be loaded for that path.

## State And Persistence
The factory has no mutable state.

## Dependencies And Integration Points
It integrates with Alluxio UFS registry, HDFS UFS factory logic, generated Ozone constants, and Ozone Hadoop filesystem classes.

## Risks
Scheme support is broader than simple URI prefixes and includes `o3fs:`. Runtime support can differ from path support if dependencies or Hadoop profiles are missing.

## Test Signals
No direct test is present in this subset. Build-time dependency/profile validation and generic UFS registry tests elsewhere would be expected signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/ozone/src/main/java/alluxio/underfs/ozone/OzoneUnderFileSystemFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/pom.xml -->
# sources/distributed-fs/alluxio/underfs/pom.xml

## Purpose
This parent Maven module aggregates Alluxio under file system implementations.

## Important APIs, Types, And Functions
The artifact is `alluxio-underfs` and it lists modules including ABFS, ADL, CephFS, COS, GCS, HDFS, local, OSS, Ozone, S3A, Swift, WASB, web, OBS, and TOS. It defines shared properties and shared dependencies such as Guava, Log4j, SLF4J, and test `s3proxy`.

## Control Flow
The build configures shared shade behavior, copy/rename packaging, and clean behavior for UFS modules. Child modules inherit plugin management and dependency versions from this parent and higher Alluxio parent POMs.

## State And Persistence
The POM controls build graph, dependency classpaths, shaded artifacts, and generated/cleaned outputs. It has no runtime state.

## Dependencies And Integration Points
It is the integration point for all underfs modules, including the object-store adapters researched here.

## Risks
Parent-level module ordering and shared plugin behavior affect every UFS. Shading or service metadata mistakes can break discovery at runtime.

## Test Signals
Successful reactor builds and per-module registry tests are the main signals that this parent still assembles UFS modules correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/pom.xml -->
# sources/distributed-fs/alluxio/underfs/s3a/pom.xml

## Purpose
This Maven descriptor builds the AWS S3A under file system module.

## Important APIs, Types, And Functions
The artifact is `alluxio-underfs-s3a`. Dependencies include AWS SDK v2 `s3` and `netty-nio-client`, AWS SDK v1 core/S3/STS, JAXB runtime binding, Commons Codec, Commons Collections, and Alluxio core common with a test-jar dependency.

## Control Flow
The module inherits parent build behavior and configures shade and copy-rename plugins. Having both AWS SDK generations supports synchronous object operations with SDK v1 and async listing/status with SDK v2.

## State And Persistence
The POM controls compile/runtime/test classpaths and packaging. It has no runtime state.

## Dependencies And Integration Points
It plugs into the underfs parent module and packages S3A implementation/factory/service resources.

## Risks
Dual AWS SDK generations increase dependency conflict and configuration drift risk. Netty async client configuration must remain compatible with SDK v2 versions.

## Test Signals
Module tests include stream unit tests, mock-server S3Proxy integration tests, factory tests, ACL translation tests, and exception/permission unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/AlluxioS3Exception.java -->
# sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/AlluxioS3Exception.java

## Purpose
`AlluxioS3Exception` translates AWS client/service failures into Alluxio runtime exceptions with gRPC status and external error type.

## Important APIs, Types, And Functions
Static `from(AmazonClientException)` and `from(String, AmazonClientException)` create exceptions. `httpStatusToGrpcStatus` maps HTTP status codes to `io.grpc.Status`. The private constructor passes `ErrorType.External` and retryability to `AlluxioRuntimeException`.

## Control Flow
Generic `AmazonClientException` becomes `Status.UNKNOWN` with a client-exception description. `AmazonS3Exception` contributes HTTP status, S3 error code/message, and retryable flag. Optional caller-provided messages override generated descriptions.

## State And Persistence
The class has no mutable state. It encapsulates cause, status, message, error type, and retryability in the exception object.

## Dependencies And Integration Points
It is used by S3A UFS, input stream, listing, metadata, and delete paths to convert SDK failures into Alluxio's runtime error model.

## Risks
Mapping is approximate; some S3-compatible stores return nonstandard status/error combinations. Generic client failures lose detailed status.

## Test Signals
S3A UFS tests expect `AlluxioS3Exception` for listing, metadata, and rename failures. No direct exhaustive status-map test is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/AlluxioS3Exception.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/S3AInputStream.java -->
# sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/S3AInputStream.java

## Purpose
`S3AInputStream` wraps AWS SDK S3 object streams and implements efficient skip by reopening the object at a byte range.

## Important APIs, Types, And Functions
Constructors accept bucket, key, `AmazonS3` client, optional position, and retry policy. Public methods are `read`, `read(byte[])`, `read(byte[], int, int)`, `skip`, and `close`. Internals include `openStream`, `closeStream`, and `getClient`.

## Control Flow
Reads lazily open the S3 object at `mPos`; non-empty reads advance `mPos`. `skip` closes the current stream, increments `mPos`, and opens a new ranged request. `openStream` omits range when position is zero to avoid zero-length object issues.

## State And Persistence
State includes client, bucket, key, active `S3ObjectInputStream`, current position, and retry policy. No local persistence is used.

## Dependencies And Integration Points
It depends on AWS SDK v1 `AmazonS3` and `GetObjectRequest`. `S3AUnderFileSystem.openObject` constructs it.

## Risks
The retry loop immediately throws on the first `AmazonS3Exception`, so the retry policy is not actually used for those exceptions. `skip` always returns requested bytes even if beyond EOF.

## Test Signals
Behavior is indirectly covered through S3Proxy read tests and generic object open flows; this subset has no dedicated `S3AInputStreamTest`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/S3AInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/S3ALowLevelOutputStream.java -->
# sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/S3ALowLevelOutputStream.java

## Purpose
`S3ALowLevelOutputStream` provides streaming multipart uploads to S3.

## Important APIs, Types, And Functions
It extends `ObjectLowLevelOutputStream` and implements multipart hooks for initiate, upload part, complete, abort, small/empty put, and content hash retrieval. It supports server-side encryption metadata when configured.

## Control Flow
The parent stream buffers chunks and schedules uploads. This subclass starts an AWS multipart upload, uploads part files with optional MD5, accumulates `PartETag`s, completes multipart upload to receive an ETag, or aborts by upload id. Small writes use `putObject`.

## State And Persistence
State includes AWS client, synchronized part tag list, upload id, optional content hash, and SSE flag. Remote persistence occurs in S3 objects and multipart upload sessions.

## Dependencies And Integration Points
It depends on AWS SDK v1 multipart request/result classes, Alluxio object low-level streaming, and S3 partition-size configuration.

## Risks
Concurrent part completion ordering and tag list ordering are critical. Server-side encryption changes metadata for put/initiate paths and must stay aligned with provider requirements.

## Test Signals
`S3ALowLevelOutputStreamTest` covers small and large writes, multipart lifecycle, flush, empty object, close, and ETag propagation with mocked AWS calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/S3ALowLevelOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/S3AOutputStream.java -->
# sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/S3AOutputStream.java

## Purpose
`S3AOutputStream` is the non-streaming S3 write path that uploads a local temporary file on close.

## Important APIs, Types, And Functions
The constructor validates inputs, selects a temp file, initializes MD5 digesting, and stores a `TransferManager`. Public methods implement `write`, `flush`, `close`, `getContentHash`, with protected `getUploadPath` and `getTransferManager`.

## Control Flow
Writes are buffered to local disk. `close` closes the local stream, builds `ObjectMetadata` with MD5 and optional AES256 SSE, submits a `PutObjectRequest` to `TransferManager.upload`, waits for completion, records ETag, and deletes the temp file.

## State And Persistence
State includes bucket, key, temp file, transfer manager, local output stream, digest, closed flag, and content hash. Data is local until close then persisted in S3.

## Dependencies And Integration Points
It depends on AWS SDK v1 transfer manager, Commons Codec Base64, Alluxio temp-dir utilities, and `ContentHashable`. `S3AUnderFileSystem.createObject` uses it when streaming upload is disabled.

## Risks
Large writes consume local disk. Interrupted or failed uploads can leave temp files or incomplete remote operations. `close` must remain idempotent.

## Test Signals
`S3AOutputStreamTest` verifies write/flush delegation, upload-on-close, content hash after close, and mocked transfer manager interaction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/S3AOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/S3AUnderFileSystem.java -->
# sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/S3AUnderFileSystem.java

## Purpose
`S3AUnderFileSystem` is Alluxio's AWS/S3-compatible object store adapter, implementing object operations, listing, permissions, reads, writes, and async loading.

## Important APIs, Types, And Functions
Creation APIs include `createAwsCredentialsProvider`, `createInstance`, `createAmazonS3`, `createAmazonS3Async`, and endpoint/region helpers. UFS overrides include `cleanup`, `close`, `copyObject`, `createEmptyObject`, `createObject`, `deleteObject`, `deleteObjects`, `getObjectListingChunk`, `performListingAsync`, `getObjectStatus`, `getPermissions`, `getRootKey`, and `openObject`. Inner classes wrap v1 list-object result pages.

## Control Flow
Construction builds AWS SDK v1 sync client, SDK v2 async client, transfer executor, and transfer manager from Alluxio configuration. Object operations use v1 client/transfer manager. Listing supports v1 or v2 sync APIs and async SDK v2 listing/status for load paths. Async listing optionally checks base status, handles `DescendantType`, merges common prefixes and objects into ordered `UfsStatus` streams, and returns continuation metadata.

## State And Persistence
State includes sync and async clients, bucket name, executor, transfer manager, streaming upload flag, and memoized permissions. Remote state is S3 objects and multipart uploads; `cleanup` aborts old multipart uploads.

## Dependencies And Integration Points
It integrates Alluxio `ObjectUnderFileSystem` with AWS SDK v1/v2, `S3AInputStream`, `S3AOutputStream`, `S3ALowLevelOutputStream`, `S3AUtils`, and Alluxio permission/status/load-result types.

## Risks
Dual SDK clients can diverge in endpoint, region, proxy, and credential behavior. SDK v2 async client does not support global bucket access, so missing region can break async listing. ETag substring handling assumes quoted SDK v2 ETags. Permissions are memoized and may become stale.

## Test Signals
Unit tests cover credential providers, exception conversion, metadata 404/403, permissions caching/mapping, operation mode, prefix stripping, and null last-modified time. S3Proxy integration tests cover real reads, recursive and async listings, descendant modes, and iterable listing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/S3AUnderFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/S3AUnderFileSystemFactory.java -->
# sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/S3AUnderFileSystemFactory.java

## Purpose
This factory registers S3 and S3A URI support with Alluxio.

## Important APIs, Types, And Functions
It implements `UnderFileSystemFactory`. `create` checks for non-null path and constructs `S3AUnderFileSystem`. `supportsPath` accepts `Constants.HEADER_S3A` and `Constants.HEADER_S3`, but not `s3n://`.

## Control Flow
Creation wraps any construction exception into an `IllegalArgumentException` with path context. Support checks are prefix-based and null-safe.

## State And Persistence
The factory is stateless.

## Dependencies And Integration Points
It integrates with `UnderFileSystemFactoryRegistry` and delegates to `S3AUnderFileSystem.createInstance`.

## Risks
Prefix-based matching is simple and can accept malformed URI strings with the right prefix. Creation builds real clients, so tests using default config may trigger environment-dependent credential/provider behavior if not isolated.

## Test Signals
`S3AUnderFileSystemFactoryTest` verifies registry lookup for `s3a://` and `s3://`, rejection of `s3n://`, null path error, create success, and supports-path negatives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/S3AUnderFileSystemFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/S3AUtils.java -->
# sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/S3AUtils.java

## Purpose
`S3AUtils` contains S3 ACL translation helpers used to derive Alluxio-style permission bits.

## Important APIs, Types, And Functions
`translateBucketAcl(AccessControlList acl, String userId)` returns a short mode. `isUserIdInGrantee` checks whether a canonical grantee identifies the requested user. The constructor is private.

## Control Flow
The translator iterates grants and maps `Read`/`ReadAcp` to read/execute bits, `Write`/`WriteAcp` to write, and `FullControl` to read/write/execute. Grants apply when the grantee is the matching canonical user, all users, or authenticated users.

## State And Persistence
The utility is stateless.

## Dependencies And Integration Points
It depends on AWS SDK v1 ACL, grantee, owner, group, and permission types. `S3AUnderFileSystem.getPermissionsInternal` uses it when ACL inheritance is enabled.

## Risks
S3 ACLs do not map naturally to POSIX permissions, so group/other distinctions are collapsed. Null or provider-specific grantee identifiers must be handled defensively.

## Test Signals
`S3AUtilsTest` covers user, everyone, authenticated-user, read/write/full-control grants, other-user behavior, and null canonical identifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/S3AUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/src/test/java/alluxio/underfs/s3a/S3ALowLevelOutputStreamTest.java -->
# sources/distributed-fs/alluxio/underfs/s3a/src/test/java/alluxio/underfs/s3a/S3ALowLevelOutputStreamTest.java

## Purpose
This test validates S3A streaming multipart upload behavior.

## Important APIs, Types, And Functions
It mocks `AmazonS3`, executor futures, local file creation, and output streams. Tests cover `writeByte`, `writeByteArrayForSmallFile`, `writeByteArrayForLargeFile`, `createEmptyFile`, `flush`, and `close`.

## Control Flow
Small writes should never initiate multipart upload and should call `putObject`. Large writes should initiate multipart, submit upload tasks, advance part numbers, wait on futures during flush, and complete multipart on close.

## State And Persistence
State under test includes part number, upload id, mocked temp buffering, future tags, and final content hash. No real S3 or local files are used.

## Dependencies And Integration Points
It exercises `S3ALowLevelOutputStream` hooks inherited from `ObjectLowLevelOutputStream`.

## Risks
Abort/error behavior and real part ordering are not covered. PowerMock constructor interception makes the test sensitive to implementation details.

## Test Signals
Passing tests confirm the expected threshold and multipart lifecycle for streaming S3 uploads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/src/test/java/alluxio/underfs/s3a/S3ALowLevelOutputStreamTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/src/test/java/alluxio/underfs/s3a/S3AOutputStreamTest.java -->
# sources/distributed-fs/alluxio/underfs/s3a/src/test/java/alluxio/underfs/s3a/S3AOutputStreamTest.java

## Purpose
This test covers the S3A local-buffered output stream.

## Important APIs, Types, And Functions
The fixture mocks `TransferManager`, `Upload`, `UploadResult`, temp `File`, and local stream construction. Tests cover write variants, close, and flush.

## Control Flow
Writes and flush should delegate to the local buffered stream. Close should upload a `PutObjectRequest` through the transfer manager, wait for upload result, capture ETag as content hash, and delete the temp file.

## State And Persistence
Production state is local temp file plus remote S3 upload on close; the test replaces both with mocks and verifies interactions.

## Dependencies And Integration Points
It validates `S3AOutputStream` behavior used when `UNDERFS_S3_STREAMING_UPLOAD_ENABLED` is false.

## Risks
The test does not exercise MD5 metadata contents, SSE metadata, interrupted upload, or temp deletion failures.

## Test Signals
Passing tests confirm write delegation, close upload, and content hash availability after upload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/src/test/java/alluxio/underfs/s3a/S3AOutputStreamTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/src/test/java/alluxio/underfs/s3a/S3AUnderFileSystemFactoryTest.java -->
# sources/distributed-fs/alluxio/underfs/s3a/src/test/java/alluxio/underfs/s3a/S3AUnderFileSystemFactoryTest.java

## Purpose
This test verifies S3A factory registration, URI support, and basic creation.

## Important APIs, Types, And Functions
Tests cover registry lookup for `s3a://`, `s3://`, and `s3n://`, `create` with null path, `create` with a valid path, and `supportsPath`.

## Control Flow
The registry should find a factory for S3A/S3 but not S3N. Null creation should throw a helpful `NullPointerException` wrapped in the factory error message. Valid creation should produce `S3AUnderFileSystem`.

## State And Persistence
Only global configuration and a default UFS configuration are used.

## Dependencies And Integration Points
It exercises Alluxio factory registry service loading and `S3AUnderFileSystemFactory`.

## Risks
Create success may rely on client construction not contacting AWS immediately. It does not validate credentials or endpoint behavior.

## Test Signals
Passing tests confirm that S3/S3A schemes are routed to this module and unsupported schemes are rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/src/test/java/alluxio/underfs/s3a/S3AUnderFileSystemFactoryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/src/test/java/alluxio/underfs/s3a/S3AUnderFileSystemMockServerTest.java -->
# sources/distributed-fs/alluxio/underfs/s3a/src/test/java/alluxio/underfs/s3a/S3AUnderFileSystemMockServerTest.java

## Purpose
This integration-style test validates S3A UFS behavior against an in-process S3Proxy server.

## Important APIs, Types, And Functions
The fixture creates an S3Proxy transient store, AWS SDK v1 client, SDK v2 async client, bucket, and `S3AUnderFileSystem`. Tests cover `read`, `nestedDirectory`, and `iterator`.

## Control Flow
The read test writes an object through the client and reads it through the UFS. The nested-directory test creates objects and marker directories, then compares recursive `listStatus` and async `performListingAsync` results for `ALL`, `ONE`, and `NONE`. The iterator test compares paged iterable listing with full recursive listing.

## State And Persistence
State lives in the transient S3Proxy bucket during each test. No real AWS service is used.

## Dependencies And Integration Points
It exercises real AWS SDK calls, Alluxio open/list/listStatusIterable/async-load behavior, and path-style endpoint configuration.

## Risks
S3Proxy is close but not identical to AWS S3; the fixture notes path-style behavior to close one gap. Fixed port `8001` can conflict in shared test environments.

## Test Signals
Passing tests provide strong evidence for read, directory inference, async descendant listing, continuation/last-item handling, and iterable pagination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/src/test/java/alluxio/underfs/s3a/S3AUnderFileSystemMockServerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/src/test/java/alluxio/underfs/s3a/S3AUnderFileSystemTest.java -->
# sources/distributed-fs/alluxio/underfs/s3a/src/test/java/alluxio/underfs/s3a/S3AUnderFileSystemTest.java

## Purpose
This unit test covers S3A UFS exception, credential, permission, operation-mode, and path-normalization behavior.

## Important APIs, Types, And Functions
Tests include delete failures, `isFile` 404/403 behavior, rename failure, static/default credential providers, permission caching/default/mapping, operation mode lookup, prefix stripping, and null last-modified metadata.

## Control Flow
Mocked AWS client calls throw or return metadata/ACL data. The UFS should translate service errors, cache permission lookup results, derive owner/group/mode, respect physical UFS state by root path, and normalize S3A prefixes into object keys.

## State And Persistence
State is mocked client behavior plus memoized permissions inside the UFS instance. No remote persistence is used.

## Dependencies And Integration Points
It exercises `S3AUnderFileSystem`, `AlluxioS3Exception`, `S3AUtils`, and Alluxio UFS mode/path contracts.

## Risks
Async SDK v2 behavior and real provider endpoints are not covered. Permission tests use simplified ACL mocks.

## Test Signals
Passing tests validate many high-risk S3A edge cases: credential source choice, exception translation, ACL-derived permissions, cached permission state, and root/path handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/src/test/java/alluxio/underfs/s3a/S3AUnderFileSystemTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/src/test/java/alluxio/underfs/s3a/S3AUtilsTest.java -->
# sources/distributed-fs/alluxio/underfs/s3a/src/test/java/alluxio/underfs/s3a/S3AUtilsTest.java

## Purpose
This test validates S3 ACL-to-mode translation.

## Important APIs, Types, And Functions
The fixture creates a canonical user grantee and `AccessControlList`. Tests cover user read/write/full control, all-users grants, authenticated-users grants, other-user behavior, and null canonical identifiers.

## Control Flow
Each test grants a permission and asserts the resulting mode for the owner id and another id. Read maps to `0500`, write to `0200`, read plus write or full control to `0700`, and unrelated users receive `0000` unless a group grantee applies.

## State And Persistence
All state is in-memory ACL model objects.

## Dependencies And Integration Points
It tests `S3AUtils.translateBucketAcl`, which feeds `S3AUnderFileSystem` permission inference when ACL inheritance is enabled.

## Risks
The tests intentionally simplify POSIX mapping and do not cover every AWS grantee class or combined grant ordering.

## Test Signals
Passing tests confirm the key mode mapping logic and null-identifier guard.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/s3a/src/test/java/alluxio/underfs/s3a/S3AUtilsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/swift/pom.xml -->
# sources/distributed-fs/alluxio/underfs/swift/pom.xml

## Purpose
This Maven descriptor builds the OpenStack Swift under file system module.

## Important APIs, Types, And Functions
The artifact is `alluxio-underfs-swift`. It depends on external `org.javaswift:joss`, provided `alluxio-core-common`, and the Alluxio core common test jar.

## Control Flow
The module inherits the parent build and configures shade and copy-rename plugins. Dependency packaging is primarily controlled by parent plugin configuration.

## State And Persistence
The POM has no runtime state. It controls Swift adapter compilation, test classpath, and packaging.

## Dependencies And Integration Points
It integrates Swift/JOSS support into the Alluxio underfs reactor and service-provider packaging.

## Risks
JOSS dependency compatibility and Keystone authentication behavior are the main module-level risks. Shading must preserve service metadata and avoid conflicts with HTTP/Jackson dependencies.

## Test Signals
Build success and Swift-specific tests elsewhere validate module wiring; this subset includes source for Keystone and input range handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/swift/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/KeystoneV3Access.java -->
# sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/KeystoneV3Access.java

## Purpose
`KeystoneV3Access` is a JOSS `Access` implementation carrying Keystone v3 token and endpoint URLs.

## Important APIs, Types, And Functions
It stores internal URL, preferred region, public URL, and token. It implements `getInternalURL`, `getPublicURL`, `getTempUrlPrefix`, `getToken`, `isTenantSupplied`, and `setPreferredRegion`.

## Control Flow
The object is a simple value holder. `setPreferredRegion` updates the region field and logs it; `getTempUrlPrefix` returns null, indicating temp URL support is not implemented here.

## State And Persistence
State is in-memory endpoint/token data for the lifetime of the JOSS account access object.

## Dependencies And Integration Points
It is produced by `KeystoneV3AccessProvider.authenticate` and consumed by JOSS Swift clients.

## Risks
The field name `mPrefferedRegion` is misspelled but internally consistent. Returning null for temp URL prefix may break callers expecting temporary URL support.

## Test Signals
No direct test is present in this subset. Coverage is expected through Keystone authentication and Swift client construction paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/KeystoneV3Access.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/KeystoneV3AccessProvider.java -->
# sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/KeystoneV3AccessProvider.java

## Purpose
`KeystoneV3AccessProvider` authenticates a Swift/JOSS account against Keystone v3 using password credentials.

## Important APIs, Types, And Functions
It implements JOSS `AccessProvider`. `authenticate` builds Keystone JSON request objects, posts to `AccountConfig.getAuthUrl`, expects HTTP 201, reads `X-Subject-Token`, parses the service catalog, and returns `KeystoneV3Access`. Nested request/response classes map Jackson JSON fields.

## Control Flow
Authentication constructs a password-scope request using username, password, and tenant/project id. It sends JSON via Apache HTTP client, rejects non-201 responses, parses the first response-body line, scans catalog entries named `swift` with type `object-store`, selects endpoints matching preferred region, and captures public/internal URLs.

## State And Persistence
The provider stores only `AccountConfig`. Tokens and endpoints are returned in an access object and are not persisted.

## Dependencies And Integration Points
It depends on JOSS, Apache HttpClient, Jackson, and Keystone response schema. Swift UFS account creation can use it for v3 auth.

## Risks
It returns null on many failures instead of throwing, which can defer errors. It reads only one response line and assumes headers/catalog fields exist. Endpoint selection is region-exact and may return access with null URLs.

## Test Signals
No direct test is listed in this subset, so behavior is mainly protected by compilation and any higher-level Swift authentication tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/KeystoneV3AccessProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/MidPartLongRange.java -->
# sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/MidPartLongRange.java

## Purpose
`MidPartLongRange` is a Swift/JOSS range helper for requesting a byte range from the middle of an object.

## Important APIs, Types, And Functions
It extends JOSS `MidPartRange` semantics for long offsets. The constructor stores start and end positions, and range formatting is used by `DownloadInstructions.setRange`.

## Control Flow
There is no complex control flow. It represents an inclusive byte range suitable for HTTP range downloads.

## State And Persistence
State is the requested start and end offsets. No data is persisted.

## Dependencies And Integration Points
`SwiftInputStream.createStream` constructs it with `startPos` and `endPos - 1` so JOSS downloads a bounded chunk for `MultiRangeObjectInputStream`.

## Risks
Inclusive/exclusive boundary mistakes can cause off-by-one reads. Long-range support must match JOSS and Swift HTTP range expectations.

## Test Signals
No direct test is present in this subset; `SwiftInputStream` behavior depends on it indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/MidPartLongRange.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/SwiftInputStream.java -->
# sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/SwiftInputStream.java

## Purpose
`SwiftInputStream` reads Swift objects through ranged JOSS downloads and Alluxio's multi-range stream abstraction.

## Important APIs, Types, And Functions
It extends `MultiRangeObjectInputStream`. Constructors accept JOSS `Account`, container name, object path, optional initial position, retry policy, and multi-range chunk size. `createStream(long startPos, long endPos)` creates ranged download instructions and returns the object input stream.

## Control Flow
For each requested range, the stream copies the retry policy, gets the container/object, sets a `MidPartLongRange(startPos, endPos - 1)`, and downloads an input stream. `NotFoundException` is retried and logged; after retries, the last exception is thrown.

## State And Persistence
State includes JOSS account, container, object path, inherited cursor, retry policy, and chunk size. Data is fetched from Swift on demand and not buffered persistently by this class.

## Dependencies And Integration Points
It depends on JOSS account/container/object APIs, `DownloadInstructions`, `MidPartLongRange`, and Alluxio retry/multi-range stream support. Swift UFS open paths construct it.

## Risks
Only `NotFoundException` is retried; other transient network errors are not. Throwing `lastException` can produce null if retry policy never attempts. Range boundary correctness depends on `MidPartLongRange`.

## Test Signals
No direct test is included here. Comparable OBS/OSS input-stream tests provide pattern-level signals, but Swift-specific JOSS behavior lacks coverage in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/SwiftInputStream.java -->
