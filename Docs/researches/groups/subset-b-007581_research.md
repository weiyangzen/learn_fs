# Research: subset-b-007581

This grouped report covers the Hadoop S3A implementation files assigned to `subset-b-007581`. Each section is delimited for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/OpenFileSupport.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/OpenFileSupport.java

## Purpose
`OpenFileSupport` centralizes S3A `openFile()` option handling so `S3AFileSystem` does not directly contain all builder parsing, status conversion, split/range handling, and read-policy defaults. It converts `OpenFileParameters` and filesystem defaults into an `OpenFileInformation` value used to build `S3AReadOpContext` for later stream creation.

## Important APIs and Types
- `OpenFileSupport(...)` stores immutable defaults: `ChangeDetectionPolicy`, default readahead, username, default buffer size, async drain threshold, and default `S3AInputPolicy`.
- `applyDefaultOptions(S3AReadOpContext)` applies default input policy, change detection, async drain threshold, and readahead to a read context.
- `prepareToOpenFile(Path, OpenFileParameters, long)` is the core parser for builder options and optional supplied status.
- `openSimpleFile(int)` creates the equivalent options for legacy `open(path, bufferSize)`.
- Nested `OpenFileInformation` is a fluent mutable value object with getters, `with...` setters, and `applyOptions(S3AReadOpContext)`.

## Control Flow
`prepareToOpenFile()` first rejects S3 Select when mandatory and logs once when optional, then validates mandatory option keys against `InternalConstants.S3A_OPENFILE_KEYS`. If the caller supplied a `FileStatus`, it verifies filename equality, rejects directories, extracts length/modification time plus S3A eTag/version metadata where available, and creates an `S3AFileStatus` using the target path. It then parses split start/end, file length, read policy, buffer size, async drain threshold, and readahead through `FSBuilderSupport`. If a length is known but no status was supplied, it builds a minimal status with unknown modification time and no eTag/version. The result is built as `OpenFileInformation`.

## State and Persistence
The support object is immutable after construction. `OpenFileInformation` is mutable during fluent setup but returned as the per-open state container. No persistent storage is modified; it only influences future S3 GET/HEAD behavior and stream configuration.

## Dependencies and Integration Points
It depends on Hadoop open-file option keys, S3A constants (`READAHEAD_RANGE`, `ASYNC_DRAIN_THRESHOLD`, `INPUT_FADVISE`), `S3AInputPolicy`, `S3AFileStatus`, `S3ALocatedFileStatus`, `ChangeDetectionPolicy`, and S3 Select constants. Integration is with S3A file opening, change detection, and stream factories through `S3AReadOpContext`.

## Risks and Edge Cases
Supplied status validation intentionally compares only final filename, not full path, so callers must avoid passing stale status for a different object with the same basename. Split-start greater than split-end is reset to zero with a warning, which prevents invalid ranges but may hide bad caller options. Minimal status from `FS_OPTION_OPENFILE_LENGTH` lacks eTag/version metadata, so change detection cannot use those fields. S3 Select is explicitly unsupported and mandatory use fails.

## Test Signals
Tests should cover mandatory-key rejection, optional vs mandatory S3 Select handling, supplied `S3AFileStatus` and `S3ALocatedFileStatus` metadata propagation, directory status rejection, split reset behavior, option precedence between standard open-file read policy and `INPUT_FADVISE`, and `applyOptions()` propagation into `S3AReadOpContext`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/OpenFileSupport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/OperationCallbacks.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/OperationCallbacks.java

## Purpose
`OperationCallbacks` defines the filesystem callbacks needed by store operations such as `RenameOperation` and `DeleteOperation`, allowing those operations to be tested and executed without tight direct coupling to the full `S3AFileSystem`.

## Important APIs and Types
The interface exposes callbacks for object attribute construction, read context creation, rename completion cleanup, single-object delete, recursive listing including directory markers, object copy, bulk key removal, object listing, and optional multipart-upload abortion under a prefix. Retry annotations document expected retry/translation behavior.

## Control Flow
Implementations are invoked by higher-level operations in copy/list/delete sequences. `RenameOperation` uses attributes/read contexts before copy, queues deletes through `removeKeys()`, and calls `finishRename()` once the destination has been created. The default `abortMultipartUploadsUnderPrefix()` returns zero so implementations opt in to upload purging.

## State and Persistence
The interface stores no state, but implementations perform persistent object-store mutations: delete, copy, bulk delete, directory marker cleanup, and multipart upload aborts.

## Dependencies and Integration Points
It uses AWS SDK v2 `CopyObjectResponse`, `ObjectIdentifier`, and `AwsServiceException`, plus Hadoop `Path`, `RemoteIterator`, S3A statuses, `S3ObjectAttributes`, and `S3AReadOpContext`. It is the main seam between store operations and concrete filesystem behavior.

## Risks and Edge Cases
Misimplemented callbacks can break rename atomicity expectations because S3A rename is copy-then-delete. `removeKeys()` must handle empty lists, root delete protection, and partial failures. Listing must include directory markers when requested or marker cleanup will be incorrect. Default multipart abort no-op means callers must explicitly configure implementations for purging pending uploads.

## Test Signals
Mock callback tests should assert call order during rename, correct copy source attributes, delete batching, marker listing behavior, translated exception paths, and multipart abort counts when enabled or disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/OperationCallbacks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ProgressListener.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ProgressListener.java

## Purpose
`ProgressListener` is a minimal callback interface for upload/progress notifications in S3A implementation code.

## Important APIs and Types
It has one default method: `progressChanged(ProgressListenerEvent eventType, long bytesTransferred)`. The default implementation is a no-op, making listener attachment optional.

## Control Flow
Upload code can call `progressChanged()` with a typed event and byte count without checking for special behavior. Implementations override the method to update counters, notify clients, or assert behavior in tests.

## State and Persistence
The interface has no fields and no persistence. State effects are entirely in implementations.

## Dependencies and Integration Points
It depends only on `ProgressListenerEvent`. It integrates with block output streams and transfer progress plumbing where progress and lifecycle events need to be observed.

## Risks and Edge Cases
Because the default method ignores all events, missing overrides silently drop progress. Implementations must tolerate frequent byte-transfer events and terminal events with zero or irrelevant byte counts.

## Test Signals
Tests should verify event propagation in upload paths and confirm no listener behavior does not affect upload success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ProgressListener.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ProgressListenerEvent.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ProgressListenerEvent.java

## Purpose
`ProgressListenerEvent` enumerates upload and stream progress lifecycle events used by S3A progress listeners and tests.

## Important APIs and Types
Events include close, put start/completion/interruption/failure, byte transfer, multipart initiation/abort/completion, and part start/completion/success/abort/failure.

## Control Flow
Upload implementations emit these enum values through `ProgressListener.progressChanged()`. Consumers distinguish lifecycle transitions and byte-count progress by event type.

## State and Persistence
The enum is stateless and persistent only as an in-process event vocabulary.

## Dependencies and Integration Points
It integrates with S3A block output stream and progress listener implementations. It has no external dependencies.

## Risks and Edge Cases
Some event comments are imprecise or contain typos; consumers should rely on enum names. `TRANSFER_PART_COMPLETED_EVENT` explicitly does not imply success, so success/failure handling must use the more specific events where available.

## Test Signals
Tests should check that upload paths emit terminal events consistently and that multipart part completion and success/failure events are not conflated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ProgressListenerEvent.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/PutObjectOptions.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/PutObjectOptions.java

## Purpose
`PutObjectOptions` is an immutable option bundle for S3 PUT and multipart create/complete operations, carrying metadata headers, write flags, and conditional overwrite eTag state.

## Important APIs and Types
Fields include `storageClass`, `headers`, `EnumSet<WriteObjectFlags>`, and `etagOverwrite`. `isNoObjectOverwrite()` checks `ConditionalOverwrite`; `isEtagOverwrite()` checks `ConditionalOverwriteEtag`; `hasFlag()` exposes flag membership; `defaultOptions()` returns a shared empty option instance.

## Control Flow
Constructors validate that if conditional eTag overwrite is enabled, the eTag is non-empty. Request-building code checks these flags to set `If-None-Match: *` or `If-Match: <etag>` headers and attaches metadata headers to PUT/multipart requests.

## State and Persistence
The object is immutable by reference, though the provided map and `EnumSet` are not defensively copied. It does not persist state itself; it alters object-store write conditions and metadata when passed to request factories.

## Dependencies and Integration Points
It depends on `WriteObjectFlags` and Apache commons string helpers. It integrates directly with `RequestFactoryImpl` and write operations.

## Risks and Edge Cases
Lack of defensive copying means external mutation of headers or flag set after construction can change behavior. `storageClass` is stored and printed but request factory storage-class behavior is mostly controlled by factory-level configuration, so callers should confirm intended propagation. Conditional overwrite and eTag overwrite semantics must remain mutually sensible at request construction time.

## Test Signals
Tests should validate constructor rejection for empty eTag with eTag flag, default options immutability expectations, request factory conditional header output, and behavior when null headers are supplied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/PutObjectOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/RenameOperation.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/RenameOperation.java

## Purpose
`RenameOperation` implements S3A rename as a copy-then-delete workflow. It supports file renames, recursive directory renames, directory-marker handling, batched source deletion, bounded parallel copy submission, and optional abort of pending multipart uploads under renamed directory prefixes.

## Important APIs and Types
- Constructor captures source/destination paths and keys, source/destination statuses, `OperationCallbacks`, delete page size, and upload purge policy.
- `execute()` runs the operation once and returns copied byte count.
- `renameFileToDest()` handles single-file source rename, including `rename(file, dir)` semantics.
- `recursiveDirectoryRename()` lists source tree entries, copies files and leaf markers, queues deletes, and waits on copy/delete batches.
- `initiateCopy()` submits copy tasks into the store executor while preserving audit span.
- `getUploadsAborted()` reports optional multipart upload abort count after successful directory rename.

## Control Flow
For file sources, it builds source attributes/read context, adjusts destination under an existing directory if needed, copies the source object, increments byte count, deletes the source object, and returns the actual destination path. For directory sources, it normalizes source/destination keys with trailing slashes, rejects destination inside source, optionally starts async multipart upload abort under the source prefix, removes an empty destination marker, lists source files and directory markers recursively, tracks markers with `DirMarkerTracker`, copies files to corresponding destination keys, queues copied sources for batched deletion, and triggers batch waits when active copies reach `RENAME_PARALLEL_LIMIT` or queued deletes reach `pageSize`. After iteration, it copies only leaf directory markers, deletes remaining sources, waits for upload purge, and calls `finishRename()`.

## State and Persistence
Operation-local mutable state includes `bytesCopied`, `activeCopies`, `keysToDelete`, and `uploadsAborted`. Persistent effects are S3 COPY operations, source object deletes, destination marker deletion, source marker cleanup, and optional multipart upload aborts. The operation is guarded by `executeOnlyOnce()`.

## Dependencies and Integration Points
It extends `ExecutingStoreOperation<Long>` and depends on `StoreContext`, `OperationCallbacks`, `DirMarkerTracker`, `S3ALocatedFileStatus`, `S3ObjectAttributes`, `S3AReadOpContext`, AWS `ObjectIdentifier`, `SdkException`, and auditing helper `callableWithinAuditSpan`. It integrates with S3A listing, copy, delete, and marker policy code.

## Risks and Edge Cases
S3 rename is not atomic; failures may leave copied destination objects and undeleted sources. The code waits for active copies before deleting queued sources, but bytes copied for directory files adds `sourceStatus.getLen()` rather than each child length, which is suspicious for metrics. Marker handling intentionally does not copy non-leaf markers. Root/key normalization and destination-under-source validation are critical. Exception conversion must preserve S3 service failure semantics. Optional multipart upload purge runs concurrently and failures are ignored through `waitForCompletionIgnoringExceptions()`.

## Test Signals
Tests should cover file-to-file, file-to-directory, directory-to-directory, destination inside source rejection, delete pagination, active copy batching, marker deletion/copy rules, empty destination marker removal, upload purge enabled/disabled, exception conversion, and audit-span propagation to copy workers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/RenameOperation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/RequestFactoryImpl.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/RequestFactoryImpl.java

## Purpose
`RequestFactoryImpl` is the central AWS SDK v2 S3 request builder for S3A. It attaches bucket, ACL, storage class, content encoding, checksums, encryption parameters, conditional write headers, upload timeouts, and audit/request preparation callbacks consistently across S3 operations.

## Important APIs and Types
It implements `RequestFactory` with builders for copy, put, directory marker put, multipart list/abort/create/complete/upload part, head object/bucket, get object, list objects v1/v2, single delete, and bulk delete. It exposes encryption and configuration accessors, `setEncryptionSecrets()`, and a nested `RequestFactoryBuilder`. The nested `PrepareRequest` callback lets audit/request preparation mutate every builder before use.

## Control Flow
Every public builder method constructs an AWS SDK request builder, sets common bucket/key values, applies operation-specific fields, calls encryption helper methods where needed, and returns `prepareRequest(builder)`. Copy requests clone metadata from source HEAD, use `MetadataDirective.REPLACE`, propagate source KMS key when present, otherwise apply filesystem encryption settings. PUT and multipart create requests attach metadata headers, ACL, storage class, content encoding, checksum algorithm, and encryption settings. Conditional overwrite options become `If-None-Match` or `If-Match` override headers. Upload-part requests validate upload id, part number, size, part-count limit, optional last-part marker, SSE-C parameters, timeout, and checksum. Complete multipart optionally includes conditional headers and SSE-C headers when checksums are used.

## State and Persistence
The factory stores mostly immutable configuration but `encryptionSecrets` is mutable through `setEncryptionSecrets()`, allowing token or encryption state refresh. It does not execute requests; it shapes all later persisted S3 mutations and reads.

## Dependencies and Integration Points
It depends heavily on AWS SDK v2 S3 model builders, `EncryptionSecrets`, `EncryptionSecretOperations`, `S3AEncryptionMethods`, `HeaderProcessing`, `AWSClientConfig.setRequestTimeout`, `WriteObjectFlags`, and S3A constants. It is used by `S3AStoreImpl`, write operations, stream callbacks, and listing/delete code.

## Risks and Edge Cases
Incorrect encryption parameter selection can make objects unreadable or copy operations fail, especially SSE-C and KMS context handling. Mutable `encryptionSecrets` may be a concurrency concern if changed while requests are being built. Multipart upload disabled causes `PathIOException` at create time. Part count limit is test-tunable and must be enforced. Conditional overwrite headers must be sent on both PUT and complete-multipart paths. Directory markers intentionally omit content encoding and upload timeout.

## Test Signals
Tests should inspect built requests for each encryption mode (`SSE_S3`, `SSE_KMS`, `DSSE_KMS`, `SSE_C`, CSE, none), content encoding, checksum, ACL, storage class, conditional headers, request timeout, multipart disabled errors, part-count limit errors, bulk delete quiet flag behavior, and invocation of `PrepareRequest`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/RequestFactoryImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/S3AEncryption.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/S3AEncryption.java

## Purpose
`S3AEncryption` provides utilities for retrieving and encoding SSE-KMS encryption context configuration for S3A.

## Important APIs and Types
`getS3EncryptionContext(bucket, conf)` looks up per-bucket then global `S3_ENCRYPTION_CONTEXT` secrets. `getS3EncryptionContextBase64Encoded(bucket, conf, propagateExceptions)` parses key-value context strings, serializes them as JSON, and Base64-encodes the UTF-8 JSON.

## Control Flow
The lookup first asks `S3AUtils.lookupBucketSecret()`, then global `S3AUtils.lookupPassword()`. Base64 encoding returns empty string for blank or empty parsed values. IO failures are either propagated or logged and converted to empty string depending on `propagateExceptions`.

## State and Persistence
The class is stateless. It reads configuration/credential provider state and returns strings used in future S3 requests.

## Dependencies and Integration Points
It depends on Jackson `ObjectMapper`, Apache commons Base64/StringUtils, Hadoop `Configuration`, and S3A secret lookup utilities. The output integrates with encryption secret setup and request builders for KMS encryption context.

## Risks and Edge Cases
Malformed key-value context strings may parse to empty or throw depending on helper behavior. Suppressing IO exceptions can silently omit encryption context, which may affect access policies. Base64 JSON key order follows map serialization and should not be assumed stable unless the parser returns ordered maps.

## Test Signals
Tests should cover per-bucket override precedence, global fallback, blank/empty values, valid multi-entry encoding, IO exception propagation vs warning path, and bad context parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/S3AEncryption.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/S3AFileSystemOperations.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/S3AFileSystemOperations.java

## Purpose
`S3AFileSystemOperations` abstracts filesystem-level operations that differ for normal, encrypted, and client-side encrypted S3A modes.

## Important APIs and Types
The interface defines methods for `getObject()`, setting the CSE gauge, obtaining CSE materials, selecting encrypted and unencrypted `S3ClientFactory` instances, and computing true S3 object size from HEAD metadata.

## Control Flow
`S3AStoreImpl.headObject()` can call `getS3ObjectSize()` to replace content length with unencrypted length when needed. Stream callbacks can call `getObject()` to choose encrypted or unencrypted client behavior. Initialization code asks for client factories and CSE materials based on configured encryption method.

## State and Persistence
The interface is stateless. Implementations may read configuration, set metrics gauges, and choose S3 clients; object-store persistence occurs through returned clients and store calls.

## Dependencies and Integration Points
It depends on AWS SDK get/head response types, `S3AStore`, `RequestFactory`, `S3ClientFactory`, CSE materials, `S3AEncryptionMethods`, and `IOStatisticsStore`. It is an encryption integration point for S3A store and filesystem initialization.

## Risks and Edge Cases
Incorrect size translation breaks reads against client-side encrypted objects. Wrong client factory selection can expose encrypted bytes to normal reads or use encrypted clients where not needed. Metrics gauge setup must reflect actual CSE mode.

## Test Signals
Tests should use normal and CSE implementations to validate GET client selection, unencrypted size calculation, CSE materials loading, factory class resolution, and gauge values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/S3AFileSystemOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/S3AMultipartUploader.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/S3AMultipartUploader.java

## Purpose
`S3AMultipartUploader` implements Hadoop's `MultipartUploader` contract using S3 multipart uploads. It turns start, part upload, complete, and abort calls into S3A `WriteOperations` and serializes part handles with enough metadata to safely complete uploads.

## Important APIs and Types
Core methods are `startUpload()`, `putPart()`, `complete()`, `abort()`, and `abortUploadsUnderPath()`. Static helpers `buildPartHandlePayload()`, `parsePartHandlePayload()`, and `extractChecksum()` support handle serialization. Nested `PartHandlePayload` stores path, upload id, part number, length, eTag, optional checksum algorithm, and checksum.

## Control Flow
Each public operation qualifies and validates the path, decodes the upload id, and submits work asynchronously through `StoreContext.submit()`. `startUpload()` initiates the MPU and returns a byte-buffer upload handle. `putPart()` builds an upload-part request, wraps the input stream as a `RequestBody`, uploads through `WriteOperations`, extracts eTag/checksum, and returns a serialized part handle. `complete()` sorts part handles by part number, parses and validates payloads against upload id and file path, rejects duplicate part numbers, converts eTags/checksums to AWS `CompletedPart` entries, commits the upload, and returns the final eTag as a `PathHandle`. `abort()` aborts the upload id for the key.

## State and Persistence
The uploader stores references to builder, write operations, store context, and statistics. Persistent effects are S3 multipart upload creation, part upload, final commit, abort, and bulk abort under path. Part handles persist serialized state across method calls.

## Dependencies and Integration Points
It depends on Hadoop `AbstractMultipartUploader`, S3A `WriteOperations`, `StoreContext`, AWS `UploadPartRequest/Response` and `CompleteMultipartUploadResponse`, S3A multipart statistics, and commit-file `UploadEtag`. It is created by `S3AMultipartUploaderBuilder`.

## Risks and Edge Cases
Path validation uses URI string equality in part payloads, so path qualification consistency matters. The handle format is versioned only by string header `S3A-part01`; compatibility changes require care. Duplicate detection uses payload part numbers while `CompletedPart` conversion uses map keys, so mismatched map key vs payload part number should be scrutinized. Input streams are not closed here. Checksum algorithm and value must appear together.

## Test Signals
Tests should cover full MPU lifecycle, part handle round trip, wrong header, negative length, empty eTag/path/upload id, checksum extraction for all supported algorithms, path/upload-id mismatch, duplicate handles, abort behavior, and async statistics counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/S3AMultipartUploader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/S3AMultipartUploaderBuilder.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/S3AMultipartUploaderBuilder.java

## Purpose
`S3AMultipartUploaderBuilder` adapts Hadoop's multipart uploader builder pattern to construct `S3AMultipartUploader` instances with S3A-specific dependencies.

## Important APIs and Types
The constructor accepts `S3AFileSystem`, `WriteOperations`, `StoreContext`, target `Path`, and multipart uploader statistics. `getThisBuilder()` returns the typed builder. `build()` creates the uploader.

## Control Flow
The builder stores dependencies and defers all validation and operation behavior to the superclass and `S3AMultipartUploader` constructor. `build()` performs a direct instantiation.

## State and Persistence
The builder is an in-memory dependency holder and performs no persistence.

## Dependencies and Integration Points
It extends `MultipartUploaderBuilderImpl<S3AMultipartUploader, S3AMultipartUploaderBuilder>` and integrates with `S3AFileSystem` multipart uploader factory methods.

## Risks and Edge Cases
Nullability is annotated but not explicitly checked in this class. Incorrect dependency wiring will fail later during uploader operations.

## Test Signals
Tests should verify builder path propagation, dependency injection, type-safe fluent behavior, and that built uploaders operate against the qualified base path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/S3AMultipartUploaderBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/S3AStoreBuilder.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/S3AStoreBuilder.java

## Purpose
`S3AStoreBuilder` is a simple builder for `S3AStoreImpl`, collecting filesystem infrastructure dependencies before constructing the store layer.

## Important APIs and Types
It has fluent `with...` methods for `StoreContextFactory`, `ClientManager`, duration tracking, instrumentation/statistics, storage statistics, read/write rate limiters, audit span source, and optional `FileSystem.Statistics`. `build()` returns a new `S3AStoreImpl`.

## Control Flow
The builder only assigns fields and passes them to the `S3AStoreImpl` constructor. Constructor-level `requireNonNull` checks in `S3AStoreImpl` enforce most required dependencies.

## State and Persistence
Builder state is transient. It creates a service object but does not start it or persist anything.

## Dependencies and Integration Points
It integrates S3A filesystem initialization with the `S3AStore` service abstraction, client manager service, rate limiters, audit spans, and metrics.

## Risks and Edge Cases
Missing dependencies fail at store construction, not at setter time. The builder is reusable but not immutable, so accidental reuse can carry stale dependencies.

## Test Signals
Tests should cover construction with all required dependencies, failure on missing critical dependencies, optional filesystem statistics, and service initialization after build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/S3AStoreBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/S3AStoreImpl.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/S3AStoreImpl.java

## Purpose
`S3AStoreImpl` is the S3A store layer service. It owns low-level S3 clients through `ClientManager`, request construction, rate limiting, retry/invocation integration, metrics, temporary file allocation, upload/delete/head/get operations, and input stream factory delegation.

## Important APIs and Types
It extends `CompositeService` and implements `S3AStore` plus `ObjectInputStreamFactory`. Key methods include service lifecycle (`serviceInit`, `serviceStart`), client accessors, rate limiter methods, metric increment helpers, `deleteObjects()`, `headObject()`, `getRangedS3Object()`, `deleteObject()`, `uploadPart()`, `putObject()`, `waitForUploadCompletion()`, `completeMultipartUpload()`, temporary file creation, and stream factory methods (`readObject`, `factoryRequirements`, `streamType`). Inner `FactoryCallbacks` supplies S3 clients and statistics callbacks to stream factories.

## Control Flow
During construction, the store creates a `StoreContext`, captures bucket/request factory/invoker, and registers `ClientManager` as a child service. During init it selects an object input stream factory from configuration, adds it as a child service, initializes children, then binds stream-factory callbacks while still in the initialized state. Start initializes the local directory allocator. S3 operations are routed through `Invoker` retry helpers, duration trackers, rate limiters, and request factories. PUT/upload methods update active, pending, completed, and byte counters around transfer-manager or direct upload-part calls. Stream reads are delegated to the configured factory after adding the local directory allocator to `ObjectReadParameters`.

## State and Persistence
The store maintains service state, client manager, immutable store context, request factory reference, rate limiters, metrics contexts, local directory allocator, and selected object stream factory. Persistent effects include S3 object deletes, bulk deletes, head/get calls, upload part, full object upload, and multipart completion. It also creates local temporary files for buffering.

## Dependencies and Integration Points
It depends on AWS SDK v2 clients, `S3TransferManager`, S3 request/response model classes, `Invoker`, S3A instrumentation/statistics, `RequestFactory`, `ClientManager`, stream integration classes, `LocalDirAllocator`, Hadoop service lifecycle, and rate limiting. It is a major integration point between `S3AFileSystem` and lower-level S3 operations.

## Risks and Edge Cases
Root delete protection is critical for both single and bulk delete. Bulk delete partial failures are logged but returned to callers, so callers must inspect response errors or higher layers must translate. `deleteObject()` swallows object-not-found as success. `headObject()` only marks duration failure for non-not-found AWS errors and may rewrite content length through encryption handlers. Upload counters must be balanced on success/failure; transfer-manager failures are raised through `CompletionException`. Stream factory binding depends on service state and client manager state. `getOrCreateAsyncS3ClientUnchecked()` returns the unchecked async S3 client from client manager despite method naming inconsistency.

## Test Signals
Tests should cover service lifecycle and stream factory binding, capability queries, rate limiter duration recording, root delete rejection, bulk delete retry handler behavior, not-found delete/head semantics, CSE length rewrite in `headObject()`, ranged GET range header and duration, upload counter balancing on success/failure, temp file allocator selection, and stream factory callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/S3AStoreImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/S3ExpressStorage.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/S3ExpressStorage.java

## Purpose
`S3ExpressStorage` holds constants and helpers for detecting Amazon S3 Express One Zone bucket names and capability signaling.

## Important APIs and Types
Constants include `STORE_CAPABILITY_S3_EXPRESS_STORAGE`, `PRODUCT_NAME`, `ZONE_LENGTH`, and `S3EXPRESS_STORE_SUFFIX`. `isS3ExpressStore(bucket, endpoint)` checks AWS endpoint plus bucket suffix. `hasS3ExpressSuffix(bucket)` checks suffix only.

## Control Flow
Detection is a simple suffix check gated by `NetworkBinding.isAwsEndpoint(endpoint)` to avoid false positives on third-party endpoints.

## State and Persistence
The class is stateless.

## Dependencies and Integration Points
It depends on `NetworkBinding.isAwsEndpoint`. It integrates with capability reporting and S3 Express-specific configuration or warnings elsewhere in S3A.

## Risks and Edge Cases
Suffix-only detection may misclassify names on AWS-compatible stores if endpoint detection is wrong. `SUFFIX_LENGTH` is private and not used in this file. Null bucket values would throw from `endsWith`.

## Test Signals
Tests should cover AWS endpoint empty/default behavior, non-AWS endpoint false negatives, valid S3 Express suffixes, normal buckets, and null/empty bucket handling if expected by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/S3ExpressStorage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/SDKStreamDrainer.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/SDKStreamDrainer.java

## Purpose
`SDKStreamDrainer` encapsulates the decision to drain and close or abort an AWS SDK response stream when an S3A input stream is closed. It protects connection reuse while avoiding pathological reads of large remaining payloads when abort is requested or close fails.

## Important APIs and Types
It is generic over `TStream extends InputStream & Abortable` and implements `CallableRaisingIOE<Boolean>`. Constructor captures URI, stream, abort flag, remaining bytes, stream statistics, and reason. `apply()` records duration and returns whether abort occurred. `applyRaisingException()` is testing-only. Getters expose execution outcome, thrown exception, drained count, and abort state.

## Control Flow
`apply()` wraps `drainOrAbortHttpStream()` in stream-statistics duration tracking and stores any thrown exception instead of rethrowing. `drainOrAbortHttpStream()` enforces single execution with `AtomicBoolean`. If not forced to abort, it drains up to `remaining` bytes using `DRAIN_BUFFER_SIZE`, closes the stream, records non-abort close stats, and returns false. If draining/closing fails or abort was requested, it calls `sdkStream.abort()`, records abort close stats, and returns true.

## State and Persistence
Mutable per-call state includes `remaining`, `drained`, `executed`, `thrown`, and `aborted`. It does not persist data, but it releases or aborts HTTP connections and updates input stream statistics.

## Dependencies and Integration Points
It depends on AWS SDK `Abortable`, S3A input stream statistics, `InternalConstants.DRAIN_BUFFER_SIZE`, and IOStatistics duration helpers. It is used by S3A input stream close/unbuffer code paths.

## Risks and Edge Cases
The operation is one-shot; repeated invocation throws. If `InputStream.read()` returns zero repeatedly, the loop exits early and close may still cause SDK abort internally. Aborting after close failure preserves the last exception in `thrown` but `apply()` swallows it. The remaining byte count is an `int`, so callers must not pass values above integer range.

## Test Signals
Tests should cover full drain and close, forced abort, close failure escalation to abort, abort failure recording, duplicate invocation rejection, short reads, zero/negative remaining assumptions, duration/statistic updates, and `applyRaisingException()` propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/SDKStreamDrainer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/StatusProbeEnum.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/StatusProbeEnum.java

## Purpose
`StatusProbeEnum` defines the S3 probes used to resolve path status: object HEAD, directory marker HEAD, and LIST.

## Important APIs and Types
Enum values are `Head`, `DirMarker`, and `List`. Static sets include `ALL`, `HEAD_ONLY`, `LIST_ONLY`, `FILE`, and `DIRECTORIES`.

## Control Flow
Callers choose a static set to control status resolution strategy. `FILE` maps to HEAD only; `DIRECTORIES` maps to list only; `ALL` contains `Head` and `List` but not `DirMarker`.

## State and Persistence
The enum and sets are in-memory constants. No persistence.

## Dependencies and Integration Points
It depends on `EnumSet` and Hadoop classification annotations. It integrates with S3A status probing/listing logic.

## Risks and Edge Cases
The naming can mislead: `ALL` excludes `DirMarker`. If callers expect directory marker HEADs, they must request it explicitly or use logic elsewhere.

## Test Signals
Status-resolution tests should assert exactly which probes are attempted for each set and verify marker-only directories with relevant probe configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/StatusProbeEnum.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/StoreContext.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/StoreContext.java

## Purpose
`StoreContext` is an immutable capability/context object passed to S3A subsidiary components so they can access filesystem configuration, path/key conversion, executors, invokers, metrics, audit spans, request factory, and selected performance/encryption flags without depending on the whole filesystem class.

## Important APIs and Types
It exposes getters for URI, bucket, configuration, username, owner, executor, invoker, instrumentation, storage statistics, input policy, change detection, delete/list flags, accessors, auditor, CSE flag, and performance flags. It provides `keyToPath()`, `pathToKey()`, `makeQualified()`, statistic increment/gauge helpers, throttled executor creation, temp file and bucket-location callbacks, `fullKey(S3AFileStatus)`, `submit(CompletableFuture, Callable)`, active audit span lookup, and request factory lookup.

## Control Flow
Most methods delegate to captured fields or `ContextAccessors`. `createThrottledExecutor()` wraps the base executor with `SemaphoredDelegatingExecutor`. `submit()` schedules a callable on the executor and completes the supplied `CompletableFuture` through `LambdaUtils.eval()`. `fullKey()` appends a slash to directory keys when absent.

## State and Persistence
The context fields are final and stable after construction. It mutates metrics counters/gauges and schedules asynchronous work but does not directly persist object-store state.

## Dependencies and Integration Points
It depends on Hadoop `Configuration`, `Path`, UGI, S3A metrics/statistics, `Invoker`, `RequestFactory`, `ContextAccessors`, audit span types, `FlagSet<PerformanceFlagEnum>`, and executor utilities. It is used throughout S3A operations, multipart uploader, stream factory setup, and store logic.

## Risks and Edge Cases
Some tests may pass a null executor, but production async paths expect non-null. `submit()` assumes executor exists and can accept work. Because active audit span is thread-local, worker code must capture/pass spans explicitly. `ContextAccessors` correctness is critical for path/key conversions and temp-file creation.

## Test Signals
Tests should validate path/key conversion delegation, directory `fullKey()` slash behavior, statistic counter/gauge forwarding, throttled executor capacity, future completion and exception handling in `submit()`, null executor test behavior, audit span retrieval, and request factory delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/StoreContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/StoreContextBuilder.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/StoreContextBuilder.java

## Purpose
`StoreContextBuilder` assembles the inputs needed to create a `StoreContext`.

## Important APIs and Types
It has setters for filesystem URI, bucket, configuration, username, owner, executor, executor capacity, invoker, statistics, storage statistics, input policy, change detection, multi-object delete flag, list-v1 flag, context accessors, auditor, CSE enablement, and performance flags. `build()` constructs `StoreContext`.

## Control Flow
Each setter assigns a field and returns the builder. Defaults are `S3AInputPolicy.Normal`, multi-object delete enabled, list-v1 disabled, and CSE disabled. `build()` passes all fields directly to the package-private `StoreContext` constructor.

## State and Persistence
The builder is mutable transient state only. It creates immutable context objects.

## Dependencies and Integration Points
It integrates `S3AFileSystem` initialization with `StoreContext` creation and depends on S3A metrics, audit, security, and performance flag types.

## Risks and Edge Cases
No validation is performed in the builder, so missing dependencies may surface later as null dereferences. Builder reuse can unintentionally carry previous settings.

## Test Signals
Tests should verify defaults, all setter propagation, CSE and performance flag handling, and behavior when optional vs required fields are omitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/StoreContextBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/StoreContextFactory.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/StoreContextFactory.java

## Purpose
`StoreContextFactory` abstracts creation of `StoreContext` instances, including capture of current audit span where needed.

## Important APIs and Types
It defines one method: `StoreContext createStoreContext()`.

## Control Flow
Consumers call the factory during store construction or when fresh operation-specific context is needed. Implementations decide what runtime state to capture.

## State and Persistence
The interface has no state. Implementations may snapshot current filesystem/audit state into new context objects.

## Dependencies and Integration Points
It is used by `S3AStoreBuilder` and `S3AStoreImpl`; implementations are usually provided by `S3AFileSystem` or tests.

## Risks and Edge Cases
Returning contexts with stale audit spans, missing executors, or inconsistent request factories will affect every downstream operation.

## Test Signals
Tests should verify factories capture expected audit context and produce contexts with all required dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/StoreContextFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/UploadContentProviders.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/UploadContentProviders.java

## Purpose
`UploadContentProviders` supplies retry-safe AWS SDK `ContentStreamProvider` implementations for S3A uploads from files, byte buffers, and byte arrays. It avoids SDK defaults to control stream recreation, offsets, and resource cleanup.

## Important APIs and Types
Static factories create `BaseContentProvider` instances for file slices, byte buffers, and byte arrays, optionally guarded by an `isOpen` predicate. `BaseContentProvider<T>` tracks size, stream creation count, current stream, start time, and close behavior. Private subclasses implement file-with-offset, byte-buffer, and byte-array stream creation.

## Control Flow
`BaseContentProvider.newStream()` closes any current stream, checks the optional open predicate, increments creation count, logs on first recreation, and delegates to subclass `createNewStream()`. File providers open a `FileInputStream`, seek to offset, and wrap it in `BufferedInputStream`. Byte-buffer providers reset buffer limit/position and wrap it in `ByteBufferInputStream`. Byte-array providers create `ByteArrayInputStream` with offset and size.

## State and Persistence
Providers maintain current stream references and creation counts. They do not copy byte buffer or byte array contents, so external data remains shared. They read local files or in-memory buffers during upload retries; no object-store persistence happens in this class.

## Dependencies and Integration Points
It depends on AWS SDK `ContentStreamProvider`, Hadoop `ByteBufferInputStream`, `IOUtils.cleanupWithLogger`, and functional IO helpers. It is used by S3A upload code to provide replayable request bodies.

## Risks and Edge Cases
Byte buffers and arrays are not copied; mutation during upload corrupts data. `ByteBufferContentProvider.createNewStream()` mutates the source buffer position/limit, which callers must not reuse concurrently. `isOpen` predicate failures prevent retry after stream close. File provider IO failures are wrapped as `UncheckedIOException`. Size is long in base but byte-buffer/array streams require integer size.

## Test Signals
Tests should cover stream recreation counts, closing previous streams, file offset reads, byte buffer position/limit reset, byte-array offset bounds, negative offset/size rejection, open-predicate failure, mutation caveats, and retry behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/UploadContentProviders.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/V2Migration.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/V2Migration.java

## Purpose
`V2Migration` retains SDK v1 migration diagnostics after S3A's move to AWS SDK v2.

## Important APIs and Types
It exposes `SDK_V2_UPGRADE_LOG` and `v1RequestHandlersUsed(String handlers)`, which logs ignored v1 request handler configuration through `LogExactlyOnce`.

## Control Flow
When legacy v1 request handlers are encountered, callers invoke `v1RequestHandlersUsed()`. The warning is emitted once on the SDK v2 upgrade logger.

## State and Persistence
The class is stateless except for logger and `LogExactlyOnce` suppression state. It does not persist or alter configuration.

## Dependencies and Integration Points
It depends on S3A audit constants, internal upgrade log name, SLF4J, and Hadoop `LogExactlyOnce`. It integrates with configuration migration/compatibility checks.

## Risks and Edge Cases
The method says handlers are ignored; users relying on v1 request handlers may lose behavior silently after the one-time warning. Logging level/wording matters for migration diagnostics.

## Test Signals
Tests should verify one-time logging behavior and invocation when legacy audit request handler settings are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/V2Migration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/logging/Log4JController.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/logging/Log4JController.java

## Purpose
`Log4JController` is the concrete Log4j-backed implementation of S3A's reflection-based log-level controller.

## Important APIs and Types
It extends `LogControl` and implements `setLevel(String logName, LogLevel level)` by resolving a Log4j logger and applying `Level.toLevel(level.getLog4Jname())`.

## Control Flow
The method catches all exceptions and returns false on failure, allowing S3A to run with other SLF4J backends or absent Log4j classes.

## State and Persistence
It changes in-process Log4j logger levels. No files or external persistent state are written.

## Dependencies and Integration Points
It directly imports `org.apache.log4j.Level` and `Logger`, so it is package-private and instantiated only reflectively by `LogControllerFactory` to avoid hard failures when Log4j is absent.

## Risks and Edge Cases
Direct instantiation outside reflection can trigger classpath failures. Swallowed exceptions make failures non-fatal but harder to diagnose.

## Test Signals
Tests should verify successful level changes when Log4j is present and false return when logger backend operations fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/logging/Log4JController.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/logging/LogControl.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/logging/LogControl.java

## Purpose
`LogControl` defines a backend-neutral abstraction for changing logger levels at runtime.

## Important APIs and Types
Nested enum `LogLevel` lists `ALL`, `FATAL`, `ERROR`, `WARN`, `INFO`, `DEBUG`, `TRACE`, and `OFF`, each with a Log4j name. `setLogLevel(String, LogLevel)` is the public final safe wrapper. `setLevel()` is the backend-specific abstract implementation.

## Control Flow
`setLogLevel()` invokes `setLevel()` and catches all exceptions, returning false on failure. Subclasses implement actual backend mutation.

## State and Persistence
The base class is stateless. Subclasses may mutate in-process logging configuration only.

## Dependencies and Integration Points
It is used by `Log4JController` and `LogControllerFactory`. It has no direct logging backend dependency.

## Risks and Edge Cases
Broad exception swallowing is intentional but hides detailed failure causes unless subclasses or factory log them elsewhere. Level enum names are Log4j-oriented even though the abstraction is nominally backend-neutral.

## Test Signals
Tests should validate enum mappings, exception swallowing, false return on failure, and successful delegation to subclass implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/logging/LogControl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/logging/LogControllerFactory.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/logging/LogControllerFactory.java

## Purpose
`LogControllerFactory` creates `LogControl` instances reflectively, preferring Log4j but falling back to a no-op stub when unavailable.

## Important APIs and Types
`createController(String classname)` reflectively loads and instantiates a controller. `createLog4JController()` targets the package-private Log4j controller class. `createController()` returns the Log4j controller or `StubLogControl`, whose `setLevel()` always returns false.

## Control Flow
Reflection failures are logged once at debug level via `LogExactlyOnce` and return null. The public default factory converts null to stub so callers always get a non-null `LogControl`.

## State and Persistence
State is limited to logger and one-time log suppression. It does not persist anything; created controllers may mutate in-process log levels.

## Dependencies and Integration Points
It depends on SLF4J and `LogExactlyOnce`, and indirectly on Log4j only via reflection string. It is the safe entry point for code that wants optional runtime log control.

## Risks and Edge Cases
`Class.newInstance()` requires a no-arg constructor and is deprecated in newer Java APIs, though still functional here. Stub fallback can make caller requests appear harmless but ineffective. Classloader isolation can affect reflective loading.

## Test Signals
Tests should cover successful reflective load, failed class load returning null, default stub fallback, one-time debug logging, and stub `setLogLevel()` returning false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/logging/LogControllerFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/logging/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/logging/package-info.java

## Purpose
This package descriptor documents the `org.apache.hadoop.fs.s3a.impl.logging` package as reflection-based code for manipulating logging levels in external libraries.

## Important APIs and Types
It applies `@InterfaceAudience.Private` to the package.

## Control Flow
There is no runtime control flow beyond Java package annotation metadata.

## State and Persistence
No state or persistence.

## Dependencies and Integration Points
It depends on Hadoop classification annotations and describes the package containing `LogControl`, `Log4JController`, and `LogControllerFactory`.

## Risks and Edge Cases
The package is explicitly private; downstream users should not treat it as stable API.

## Test Signals
No direct behavioral tests are needed beyond compilation and annotation visibility checks if the build validates package annotations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/logging/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/package-info.java

## Purpose
This package descriptor marks `org.apache.hadoop.fs.s3a.impl` as private, unstable implementation code for the S3A store.

## Important APIs and Types
It applies `@InterfaceAudience.Private` and `@InterfaceStability.Unstable` package annotations.

## Control Flow
No runtime control flow beyond package annotation metadata.

## State and Persistence
No state or persistence.

## Dependencies and Integration Points
It depends on Hadoop classification annotations and applies to all implementation classes in the package.

## Risks and Edge Cases
External consumers should not depend on binary or source stability of this package. The annotations reinforce that these classes may change without compatibility promises.

## Test Signals
Compilation and package annotation processing are the only direct signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/AbstractObjectInputStreamFactory.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/AbstractObjectInputStreamFactory.java

## Purpose
`AbstractObjectInputStreamFactory` provides shared service lifecycle binding and base capability reporting for S3A object input stream factories.

## Important APIs and Types
It extends `AbstractService` and implements `ObjectInputStreamFactory`. `bind(FactoryBindingParameters)` stores callbacks after checking the service is initialized. `hasCapability(String)` reports IO statistics, stream leak tracking, and stream-type capability support. `callbacks()` exposes bound factory callbacks to subclasses.

## Control Flow
During `S3AStoreImpl` initialization, concrete factories are initialized as services, then bound with callbacks. Capability queries normalize input to lower case and match base capabilities or `streamType().capability()`.

## State and Persistence
It stores binding parameters and callbacks in memory. No persistence.

## Dependencies and Integration Points
It depends on Hadoop service lifecycle, stream capability names, statistic names, and `FactoryBindingParameters`. Concrete subclasses include classic and analytics factories.

## Risks and Edge Cases
Binding before or after the initialized state fails. Subclasses depend on non-null callbacks after bind. Capability string case handling uses Hadoop lower-case utility.

## Test Signals
Tests should verify bind state checks, callback availability after bind, base capabilities, stream-type dynamic capability, and subclass override interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/AbstractObjectInputStreamFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/AnalyticsRequestCallback.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/AnalyticsRequestCallback.java

## Purpose
`AnalyticsRequestCallback` adapts AWS Analytics Accelerator request callbacks into S3A input stream statistics updates.

## Important APIs and Types
It implements AAL `RequestCallback` and holds `S3AInputStreamStatistics`. Methods map GET, HEAD, block prefetch, footer parse failure, vectored read, and cache-hit callbacks to statistics methods.

## Control Flow
The analytics stream passes an instance into `OpenStreamInformation`; AAL invokes callbacks during read operations and prefetch. Each callback immediately updates S3A statistics.

## State and Persistence
It stores a statistics reference and mutates in-memory metrics. No persistence.

## Dependencies and Integration Points
It depends on `software.amazon.s3.analyticsaccelerator.util.RequestCallback` and S3A input stream statistics. It is created by `AnalyticsStream`.

## Risks and Edge Cases
Statistics must be non-null; no null checks are performed. Callback frequency may be high, so stats methods should be lightweight.

## Test Signals
Tests should assert each AAL callback increments the intended S3A statistic, including prefetch byte calculation `end - start + 1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/AnalyticsRequestCallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/AnalyticsStream.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/AnalyticsStream.java

## Purpose
`AnalyticsStream` is an `ObjectInputStream` implementation backed by AWS Analytics Accelerator for S3. It enables parquet-aware optimizations, tail reads, vectored reads, cache/prefetch statistics, and audit context propagation.

## Important APIs and Types
The constructor creates an AAL `S3SeekableInputStream` from object attributes and `OpenStreamInformation`. It overrides `read()`, `read(byte[],int,int)`, `seek()`, `getPos()`, `readTail()`, both `readVectored()` overloads, `available()`, `close()`, stream-open checks, and leak finalizer abort. Helpers build AAL open-stream info, map S3A input policy to AAL `InputPolicy`, handle read failure, and increment bytes-read counters.

## Control Flow
Read methods check closed state, record read-start stats at current position, delegate to AAL stream, close on IO failure, and update bytes-read stats on successful reads. `readVectored()` converts Hadoop `FileRange` entries into AAL `ObjectRange` futures and assigns those futures back to ranges before delegating to AAL. `buildOpenStreamInformation()` attaches request callback, object metadata when eTag is present, SSE-C secrets when configured, and audit span operation/span ids. Sequential S3A input policy disables AAL optimizations by mapping to AAL sequential mode; other policies map to `None`.

## State and Persistence
Mutable state includes the AAL input stream, cached last position, and volatile/synchronized close flags. No object-store writes occur; reads and prefetches issue S3 requests through AAL. Close releases the AAL stream and merges base stream statistics through `super.close()`.

## Dependencies and Integration Points
It depends on AAL stream factory/types, S3A encryption secret operations, S3A object attributes/read context/statistics, Hadoop vectored read APIs, and `ObjectInputStream`. It is created by `AnalyticsStreamFactory` when configured stream type is analytics.

## Risks and Edge Cases
On read failure there is no recovery; the stream closes and rethrows. `isClosed()` checks `inputStream == null` while `throwIfClosed()` checks a separate `closed` flag; close sets both. `getPos()` caches position before close. SSE-C support passes customer key to AAL, but other encryption modes rely on normal request behavior. Vectored read futures are controlled by AAL; range validation is delegated. Close logging omits exception argument formatting detail.

## Test Signals
Tests should cover read/readTail/readVectored success stats, negative seek rejection, close idempotence, read failure close behavior, SSE-C open info, audit context propagation, input policy mapping, cache/prefetch callbacks, bytes-read propagation to FS statistics, and stream-leak finalizer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/AnalyticsStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/AnalyticsStreamFactory.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/AnalyticsStreamFactory.java

## Purpose
`AnalyticsStreamFactory` creates `AnalyticsStream` instances and manages the shared lazy AAL `S3SeekableInputStreamFactory`.

## Important APIs and Types
It extends `AbstractObjectInputStreamFactory`. `serviceInit()` builds AAL configuration from Hadoop config and the analytics prefix. `bind()` creates a `LazyAutoCloseableReference` for the AAL factory. `readObject()` creates streams. `streamType()` returns `InputStreamType.Analytics`. `factoryRequirements()` returns vectored IO requirements with range merging disabled. `serviceStop()` closes the lazy factory and increments close statistics.

## Control Flow
The factory is initialized by `S3AStoreImpl`, then bound to callbacks. The AAL factory is created lazily on first read using a sync S3 client from callbacks wrapped in `S3SyncSdkObjectClient`. Stop closes the lazy reference and then stops the service.

## State and Persistence
It stores AAL configuration and a lazy closeable reference. No object-store persistence; it creates read streams and updates statistics on close.

## Dependencies and Integration Points
It depends on AAL configuration and factory classes, S3A stream integration, vectored IO context, lazy reference utility, and factory callbacks from the store.

## Risks and Edge Cases
`serviceStop()` assumes the lazy reference is non-null after bind; stopping before bind would need lifecycle coverage. Disabling range merging changes vectored read behavior deliberately to avoid discarded reads. Lazy factory creation can fail on first read rather than during service init.

## Test Signals
Tests should cover configuration prefix loading, lazy factory creation with sync client callback, readObject construction, factory requirements range-merge setting, close statistic increment, and service stop before/after factory creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/AnalyticsStreamFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/ClassicObjectInputStreamFactory.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/ClassicObjectInputStreamFactory.java

## Purpose
`ClassicObjectInputStreamFactory` creates the traditional `S3AInputStream` implementation and declares its stream capabilities.

## Important APIs and Types
`readObject(ObjectReadParameters)` returns a new `S3AInputStream`. `hasCapability()` adds IO statistics context, readahead, unbuffer, and vectored IO capabilities before delegating to base capability checks. `streamType()` returns `Classic`. `factoryRequirements()` returns vectored IO context from configuration and no extra threads.

## Control Flow
S3A store delegates stream creation here when configured for classic streams. Capability queries are normalized and matched against known stream capability constants.

## State and Persistence
The factory has service lifecycle state inherited from `AbstractService` but no custom mutable state. It creates read streams only.

## Dependencies and Integration Points
It depends on `S3AInputStream`, `ObjectReadParameters`, stream capability constants, and `StreamIntegration.populateVectoredIOContext`.

## Risks and Edge Cases
Capability declarations must match actual `S3AInputStream` behavior. Changes to classic stream features require updating this factory.

## Test Signals
Tests should verify stream type, created class, capability responses, and vectored IO configuration propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/ClassicObjectInputStreamFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/FactoryBindingParameters.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/FactoryBindingParameters.java

## Purpose
`FactoryBindingParameters` packages callbacks supplied to object input stream factories during binding.

## Important APIs and Types
The constructor requires `ObjectInputStreamFactory.StreamFactoryCallbacks`. Package-private `callbacks()` returns the stored callbacks.

## Control Flow
`S3AStoreImpl.finishStreamFactoryInit()` creates this object and passes it to `ObjectInputStreamFactory.bind()`. Factories extract callbacks for client access and statistics.

## State and Persistence
It is an immutable in-memory holder. No persistence.

## Dependencies and Integration Points
It depends on `ObjectInputStreamFactory.StreamFactoryCallbacks` and Java `requireNonNull`. It is part of stream factory lifecycle wiring.

## Risks and Edge Cases
Callback visibility is package-private, so only stream package code can access it. Null callbacks fail immediately.

## Test Signals
Tests should verify null rejection and callback identity propagation through factory binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/FactoryBindingParameters.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/InputStreamType.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/InputStreamType.java

## Purpose
`InputStreamType` enumerates S3A object input stream implementations and maps each type to a factory-construction function, numeric stream ID, and capability name.

## Important APIs and Types
Values are `Classic`, `Prefetch`, `Analytics`, and `Custom`. Each has a config name, stable stream ID, and `Function<Configuration,ObjectInputStreamFactory>`. Methods expose `getName()`, `streamID()`, `capability()`, and `factory()`.

## Control Flow
Stream integration code selects an enum value from configuration and invokes `factory()` to create the selected factory. `Custom` delegates to `StreamIntegration.loadCustomFactory()`.

## State and Persistence
Enum constants are immutable. No persistence.

## Dependencies and Integration Points
It depends on stream integration constants, `PrefetchingInputStreamFactory`, classic and analytics factories, and Hadoop `Configuration`. It drives `fs.s3a.input.stream.type` behavior and capability reporting.

## Risks and Edge Cases
Numeric IDs are intentionally decoupled from enum ordinals; metrics should use `streamID()` rather than `ordinal()` if stable IDs are needed. Custom factory loading can fail due to classpath/configuration errors.

## Test Signals
Tests should validate name-to-factory mapping, capability strings, stable IDs, custom factory loading, and configured stream selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/InputStreamType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/ObjectInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/ObjectInputStream.java

## Purpose
`ObjectInputStream` is the common base class for streams reading S3 objects. It stores immutable object/read context, statistics, callbacks, leak reporting, vectored IO configuration, and base capabilities shared by classic, prefetch, analytics, and custom streams.

## Important APIs and Types
The constructor takes `InputStreamType` and `ObjectReadParameters`, validates bucket/key/content length, captures callbacks, stream statistics, bounded thread pool, thread IO statistics aggregator, and vectored context. It defines abstract `isStreamOpen()` and `abortInFinalizer()`, implements synchronized `close()`, `finalize()` leak reporting, `getInputPolicy()/setInputPolicy()`, `getS3AStreamStatistics()`, `getIOStatistics()`, `hasCapability()`, vectored read size methods, `streamType()`, and protected accessors for context/callbacks/object identity.

## Control Flow
Subclasses perform actual reads. On close, base class closes callbacks, closes stream statistics, and aggregates stream IO stats into the current thread statistics context. The finalizer asks `LeakReporter` to warn and call subclass abort behavior if the stream remains open. Capability queries advertise IO statistics, stream leaks, and the configured stream-type capability.

## State and Persistence
It stores per-stream state and updates in-memory statistics. It does not directly issue S3 requests or persist data. Close merges metrics back to filesystem/thread aggregates.

## Dependencies and Integration Points
It depends on Hadoop `FSInputStream`, `StreamCapabilities`, `LeakReporter`, S3A read context/object attributes/statistics, IO statistics aggregator, and vectored IO context. Subclasses like `S3AInputStream` and `AnalyticsStream` build on it.

## Risks and Edge Cases
Finalizers are defensive and not deterministic; applications must close streams. Subclasses must ensure `isStreamOpen()` is cheap and thread-safe enough for leak reporting. Base `close()` does not guard idempotence itself; subclasses should avoid double-closing resources. Content length must be non-negative at construction.

## Test Signals
Tests should validate constructor validation, base capabilities, input policy statistic updates, close callback/stat merge behavior, leak reporter invocation, vectored min/max propagation, and subclass close idempotence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/ObjectInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/ObjectInputStreamCallbacks.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/ObjectInputStreamCallbacks.java

## Purpose
`ObjectInputStreamCallbacks` defines the operations an object input stream needs from the S3A store/filesystem: building GET requests, executing GETs, submitting async work, and closing associated context.

## Important APIs and Types
It extends `Closeable`. Methods are `newGetRequestBuilder(String key)`, `getObject(GetObjectRequest)`, and `<T> CompletableFuture<T> submit(CallableRaisingIOE<T> operation)`.

## Control Flow
Streams use `newGetRequestBuilder()` to create request builders with common request factory settings, `getObject()` to execute reads with encryption-aware client selection, and `submit()` for background work such as stream draining. `ObjectInputStream.close()` calls `callbacks.close()`.

## State and Persistence
The interface has no state. Implementations may hold audit spans, clients, and per-stream resources. GET calls read persistent object data; submit can run cleanup operations.

## Dependencies and Integration Points
It depends on AWS SDK get request/response types, S3A retry annotations, and Hadoop functional callable utilities. It is implemented by S3A stream callback classes outside this subset.

## Risks and Edge Cases
Implementations must be close-safe and preserve audit/encryption semantics. Async operations must complete futures with exceptions reliably. GET execution behavior differs when client-side encryption is enabled.

## Test Signals
Tests should validate GET request construction, encrypted vs unencrypted GET paths, async drain submission, callback close idempotence, and exception propagation from submitted operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/ObjectInputStreamCallbacks.java -->
