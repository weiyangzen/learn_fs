# subset-b-008200 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-putobject_test.go -->
# sources/object-store/minio/cmd/object-api-putobject_test.go

## Purpose
This test file validates the lower-level `ObjectLayer.PutObject` behavior across MinIO's single-node and erasure-coded test backends. It focuses on object write correctness, request body integrity, bucket/object validation, degraded disk behavior, stale temporary file cleanup, multipart cleanup, and PUT performance benchmarks.

## Important APIs, types, and functions
- `md5Header` builds object metadata containing an expected ETag.
- `TestObjectAPIPutObjectSingle` delegates to `ExecExtendedObjectLayerTest` so the same `testObjectAPIPutObject` table runs against the supported object layer implementations.
- `testObjectAPIPutObject` is the main table-driven correctness test. It creates buckets, constructs `PutObjReader` instances through `mustGetPutObjReader`, calls `obj.PutObject`, and compares exact expected errors and returned ETags.
- `TestObjectAPIPutObjectDiskNotFound` and `testObjectAPIPutObjectDiskNotFound` exercise erasure writes with disks removed, first below and then beyond write quorum.
- `TestObjectAPIPutObjectStaleFiles` and `TestObjectAPIMultipartPutObjectStaleFiles` verify `.minio.sys/tmp` cleanup after normal and multipart object writes.
- The benchmark functions call shared helpers such as `benchmarkPutObject` and `benchmarkPutObjectParallel` for sizes from very small payloads through 50 MiB and for FS/erasure backends.

## Control flow
The main table creates one valid bucket and one unused bucket, then runs invalid bucket names, invalid object names, missing buckets, bad MD5, bad SHA256, size mismatch, valid small/empty/5 MiB payloads, arbitrary metadata, valid combined checksum cases, invalid checksum cases, directory-marker objects with trailing slash, and an invalid CRC32 metadata case. Each case constructs a `PutObjReader` with declared size and checksum expectations, then calls `obj.PutObject` with `ObjectOptions{UserDefined: inputMeta}`.

The disk-not-found test removes four disks in a 16-disk erasure setup and expects writes to continue, then removes one additional disk and expects `errErasureWriteQuorum`. The stale-file tests write a regular object or complete multipart upload and inspect each disk's `minioMetaTmpBucket`, ignoring `.trash`, to ensure no temporary write artifacts remain.

## State and persistence behavior
The tests mutate real test object layer storage: buckets are created, objects and multipart parts are written, disks may be removed with `os.RemoveAll`, and backend temp directories are inspected directly. The table expects persistence-layer checksum and length validation to be enforced during streaming reads, not merely by handler pre-validation. Cleanup tests specifically protect the invariant that successful object writes do not leave stale files under `.minio.sys/tmp`.

## Dependencies and integration points
The file depends on MinIO's test harness helpers (`ExecExtendedObjectLayerTest`, `ExecObjectLayerDiskAlteredTest`, `ExecObjectLayerStaleFilesTest`, `mustGetPutObjReader`), object layer interfaces, `hash` errors, MinIO internal I/O errors, `humanize` sizing constants, and object metadata conventions such as `etag`. It integrates directly with erasure quorum behavior and multipart upload APIs (`NewMultipartUpload`, `PutObjectPart`, `CompleteMultipartUpload`).

## Risks and edge cases
The tests compare some errors by direct equality and others with `errors.Is`, so wrapped errors in the main PutObject table could cause brittle failures. Temp cleanup checks are storage-layout-aware and could need updates if `.minio.sys/tmp` internals change. The invalid CRC32 case currently expects success, which documents that this lower object-layer path does not reject that metadata shape in the same way the HTTP handler might.

## Test signals
Coverage is strong for object-layer PUT validation, degraded erasure writes, and temporary artifact cleanup. It does not exercise the HTTP `PutObjectHandler` authentication, encryption, object lock, replication, or lifecycle paths; those are handler-level responsibilities in `object-handlers.go`.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-putobject_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-utils.go -->
# sources/object-store/minio/cmd/object-api-utils.go

## Purpose
This file contains shared object API utilities used by MinIO handlers and object-layer code. It covers bucket and object name validation, path joining optimized for object paths, metadata cleanup, multipart ETag synthesis, compression eligibility and S2 compression helpers, object size interpretation for compressed/encrypted data, range translation, GET reader construction, PUT reader wrapping, and disk-space checks.

## Important APIs, types, and functions
- Constants define internal buckets and prefixes such as `.minio.sys`, multipart metadata, temporary metadata, compression thresholds, and compression padding.
- `IsValidBucketName`, `IsValidObjectName`, `IsValidObjectPrefix`, and `checkObjectNameForLengthAndSlash` enforce S3-compatible and filesystem-safe names, with Windows-specific invalid character handling.
- `pathJoin`, `pathJoinBuf`, `pathNeedsClean`, `retainSlash`, and `pathsJoinPrefix` provide low-allocation path operations while preserving significant trailing slashes.
- `getCompleteMultipartMD5`, `cleanMetadata`, `removeStandardStorageClass`, `cleanMetadataKeys`, and `extractETag` normalize metadata and S3 multipart ETag behavior.
- `ObjectInfo.IsCompressed`, `IsCompressedOK`, and `GetActualSize` interpret persisted metadata and part metadata for compressed and encrypted objects.
- `excludeForCompression`, `isCompressible`, `hasStringSuffixInSlice`, and `hasPattern` implement the compression policy.
- `getPartFile`, `partNumberToRangeSpec`, and `getCompressedOffsets` map logical parts/ranges to on-disk part files and compressed offsets.
- `GetObjectReader`, `NewGetObjectReaderFromReader`, and `NewGetObjectReader` wrap object readers with precondition, decryption, decompression, range, and cleanup semantics.
- `PutObjReader`, `NewPutObjReader`, `WithEncryption`, `MD5CurrentHexString`, and `RawServerSideChecksumResult` preserve original checksums while allowing encrypted writes.
- `newS2CompressReader` streams S2 compression through a pipe and optionally returns a seek index; `compressSelfTest` validates compression/decompression at startup.
- `getDiskInfos` and `hasSpaceFor` aggregate disk capacity and enforce write-space constraints.

## Control flow
Validation helpers reject dangerous path components, invalid UTF-8, double slashes, null bytes, overlong object names, and Windows-only forbidden characters. `pathJoinBuf` writes path segments into a pooled byte buffer, checks whether `path.Clean` is needed, and preserves the last argument's trailing slash when required.

`NewGetObjectReader` first evaluates any precondition callback, derives a range from a part number if necessary, detects encryption and compression metadata, and then returns a closure plus storage offset and length. For compressed objects it may translate decompressed ranges into compressed storage offsets with `getCompressedOffsets`, decrypt compressed indices when needed, attach a block decrypter, S2 reader, skip/limit logic, and optional readahead. For encrypted-only objects it computes encrypted read ranges and wraps the input reader in DARE decryption before limiting to the logical range. For plain objects it returns the original reader.

`newS2CompressReader` creates an `io.Pipe`, copies the input into an S2 writer in a goroutine, validates the expected original byte count, emits a stripped S2 index for large streams, and propagates copy/close errors through the pipe. `PutObjReader` keeps both the current write reader and raw original reader so ETags and server-side checksum results can be reported for plaintext input even after encryption wrappers are installed.

## State and persistence behavior
Most utilities are stateless, but several encode persistent metadata contracts: compression metadata uses reserved keys for algorithm and actual size; encrypted/compressed metadata may include encrypted compression indexes; storage class `STANDARD` is removed from response metadata; multipart ETags concatenate part MD5s and append the part count. `hasSpaceFor` reads `DiskInfo` from storage APIs and applies cluster-level availability, inode, per-disk free-space, and fill-fraction checks before writes proceed.

## Dependencies and integration points
This file integrates with MinIO object metadata (`ObjectInfo`, `ObjectPartInfo`, `ObjectOptions`), encryption helpers (`crypto`, DARE decryption, metadata encryption), hash readers, HTTP range parsing, compression config, DNS SRV discovery, byte buffer pooling, trie-based part lookup, wildcard MIME matching, readahead, and storage APIs. Handler code in `object-handlers.go` relies on these utilities for PUT/COPY reader setup, GET/HEAD range serving, compression, encryption, and checksum reporting.

## Risks and edge cases
Compression plus encryption range math is sensitive: wrong index decryption, padding, sequence number, or skip calculations can corrupt ranged reads. `concat` uses `unsafe.String` from a byte slice, so future changes must preserve the allocation lifetime assumptions. `newS2CompressReader` runs a goroutine and pipe; callers must close the reader on incomplete streams to avoid resource leaks. `pathNeedsClean` intentionally allows false positives but should not produce false negatives for paths that need cleaning. Disk-space checks are approximate and assume erasure overhead by multiplying size by two.

## Test signals
The paired utility tests cover bucket/object validation, path traversal regression, metadata cleaning, multipart MD5s, compression detection and policy, actual-size derivation, compressed offset mapping, S2 compression/index generation, and path-clean detection. The more complex `NewGetObjectReader` encryption/decompression combinations are indirectly covered through object handler and integration tests rather than direct exhaustive unit tests here.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-utils_test.go -->
# sources/object-store/minio/cmd/object-api-utils_test.go

## Purpose
This file tests and benchmarks the object API utility layer. It validates path joining and concatenation performance, object and bucket validation, Windows path traversal protection, multipart ETag generation, metadata cleanup, compression metadata semantics, compression policy, compressed range offset math, S2 compression reader behavior, and path cleaning detection.

## Important APIs, types, and functions
- `pathJoinOld` and `concatNaive` are baseline implementations used by benchmarks.
- `BenchmarkConcatImplementation`, `BenchmarkPathJoinOld`, and `BenchmarkPathJoin` measure optimized helpers.
- `TestPathTraversalExploit` runs only on Windows and drives a signed HTTP PUT through the API router.
- `TestIsValidBucketName`, `TestIsValidObjectName`, and `TestIsMinioMetaBucketName` cover validation rules.
- `TestGetCompleteMultipartMD5`, `TestRemoveStandardStorageClass`, `TestCleanMetadata`, and `TestCleanMetadataKeys` cover metadata helpers.
- `TestIsCompressed`, `TestExcludeForCompression`, `TestGetActualSize`, `TestGetCompressedOffsets`, `TestS2CompressReader`, and `Test_pathNeedsClean` cover compression-related behavior.

## Control flow
The Windows path traversal regression initializes test config, sends a signed PUT for an object name containing a backslash traversal into `.minio.sys`, then directly inspects erasure disks with `readAllFileInfo` to ensure no backend part was written with that unsafe name. Validation tests use explicit tables of accepted and rejected bucket/object names, including IP-like buckets, uppercase names, dot/dash boundary cases, UTF-8 names, relative-path attempts, double slashes, invalid bytes, and trailing slash object names.

Compression tests construct `ObjectInfo` values with reserved metadata and parts. They confirm known compression algorithms are accepted, unknown algorithms return an error while still indicating compressed metadata is present, actual size can come from metadata or part sums, and missing actual-size evidence is invalid. `TestS2CompressReader` streams empty, small, and large payloads through `newS2CompressReader`, compares output with a standard S2 writer, verifies large-stream indexes, and round-trips decompression.

## State and persistence behavior
Most tests are pure unit tests over in-memory maps, headers, and readers. `TestPathTraversalExploit` is integration-like: it writes through the HTTP stack to a real test erasure object layer and inspects on-disk object metadata. The benchmark tests do not persist state. Compression reader tests exercise goroutine and pipe behavior by fully reading and closing the returned reader before consuming the index callback.

## Dependencies and integration points
The tests use MinIO's object-layer API test harness, auth credentials, signed request helpers, S2 compression package, compression config, crypto metadata keys, trie utilities, and standard `httptest`. They are directly tied to utility functions from `object-api-utils.go` and indirectly to handler/router behavior for the path traversal regression.

## Risks and edge cases
The Windows-only traversal test can silently skip on non-Windows builders, so cross-platform CI must include Windows to retain that signal. Validation tables encode MinIO-specific differences from S3, such as rejecting trailing slash object names in `IsValidObjectName` while lower object-layer tests still allow certain empty directory marker writes. `TestGetActualSize` ignores returned errors in assertions, so it primarily validates sentinel sizes rather than exact error classes.

## Test signals
This file provides strong regression coverage for security-sensitive path handling, metadata normalization, and compression helper behavior. It is less exhaustive for encrypted compressed ranges with populated S2 indexes, direct `NewGetObjectReader` closure behavior, and disk-space checks.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/object-handlers-common.go -->
# sources/object-store/minio/cmd/object-handlers-common.go

## Purpose
This file contains shared HTTP object-handler helpers for conditional request evaluation, ETag normalization, common PUT/COPY/DELETE response headers, and lifecycle-driven batched object version deletion. It centralizes S3 precondition semantics used by GET, HEAD, PUT, CopyObject, and CopyObjectPart handlers.

## Important APIs, types, and functions
- `checkCopyObjectPartPreconditions` delegates to `checkCopyObjectPreconditions`.
- `checkCopyObjectPreconditions` evaluates `x-amz-copy-source-if-*` headers for CopyObject and CopyObjectPart PUT requests.
- `checkPreconditionsPUT` evaluates PUT `If-Match`, `If-None-Match`, and MinIO preserve-ETag/version safeguards.
- `writeHeadersPrecondition` writes common object metadata headers for 304 and 412 responses.
- `checkPreconditions` evaluates GET/HEAD `If-*` headers and part-number validity.
- `ifModifiedSince` performs S3-compatible one-second timestamp precision comparison.
- `canonicalizeETag` and `isETagEqual` normalize quoted ETags and wildcard matching.
- `setPutObjHeaders` writes success headers for PUT/COPY/complete multipart/delete, including version IDs, delete-marker state, lifecycle prediction headers, and checksums.
- `deleteObjectVersions` deletes lifecycle-selected object versions in batches and emits lifecycle audit/events.

## Control flow
Copy preconditions only run for PUT. They skip modtime conditions if object modification time is zero or Unix epoch, write common headers before failure responses, and map failed copy-source conditions to `ErrPreconditionFailed`.

GET/HEAD preconditions first reject invalid requested part numbers when `opts.PartNumber > 1`. They then apply S3 precedence: matching `If-None-Match` returns `304 Not Modified` before considering `If-Modified-Since`; stale `If-Modified-Since` also returns 304; failing `If-Match` returns 412; `If-Unmodified-Since` returns 412 only when `If-Match` is absent. `writeHeadersPrecondition` preserves metadata such as version ID, expiry, and cache-control on conditional responses.

PUT preconditions skip non-PUT/POST methods, zero/epoch modtimes, and delete markers. They fail on mismatched `If-Match`, matching `If-None-Match`, or an exact match of `opts.PreserveETag` and `opts.VersionID`, preventing redundant or conflicting writes.

`deleteObjectVersions` chunks lifecycle deletes by `maxDeleteList`, reads bucket versioning state, calls `ObjectLayer.DeleteObjects`, emits lifecycle audit logs, and sends delete events with per-object error response details when necessary.

## State and persistence behavior
Precondition helpers do not mutate object storage, but they write response headers and status codes, and their boolean return value controls whether handlers proceed to read or write persistent object data. `setPutObjHeaders` exposes persisted object state such as ETag, version ID, delete-marker flag, lifecycle predictions, and decrypted checksums. `deleteObjectVersions` directly mutates storage by deleting object versions through `ObjectLayer.DeleteObjects`.

## Dependencies and integration points
The helpers depend on `ObjectInfo`, `ObjectOptions`, MinIO error mapping, HTTP constants, lifecycle and event systems, object versioning configuration, checksum decryption, and audit logging. `object-handlers.go` uses these functions in GET, HEAD, PUT, COPY, DELETE, object lock, and metadata update paths.

## Risks and edge cases
S3 conditional precedence is subtle; reordering checks can change compatibility. Timestamp comparison intentionally rounds with `givenTime.Add(1 * time.Second)` to account for HTTP date precision. `isETagEqual` treats right-side `*` as wildcard, which is correct for headers but should not be reused for arbitrary ETag equality without considering that behavior. `deleteObjectVersions` assumes `lcEvent` aligns with `toDel` indexes across batching.

## Test signals
The paired test file covers ETag canonicalization and important `If-None-Match`/`If-Modified-Since` plus `If-Match`/`If-Unmodified-Since` precedence. Copy-source preconditions, PUT preconditions, response checksum headers, and lifecycle deletion batching are not directly tested here.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/object-handlers-common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/object-handlers-common_test.go -->
# sources/object-store/minio/cmd/object-handlers-common_test.go

## Purpose
This test file verifies selected shared object-handler precondition helpers. It focuses on ETag canonicalization and S3-compatible conditional GET/HEAD precedence for `If-None-Match`, `If-Modified-Since`, `If-Match`, and `If-Unmodified-Since`.

## Important APIs, types, and functions
- `TestCanonicalizeETag` checks quote stripping behavior for unusual and ordinary ETag strings.
- `TestCheckPreconditions` builds HEAD requests with conditional headers, passes a fixed `ObjectInfo`, and asserts both the boolean "request should stop" result and the recorded HTTP status code.

## Control flow
The first test table in `TestCheckPreconditions` covers cases where `If-None-Match` matches or `If-Modified-Since` indicates no modification. The expected outcome is `true` with HTTP 304. The second table covers cases where `If-Match` succeeds while `If-Unmodified-Since` would otherwise be problematic; the expected outcome is to proceed with no status override, leaving the recorder at its default 200.

## State and persistence behavior
The tests are pure HTTP helper tests. They use `httptest.NewRecorder`, in-memory requests, and a fixed `ObjectInfo{ETag: "aa", ModTime: ...}`. No object layer or persistent storage is touched.

## Dependencies and integration points
The file depends on `checkPreconditions`, `canonicalizeETag`, `ObjectInfo`, `ObjectOptions`, and MinIO HTTP header constants. It protects behavior that GET and HEAD handlers in `object-handlers.go` rely on before serving object bytes or headers.

## Risks and edge cases
The tests cover only a subset of conditional behavior. They do not validate failing `If-Match`, failing `If-Unmodified-Since` when `If-Match` is absent, part-number validation, copy-source preconditions, or PUT preconditions. The chosen timestamp is fixed and tests the one-second HTTP date precision behavior indirectly.

## Test signals
The file gives focused regression signal for the conditional precedence that is easy to break during refactoring. Broader handler-level tests are still needed for complete S3 compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/object-handlers-common_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/object-handlers.go -->
# sources/object-store/minio/cmd/object-handlers.go

## Purpose
This file implements MinIO's HTTP object API handlers for S3 object operations: SelectObjectContent, GET, HEAD, GetObjectAttributes, COPY, PUT, Snowball-style archive extract, DELETE, object legal hold, retention, tagging, and restore of transitioned objects. It is the integration layer between HTTP/auth/policy semantics and persistent object-layer operations.

## Important APIs, types, and functions
- `setHeadGetRespHeaders` maps supported presigned response override query parameters to response headers.
- `SelectObjectContentHandler` evaluates S3 Select requests over object content using ranged read-seek closures.
- `getObjectHandler`, `GetObjectHandler`, `headObjectHandler`, `HeadObjectHandler`, and `getObjectAttributesHandler` serve object bytes, metadata, ranges, part metadata, checksums, and conditional responses.
- `getCpObjMetadataFromHeader`, `CopyObjectHandler`, remote instance transport/client helpers, and federation checks implement local and federated copy behavior.
- `PutObjectHandler` implements normal PUT object upload with auth, signature verification, checksums, quota, compression, encryption, object lock, replication, lifecycle transition, and event handling.
- `PutObjectExtractHandler` ingests a tar stream and writes extracted entries as individual objects.
- `DeleteObjectHandler` deletes objects or creates delete markers, with object lock retention bypass and delete replication decisions.
- `Put/GetObjectLegalHoldHandler` and `Put/GetObjectRetentionHandler` mutate/read object lock metadata through `PutObjectMetadata`.
- `ObjectTagSet`, `objectTagging`, and tagging handlers manage object tag XML and metadata replication.
- `PostRestoreObjectHandler` validates restore XML, updates restore metadata, and starts background restoration from transitioned storage.

## Control flow
All public handlers create request context, defer audit logging, resolve `ObjectLayer`, decode mux bucket/object variables, authenticate/authorize required policy actions, build operation-specific `ObjectOptions`, and translate internal errors to S3 XML or headers-only responses.

GET and HEAD reject invalid SSE request headers, parse ranges and part numbers, install precondition callbacks, authorize using object tags after fetching metadata, optionally proxy missing/read-quorum objects to replication targets, apply lifecycle expiry locally, filter object lock metadata based on permissions, decrypt object info, emit encryption/checksum/parts headers, apply response header overrides, and send events. GET streams `GetObjectReader` to the response and only writes an error if no data has been sent.

COPY parses and validates `x-amz-copy-source`, source/destination permissions, metadata and tag directives, storage class, bucket encryption defaults, source and destination options, preconditions, source reader acquisition, maximum size, quota, optional recompression, source/target encryption conversion or key rotation, checksum inheritance/recalculation, tag and object-lock metadata, replication metadata, remote federation, and finally `ObjectLayer.CopyObject` or minio-go remote `PutObject`.

PUT validates headers, content length, object size, metadata, tags, authorization, streaming signature mode, SHA256 and MD5 expectations, replication permission checks, quota, bucket encryption defaults, compression, server-side checksums, conditional write callbacks, object lock defaults, replication status, encryption, sensitive metadata removal, tier sweeper setup, and `ObjectLayer.PutObject`. It then writes ETag/encryption/version/checksum headers, emits creation and many-version events, schedules replication and lifecycle transition, and sweeps overwritten transitioned objects.

DELETE builds delete options, blocks force delete on object-lock buckets, configures replication and retention-bypass callbacks, calls `ObjectLayer.DeleteObject`, handles not-found as a successful no-op with event emission, writes delete marker/version headers, schedules delete replication, and sweeps transitioned state.

Object lock and tagging handlers mostly read or mutate metadata while preserving S3 authorization, version ID, replication timestamp/status, and event semantics. Restore updates restore metadata via metadata-only self-copy, returns immediately, and performs actual restore or select restore asynchronously.

## State and persistence behavior
This file is heavily stateful through the object layer. PUT, COPY, archive extract, DELETE, legal hold, retention, tagging, and restore metadata paths all mutate object data or object metadata. Metadata keys drive persistent compression state, actual size, encryption state, object lock retention/legal hold, replication status/timestamps, restore status, storage class, and checksums. Object sweepers remove replaced transitioned objects after successful writes/deletes. Restore launches background work with `GlobalContext`, and replication scheduling queues asynchronous object or delete replication.

## Dependencies and integration points
The handlers integrate with mux routing, MinIO auth and policy systems, bucket encryption config, KMS/SSE-C/SSE-S3/SSE-KMS helpers, hash and checksum readers, object lock, lifecycle, replication, DNS federation, minio-go remote clients, S3 Select, tar extraction, tiering/transition, event notification, audit logging, and shared helpers from `object-api-utils.go` and `object-handlers-common.go`.

## Risks and edge cases
Wrapper ordering around hashing, compression, encryption, ETag sealing, and checksum propagation is critical; a misplaced wrapper can validate the wrong byte stream or leak incorrect ETags. Conditional request semantics depend on callbacks being run after object metadata is available but before data is streamed or overwritten. Several paths mutate `ObjectInfo.UserDefined` maps in place, so unintended aliasing can leak source metadata into destination metadata. GET/HEAD proxy fallback must preserve S3 error compatibility for anonymous requests and missing keys. Restore starts goroutines that must avoid writing to the original response after it has returned; select-restore handling is especially delicate. Object lock and replication metadata timestamp comparisons determine whether incoming replica metadata overwrites local state.

## Test signals
Direct tests in this subset cover object-layer PUT behavior and shared utility/precondition behavior, not this whole handler file. Existing signals include path traversal through the HTTP PUT router, conditional precondition tests, compression utility tests, stale temporary file tests, and object-layer quorum tests. Handler-specific areas needing broader tests include encryption plus compression PUT/COPY, metadata-only copy/key rotation, object lock metadata replication, tag proxying, transitioned-object restore, and anonymous error compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/object-handlers.go -->
