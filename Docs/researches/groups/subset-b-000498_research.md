# subset-b-000498 Research

Grouped research for subset B work item `subset-b-000498`. Each section preserves the original source path and is wrapped for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/SwiftMockOutputStream.java -->
# sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/SwiftMockOutputStream.java

## Purpose
`SwiftMockOutputStream` is the simulation-mode output stream for Alluxio's Swift under file system. Instead of streaming bytes to Swift as they are written, it buffers all writes into a local temporary file and uploads that file to a JOSS mock `StoredObject` when `close()` succeeds.

## APIs and Control Flow
The constructor accepts a JOSS `Account`, container name, object name, and Alluxio temporary directory list. It chooses a temp directory with `CommonUtils.getTmpDir`, builds a UUID-named local file with `PathUtils.concatPath`, and wraps a `FileOutputStream` in a `BufferedOutputStream`. The three `write` overloads and `flush` delegate directly to the local stream. `close()` is guarded by `mClosed`; on first close it closes the local stream, resolves `Container` and `StoredObject` through JOSS, and calls `uploadObject(mFile)`.

## State, Dependencies, and Integration
State is local to one stream: the temp `File`, delegate output stream, target Swift identifiers, JOSS account, and close flag. It integrates with `SwiftUnderFileSystem.createObject` only when `SWIFT_SIMULATION` is enabled. Dependencies are JOSS model objects, Alluxio temp path utilities, and SLF4J logging.

## Risks and Test Signals
The temp file is not deleted after upload, so repeated simulation writes can leave local artifacts. `mClosed` is not thread-safe, which matches the `@NotThreadSafe` annotation. Errors during JOSS upload are wrapped as `IOException`. There is no direct test for this class in the listed subset; coverage is indirect through Swift simulation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/SwiftMockOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/SwiftOutputStream.java -->
# sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/SwiftOutputStream.java

## Purpose
`SwiftOutputStream` wraps an `HttpURLConnection` output stream for direct Swift PUT uploads. It exists because `SwiftDirectClient` bypasses JOSS for object creation and needs an `OutputStream` facade compatible with Alluxio object creation.

## APIs and Control Flow
The constructor opens `httpCon.getOutputStream()` and stores both the delegate stream and connection. `write(int)`, `write(byte[])`, `write(byte[], int, int)`, and `flush()` delegate unchanged. `close()` closes the request body, reads either `getErrorStream()` for HTTP status >= 400 or `getInputStream()` otherwise, closes that response stream, logs close errors, and disconnects the HTTP connection.

## State, Dependencies, and Integration
State is the delegate stream and `HttpURLConnection`. It is constructed by `SwiftDirectClient.put`, which sets method, token, content type, chunked transfer, and timeouts. The class depends only on JDK networking and SLF4J and is explicitly not thread-safe.

## Risks and Test Signals
A failed Swift response status is logged but not surfaced to the caller unless stream handling throws, so callers may treat failed uploads as successful. The catch block can close `is` and swallow the original exception after logging. `SwiftOutputStreamTest` covers constructor failure, write and flush delegation, choosing error vs input stream by response code, and disconnect on close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/SwiftOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/SwiftUnderFileSystem.java -->
# sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/SwiftUnderFileSystem.java

## Purpose
`SwiftUnderFileSystem` is Alluxio's OpenStack Swift object-store adapter. It extends `ObjectUnderFileSystem`, maps Swift containers and objects to Alluxio UFS paths, creates directory marker objects with a trailing slash, lists objects through JOSS pagination, and opens reads through `SwiftInputStream`.

## APIs and Control Flow
Construction derives the container name from the mount URI, builds a JOSS `AccountConfig`, and supports simulation, Keystone, Keystone v3 external provider, SwiftAuth, and TempAuth-style authentication. It authenticates, disables container caching, verifies that the container exists, and derives owner/mode from Swift container ACLs. Object operations implement `copyObject`, `createEmptyObject`, `createObject`, `deleteObject`, `getObjectListingChunk`, `getObjectStatus`, `getPermissions`, `getRootKey`, and `openObject`.

## State, Persistence, and Listing
Persistent state lives in Swift objects; directories are zero-byte marker objects ending in `/`. Runtime state includes the JOSS `Account`, `Access`, container name, simulation flag, account owner, and calculated mode. Listing obtains a `PaginationMap`, then `SwiftObjectListingChunk` either calls `listDirectory` for non-recursive delimiter listings or `list` for recursive listings. Object status captures key, ETag, content length, and last-modified time when available.

## Dependencies and Integration
This class depends on Alluxio UFS abstractions, retry policy, configuration keys, path utilities, JOSS account/container/object APIs, Jackson configuration, and `SwiftDirectClient` for non-simulation writes. It integrates with `SwiftUnderFileSystemFactory` for path support and credentials gating.

## Risks and Test Signals
JOSS ACL strings are split without null checks, so unusual backend responses may fail construction. Copy retries only for generic exceptions and immediately returns false on `CommandException`. Direct writes inherit `SwiftOutputStream`'s weak failure propagation. Factory-level tests verify registry support, but no listed test exercises constructor auth modes, ACL translation, pagination, copy retries, or real Swift integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/SwiftUnderFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/SwiftUnderFileSystemFactory.java -->
# sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/SwiftUnderFileSystemFactory.java

## Purpose
`SwiftUnderFileSystemFactory` registers and constructs the Swift UFS implementation for paths beginning with Alluxio's `swift://` header.

## APIs and Control Flow
`supportsPath` returns true for non-null paths starting with `Constants.HEADER_SWIFT`. `create` validates the path, checks credentials, and returns a new `SwiftUnderFileSystem`; construction exceptions are propagated through Guava `Throwables.propagate`. `checkSwiftCredentials` accepts simulation mode without credentials; otherwise it requires password, tenant, auth URL, and user keys.

## State, Dependencies, and Integration
The factory is stateless and `@ThreadSafe`. It depends on Alluxio configuration keys, URI construction, the UFS factory interface, and Guava preconditions/throwables. It is consumed through `UnderFileSystemFactoryRegistry`.

## Risks and Test Signals
Credential checking does not require an auth method or region, leaving those to the UFS constructor. Missing credentials become a propagated `IOException` rather than a checked failure. `SwiftUnderFileSystemFactoryTest` verifies registry discovery for `swift://` and rejection of `file://`, but not credential permutations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/SwiftUnderFileSystemFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/http/SwiftDirectClient.java -->
# sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/http/SwiftDirectClient.java

## Purpose
`SwiftDirectClient` provides direct HTTP PUT upload setup for Swift objects, bypassing JOSS upload limitations while still using JOSS `Access` for public URL and auth token.

## APIs and Control Flow
`put(Access, String)` builds a URL from `access.getPublicURL()` and the object name, opens a URL connection, verifies it is an `HttpURLConnection`, sets method `PUT`, adds `X-Auth-Token`, content type, input/output flags, `Connection: close`, read timeout, `Transfer-Encoding: chunked`, and an 8 MiB chunked streaming mode. It connects and returns a `SwiftOutputStream`.

## State, Dependencies, and Integration
The class is stateless and thread-safe. It depends on JDK URL connections, JOSS `Access`, SLF4J, and `SwiftOutputStream`. `SwiftUnderFileSystem.createObject` calls it for all non-simulation object writes.

## Risks and Test Signals
Object names are concatenated into the URL without explicit URL encoding, so keys containing unsafe characters depend on prior normalization or backend tolerance. The fixed read timeout and chunk size are not configurable here. There is no listed direct unit test for request headers or URL formation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/http/SwiftDirectClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/swift/src/test/java/alluxio/underfs/swift/SwiftOutputStreamTest.java -->
# sources/distributed-fs/alluxio/underfs/swift/src/test/java/alluxio/underfs/swift/SwiftOutputStreamTest.java

## Purpose
This PowerMock/JUnit test suite verifies the thin delegation and close behavior of `SwiftOutputStream`.

## Important Tests
`testConstructor` forces `HttpURLConnection.getOutputStream()` to throw and expects an `IOException` containing the original message. `testWrite1`, `testWrite2`, and `testWrite3` verify delegation to the wrapped output stream. `testCloseError` checks that HTTP 400 causes `getErrorStream()` and disconnect. `testCloseSuccess` checks that HTTP 200 uses `getInputStream()` and disconnect. `testFlush` verifies flush delegation.

## Dependencies and Integration
The suite uses PowerMock runner, Mockito verification, and `ExpectedException`. It mocks the HTTP connection and output stream rather than making network calls.

## Signals and Gaps
The tests document the current behavior that close inspects the response stream but does not assert failure for HTTP 400. They do not cover null response/error streams, double close behavior, response stream close failures, or status codes such as 201/202 that are expected for Swift writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/swift/src/test/java/alluxio/underfs/swift/SwiftOutputStreamTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/swift/src/test/java/alluxio/underfs/swift/SwiftUnderFileSystemFactoryTest.java -->
# sources/distributed-fs/alluxio/underfs/swift/src/test/java/alluxio/underfs/swift/SwiftUnderFileSystemFactoryTest.java

## Purpose
This JUnit test verifies that the Swift UFS factory is discoverable through Alluxio's factory registry for supported path schemes.

## Important Tests
The single `factory` test asks `UnderFileSystemFactoryRegistry.find` for a `swift://localhost/test/path` URI and expects a non-null factory. It also asks for a `file://localhost/test/path` URI and expects no Swift factory match.

## Dependencies and Integration
The test uses `Configuration.global()` and the shared UFS registry, so it validates service registration in addition to the factory's `supportsPath` logic.

## Signals and Gaps
This is a narrow registration test. It does not exercise `create`, Swift credential gating, simulation mode, or constructor failures when the target Swift container is missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/swift/src/test/java/alluxio/underfs/swift/SwiftUnderFileSystemFactoryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/tos/pom.xml -->
# sources/distributed-fs/alluxio/underfs/tos/pom.xml

## Purpose
This Maven module declares Alluxio's Tinder Object Storage under file system implementation as `alluxio-underfs-tos`.

## Important Configuration
The module inherits from `alluxio-underfs` version `2.10.0-SNAPSHOT`, sets `build.path` for subproject builds, and describes the artifact as the Tinder Object Storage UFS. Runtime dependencies include `com.volcengine:ve-tos-java-sdk`, `commons-codec`, and provided `alluxio-core-common`. Tests depend on Alluxio common test jar and Mockito inline.

## Build and Integration
The build uses the shared `maven-shade-plugin` and `copy-rename-maven-plugin`, aligning it with the packaging model used by other Alluxio UFS modules. The Volcengine SDK dependency is the key external integration for all TOS client operations.

## Risks and Test Signals
Dependency versions are inherited, so module behavior depends on parent dependency management. The module name and description use "Tinder Object Storage"; any product rename must be handled consistently in docs and configuration keys. Test dependencies show the implementation is designed for mock-heavy unit tests rather than live TOS integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/tos/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/tos/src/main/java/alluxio/underfs/tos/AlluxioTosException.java -->
# sources/distributed-fs/alluxio/underfs/tos/src/main/java/alluxio/underfs/tos/AlluxioTosException.java

## Purpose
`AlluxioTosException` translates Volcengine `TosException` failures into Alluxio runtime exceptions with gRPC status codes and `ErrorType.External`.

## APIs and Control Flow
`from(TosException)` and `from(String, TosException)` map the HTTP status code from the TOS exception to a gRPC `Status`, derive a default message from TOS code and message, and construct a retryable `AlluxioTosException`. `httpStatusToGrpcStatus` maps common HTTP statuses to `INVALID_ARGUMENT`, `UNAUTHENTICATED`, `PERMISSION_DENIED`, `NOT_FOUND`, `UNIMPLEMENTED`, `ABORTED`, `FAILED_PRECONDITION`, `OUT_OF_RANGE`, `INTERNAL`, `UNAVAILABLE`, `DEADLINE_EXCEEDED`, or `UNKNOWN`.

## State, Dependencies, and Integration
The class is immutable after construction and stores no additional fields beyond its superclass. It is used by TOS streams, the UFS, and the factory when SDK calls fail.

## Risks and Test Signals
All converted exceptions are marked retryable, including client-side or permission failures that may not be usefully retried. The default message builds `code:message`, which can degrade if either field is null. No listed test directly verifies HTTP-to-gRPC status mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/tos/src/main/java/alluxio/underfs/tos/AlluxioTosException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/tos/src/main/java/alluxio/underfs/tos/TOSInputStream.java -->
# sources/distributed-fs/alluxio/underfs/tos/src/main/java/alluxio/underfs/tos/TOSInputStream.java

## Purpose
`TOSInputStream` implements ranged reads from TOS using Alluxio's `MultiRangeObjectInputStream`, including retry behavior for eventually consistent not-found responses.

## APIs and Control Flow
Constructors store bucket, key, client, retry policy, initial position, and multi-range chunk size. They perform a `headObject` call to capture content length. `createStream(startPos, endPos)` builds a `GetObjectV2Input` with range options, clamps the end offset to `mContentLength - 1`, copies the retry policy, and repeatedly calls `getObject`. Non-404 TOS errors are thrown immediately as `IOException`; 404 errors are retried until policy exhaustion.

## State, Dependencies, and Integration
Runtime state includes bucket, key, `TOSV2` client, object length, and retry policy. It is created by `TOSUnderFileSystem.openObject`. It depends on Volcengine SDK request/response types, Apache `HttpStatus`, and Alluxio range-stream machinery.

## Risks and Test Signals
The implementation assumes `headObject` succeeds and does not wrap its exceptions locally. Empty objects can produce a range ending at `-1`. Test setup mocks range strings such as `bytes=0-`, but the implementation clamps against content length from `headObject`, so realistic range behavior depends on metadata mocking. `TOSInputStreamTest` covers close, sequential reads, byte-array reads, and skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/tos/src/main/java/alluxio/underfs/tos/TOSInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/tos/src/main/java/alluxio/underfs/tos/TOSLowLevelOutputStream.java -->
# sources/distributed-fs/alluxio/underfs/tos/src/main/java/alluxio/underfs/tos/TOSLowLevelOutputStream.java

## Purpose
`TOSLowLevelOutputStream` is the streaming/multipart upload implementation for TOS. It extends Alluxio's `ObjectLowLevelOutputStream` and supplies TOS-specific multipart init, upload, complete, abort, and single-object upload hooks.

## APIs and Control Flow
The constructor passes bucket, key, executor, configured partition size, and UFS config to the superclass and stores the `TOSV2` client. `initMultiPartUploadInternal` calls `createMultipartUpload` and stores the upload ID. `uploadPartInternal` wraps a file input stream with `TosRepeatableBoundedFileInputStream`, chooses the last-part size when needed, uploads a part, and records its ETag in `mTags`. `completeMultiPartUploadInternal` sends the uploaded part list and stores the completed ETag. `abortMultiPartUploadInternal`, `createEmptyObject`, and `putObject` map the remaining object-store operations.

## State, Persistence, and Dependencies
Persistent state is the target TOS object or multipart upload. Runtime state includes the TOS client, synchronized uploaded-part list, volatile upload ID, and content hash. It depends on Alluxio streaming upload infrastructure, Guava `ListeningExecutorService`, Volcengine multipart model types, and Java file I/O.

## Risks and Test Signals
`uploadPartInternal` catches `IOException` but not `TosException`, so SDK part-upload failures may propagate differently from other methods. `mTags` is synchronized but multipart completion order depends on how the superclass schedules and waits for uploads. MD5 parameters are accepted but unused. `TOSLowLevelOutputStreamTest` covers empty, small, large, and flushed writes, plus content hash selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/tos/src/main/java/alluxio/underfs/tos/TOSLowLevelOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/tos/src/main/java/alluxio/underfs/tos/TOSOutputStream.java -->
# sources/distributed-fs/alluxio/underfs/tos/src/main/java/alluxio/underfs/tos/TOSOutputStream.java

## Purpose
`TOSOutputStream` is the non-streaming TOS upload path. It buffers the complete object in a local temporary file, calculates an MD5 when available, and uploads the file to TOS on close.

## APIs and Control Flow
The constructor validates bucket, key, and client, creates a UUID temp file under Alluxio temp dirs, initializes an MD5 `MessageDigest`, and wraps file output in a `DigestOutputStream` when possible. Writes and flushes delegate to the local output stream. `close()` uses an `AtomicBoolean` to make the method idempotent, closes the local stream, opens a buffered input stream from the temp file, sets content length and content MD5 metadata, uploads with `putObject`, stores the returned ETag, and deletes the temp file in `finally`.

## State, Dependencies, and Integration
State includes bucket, key, temp file, TOS client, local stream, digest, close flag, and optional content hash. It implements `ContentHashable` so callers can retrieve the ETag. `TOSUnderFileSystem.createObject` chooses this class when streaming upload is disabled.

## Risks and Test Signals
The class is marked not thread-safe despite an atomic close guard; concurrent writes and close are unsafe. Temp-file delete failure is logged but not raised. SDK errors are converted to `AlluxioTosException`. `TOSOutputStreamTest` covers constructor I/O failure, write delegation, flush, upload failure, delete-on-close, and ETag exposure, but uses heavy static/constructor mocking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/tos/src/main/java/alluxio/underfs/tos/TOSOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/tos/src/main/java/alluxio/underfs/tos/TOSUnderFileSystem.java -->
# sources/distributed-fs/alluxio/underfs/tos/src/main/java/alluxio/underfs/tos/TOSUnderFileSystem.java

## Purpose
`TOSUnderFileSystem` adapts Volcengine TOS into Alluxio's object-store UFS abstraction. It handles credential-based client construction, object CRUD, listing, ranged reads, buffered or streaming writes, multipart cleanup, and default object-store permissions.

## APIs and Control Flow
`createInstance` validates access key, secret key, region, and endpoint configuration, builds `TOSClientConfiguration` with `initializeTOSClientConfig`, and constructs a `TOSV2` client. `cleanup` pages through multipart uploads and aborts uploads older than the configured clean age. `copyObject`, `createEmptyObject`, `deleteObject`, and `deleteObjects` translate Alluxio operations to SDK requests. `createObject` chooses `TOSLowLevelOutputStream` when streaming upload is enabled, otherwise `TOSOutputStream`. Listing builds `ListObjectsType2Input` with delimiter based on recursion and wraps output in `TOSObjectListingChunk`.

## State, Persistence, and Dependencies
Persistent data is stored as TOS objects with `/` folder markers. Runtime state includes `TOSV2`, bucket name, and a memoized streaming-upload executor. The class depends on Alluxio object-store UFS classes, Volcengine TOS SDK, Guava suppliers, Alluxio executor factories, path utilities, and retry/open options.

## Risks and Test Signals
`close()` closes `mClient` without null protection, though production construction supplies a client. `copyObject` returns false for all TOS errors and may hide permission or service problems. `cleanup` mutates server-side multipart uploads and throws runtime exceptions on SDK failure. Tests cover delete-directory behavior when listing throws, 404 vs non-404 status handling, rename error propagation, prefix stripping, and folder suffix; many real SDK paths remain mock-only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/tos/src/main/java/alluxio/underfs/tos/TOSUnderFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/tos/src/main/java/alluxio/underfs/tos/TOSUnderFileSystemFactory.java -->
# sources/distributed-fs/alluxio/underfs/tos/src/main/java/alluxio/underfs/tos/TOSUnderFileSystemFactory.java

## Purpose
`TOSUnderFileSystemFactory` registers the `tos://` scheme and creates configured TOS UFS instances.

## APIs and Control Flow
`supportsPath` checks for non-null paths starting with `Constants.HEADER_TOS`. `create` validates the path, checks for access key, secret key, endpoint, and region, then delegates to `TOSUnderFileSystem.createInstance`. SDK `TosException` is logged and converted to `AlluxioTosException`; other exceptions are propagated.

## State, Dependencies, and Integration
The factory is stateless. It depends on Alluxio URI/config/factory interfaces, TOS property keys, Guava preconditions/throwables, and the TOS exception type. It is loaded by Alluxio's factory registry.

## Risks and Test Signals
Credential checking uses `isSet`, so empty configured values may pass initial gating and fail later. Missing credentials become propagated runtime exceptions. `TOSUnderFileSystemFactoryTest` covers registry discovery, null path, supported and unsupported schemes, and missing credentials.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/tos/src/main/java/alluxio/underfs/tos/TOSUnderFileSystemFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/tos/src/test/java/alluxio/underfs/tos/TOSInputStreamTest.java -->
# sources/distributed-fs/alluxio/underfs/tos/src/test/java/alluxio/underfs/tos/TOSInputStreamTest.java

## Purpose
This JUnit/Mockito suite validates basic read behavior for `TOSInputStream`.

## Important Tests
Setup mocks `TOSV2.getObject` to return byte-array streams for positional ranges and constructs a `TOSInputStream` with `CountingRetry(1)`. `close` expects reads after close to throw `IOException("Stream closed")`. `readInt` reads three bytes sequentially. `readByteArray` reads into a buffer. `skip` confirms skipping one byte advances the stream.

## Dependencies and Integration
The test depends on Alluxio global configuration for multi-range chunk size, Volcengine SDK model classes, Mockito argument matching, and JUnit `ExpectedException`.

## Signals and Gaps
The tests exercise `MultiRangeObjectInputStream` integration more than TOS metadata handling. They do not cover 404 retry exhaustion, non-404 TOS errors, empty objects, range clamping, or `headObject` metadata failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/tos/src/test/java/alluxio/underfs/tos/TOSInputStreamTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/tos/src/test/java/alluxio/underfs/tos/TOSLowLevelOutputStreamTest.java -->
# sources/distributed-fs/alluxio/underfs/tos/src/test/java/alluxio/underfs/tos/TOSLowLevelOutputStreamTest.java

## Purpose
This PowerMock/Mockito suite verifies the streaming TOS upload implementation's small-object and multipart boundaries.

## Important Tests
`writeByte`, `writeByteArrayForSmallFile`, and `createEmptyFile` verify that small or empty writes use `putObject` rather than multipart upload. `writeByteArrayForLargeFile` writes one byte over the 8 MiB partition size and expects multipart creation, two executor submissions, completion, and multipart ETag. `flush` verifies upload tasks are submitted and waited for before close. `close` checks empty close behavior and content hash.

## Dependencies and Integration
The test configures `UNDERFS_TOS_STREAMING_UPLOAD_PARTITION_SIZE` and `UNDERFS_TOS_STREAMING_UPLOAD_ENABLED`, mocks `TOSV2`, `ListeningExecutorService`, and SDK output types, and relies on the superclass upload scheduling behavior.

## Signals and Gaps
Coverage establishes the partition threshold and content hash paths. It does not cover failed part upload, abort-on-error, ordering of uploaded parts under true concurrency, or SDK exception conversion in all multipart operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/tos/src/test/java/alluxio/underfs/tos/TOSLowLevelOutputStreamTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/tos/src/test/java/alluxio/underfs/tos/TOSOutputStreamTest.java -->
# sources/distributed-fs/alluxio/underfs/tos/src/test/java/alluxio/underfs/tos/TOSOutputStreamTest.java

## Purpose
This test suite validates `TOSOutputStream` delegation, upload close behavior, exception propagation, and content hash reporting.

## Important Tests
`testConstructor` forces `Files.newOutputStream` to throw and expects an `IOException`. `testWrite1`, `testWrite2`, and `testWrite3` verify writes reach the buffered local stream. `testCloseError` makes `putObject` throw a `TosException` and expects `AlluxioTosException`. `testCloseSuccess` verifies temp file deletion. `testFlush` verifies flush delegation. Successful tests assert that `getContentHash()` exposes the mocked ETag.

## Dependencies and Integration
The suite uses PowerMock to intercept constructors and static `Files` methods, Mockito for the TOS client, and Alluxio temp directory configuration.

## Signals and Gaps
The tests confirm the local-buffer upload design but do not exercise actual MD5 metadata generation, idempotent double close, temp file delete failure logging, or real filesystem writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/tos/src/test/java/alluxio/underfs/tos/TOSOutputStreamTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/tos/src/test/java/alluxio/underfs/tos/TOSUnderFileSystemFactoryTest.java -->
# sources/distributed-fs/alluxio/underfs/tos/src/test/java/alluxio/underfs/tos/TOSUnderFileSystemFactoryTest.java

## Purpose
This test suite verifies TOS UFS factory registration, scheme support, null-path handling, and credential gating.

## Important Tests
`setUp` mocks an `InstancedConfiguration` with root TOS URI and credential properties, then obtains the factory through `UnderFileSystemFactoryRegistry`. `factory` expects the registry lookup to succeed. `createInstanceWithNullPath` expects a path-related `NullPointerException`. `supportsPath` accepts `tos://` and rejects `s3a://`, invalid strings, and null. `createInstanceWithMissingCredentials` clears access and secret keys and expects a runtime failure containing the credential error.

## Dependencies and Integration
The test relies on Alluxio registry loading, mocked configuration, and default UFS configuration wrapping.

## Signals and Gaps
The suite validates early factory behavior, not actual TOS client construction. Endpoint and region missing-credential permutations are not separately tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/tos/src/test/java/alluxio/underfs/tos/TOSUnderFileSystemFactoryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/tos/src/test/java/alluxio/underfs/tos/TOSUnderFileSystemTest.java -->
# sources/distributed-fs/alluxio/underfs/tos/src/test/java/alluxio/underfs/tos/TOSUnderFileSystemTest.java

## Purpose
This JUnit/Mockito suite checks selected `TOSUnderFileSystem` behaviors around listing failures, status exceptions, rename propagation, and path prefix handling.

## Important Tests
Setup constructs a protected `TOSUnderFileSystem` with a mocked `TOSV2` client. Non-recursive and recursive directory deletes return false when `listObjectsType2` throws `TosClientException`. `isFile404` returns false for a 404 `TosServerException`, while `isFileException` expects `AlluxioTosException` for 403. `renameOnTosClientException` expects an `AlluxioTosException`. `stripPrefixIfPresent` verifies `tos://bucket` and slash normalization, and `getFolderSuffix` expects `/`.

## Dependencies and Integration
The suite uses Alluxio delete options, default configuration, Mockito, and Volcengine exception types.

## Signals and Gaps
The tests cover important error translation behavior but leave most object operations untested: copy success/failure, multi-delete, cleanup pagination, object listing chunks, streaming selection, and close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/tos/src/test/java/alluxio/underfs/tos/TOSUnderFileSystemTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/wasb/pom.xml -->
# sources/distributed-fs/alluxio/underfs/wasb/pom.xml

## Purpose
This Maven module packages the Microsoft Azure Blob Storage UFS implementation as `alluxio-underfs-wasb`.

## Important Configuration
The module inherits from `alluxio-underfs`, sets `ufs.hadoop.version` to `3.3.4`, and depends on `hadoop-azure`, provided `alluxio-core-common`, and `alluxio-underfs-hdfs`. Test dependencies include Apache commons-lang3 and Alluxio common test jar.

## Build and Integration
The shade plugin packages dependencies while excluding license/signature metadata and excluding HDFS UFS factory service entries because the module depends on the HDFS UFS implementation but should not register HDFS from this artifact. The copy-rename plugin follows Alluxio UFS packaging conventions.

## Risks and Test Signals
The module is tightly coupled to Hadoop Azure filesystem implementation class names. Shading exclusions are important; if HDFS factory metadata leaks into the WASB artifact, registry behavior can change. The module's tests focus on factory support rather than full Azure integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/wasb/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/wasb/src/main/java/alluxio/underfs/wasb/WasbUnderFileSystem.java -->
# sources/distributed-fs/alluxio/underfs/wasb/src/main/java/alluxio/underfs/wasb/WasbUnderFileSystem.java

## Purpose
`WasbUnderFileSystem` adapts Azure Blob Storage through Hadoop's WASB/WASBS filesystem by extending Alluxio's `HdfsUnderFileSystem`.

## APIs and Control Flow
`createConfiguration` starts with HDFS UFS configuration, copies Alluxio Azure account keys matching `UNDERFS_AZURE_ACCOUNT_KEY` templates, and sets Hadoop implementation classes for secure `wasbs` or plain `wasb`. `createInstance` detects the URI scheme and constructs the UFS. `getUnderFSType` returns `wasb`. `getBlockSizeByte` returns Alluxio's default block size. `getStatus` delegates to HDFS UFS, then rewrites file statuses to use object-store block size instead of Azure's reported 512 MiB.

## State, Dependencies, and Integration
State is inherited from `HdfsUnderFileSystem`; this class mainly supplies the Hadoop `Configuration`. It depends on Hadoop Azure classes by class-name string, Alluxio property keys, and HDFS UFS behavior. File locations are unsupported and return null.

## Risks and Test Signals
Returning null for file locations requires callers to tolerate unsupported locality. The status rewrite preserves most metadata but substitutes last-modified null with `0L`. Tests only verify factory registration for schemes; configuration rewriting and status replacement are not covered here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/wasb/src/main/java/alluxio/underfs/wasb/WasbUnderFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/wasb/src/main/java/alluxio/underfs/wasb/WasbUnderFileSystemFactory.java -->
# sources/distributed-fs/alluxio/underfs/wasb/src/main/java/alluxio/underfs/wasb/WasbUnderFileSystemFactory.java

## Purpose
`WasbUnderFileSystemFactory` registers Azure Blob Storage UFS support for `wasb://` and `wasbs://` paths.

## APIs and Control Flow
`create` checks that `path` is non-null and delegates to `WasbUnderFileSystem.createInstance`. `supportsPath` returns true for non-null paths starting with `Constants.HEADER_WASB` or `Constants.HEADER_WASBS`.

## State, Dependencies, and Integration
The factory is stateless and thread-safe. It depends on Alluxio URI construction, UFS configuration, and factory registry conventions.

## Risks and Test Signals
The factory performs no credential validation; Hadoop Azure initialization is responsible for later failures. `WasbUnderFileSystemFactoryTest` validates registry discovery for both schemes and rejection of an `alluxio://` path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/wasb/src/main/java/alluxio/underfs/wasb/WasbUnderFileSystemFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/wasb/src/test/java/alluxio/underfs/wasb/WasbUnderFileSystemFactoryTest.java -->
# sources/distributed-fs/alluxio/underfs/wasb/src/test/java/alluxio/underfs/wasb/WasbUnderFileSystemFactoryTest.java

## Purpose
This JUnit test verifies that the WASB module is registered for Azure Blob Storage schemes.

## Important Tests
The single `factory` test uses `UnderFileSystemFactoryRegistry.find` to assert non-null factories for `wasb://localhost/test/path` and `wasbs://localhost/test/path`, then asserts no matching factory for `alluxio://localhost/test/path`.

## Dependencies and Integration
The test uses Alluxio global configuration and the shared UFS registry, so it checks service registration rather than just calling `supportsPath` directly.

## Signals and Gaps
Coverage is limited to path support. It does not verify Hadoop Azure class configuration, account-key propagation, secure vs insecure configuration, or block-size status rewriting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/wasb/src/test/java/alluxio/underfs/wasb/WasbUnderFileSystemFactoryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/web/pom.xml -->
# sources/distributed-fs/alluxio/underfs/web/pom.xml

## Purpose
This Maven module packages the read-only Web UFS implementation as `alluxio-underfs-web`.

## Important Configuration
The module inherits from `alluxio-underfs`, sets `build.path`, depends on provided `alluxio-core-common`, and adds `org.jsoup:jsoup:1.15.3` for HTML parsing. It uses the shared shade and copy-rename Maven plugins.

## Build and Integration
The dependency set is intentionally small because Web UFS relies on Alluxio HTTP utilities and Jsoup rather than a cloud SDK. Shading makes the implementation deployable as an Alluxio UFS extension.

## Risks and Test Signals
The explicit Jsoup version can age independently of parent dependency management. The module supports network-facing HTML parsing, so dependency security matters. Tests in this subset include factory support and a live-style check against an Apache archive URL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/web/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/web/src/main/java/alluxio/underfs/web/WebUnderFileSystem.java -->
# sources/distributed-fs/alluxio/underfs/web/src/main/java/alluxio/underfs/web/WebUnderFileSystem.java

## Purpose
`WebUnderFileSystem` is a read-only HTTP/HTTPS UFS. It treats web URLs as files or directory listings, reads content via HTTP GET, and parses HTML directory indexes with Jsoup.

## APIs and Control Flow
Unsupported mutating or connection operations throw `IOException` with a shared unsupported message. `exists` uses `HttpUtils.head`. `getBlockSizeByte`, `getFileStatus`, and `getDirectoryStatus` rely on `getStatus`. Private `getStatus(path, fileName)` reads HEAD headers for content length and last modified, computes an approximate content hash for files, and returns file or directory status based on `isFile`. `isDirectory` checks `Content-Type` for `text/html`, downloads the page, and compares the `<title>` text against configured directory-title markers. `listStatus` downloads HTML, finds anchor elements, skips from configured parent markers, resolves relative links, and obtains statuses for each link. `open` gets an input stream and skips the requested offset.

## State, Dependencies, and Integration
State is limited to configured HTTP timeout and unsupported-operation text. Dependencies include `ConsistentUnderFileSystem`, Alluxio status/options classes, `HttpUtils`, `ByteStreams`, Jsoup, Apache HTTP headers, and web-specific configuration keys for timeout, title matching, parent names, and last-modified format.

## Risks and Test Signals
`isFile` calls `isDirectory`, so status checks can issue HEAD plus GET requests and may misclassify arbitrary HTML files as directories based on title text. `listStatus` builds relative URLs with `path + "/" + href`, which can double slashes or mishandle `../`/absolute-root links. Live tests depend on external network availability and remote HTML layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/web/src/main/java/alluxio/underfs/web/WebUnderFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/web/src/main/java/alluxio/underfs/web/WebUnderFileSystemFactory.java -->
# sources/distributed-fs/alluxio/underfs/web/src/main/java/alluxio/underfs/web/WebUnderFileSystemFactory.java

## Purpose
`WebUnderFileSystemFactory` registers Web UFS support for `http://` and `https://` paths.

## APIs and Control Flow
`create` validates a non-null path and constructs `WebUnderFileSystem` with an `AlluxioURI` and UFS configuration. `supportsPath` accepts non-null paths starting with `Constants.HEADER_HTTP` or `Constants.HEADER_HTTPS`.

## State, Dependencies, and Integration
The factory is stateless and thread-safe. It depends on Alluxio URI and UFS factory APIs and is consumed by the factory registry.

## Risks and Test Signals
There is no validation that a URL is reachable or syntactically complete before constructing the UFS. `WebUnderFileSystemFactoryTest` confirms registry support for HTTP/HTTPS and rejects a near-miss `httpx://` scheme.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/web/src/main/java/alluxio/underfs/web/WebUnderFileSystemFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/web/src/test/java/alluxio/underfs/web/WebUnderFileSystemFactoryTest.java -->
# sources/distributed-fs/alluxio/underfs/web/src/test/java/alluxio/underfs/web/WebUnderFileSystemFactoryTest.java

## Purpose
This JUnit test verifies Web UFS factory discovery for HTTP and HTTPS URLs.

## Important Tests
The `factory` test asks `UnderFileSystemFactoryRegistry.find` for an HTTPS Alluxio downloads URL and an HTTP Alluxio downloads URL and expects factories for both. It asks for `httpx://path` and expects no factory.

## Dependencies and Integration
The test uses Alluxio global configuration and registry lookup, so it validates service registration and scheme matching.

## Signals and Gaps
The comment mentions `/` or `file://`, but the actual test covers HTTP/HTTPS only. The suite does not test `create`, malformed URLs, timeout configuration, or network operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/web/src/test/java/alluxio/underfs/web/WebUnderFileSystemFactoryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/web/src/test/java/alluxio/underfs/web/WebUnderFileSystemTest.java -->
# sources/distributed-fs/alluxio/underfs/web/src/test/java/alluxio/underfs/web/WebUnderFileSystemTest.java

## Purpose
This test suite performs basic behavioral checks against a Web UFS instance rooted at `https://archive.apache.org/dist/`.

## Important Tests
Setup creates the UFS through `UnderFileSystem.Factory.create`. `exists` expects the root URL to exist. `isDirectory` expects the archive URL to be recognized as a directory. `isFile` expects the same URL not to be considered a file.

## Dependencies and Integration
The test depends on Alluxio global configuration, the Web factory, live HTTP access, remote server availability, and the archive page retaining a directory-style title/body.

## Signals and Gaps
The test provides useful end-to-end signal but can be flaky in offline or restricted CI. It does not cover `listStatus`, offset `open`, status metadata parsing, unsupported mutating operations, or relative link normalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/underfs/web/src/test/java/alluxio/underfs/web/WebUnderFileSystemTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/.github/workflows/checks.yml -->
# sources/distributed-fs/beegfs-go/.github/workflows/checks.yml

## Purpose
This GitHub Actions workflow runs the BeeGFS Go repository's standard checks and unit tests.

## Control Flow
It triggers on pull requests except Markdown-only path changes and can also be invoked by `workflow_call`. The single `checks` job runs on Ubuntu, grants read-only contents permission, checks out the repository, installs Go using `go.mod`, and runs `make test`.

## Dependencies and Integration
The workflow depends on `actions/checkout@v4`, `actions/setup-go@v5`, and the repository `Makefile`. `make test` fans out to Go version, formatting, static analysis, tidy, unit tests, vulnerabilities, and license checks.

## Risks and Test Signals
Markdown-only PRs skip this workflow, so code embedded in docs would not be checked here. The workflow is concise and delegates risk to `Makefile` targets, which may modify `go.mod`, `go.sum`, and NOTICE files during validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/.github/workflows/checks.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/.github/workflows/contributors.yml -->
# sources/distributed-fs/beegfs-go/.github/workflows/contributors.yml

## Purpose
This workflow enforces ThinkParQ contributor policy on pull requests by checking CLA approval and allowed author/committer identities.

## Control Flow
On opened or synchronized pull requests, the job checks out full history. The first shell step compares the PR creator login against the space-separated `APPROVED_CONTRIBUTORS` repository variable. The second step gathers commits unique to the PR base branch, parses `APPROVED_COMMITTERS` JSON with `jq`, masks actual emails in logs, and verifies author and committer names map to the expected emails.

## Dependencies and Integration
Dependencies include GitHub repository variables, `jq` on the runner image, `git log`, and `git show`. The workflow integrates with PR status checks and GitHub log annotations through `::error::`, `::notice::`, and `::add-mask::`.

## Risks and Test Signals
An unset or malformed `APPROVED_COMMITTERS` variable will fail all or many commits. It trusts names as JSON keys, so unusual characters may need careful encoding. Full checkout is required for base comparisons; forks or rewritten histories can expose edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/.github/workflows/contributors.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/.github/workflows/no-todo-commits.yml -->
# sources/distributed-fs/beegfs-go/.github/workflows/no-todo-commits.yml

## Purpose
This GitHub Actions workflow prevents pull requests from merging commits whose first commit-message line contains TODO or WIP.

## Control Flow
On opened, synchronized, or reopened pull requests, an `actions/github-script@v7` step lists PR commits, extracts each commit message's first line, filters case-insensitively for word-boundary `TODO` and `WIP`, and fails the check with a formatted message if any are found.

## Dependencies and Integration
The workflow uses the GitHub REST pulls API through `github-script` and read-only repository permissions. It integrates as a PR status check.

## Risks and Test Signals
Only the first line is checked, so TODO/WIP in message bodies is allowed. The regex is word-boundary based and may flag intended words in commit prefixes. The failure message includes commit first lines but not SHAs, although the script records SHAs internally.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/.github/workflows/no-todo-commits.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/.github/workflows/release.yml -->
# sources/distributed-fs/beegfs-go/.github/workflows/release.yml

## Purpose
This workflow runs GoReleaser for BeeGFS binary/package releases when version tags matching `v8.*` are pushed.

## Control Flow
The `goreleaser` job checks out full history, logs into GHCR, imports a GPG package key, sets up Go from `go.mod`, computes `GORELEASER_CURRENT_TAG` and `GORELEASER_PREVIOUS_TAG`, and runs `goreleaser release --clean`. Tag selection sorts semantic tags by temporarily replacing prerelease dashes with tildes before `sort -Vr`.

## Dependencies and Integration
The workflow needs `contents: write` for releases, `packages: write` for GHCR, Docker login action, GPG import action, `actions/setup-go`, GoReleaser action v6, secrets for GPG material, and `GITHUB_TOKEN`.

## Risks and Test Signals
Release correctness depends on tag naming and the custom previous-tag pipeline. The workflow is restricted to `v8.*`, intentionally avoiding Go module API tags. GPG and GHCR credentials are hard release blockers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/.github/workflows/release.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/.goreleaser.yml -->
# sources/distributed-fs/beegfs-go/.goreleaser.yml

## Purpose
This GoReleaser configuration builds BeeGFS Go binaries, packages them as RPM/DEB artifacts, publishes a container image for `beegfs-watch`, generates changelogs, and signs checksums.

## Important Configuration
Four Linux CGO-disabled builds target amd64 and arm64: `beegfs`, `beegfs-remote`, `beegfs-sync`, and `beegfs-watch`. Linker flags inject version, binary name, commit, and build time. NFPM packages define vendor, maintainer, descriptions, epoch `20`, install paths under `/opt/beegfs/sbin`, symlinks into `/usr/sbin`, service/config files, notices, and licenses. A post-build hook generates bash completion for `beegfs`.

## Dependencies and Integration
The config integrates with GoReleaser v2, nfpm, Docker/GHCR, GPG signing, systemd units, package install scripts, and repository NOTICE/LICENSE files. The Docker section builds only the `beegfs-watch` image and adds OCI labels.

## Risks and Test Signals
Packaging paths and service locations assume Linux system layout. The TODO notes no multi-platform Docker image support. Checksums require `GPG_FINGERPRINT`. Changelog excludes docs and test commits, so release notes may omit some user-visible changes if commit classification is inconsistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/.goreleaser.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/Makefile -->
# sources/distributed-fs/beegfs-go/Makefile

## Purpose
The Makefile centralizes local install, uninstall, package, notice generation, and validation targets for the BeeGFS Go repository.

## APIs and Control Flow
Generated install/uninstall rules cover `beegfs`, `beegfs-remote`, `beegfs-sync`, and `beegfs-watch`, installing to `$(HOME)/go/bin`. `package-all` runs local snapshot GoReleaser packaging. `generate-notices` uses `go tool go-licenses report` for ctl, remote, sync, and watch notices. `test` chains `check-go-version`, `check-gofmt`, `check-linters`, `check-go-tidy`, `test-unit`, `check-vulnerabilities`, and `check-licenses`. `tidy` runs `go mod tidy`.

## Dependencies and Integration
The file depends on Bash, Go toolchain/tool directives, staticcheck, govulncheck, go-licenses, GoReleaser for packaging, Git status checks, and repository notice templates.

## Risks and Test Signals
`make test` can modify local files through tidy and notice generation, then fails if changes appear. Go version checking requires exact `go version` match with `go.mod`. License checking intentionally ignores selected private or manually reviewed dependencies. The Makefile is the core CI signal invoked by `.github/workflows/checks.yml`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/beegrpc/grpc.go -->
# sources/distributed-fs/beegfs-go/common/beegfs/beegrpc/grpc.go

## Purpose
`grpc.go` provides common gRPC client connection setup for BeeGFS services, including target validation, TLS configuration, proxy control, custom CA certificates, and BeeGFS auth-secret metadata injection.

## APIs and Control Flow
Functional options populate `connOpts`: `WithTLSDisableVerification`, `WithTLSDisable`, `WithTLSCaCert`, `WithAuthSecret`, and `WithProxy`. `NewClientConn` rejects addresses containing URI schemes, requires `host:port` through `net.SplitHostPort`, applies `grpc.WithNoProxy` unless enabled, adds unary and stream interceptors that append `auth-secret` metadata when configured, then chooses insecure credentials or TLS credentials with system cert pool plus optional CA. It returns `grpc.NewClient(address, opts...)`.

## State, Dependencies, and Integration
The function is stateless outside option values. It depends on Go TLS/x509, net parsing, BeeGFS auth-secret generation, gRPC credentials, interceptors, and metadata. `NewMgmtd` reuses it for management clients.

## Risks and Test Signals
`TLSDisableVerification` sets `InsecureSkipVerify`, which is useful operationally but weakens security. Interceptors recompute the auth secret on each RPC. The explicit scheme rejection avoids gRPC resolver ambiguity. `grpc_test.go` covers IPv4, IPv6, invalid address diagnostics, and URI scheme rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/beegrpc/grpc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/beegrpc/grpc_test.go -->
# sources/distributed-fs/beegfs-go/common/beegfs/beegrpc/grpc_test.go

## Purpose
This Go test suite verifies gRPC target validation behavior in `beegrpc.NewClientConn`.

## Important Tests
`TestNewClientConnAcceptsValidIPv4` and `TestNewClientConnAcceptsValidIPv6` start local gRPC servers and expect connections to loopback `host:port` addresses with TLS disabled. `TestNewClientConnRejectsInvalidAddresses` checks missing ports, malformed IPv6, empty address, error text, IPv6 guidance, and wrapping of `*net.AddrError`. `TestNewClientConnRejectsURIScheme` ensures `dns:///...` style addresses are rejected.

## Dependencies and Integration
Tests use Go's `net`, `testing`, `errors.As`, and gRPC server/client packages. IPv6 is skipped when unavailable.

## Signals and Gaps
The suite strongly documents address validation. It does not test TLS CA handling, auth-secret metadata injection, proxy toggling, or actual RPC execution over the returned connection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/beegrpc/grpc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/beegrpc/mgmtd.go -->
# sources/distributed-fs/beegfs-go/common/beegfs/beegrpc/mgmtd.go

## Purpose
`mgmtd.go` wraps the BeeGFS management gRPC client with shared connection ownership, auth-secret accessors, license verification, cleanup, and filesystem UUID retrieval.

## APIs and Control Flow
`NewMgmtd` creates a gRPC connection via `NewClientConn`, instantiates a protobuf `ManagementClient`, stores address and auth-secret bytes, and returns `Mgmtd`. `GetAuthSecret` returns the generated uint64 secret or zero, while `GetAuthSecretBytes` returns a defensive copy. `VerifyLicense` calls `GetLicense`, rejects verify errors/invalid certificates, builds zap fields for license details, checks requested feature in certificate DNS names, handles grandfathered features by valid-from date, sets `BEEGFS_LICENSED_FEATURE`, and returns details plus any error. `GetFsUUID` calls `GetNodes` and validates non-nil/non-empty UUID.

## State, Dependencies, and Integration
State includes the protobuf client, client connection, address, and auth-secret. Dependencies include BeeGFS protobuf management/license packages, auth utility, zap logging fields, slices, environment variables, and gRPC.

## Risks and Test Signals
`VerifyLicense` mutates process environment, which can leak across tests or commands. Grandfathering depends on wall-clock certificate dates. There is no listed unit test for license edge cases, auth-secret copies, cleanup idempotence, or UUID validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/beegrpc/mgmtd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/consistencystate.go -->
# sources/distributed-fs/beegfs-go/common/beegfs/consistencystate.go

## Purpose
This file defines BeeGFS target consistency states and conversions among user strings, protobuf enums, and Go string output.

## APIs and Control Flow
`ConsistencyState` has variants `ConsistencyStateUnspecified`, `Good`, `NeedsResync`, and `Bad`. `ConsistencyStateFromString` trims/lowercases input and recognizes `good`, `needs_resync`, and `bad`. `ConsistencyStateFromProto` maps protobuf values to Go constants. `ToProto` returns a pointer to the corresponding protobuf enum. `String` returns user-friendly lower-case names or `<unspecified>`.

## State, Dependencies, and Integration
The type is immutable enum-style state. It depends on `github.com/thinkparq/protobuf/go/beegfs` and is used by parsers and command/UI layers that display or submit target consistency state.

## Risks and Test Signals
The parser does not accept hyphenated or spaced variants such as `needs-resync`. Unknown protobuf values collapse to unspecified, which is safe but lossy. No direct test file is listed, though the parser wrapper may be tested elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/consistencystate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/consistencystateparser.go -->
# sources/distributed-fs/beegfs-go/common/beegfs/consistencystateparser.go

## Purpose
`ConsistencyStateParser` constrains string parsing of consistency states to an accepted set for command-line or API input validation.

## APIs and Control Flow
`NewConsistencyStateParser` defaults accepted states to `Good`, `NeedsResync`, and `Bad` when none are supplied. `Parse` converts input with `ConsistencyStateFromString`, checks whether the result is in the parser's accepted list, and returns a formatted error listing accepted values otherwise.

## State, Dependencies, and Integration
The parser is a slice of accepted `ConsistencyState` values. It uses `strings.Builder` and `fmt` for diagnostics. It integrates with CLI flag or command validation where not every state is allowed.

## Risks and Test Signals
Error messages append accepted values with a trailing comma and space. Empty accepted lists cannot represent "accept none" because construction defaults to all real states. There is no listed direct unit test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/consistencystateparser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/entity.go -->
# sources/distributed-fs/beegfs-go/common/beegfs/entity.go

## Purpose
This file defines common BeeGFS entity identity types: legacy node-type plus numeric ID, globally unique UID, alias, invalid ID, and full `EntityIdSet` values.

## APIs and Control Flow
`EntityId` requires `fmt.Stringer` and `ToProto`. `IdFromString` trims and parses unsigned decimal IDs with a caller-provided bit size and minimum one. `LegacyId` formats short and long node-type IDs and converts to protobuf. `Uid` and `Alias` format and convert to protobuf. `AliasFromString` enforces aliases beginning with a letter and containing letters, digits, dash, underscore, or dot. `EntityIdSetFromProto` converts a protobuf set into Go fields, and `EntityIdSet.ToProto` converts back.

## State, Dependencies, and Integration
These are value types used across CLI parsing, node stores, and protobuf APIs. Dependencies include regex, string/number parsing, and BeeGFS protobuf entity types.

## Risks and Test Signals
`EntityIdSetFromProto` only checks nil input or nil `LegacyId`, but dereferences `input.Uid` and `input.Alias`, so partial protobufs can panic. `LegacyId.ToProto` casts `NumId` to `uint32` without range enforcement at conversion time. Tests cover ID parsing ranges and entity parser outputs, not full `EntityIdSetFromProto` nil-field behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/entity.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/entity_test.go -->
# sources/distributed-fs/beegfs-go/common/beegfs/entity_test.go

## Purpose
This Go test suite validates numeric ID parsing and the `EntityIdParser` behavior over legacy IDs, aliases, and UIDs.

## Important Tests
`TestIdFromString` checks valid 16-bit IDs and rejects zero and overflow. `TestEntityParser` accepts node-type prefixes, trims spaces, handles case, parses aliases and UIDs, and rejects unsupported node types, invalid aliases, invalid IDs, and malformed UIDs. `TestEntityParserWithFixedNodeType` verifies that a bare integer is accepted when exactly one node type is configured.

## Dependencies and Integration
Tests use `stretchr/testify/assert` and cover parser behavior defined across `entity.go`, `entityparser.go`, and `nodetype.go`.

## Signals and Gaps
The suite provides strong coverage for CLI-facing parsing. It does not test `EntityIdSetFromProto`, protobuf conversion round trips, `EntityIdSliceParser`, pflag wrappers, or colon strings with more than two fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/entity_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/entityparser.go -->
# sources/distributed-fs/beegfs-go/common/beegfs/entityparser.go

## Purpose
`EntityIdParser` converts user input into one of BeeGFS's supported entity identity forms: UID, legacy node-type ID, bare numeric ID for a fixed node type, or alias.

## APIs and Control Flow
`NewEntityIdParser` stores ID bit size and accepted node types, defaulting to client, meta, storage, and management. `Parse` trims input. If a colon is present, it splits on `:`, treats `uid:<id>` as signed 64-bit UID greater than zero, otherwise parses `<nodeType>:<id>` and validates the node type against accepted values. Without a colon, it first tries alias validation, then tries a bare numeric ID only when exactly one node type is accepted. `EntityIdSliceParser` splits comma-separated input and parses each element with an embedded parser.

## State, Dependencies, and Integration
Parser state is immutable after construction. It integrates with pflag wrappers and CLI commands that need flexible entity identifiers.

## Risks and Test Signals
The colon path uses `strings.Split` and only reads the first two fields, so `a:b:c` is treated like `a:b` rather than rejected for extra components. For fixed node types, alias parsing wins before bare numeric parsing; numeric aliases are invalid, so the fallback works for numbers. Tests cover many normal and invalid cases but not extra-colon input or slice parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/entityparser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/entitypflag.go -->
# sources/distributed-fs/beegfs-go/common/beegfs/entitypflag.go

## Purpose
This file adapts `EntityIdParser` and `EntityIdSliceParser` to Cobra/pflag `Value` implementations.

## APIs and Control Flow
`NewEntityIdPFlag` stores a parser and pointer to the destination `EntityId`. `Type` returns `entityId`, `String` returns the current entity string or `unspecified`, and `Set` parses input then writes to the destination pointer. `NewEntityIdSlicePFlag` does the same for `[]EntityId`, with a type string indicating comma-separated values; its `String` always returns `<unspecified>`.

## State, Dependencies, and Integration
State is the parser plus a caller-owned destination pointer. The wrappers integrate directly with Cobra command flags via `Flags().Var()`.

## Risks and Test Signals
`Set` assumes destination pointers are non-nil and will panic if misconstructed. Slice flag `String` does not reflect current values, which may affect help/default rendering. There are no listed direct tests for pflag integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/entitypflag.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/entry.go -->
# sources/distributed-fs/beegfs-go/common/beegfs/entry.go

## Purpose
`entry.go` defines BeeGFS file-entry and file-state constants used by protocol, CLI, and storage workflows.

## APIs and Control Flow
`EntryType` models directory, regular file, symlink, device, FIFO, and socket entries; `IsFile` treats all non-directory concrete entry types as files. `StripePatternType` formats RAID and buddy mirror patterns. `EntryFeatureFlags` exposes bit checks and setters for inlined and buddy-mirrored entries. `FileState` packs lower five-bit `AccessFlags` and upper three-bit `DataState`, with helpers to construct, inspect, stringify, and return modified copies with new data or access states.

## State, Dependencies, and Integration
All values are small integer/bitfield types with no external persistence beyond protocol or metadata use. The file references C++ BeeGFS definitions in comments, making cross-language numeric compatibility important.

## Risks and Test Signals
`WithoutAccessState` appears to preserve the data-state bits and clear all access bits with `&^ AccessFlagMask`, ignoring the `flags` argument; if intended to clear only specified flags, this is a behavioral bug. Tests cover `EntryType.IsFile` and feature flag setters, but not `FileState` packing or access-state mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/entry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/entry_test.go -->
# sources/distributed-fs/beegfs-go/common/beegfs/entry_test.go

## Purpose
This Go test file verifies selected behavior in BeeGFS entry and feature flag types.

## Important Tests
`TestIsFile` asserts that directories are not files and regular files and sockets are files. `TestFeatureFlags` starts with zero flags, verifies buddy-mirrored and inlined bits are false, sets buddy-mirrored and checks boolean plus integer form, then sets inlined and verifies both bits.

## Dependencies and Integration
The tests use `stretchr/testify/assert` and directly exercise `entry.go`.

## Signals and Gaps
The tests document intended file classification and flag mutation. They do not cover string output, stripe pattern names, `FileState` packing, data-state extraction, or access flag modification helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/entry_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/errors.go -->
# sources/distributed-fs/beegfs-go/common/beegfs/errors.go

## Purpose
`errors.go` defines BeeGFS operation error codes and maps many of them to Linux `syscall.Errno` values so Go's `errors.Is` can match standard filesystem sentinels.

## APIs and Control Flow
`OpsErr` is an `int32` error type with constants mirroring BeeGFS C++ storage errors. `Error` delegates to `String`, which returns descriptive text for each known code. `Unwrap` returns a mapped `syscall.Errno` from `opsToSys` when present. The map covers not-found, exists, busy, not-dir, not-empty, no-space, invalid, permission, quota, stale, and many remote/internal conditions.

## State, Dependencies, and Integration
The mapping is static. Dependencies are `fmt` and `syscall`. The type is intended for call sites that may return Linux errors or BeeGFS-specific errors while still allowing checks such as `errors.Is(err, fs.ErrNotExist)`.

## Risks and Test Signals
Mappings are Linux-specific and rely on syscall constants available on target platforms. `OpsErr_SUCCESS` does not unwrap to nil-special success handling; it is still an error value if returned. `errors_test.go` covers representative mappings and forward-only matching behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/errors_test.go -->
# sources/distributed-fs/beegfs-go/common/beegfs/errors_test.go

## Purpose
This Go test verifies `OpsErr` interoperability with standard Go error matching.

## Important Tests
`TestErrMappings` checks that `OpsErr_PATHNOTEXISTS` matches `syscall.ENOENT`, `fs.ErrNotExist`, and `os.ErrNotExist`; `OpsErr_INUSE` matches `syscall.EBUSY`; `OpsErr_WOULDBLOCK` and `OpsErr_AGAIN` match EAGAIN/EWOULDBLOCK; reverse matching from `os.ErrNotExist` to `OpsErr_PATHNOTEXISTS` is false; and unrelated permission matching is false.

## Dependencies and Integration
The test uses Go `errors`, `io/fs`, `os`, `syscall`, and `stretchr/testify/assert`.

## Signals and Gaps
The suite confirms the most important sentinel behavior. It does not exhaustively verify every `opsToSys` mapping or string output for all codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/errors_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/node.go -->
# sources/distributed-fs/beegfs-go/common/beegfs/node.go

## Purpose
`node.go` defines BeeGFS node and NIC value types shared by management and CLI logic.

## APIs and Control Flow
`Node` stores UID, legacy ID, alias, and NICs. `String` returns the long legacy ID string. `Addrs` extracts NIC addresses into a new slice. `Clone` deep-copies the NIC slice before returning a node copy. `NicType` defines invalid, TCP, RDMA, and SDP variants with string output. `Nic` stores name, type, and address and formats them in a compact display string.

## State, Dependencies, and Integration
These are in-memory data models with no persistence logic. They integrate with entity ID types and user-facing output for BeeGFS nodes. The only dependency is `fmt`.

## Risks and Test Signals
The TODO notes the node should use `EntityIdSet`, indicating an identity model transition. `Clone` only deep-copies the NIC slice, which is sufficient for current scalar NIC fields. There are no listed direct tests for node cloning or formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/node.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/nodetype.go -->
# sources/distributed-fs/beegfs-go/common/beegfs/nodetype.go

## Purpose
`nodetype.go` defines BeeGFS node type values and conversions between strings, protobuf enums, and user-facing output.

## APIs and Control Flow
`NodeType` variants are invalid, client, meta, storage, and management. `NodeTypeFromString` trims/lowercases input and accepts non-ambiguous prefixes: client, storage, metadata/meta, and management/mgmtd with at least two characters for management. `NodeTypeFromProto` maps protobuf node types to Go values. `ToProto` returns a pointer to a protobuf enum. `String` returns user-facing lower-case names or `<invalid>`.

## State, Dependencies, and Integration
The type is an enum-style integer used by entity parsing, node models, protobuf requests, and pflag wrappers. Dependency is the BeeGFS protobuf package.

## Risks and Test Signals
The parser accepts `m` as metadata because it checks `metadata` after requiring two characters only for management. This is deliberate but creates a compact alias asymmetry. `nodetype_test.go` covers common prefixes and invalid values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/nodetype.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/nodetype_test.go -->
# sources/distributed-fs/beegfs-go/common/beegfs/nodetype_test.go

## Purpose
This Go test validates `NodeTypeFromString` parsing behavior.

## Important Tests
The test accepts `meta`, `m`, `storage`, `s`, trimmed `client`, `c`, trimmed `management`, and `ma`. It rejects empty input, arbitrary strings, malformed prefixes such as `me_`, and values containing spaces like `cli ent`.

## Dependencies and Integration
The suite uses `stretchr/testify/assert` and directly exercises `nodetype.go`.

## Signals and Gaps
It documents prefix behavior and invalid cases. It does not cover protobuf conversions, `String`, or pflag integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/nodetype_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/nodetypepflag.go -->
# sources/distributed-fs/beegfs-go/common/beegfs/nodetypepflag.go

## Purpose
`NodeTypePFlag` adapts BeeGFS node type parsing to Cobra/pflag command-line flags.

## APIs and Control Flow
`NewNodeTypePFlag` stores a destination pointer and accepted node types. `Type` returns `nodeType`. `String` returns the current node type string when non-invalid, otherwise an empty string. `Set` parses the input with `NodeTypeFromString`, writes the result to the destination pointer, then validates the parsed value against the accepted list and returns a formatted error on mismatch.

## State, Dependencies, and Integration
State is a caller-owned pointer plus accepted values. It integrates with CLI command flag registration.

## Risks and Test Signals
`Set` writes the parsed value before validation, so after an invalid input the destination pointer contains the invalid or unacceptable node type. It assumes `into` is non-nil. Error messages have a trailing comma and space. No direct tests are listed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/nodetypepflag.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/storagebench.go -->
# sources/distributed-fs/beegfs-go/common/beegfs/storagebench.go

## Purpose
`storagebench.go` defines common BeeGFS storage benchmark actions, benchmark types, statuses, and error codes.

## APIs and Control Flow
`StorageBenchAction` covers start, stop, status, cleanup, and unspecified with string output. `StorageBenchType` covers read, write, and unknown. `StorageBenchStatus` covers uninitialized, initialized, error, running, stopping, stopped, finishing, and finished. `StorageBenchError` implements `error` and maps communication, worker, initialization, and runtime error constants to user-friendly strings.

## State, Dependencies, and Integration
These constants are protocol/domain enums likely shared by CLI and management interactions. There are no external dependencies.

## Risks and Test Signals
Numeric values must remain compatible with BeeGFS protocol/server expectations. Unknown values stringify generically, which is safe for display but loses diagnostics. No listed tests verify the enum string mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beegfs/storagebench.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/beeserde/beeserde.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/beeserde/beeserde.go

## Purpose
`beeserde.go` implements BeeGFS BeeSerde serialization and deserialization primitives used by BeeMsg protocol messages. It serializes integers, raw bytes, C strings, sequences, string sequences, maps, padding, and matching deserialization operations.

## APIs and Control Flow
`Serializer` owns a bytes buffer, message feature flags, and sticky error. `NewSerializer`, `Finish`, `Fail`, and helpers write little-endian integers, byte slices, length-prefixed null-terminated C strings with optional alignment, sequences/maps with placeholder counts/sizes, string sequences with total size and null terminators, and zero padding. `Deserializer` mirrors this with a buffer, message feature flags, sticky error, `Finish` that requires full consumption, and helpers for integers, bytes, C strings, sequence lengths, sequences, string sequences, maps, and skip.

## State, Persistence, and Dependencies
State is in-memory serialization buffers and feature flags. The wire format is persistent protocol state shared with BeeGFS C++/Rust implementations, so exact byte compatibility is critical. Dependencies include `bytes`, `encoding/binary`, `fmt`, and `reflect`.

## Risks and Test Signals
`SerializeMap` iterates Go maps in randomized order, which can produce nondeterministic wire bytes if protocol peers expect ordering. `DeserializeBytes` uses `Read`, which can return short reads without error for some readers; `bytes.Buffer` usually behaves predictably but `io.ReadFull` semantics would be stricter. `DeserializeInt` calls `reflect.ValueOf(into).Type()` and can panic on nil interface. Tests cover ints, CStr alignment, string seq null rejection, nested sequences/maps, and non-pointer integer deserialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/beeserde/beeserde.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/beeserde/beeserde_test.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/beeserde/beeserde_test.go

## Purpose
This Go test suite validates BeeSerde serialization/deserialization primitives with round trips and error checks.

## Important Tests
`TestInt` round-trips signed and unsigned integer widths. `TestCStr` serializes/deserializes C strings with multiple alignments. `TestCStrAlignment` checks expected buffer lengths for empty and short strings under alignments. `TestStringSeq` round-trips string sequences and verifies null bytes cause serialization error. `TestNestedSeq` and `TestNestedMap` round-trip nested sequence and map structures. `TestErrorOnNonPointerDeserialization` verifies deserializing into a non-pointer records an error.

## Dependencies and Integration
The tests use `stretchr/testify/assert` and the public functions in `beeserde.go`.

## Signals and Gaps
The suite covers core happy paths and some errors. It does not test truncated buffers, leftover bytes, map ordering determinism, nil destination pointers, feature flag use, or deserialization of string sequences with malformed terminators beyond buffer read errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/beeserde/beeserde_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/chunkbalance.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/msg/chunkbalance.go

## Purpose
`chunkbalance.go` defines BeeMsg protocol messages and response structures for starting chunk balancing and reading chunk-balance job statistics.

## APIs and Control Flow
`StartChunkBalanceMsg` contains rebalance ID type, relative path, target IDs, destination IDs, entry info, and required file event context. `Serialize` writes the ID type, path CStr, target and destination sequences, entry info, sets message feature flag bit 1 when file event exists, forces the event type to protobuf `INODE_LOCKED`, and serializes the event. Missing file event fails serialization. Response and stats messages expose `MsgId` values and serialize/deserialize fixed fields. `ChunkBalancerJobState.String` formats job states.

## State, Dependencies, and Integration
The file depends on `beegfs.OpsErr`, BeeSerde, protobuf beewatch events, and message types such as `EntryInfo` and `FileEvent` defined elsewhere. Message IDs and field order are wire-protocol state and must match BeeGFS server expectations.

## Risks and Test Signals
Serialization mutates `m.FileEvent.Type`, which may surprise callers that reuse the object. There is no nil check for `EntryInfo`. Stats deserialization order is fixed and must stay in sync with the server. No listed tests cover chunk-balance message bytes or error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/chunkbalance.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/definitions.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/msg/definitions.go

## Purpose
`definitions.go` contains small BeeMsg protocol message definitions for connection authentication, heartbeat, and generic debug commands.

## APIs and Control Flow
`AuthenticateChannel` has message ID `4007`, serializes/deserializes a uint64 auth secret, and must be sent before other TCP BeeMsg traffic. `HeartbeatRequest` has message ID `1019` and no payload. `GenericDebug` has message ID `1029` and serializes a command as a CStr aligned to one byte. `GenericDebugResp` has message ID `1030` and deserializes the response CStr with the same alignment.

## State, Dependencies, and Integration
These types depend on the BeeSerde package and implement the repository's message interface pattern through `MsgId`, `Serialize`, and/or `Deserialize`. They integrate with BeeMsg node-store and debug tooling.

## Risks and Test Signals
There is no validation on generic debug command size or content in this file. Authentication semantics depend on callers sending the message in the correct order. No direct tests are listed for these message definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/definitions.go -->
