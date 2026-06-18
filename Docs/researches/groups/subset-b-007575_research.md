# subset-b-007575 Research

Grouped source research for Hadoop S3A filesystem setup, input policy selection, and the classic S3A input stream. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AFileSystem.java

## Purpose

`S3AFileSystem` is Hadoop's primary `FileSystem` implementation for the `s3a://` scheme. It translates Hadoop filesystem operations into S3 object, multipart upload, list, copy, and delete operations while layering in S3A-specific concerns such as request auditing, retry translation, change detection, delegation tokens, client-side encryption, directory markers, magic commit paths, IO statistics, and capability reporting.

## Important APIs, Types, and Functions

The class extends `FileSystem` and implements stream/capability interfaces. Public filesystem APIs include `initialize`, `open`, `openFileWithOptions`, `create`, `createFile`, `createNonRecursive`, `rename`, `delete`, `mkdirs`, `listStatus`, `listFiles`, `listLocatedStatus`, `getFileStatus`, `exists`, `isFile`, `isDirectory`, xattr/header accessors, checksum access, multipart uploader creation, bulk delete creation, delegation token methods, and `close`. Test/private integration APIs expose `getInstrumentation`, `getListing`, `getS3AInternals`, `getRequestFactory`, `createStoreContext`, `getInputPolicy`, `getChangeDetectionPolicy`, and write helpers.

Key internal collaborators are `S3AStore`, `ClientManager`, AWS SDK `S3Client`, `RequestFactory`, `Listing`, `S3AFileSystemOperations` variants for CSE/non-CSE behavior, `OpenFileSupport`, `S3AReadOpContext`, `WriteOperationHelper`, `MagicCommitIntegration`, `AuditManagerS3A`, `S3AInstrumentation`, `S3AStatisticsContext`, `ChangeDetectionPolicy`, `S3ADelegationTokens`, and operation classes such as `RenameOperation`, `DeleteOperation`, `MkdirOperation`, `GetContentSummaryOperation`, and `BulkDeleteOperation`.

## Control Flow

Initialization is a long staged setup. `initialize` derives the bucket, propagates bucket-specific configuration, handles access point ARNs, patches classloader and credential-provider settings, determines delegation-token support, sets the canonical URI, initializes instrumentation/statistics, builds encryption secrets, retry policy, CSE/analytics flags, filesystem operation handler, owner/working directory, paging and multipart settings, endpoint/region/FIPS/S3 Express flags, list version, conditional create, signer/audit service, request factory, client manager, input policy, change detection policy, magic committer integration, upload block factory, performance flags, listing/open-file helpers, store, S3 client, stream factory requirements, vector IO context, thread pools, bucket probe, and multipart upload purge. Failures during AWS SDK, IO, or runtime setup close created services and translate SDK failures.

Read flow starts in `open` or `openFileWithOptions`, which prepare `OpenFileInformation`, create input stream statistics and an audit span, fetch or validate file status, build a `S3AReadOpContext`, allocate a per-stream semaphored executor from the bounded thread pool, build `ObjectReadParameters`, and delegate actual stream construction to `S3AStore.readObject`.

Write flow goes through `create`/`createFile`/`createNonRecursive` into `innerCreateFile`. It rejects root writes, evaluates overwrite/performance/conditional-create/magic-path options, decides which HEAD/LIST probes are needed, constructs `PutTracker` and `PutObjectOptions`, validates output settings, and returns an `S3ABlockOutputStream` configured with block factory, multipart state, statistics, write helper, executor, CSE flag, and IO statistics aggregator. Append is explicitly unsupported.

Rename validates source/destination status with `initiateRename`, then executes `RenameOperation`, which implements S3 rename as copy plus delete and directory-marker fixup. Delete obtains status and executes `DeleteOperation`; on success it may recreate a parent directory marker. Listing uses the `Listing` helper to issue async/paged list requests, with fallbacks to status probes when a path may be a file or empty directory.

Status checks flow through `innerGetFileStatus` and `s3GetFileStatus`. The status algorithm first tries a HEAD for non-directory-marker keys when requested, then LISTs the slash-suffixed prefix to identify directory markers or child entries, returning file statuses, directory statuses with optional empty-directory state, root status, or `FileNotFoundException`.

Low-level S3 calls are wrapped with `Invoker`, duration tracking, statistics increments, and exception translation. `listObjects` and continuation pick V1 or V2 list APIs. `deleteObject`, `deleteObjects`, `putObject`, `putObjectDirect`, `uploadPart`, `copyFile`, multipart listing/abort, bucket metadata, and object metadata are routed through `S3AStore`, `S3Client`, or transfer manager as appropriate. `close` is one-shot and calls `stopAllServices` to close store, thread pools, delegation tokens, signer manager, audit manager, credentials, and instrumentation.

## State and Persistence Behavior

The class maintains per-filesystem in-memory state: URI, bucket/access point, working directory, owner/username, S3 store/client, credentials, request factory, retry invoker, thread pools, statistics, audit manager, listing helper, open-file helper, encryption secrets, multipart settings, performance flags, input policy, change detection policy, delegation tokens, magic committer integration, CSE and endpoint flags, and `deleteOnExit` paths. `closed` and `isClosed` gate lifecycle state.

Persistent data lives in S3 rather than in local metadata stores. Files are S3 objects; directories are inferred from prefixes and sometimes represented by zero-byte slash-suffixed directory markers. Creates and writes persist objects through PUT or multipart upload. Deletes remove objects in single or batch calls. Renames are non-atomic copy/delete sequences. Multipart uploads can persist as pending S3 state until completed or aborted. Delegation-token and credential state may influence authentication but is not stored by this class except through the token binding lifecycle.

## Dependencies and Integration Points

This class sits at the Hadoop/S3 boundary. It depends on Hadoop `FileSystem`, `Path`, `FileStatus`, `FSDataInputStream`, `FSDataOutputStream`, `BulkDelete`, `MultipartUploader`, audit/span APIs, IO statistics, retry annotations, security UGI/tokens, and common filesystem capability constants. It depends on AWS SDK v2 S3 models and clients for HEAD, LIST, PUT, COPY, DELETE, multipart, transfer manager, access point ARN, and bucket metadata operations.

Within S3A it integrates with `S3AStore`, `S3AStoreBuilder`, `S3AInputPolicy`, `S3AInputStream`/object stream factories, `S3ABlockOutputStream`, `S3ADataBlocks`, `RequestFactoryImpl`, `S3AUtils`, `S3xLoginHelper`, `ChangeTracker`, `ChangeDetectionPolicy`, `MagicCommitIntegration`, commit protocols, directory-marker tooling, multipart utilities, header processing, client factory abstractions, signer management, and CSE-specific filesystem operation implementations.

## Risks and Edge Cases

S3 renames and recursive deletes are not atomic and may leave partial results if copy/delete/list phases fail. Status and directory semantics depend on HEAD/LIST permissions and on marker/prefix interpretation; missing list permission can look different from missing object permission. Directory markers and parent-marker recreation can interact with concurrent writers and magic commit paths. Performance create flags skip safety probes and can trade correctness checks for fewer S3 calls. Conditional create requires the FS option to be enabled and can fail fast when unsupported.

Initialization has many partially constructed services, so cleanup ordering is critical. Access point ARNs alter bucket identity, endpoint, region, and list-version support. CSE changes available operations, active block count, object size interpretation, and multipart uploader support. S3 Express declares inconsistent directory listing capability. Bulk delete has page-size and partial-failure handling; `MultiObjectDeleteException` updates rejected-file metrics but callers still need to handle incomplete deletion. `getS3AInternals().getBucketLocation()` appears recursively routed in the no-argument implementation, so tests around that path should guard against accidental recursion. `setInputPolicy` is retained as a deprecated no-op, so callers expecting runtime filesystem-wide policy changes will not get them.

## Test Signals

High-value tests include initialization with normal bucket, access point ARN, required access point missing, delegation token enabled/disabled, CSE variants, FIPS/region/endpoint settings, list V1/V2 selection, S3 Express flagging, and bucket probe modes. Filesystem behavior tests should cover open with supplied status and without HEAD-skipping, open-file read policies, create overwrite/no-overwrite/performance/conditional-create modes, root create rejection, directory conflict detection, magic commit paths, append unsupported, rename file/directory/error cases, delete missing/nonrecursive/recursive cases, parent marker recreation, mkdirs on existing files and magic paths, status probes for file/directory/root/empty directory, and listing fallbacks.

Integration tests should assert AWS operation counters and IO statistics for PUT, multipart upload, copy, list, delete, and read/open. Failure tests should cover 404/403 bucket/object handling, multi-delete partial failures, request retry translation, change-detected copy failures, cleanup after initialization failure, close idempotence, delegation token issuance, `hasPathCapability` for CSE and conditional-create permutations, and xattr/checksum behavior under enabled and disabled configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AInputPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AInputPolicy.java

## Purpose

`S3AInputPolicy` is the internal enum that reduces Hadoop open-file read-policy strings into the three S3A read strategies used by S3A input streams: normal/adaptive, random, and sequential. It gives S3A a compact policy object while accepting a broader set of public option names for file formats and access patterns.

## Important APIs, Types, and Functions

The enum values are `Normal`, `Random`, and `Sequential`. Each stores the external policy string, whether the policy should be treated as random IO, and whether it is adaptive. `toString`, `getPolicy`, `isRandomIO`, and `isAdaptive` expose those fields inside the package. Static `getPolicy(String, S3AInputPolicy)` parses a single policy name with a fallback. Static `getFirstSupportedPolicy(Collection<String>, S3AInputPolicy)` scans ordered candidate names and returns the first recognized policy.

## Control Flow

`getPolicy` trims and lowercases its input using `Locale.ENGLISH`, then switches over Hadoop open-file read-policy constants and the older S3A `INPUT_FADV_NORMAL` name. Adaptive/default/normal map to `Normal`. HBase, random, vector, columnar, ORC, and Parquet names map to `Random`. Avro, CSV, JSON, sequential, and whole-file names map to `Sequential`. Unknown names return the supplied default, which may be null. `getFirstSupportedPolicy` simply calls `getPolicy` with a null default for each candidate and returns the first non-null result, otherwise the fallback.

## State and Persistence Behavior

The enum is immutable process-local state. It does not persist anything and has no external side effects. The `policy` strings come from Hadoop option constants and are used for display and option propagation.

## Dependencies and Integration Points

It depends on `Options.OpenFileOptions` read-policy constants, `Constants.INPUT_FADV_NORMAL`, Java collections/locales, and `@Nullable`. `S3AFileSystem.initialize` uses it to parse `fs.s3a.experimental.input.fadvise`/default read policy. `OpenFileSupport` and read contexts propagate selected policies into S3A input streams. `S3AInputStream` checks `isAdaptive` and policy value to decide when to switch from normal sequential-like range requests to random range requests.

## Risks and Edge Cases

`getPolicy` assumes `name` is non-null; callers must supply a real string. Unknown mandatory open options need validation elsewhere because this enum silently returns the fallback. Many format-specific names currently collapse to either random or sequential, so adding a new format-specific strategy later could change performance behavior. `Normal` is adaptive and initially treated like sequential by the stream, switching to random after backward seek or unbuffer; this distinction is important when interpreting `isRandomIO`.

## Test Signals

Tests should cover every public read-policy constant, case and whitespace normalization, fallback behavior for unknown names, null fallback returning null, first-supported selection order, and the adaptive/random/sequential boolean flags. Integration tests should verify that filesystem defaults and open-file options choose the expected stream request-limit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AInputPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AInputStream.java

## Purpose

`S3AInputStream` is the classic S3A object input stream. It implements Hadoop seekable, positioned, readahead, unbuffer, vectored-read, and IO-statistics stream behavior over S3 range GET requests. Its core job is to turn file-position reads into efficient and recoverable HTTP range reads while tracking object version changes and deciding when to drain or abort underlying AWS response streams.

## Important APIs, Types, and Functions

The class extends `ObjectInputStream` and implements `CanSetReadahead` plus stream capabilities. Constructor state comes from `ObjectReadParameters` and `S3AReadOpContext`. Public methods include `seek`, `getPos`, `read()`, `read(byte[], int, int)`, `readFully`, `readVectored` overloads, `close`, `resetConnection`, `available`, `remainingInFile`, `remainingInCurrentRequest`, `setReadahead`, `getReadahead`, `unbuffer`, `hasCapability`, and test accessors `isObjectStreamOpen` and `getWrappedStream`.

Important internals include `reopen`, `lazySeek`, `seekInStream`, `closeStream`, `onReadFailure`, `streamReadResultNegative`, `calculateRequestLimit`, `validateReadahead`, vectored helpers `readSingleRange`, `readCombinedRangeAndUpdateChildren`, `populateChildBuffers`, `drainUnnecessaryData`, `populateBuffer`, `readByteArray`, `getS3ObjectInputStream`, and `getS3Object`. The stream tracks `pos`, `nextReadPos`, `contentRangeStart`, `contentRangeFinish`, `wrappedStream`, `closed`, `fileLength`, `readahead`, `ChangeTracker`, `asyncDrainThreshold`, and `stopVectoredIOOperations`.

## Control Flow

Sequential reads are lazy-seek based. `seek` only validates and records `nextReadPos`. On `read`, the stream calls `lazySeek`, which uses the read invoker to run `seekInStream` and reopen as needed. `seekInStream` may skip forward within the current HTTP response if the target is within the forward seek limit; otherwise it closes the current response and positions for a new range GET. Backward seek records statistics and switches adaptive `Normal` policy to `Random`. `reopen` closes any existing object stream, computes a range limit with `calculateRequestLimit`, builds a GET request with change-tracker constraints, opens the AWS response through callbacks, processes the response for change detection, and updates range/position state.

`read()` and `read(byte[], int, int)` both check closure and EOF, perform lazy seek, then use retry logic around the wrapped stream read. HTTP EOF/channel or timeout failures close the current stream for recovery and rethrow so the invoker can retry. Positive reads advance `pos` and `nextReadPos`, update stream and filesystem byte counters, and complete read-operation statistics. Negative results close the wrapped stream so the next read can reopen if needed. `readFully` synchronizes the whole positioned-read sequence, seeks to the requested offset, repeatedly reads until full, and seeks back to the original position in a finally block.

Close and unbuffer are connection-management paths. `close` marks the stream closed, stops vectored IO, closes or aborts the current response, closes callbacks, and then calls superclass close. `closeStream` decides whether to abort or drain based on `forceAbort`, remaining bytes in the current request, configured readahead, and async drain threshold. Small drains or blocking calls run inline; larger soft closes can submit an async `SDKStreamDrainer`.

Vectored reads validate/sort ranges, attach futures to every `FileRange`, close the normal stream, switch adaptive policy to random, then submit either one task per disjoint range or merged combined-range tasks. Combined reads fetch a larger range once, drain bytes between child ranges, allocate/populate child buffers, and complete each range future. Single-range reads GET just the requested range and fill the caller-allocated buffer. Vectored work checks `stopVectoredIOOperations` so close or unbuffer can interrupt active tasks.

## State and Persistence Behavior

The stream persists no filesystem data; all state is transient client-side read state. `pos` is the current wrapped-stream position, while `nextReadPos` is the logical position requested by Hadoop APIs. `contentRangeStart` and `contentRangeFinish` describe the active S3 range request. `wrappedStream` is the live AWS `ResponseInputStream<GetObjectResponse>` or null. `ChangeTracker` carries expected object version/etag constraints across GETs and detects remote changes. Statistics are accumulated into the stream statistics and merged through superclass/callback lifecycle.

`Normal` input policy starts sequential-like by requesting to object end, then becomes `Random` after backward seek or unbuffer. `Random` range limits use max(request length, readahead), capped at object length. `Sequential` and `Normal` range limits read to object end. Readahead is validated as non-negative and defaults when null.

## Dependencies and Integration Points

The stream depends on `ObjectInputStream` callbacks for building GET requests, obtaining objects, submitting async drain work, and closing audit/client resources. It uses AWS SDK `GetObjectRequest`, `GetObjectResponse`, and `ResponseInputStream`; Hadoop `FileRange`, `StreamCapabilities`, `CanSetReadahead`, `VectoredReadUtils`, and positioned-read validation; S3A `S3AReadOpContext`, `S3AInputPolicy`, `ChangeTracker`, `Invoker`, statistics classes, and range-formatting helpers. It is constructed by `S3AFileSystem` through `S3AStore.readObject` using object attributes and read context created during open.

## Risks and Edge Cases

The stream's synchronization protects normal read/seek state, but vectored range tasks run asynchronously and interact with close/unbuffer through an atomic stop flag; a new vectored read after unbuffer can reset the flag, so termination of older operations is not guaranteed by the code comment. Read failures before `wrappedStream` is reset can lead to retries with a null stream, handled explicitly by reopening in the retry block. EOF can mean real file end or a broken network response; some paths downgrade EOF to `-1` and others throw `EOFException`, so callers see different behavior depending on API.

Large unread response ranges are aborted rather than drained; smaller ones may be drained to preserve connection reuse, which affects latency and connection-pool behavior. `available` and remaining calculations depend on local position state and object length. Direct buffers in vectored reads use a temporary byte array path, while heap buffers assume array-backed buffers. Vectored reads do not attempt recovery while filling or draining a combined range; failures complete affected futures exceptionally. Change tracking can raise remote-file-changed exceptions when S3 responses do not match expected etag/version.

## Test Signals

Unit tests should cover `calculateRequestLimit` for all policies, null/negative readahead validation, lazy seek without immediate GET, forward seek skip versus reopen, backward seek adaptive switch, EOF handling at and beyond object length, read retry recovery after simulated socket timeout/HTTP EOF, close-stream drain versus abort thresholds, resetConnection behavior, close idempotence, unbuffer policy switch and stop flag, and capability reporting for readahead/unbuffer/IO statistics.

Vectored tests should cover empty ranges, disjoint ranges, merged ranges with draining between children, direct and heap buffers, interruption by close/unbuffer, exceptional futures on GET/read failure, range validation against known file length, byte/statistics accounting, and change-tracker failures. Integration tests should validate that filesystem open options and file statuses flow into stream contexts and produce expected S3 range headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AInputStream.java -->
