# subset-b-007877 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy.go

Purpose: implements S3 CopyObject and UploadPartCopy for SeaweedFS, including metadata/tag directive handling, version-aware source and destination resolution, remote-only source caching, conditional request checks, chunk copy, inline object copy, ETag preservation, and server-side encryption transitions. It is the main orchestration file for object copy behavior in the S3 gateway.

Important APIs and types include `CopyObjectHandler`, `CopyObjectPartHandler`, `CopyPartResult`, `resolveDestinationMime`, `processMetadataBytes`, `mergeCopyMetadata`, `copyChunks`, `copyChunksForRange`, `copySingleChunk`, `copySingleChunkForRange`, `downloadChunkData`, `uploadChunkData`, SSE-C/KMS/S3 copy helpers, and inline encryption helpers. `copyEntryETag` prefers stored S3 ETag metadata over a recomputed filer ETag, which is important for multipart ETags and conditional copy semantics.

Control flow in `CopyObjectHandler` validates source and destination, directives, IAM source access, versioning state, source lookup, remote-only caching, self-copy rules, source and destination conditionals, and encryption headers. It then chooses a metadata-only self-copy, inline copy, or chunked copy through `executeUnifiedCopyStrategy`, merges processed metadata, and finalizes the destination under an object write lock. `finalizeCopyDestination` persists either a new version file plus latest pointer, a suspended null version, or a normal object entry. Failed version pointer updates roll back the just-created version file.

`CopyObjectPartHandler` validates upload and part numbers, resolves versioned source entries, caches remote-only data, parses `x-amz-copy-source-range`, loads the multipart upload entry, and chooses either the SSE/checksum slow path or the raw chunk-copy fast path. Fast path parts are written under `.uploads/<uploadID>/<part>.part`; destination volume assignment uses the filer path, not the S3 request URI, so bucket collection routing remains correct.

State and persistence behavior centers on filer entries, `Extended` metadata, chunk records, `.versions` directories, multipart `.uploads`, and volume server data. The file assigns destination volumes, downloads source chunk bytes or streams them, uploads destination chunks, updates chunk file IDs, and records encryption metadata at object and chunk level. It also cleans versioning metadata when copying to non-versioned or suspended buckets.

Dependencies include `filer_pb`, `operation`, `filer`, `util/http`, `s3_constants`, `s3err`, security JWT helpers, object-lock/versioning helpers elsewhere in the package, and SSE/KMS utilities. Integration points include IAM (`AuthorizeCopySource`), bucket metadata default encryption, distributed object write locks/routed owner operations, remote tier caching, volume lookup and assignment, `putToFiler` via the SSE part-copy file, metrics/logging, and S3 XML response generation.

Risks are concentrated in encryption metadata correctness, range math, memory pressure on large chunks, versioned destination atomicity, path normalization, and metadata/tag merge semantics. Several branches intentionally preserve per-chunk SSE metadata for same-key copies and force decrypt/reencrypt when encryption context, bucket-key state, or destination encryption changes. The code still buffers chunks for SSE transformations, so large encrypted multipart copy remains memory-sensitive. Test signals in companion files cover allocation bounds, upload buffer isolation, bucket collection path routing, ETag conditionals, checksum result XML, and metadata directive edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_alloc_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_alloc_test.go

Purpose: regression-tests `downloadChunkData` allocation behavior for large server-side copy chunks. It specifically protects the fix for issue #6541, where appending streamed chunks to a nil slice caused geometric growth and roughly doubled memory allocation for each copied chunk.

Important API coverage is `TestDownloadChunkData_AllocationBound`, which initializes the global HTTP client, serves a 16 MiB payload through `httptest.Server`, warms up client/pool state, measures `runtime.MemStats.TotalAlloc` around a second download, and checks both byte-for-byte correctness and allocation budget.

Control flow builds deterministic payload bytes, writes them from the fake volume server in 64 KiB chunks with flushes, invokes `S3ApiServer.downloadChunkData`, compares the returned bytes after measurement, and fails if total allocation exceeds 1.5 times the payload size. The test intentionally measures after warmup and before `bytes.Equal` so validation work does not pollute allocation accounting.

State and persistence are in-memory only: a local HTTP server, global HTTP client initialization, GC-triggered runtime memory stats, and the returned byte slice. There is no filer or volume persistence.

Dependencies include `runtime`, `httptest`, `util_http.InitGlobalHttpClient`, and the implementation's global HTTP client. The integration signal is performance rather than API response behavior: it pins the implementation's pre-sized receive buffer contract.

Risks include allocator noise across Go versions or environments, but the bound is loose enough to distinguish the intended preallocated path from the old geometric append path. This test does not cover encrypted-chunk HEAD-size adjustment or retry behavior; it focuses narrowly on heap growth during normal streaming download.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_alloc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_bench_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_bench_test.go

Purpose: benchmarks buffered versus streaming chunk-copy paths. It documents and measures the expected performance and allocation difference between `downloadChunkData` plus `uploadChunkData` and the `io.Pipe`-based `streamCopyChunkRange`.

Important APIs and helpers are `benchEnv`, `newBenchEnv`, `neturl`, `BenchmarkCopyChunk_Buffered`, `BenchmarkCopyChunk_Streamed`, and `humanByteName`. The fake source volume serves deterministic payload bytes and honors `Range`; the fake destination volume parses multipart upload bodies and verifies SHA-256 content integrity.

Control flow creates test servers per payload size, configures an `AssignVolumeResponse` pointing at the fake destination, initializes the global HTTP client, then runs benchmarks for 1 MiB, 8 MiB, and 64 MiB payloads. The buffered benchmark downloads the full chunk into memory and uploads it. The streamed benchmark calls `streamCopyChunkRange` with `isFullChunk=true` to exercise multipart pipe forwarding without a chunk-sized S3-side buffer.

State and persistence are local to benchmark servers and heap allocations. The destination server discards bytes after hashing; no filer state is used. The `AssignVolumeResponse` models the minimum volume assignment shape needed by upload code.

Dependencies include Go's benchmark framework, `httptest`, `multipart`, `sha256`, `filer_pb.AssignVolumeResponse`, and `util_http`. This file integrates with the copy implementation as a performance harness and compile-time sanity check that the standard multipart package remains available.

Risks and test signals: these are benchmarks, not pass/fail correctness tests except for benchmark fatal assertions. They are useful for detecting allocation regressions or throughput changes in streaming copy, but they do not exercise SSE, compression headers, destination auth failures, or real SeaweedFS volume servers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_bench_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_checksum_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_checksum_test.go

Purpose: unit-tests UploadPartCopy checksum propagation and XML response fields. It ensures multipart upload checksum configuration stored on the upload entry is replayed onto the fake put request and that copy-part responses expose the correct checksum element.

Important coverage includes `TestApplyDestChecksumHeaderToCopyRequest`, `TestUploadEntryHasChecksum`, and `TestBuildCopyPartResult`. These target `applyDestChecksumHeaderToCopyRequest`, `uploadEntryHasChecksum`, checksum algorithm detection, and `buildCopyPartResult`.

Control flow creates filer entries with `ExtChecksumAlgorithm`, applies checksum headers to synthetic PUT requests, then verifies `detectRequestedChecksumAlgorithm` sees the intended algorithm and header. It also checks nil entries, empty entries, and unknown algorithms do not produce false positives. The XML response test iterates over CRC32, CRC32C, CRC64NVME, SHA1, SHA256, and unknown headers, comparing struct fields and encoded XML snippets.

State and persistence are pure in-memory request headers and `filer_pb.Entry.Extended` metadata. No network, filer, or volume server is involved.

Dependencies include `s3_constants`, `s3err.EncodeXMLResponse`, checksum helper functions defined elsewhere in the package, and `SSEResponseMetadata`. Integration point is the slow UploadPartCopy path in `copyObjectPartViaReencryption`, where checksum headers are staged before calling `putToFiler`.

Risks: these tests validate header translation and response shape but not end-to-end checksum computation on uploaded bytes. They are still important because missing checksum staging causes multipart complete failures for checksum-enabled uploads copied through UploadPartCopy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_checksum_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_chunk_upload_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_chunk_upload_test.go

Purpose: protects chunk-copy upload memory behavior and concurrency safety. It verifies `newChunkUploadOption` always supplies a private pre-sized `BytesBuffer`, bypassing the package-global bytebufferpool that previously retained large multipart buffers under UploadPartCopy load.

Important APIs covered are `TestNewChunkUploadOption_AvoidsBytePool` and `TestNewChunkUploadOption_PerCallIsolation`. They exercise `newChunkUploadOption`, `multipartFramingOverhead`, `UploadOption.BytesBuffer`, `UploadOption.Cipher`, and destination URL/JWT setup through an `AssignVolumeResponse`.

Control flow iterates over empty, small, 8 MiB, and 64 MiB chunks. For each, it builds an upload option and asserts that `BytesBuffer` is non-nil, has at least `len(chunkData)+multipartFramingOverhead` capacity, starts empty, and has `Cipher=false` because chunk-copy bytes are already encrypted when the source had a cipher key. The isolation test calls the helper twice and asserts distinct buffers, preventing accidental sharing across concurrent uploads.

State and persistence are limited to allocated buffers and upload option structs. No HTTP upload is performed.

Dependencies include `filer_pb.AssignVolumeResponse` and `operation.UploadOption` returned by the implementation. Integration point is `uploadChunkData`, which passes this option into `operation.NewUploader().UploadData`.

Risks: this test does not validate multipart wire format or upload success; the benchmark file and stream-copy code cover that separately. Its core signal is preventing a regression to global pooled buffers and preventing shared mutable buffer state in concurrent copy operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_chunk_upload_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_collection_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_collection_test.go

Purpose: regression-tests destination path selection for server-side copy volume assignment. It ensures copied bytes are assigned under the destination bucket's filer path so the filer maps them to the bucket collection instead of the default collection.

Important coverage is `TestCopyDestinationPathResolvesBucketCollection`, which exercises `S3ApiServer.bucketDir`, `copyPartLocation`, and `filer.Filer.DetectBucket` with a bucket root at `/buckets`.

Control flow first proves the S3 request URI shape (`/bucket/key`) does not resolve to a bucket collection. It then builds an UploadPartCopy part path under `.uploads` and a CopyObject destination object path under `/buckets/<bucket>/...`, asserting both resolve to the expected bucket.

State and persistence are in-memory path strings and a lightweight `filer.Filer` value. No filer RPCs or volume assignments are performed.

Dependencies include `filer.Filer`, `util.FullPath`, and the S3 API server bucket path option. The integration point is `assignNewVolume`, which receives `dstPath`; passing `r.URL.Path` here would silently place copied chunks into the wrong collection.

Risks: the test is path-level only and does not prove a real assign-volume RPC respects collection placement, but it pins the critical precondition used by filer collection detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_collection_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_etag_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_etag_test.go

Purpose: verifies copy ETag semantics, especially for multipart objects whose S3 ETag is stored in extended metadata and cannot be recovered from the file's MD5 alone.

Important coverage includes `TestCopyEntryETagPrefersStoredExtendedETag`, `TestCopyEntryETagFallsBackToFilerETag`, `TestValidateConditionalCopyHeadersUsesStoredExtendedETag`, and helper `newCopyETagTestEntry`.

Control flow builds synthetic filer entries with attributes and optional `ExtETagKey`. It asserts `copyEntryETag` returns stored extended ETags when present and falls back to `filer.ETagEntry`/MD5-derived values otherwise. Conditional header tests create copy requests with `X-Amz-Copy-Source-If-Match` and `If-None-Match`, proving the source conditional path compares against the stored S3 ETag.

State and persistence are in-memory filer entries and HTTP request headers. The stored ETag lives in `Entry.Extended`, while the fallback MD5 lives in `Entry.Attributes.Md5`.

Dependencies include `s3_constants.ExtETagKey`, `s3err`, `httptest`, and a test helper for decoding MD5 hex. Integration point is both CopyObject and UploadPartCopy conditional validation, plus `finalizeCopyDestination`, which stores the destination ETag.

Risks: tests do not create real multipart objects, but they isolate the core correctness property: do not recompute or lose multipart ETags during copy or conditional matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_etag_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_mime_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_mime_test.go

Purpose: tests CopyObject metadata directive behavior for MIME type, system headers, user metadata, and tags. It protects S3 compatibility for COPY versus REPLACE semantics and backward compatibility with legacy non-canonical metadata keys.

Important coverage includes `TestResolveDestinationMime`, `TestIsValidDirective`, multiple `TestProcessMetadataBytes_*` cases, `TestIsManagedCopyMetadataKey_*`, and `TestMergeCopyMetadata_*`. These directly exercise `resolveDestinationMime`, `isValidDirective`, `processMetadataBytes`, `mergeCopyMetadata`, and `isManagedCopyMetadataKey`.

Control flow covers COPY keeping source MIME regardless of request Content-Type, REPLACE using request Content-Type or `binary/octet-stream`, uppercase-only directive validation, REPLACE dropping stale system/user metadata not re-specified, COPY promoting legacy case variants to canonical system/tag keys, deterministic canonical-wins behavior despite Go map iteration order, and tag replacement dropping old tags while preserving unrelated metadata.

State and persistence are in-memory `http.Header` values and metadata maps. The behavior maps directly to filer `Entry.Attributes.Mime` and `Entry.Extended` fields in `CopyObjectHandler`.

Dependencies include `copyReplaceSystemHeaders`, `s3_constants` through implementation helpers, tag parsing/validation helpers, and Go HTTP header canonicalization. Integration point is metadata construction before destination persistence and metadata-only self-copy updates.

Risks: these tests do not perform a full HTTP CopyObject request, so they do not validate response headers or filer writes. They strongly cover the pure functions where most metadata regressions happen, including stale managed key leakage and legacy casing collisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_mime_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_part_sse.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_part_sse.go

Purpose: implements the UploadPartCopy slow path for destination SSE and multipart checksum cases. It streams source plaintext into the existing `putToFiler` upload pipeline so destination parts receive correct encryption metadata and checksums instead of raw-copying bytes and corrupting reads.

Important APIs include `isTransientFilerError`, `uploadEntryHasSSE`, `uploadEntryHasChecksum`, `sourceEntryHasSSE`, `openSourcePlaintextReader`, `openSSES3SourcePlaintextReader`, `applyRange`, `applyDestSSEHeadersToCopyRequest`, `applyDestChecksumHeaderToCopyRequest`, `fakeContentRequest`, `copyObjectPartViaReencryption`, and `writeEmptyCopyPart`. `errCopySourceSSEUnsupported` marks unsupported SSE-C/SSE-KMS source plaintext extraction for UploadPartCopy.

Control flow begins in `CopyObjectPartHandler` when upload entry SSE/checksum or source SSE is detected. `copyObjectPartViaReencryption` opens a plaintext reader for the requested source range, clones the original request into a fake PUT body, stages destination SSE and checksum headers from the multipart upload entry, and invokes `putToFiler` with a generated part path. Empty copy ranges without checksum are written as zero-byte parts directly.

State and persistence include multipart upload entries under `.uploads`, request headers that carry staged SSE-KMS/SSE-S3 configuration, generated part objects, and response metadata from `putToFiler`. SSE-S3 source reads can use per-chunk metadata through `buildMultipartSSES3Reader` or legacy entry-level metadata fallback. SSE-KMS upload entries require key ID, bucket-key flag, encryption context, and base IV in `Extended`.

Dependencies include gRPC status codes, `filer_pb`, S3 constants/error mapping, SSE-S3/KMS helpers, `getEncryptedStreamFromVolumes`, `createEncryptedChunkReader`, `putToFiler`, and checksum helpers. Integration is intentionally with normal upload code rather than bespoke part-writing so encryption and checksums remain consistent with PutObjectPart.

Risks: SSE-C and SSE-KMS source plaintext extraction in this slow path returns NotImplemented, so some source/destination combinations are explicitly unsupported for UploadPartCopy. Incorrect upload-entry metadata yields internal errors. Range skipping on decrypted streams can be expensive for large offsets. Tests cover checksum staging and SSE detection helpers indirectly, but end-to-end SSE UploadPartCopy requires broader integration coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_part_sse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_stream.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_stream.go

Purpose: provides the memory-efficient raw chunk-copy path used when bytes can be forwarded without transformation. It replaces chunk-sized download and multipart buffers with an `io.Pipe` between source volume GET and destination volume POST.

Important APIs are `canStreamCopyChunk`, `streamCopyChunkRange`, and `shouldLogStreamError`. `canStreamCopyChunk` excludes chunks with `CipherKey` or any SSE type because those require decryption or re-encryption. Compressed chunks are eligible because full-chunk mode can forward gzip wire bytes unchanged.

Control flow in `streamCopyChunkRange` validates size, creates a cancelable child context, builds a source GET with JWT and either `Accept-Encoding: gzip` for full chunks or `Range` for partial chunks, opens an `io.Pipe`, and starts a producer goroutine that writes a multipart form part to the pipe while copying the source response body. The consumer side POSTs that multipart body to the destination volume URL with destination JWT. Errors cancel both legs and close pipe ends to avoid background draining.

State and persistence are mostly transient HTTP streams. Persistent effects occur only when the destination volume accepts the POST and stores the new file ID assigned by the caller. Source response `Content-Encoding` is treated as authoritative and copied into the multipart part only when the actual wire body is gzip.

Dependencies include `filer.JwtForVolumeServer`, `security.EncodedJwt`, global HTTP client helpers, Go `mime/multipart`, and volume server multipart upload semantics mirrored from `operation.upload_content`. Integration points are `copySingleChunk` and `copySingleChunkForRange`, which select this path for raw copy and fall back to buffered copy for transformed bytes.

Risks: the multipart framing must stay compatible with volume server parsing; the compile-time benchmark sanity uses `multipart.NewWriter` but cannot detect protocol drift. Partial ranges of compressed chunks intentionally fetch raw bytes rather than labeled gzip. Network failures must correctly unblock both goroutines, which the child context and pipe error handling address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_stream.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_unified.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_unified.go

Purpose: centralizes copy strategy selection for CopyObject across unencrypted, SSE-C, SSE-KMS, SSE-S3, key-rotation, encrypt, decrypt, and re-encrypt scenarios. It keeps `CopyObjectHandler` from embedding all encryption decision logic inline.

Important APIs are `executeUnifiedCopyStrategy`, `mapCopyErrorToS3Error`, `executeKeyRotation`, `executeEncryptCopy`, `executeDecryptCopy`, `executeReencryptCopy`, and `applyCopyBucketDefaultEncryption`.

Control flow detects encryption state using source entry and request paths, applies destination bucket default encryption when no explicit destination encryption is requested, calls `DetermineUnifiedCopyStrategy`, logs optimized size calculations, and dispatches to direct chunk copy, key rotation, encrypt, decrypt, or re-encrypt helpers. Direct copy uses `copyChunks`; SSE-C and SSE-KMS use their specialized helpers where possible; SSE-S3 and cross-type transitions route to `copyMultipartCrossEncryption`.

State and persistence are delegated to the lower-level copy helpers. This file returns destination chunks plus metadata to be merged into the destination entry. Key rotation may reuse chunks and only update metadata for some SSE-KMS same-key cases, while SSE-C key rotation falls back to re-encryption.

Dependencies include encryption-state detection, copy strategy calculation, bucket metadata lookup, KMS/SSE error mapping, and `weed_server.ErrReadOnly`. `mapCopyErrorToS3Error` maps quota/read-only failures to AccessDenied and known KMS/SSE validation errors to specific S3 codes before defaulting to InternalError.

Risks: correctness depends on `DetermineUnifiedCopyStrategy` and state detection matching actual chunk metadata. Bucket default encryption applied here must mirror inline copy and upload behavior. Strategy mistakes can either corrupt encrypted reads or unnecessarily buffer/re-encrypt large objects. Tests in adjacent files cover some downstream invariants, but this dispatcher itself has no dedicated table test in the listed set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_unified.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_delete.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_delete.go

Purpose: implements S3 DeleteObject and DeleteObjects, including versioned delete markers, suspended null-version behavior, object-lock enforcement, conditional If-Match deletes, routed owner fast paths, per-key authorization for batch delete, audit logging, and delete metrics.

Important APIs and types include `deleteMutationResult`, `ObjectIdentifier`, `DeleteObjectsRequest`, `DeleteError`, `DeleteObjectsResponse`, `validateDeleteObjectIdentifier`, `resolveDeleteConditionalEntry`, `checkDeleteIfMatch`, `deleteVersionedObject`, `deleteUnversionedObjectWithClient`, `DeleteObjectHandler`, and `DeleteMultipleObjectsHandler`.

Control flow for single delete resolves bucket/object/version, validates table-bucket paths, gets versioning state, checks `If-Match`, then tries routed delete paths when safe. Versioned deletes with no version create delete markers; specific version deletes remove the named version; suspended deletes remove the null version and create a null delete marker. If routing is unavailable, mutation happens under `withObjectWriteLock` after rechecking conditions. Successful responses set version/delete-marker headers and return 204.

Batch delete reads XML, enforces the 1000-key limit, validates each object key and version ID, authorizes each key because the route cannot know body keys in middleware, and performs each mutation under a per-object write lock. It records deleted objects unless quiet mode is enabled and accumulates per-key errors instead of aborting the whole request.

State and persistence include filer entries, version files and latest pointers, delete markers, null versions, object-lock metadata, and volume chunk deletion behavior. `deleteUnversionedObjectWithClient` translates `metadataOnly` into `IsDeleteData=false`, allowing lifecycle TTL paths to remove metadata without enqueueing chunk delete RPCs.

Dependencies include `filer_pb`, object version helpers, object lock helpers, IAM batch authorization, routed owner APIs, S3 XML/errors, stats counters, and util path joining. Risks include path traversal through keys or version IDs, stale conditional checks around routed paths, object-lock bypass handling, and consistency between version directory state and visible latest object. Companion tests cover identifier validation, unsafe version rejection, metadata-only delete plumbing, path construction, and traversal rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_delete.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_delete_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_delete_test.go

Purpose: unit-tests delete path safety and low-level unversioned delete request construction. It focuses on traversal prevention and the `metadataOnly` flag's translation to filer delete semantics.

Important coverage includes `TestValidateDeleteObjectIdentifier`, `TestGetSpecificObjectVersionRejectsUnsafeVersionID`, `TestDeleteUnversionedObjectWithClient_MetadataOnlySkipsChunkDelete`, `TestDeleteUnversionedObjectWithClient_FullDeletePreservesIsDeleteData`, `TestDeleteUnversionedObjectWithClient_FullPathFromBucketsRoot`, `TestDeleteUnversionedObjectWithClientRejectsTraversal`, and `TestDeleteUnversionedObjectWithClient_PropagatesEntryAttributesIrrelevant`.

Control flow uses table-driven invalid key/version cases with traversal segments and backslashes, calls version lookup with an unsafe version ID, and uses a fake delete client to inspect generated filer `DeleteEntryRequest` fields. It verifies metadata-only delete clears `IsDeleteData`, normal delete sets it, nested object keys split into directory/name correctly, invalid paths are rejected before RPC, and entry attributes do not influence this helper.

State and persistence are in-memory test server structs and request captures. No real filer mutation occurs.

Dependencies include `testify`, `filer_pb`, `s3err`, `errInvalidVersionID`, and the package test fake `deleteObjectEntryTestClient`. Integration point is the delete handler and lifecycle callers that rely on `deleteUnversionedObjectWithClient`.

Risks: the tests do not cover full HTTP DeleteObject/DeleteObjects, version marker creation, object-lock enforcement, or routed delete branches. They are strong guards for path safety and data-delete flag behavior, which are high-impact failure modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_delete_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_legal_hold.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_legal_hold.go

Purpose: implements S3 Object Lock legal hold GET and PUT handlers. Legal hold is version-aware and only available when object lock prerequisites are met.

Important APIs are `PutObjectLegalHoldHandler` and `GetObjectLegalHoldHandler`. They use package helpers `handleObjectLockAvailabilityCheck`, `parseObjectLegalHold`, `ValidateLegalHold`, `setObjectLegalHold`, `getObjectLegalHold`, and validation-to-S3 error mapping.

Control flow for PUT extracts bucket/object and optional `versionId`, checks object-lock availability, parses XML legal hold configuration from the request body, validates it, writes it through object-lock metadata helpers, sets `x-amz-version-id` when a version was specified, records active bucket time, and returns 200 with no body. GET performs availability checking, fetches the hold configuration, maps not-found and missing-configuration errors to S3 errors, marshals XML, writes XML header and body, and records active bucket time.

State and persistence are delegated to object-lock helpers that store legal hold metadata on object versions or current objects. The handler itself manipulates only HTTP headers/body and metrics.

Dependencies include XML encoding, object-lock errors such as `ErrObjectNotFound`, `ErrVersionNotFound`, and `ErrNoLegalHoldConfiguration`, S3 constants/errors, logging, and stats collection. Integration points are versioning/object lock subsystems and S3 route authorization configured elsewhere.

Risks: malformed XML or validation mistakes map to client errors, while persistence failures map to InternalError. The file does not include explicit tests in this subset; confidence depends on object-lock helper tests elsewhere and S3 compatibility tests. Response writing logs but cannot recover from partial write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_legal_hold.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_list.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_list.go

Purpose: implements S3 ListObjects V1 and V2 over SeaweedFS filer entries, translating hierarchical filer directories into S3 `Contents` and `CommonPrefixes` with marker/continuation-token, delimiter, prefix, URL encoding, owner, versioning, and empty-directory compatibility behavior.

Important APIs and types include `OptionalString`, `ListBucketResultV2`, `listBucketResultV1`, `toListBucketResultV1`, `ListObjectsV2Handler`, `ListObjectsV1Handler`, `sanitizeV1MarkerEcho`, `listFilerEntries`, `ListingCursor`, `normalizePrefixMarker`, `buildTruncatedNextMarker`, `doListFilerEntries`, `getListObjectsV2Args`, `getListObjectsV1Args`, `compareWithDelimiter`, and `adjustMarkerForDelimiter`.

Control flow parses request arguments, rejects invalid max-keys and unordered-with-delimiter combinations, adjusts delimiter-ending markers, calls `listFilerEntries`, checks bucket existence on empty results, and writes V1 or V2 XML. `listFilerEntries` normalizes prefix/marker into a filer directory plus child prefix, hoists versioning state, recursively traverses filer directories with `doListFilerEntries`, appends or deduplicates versioned entries, converts directories to common prefixes or directory-key objects depending on delimiter and MIME, sorts common prefixes with delimiter-aware ordering, and URL-encodes after sorting.

State and persistence are read-only filer stream state. `ListingCursor` tracks remaining max keys, truncation, and trailing-slash prefix probes. Versioned buckets synthesize logical latest object entries from `.versions` directories while skipping delete markers. Real but empty directories can be surfaced as folder markers only for explicit `<dir>/` probes; plain flat listings hide them.

Dependencies include `filer_pb.ListEntries`, S3 XML model types, `newListEntry`, `entryUrlEncode`, bucket/version helpers, and AWS SDK constants. Integration points are S3 bucket list routes, versioning metadata, directory marker semantics, and client compatibility with Hadoop/Spark style directory probes.

Risks include off-by-one truncation, marker exclusivity, delimiter sorting compatibility, duplicate versioned entries, hidden multipart upload folders affecting limits, and distinguishing real directories from S3 directory-key objects. Companion directory tests cover common-prefix directory handling and empty directory probe behavior, but broader pagination and versioning combinations need integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_list_directory_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_list_directory_test.go

Purpose: tests directory handling in `doListFilerEntries`, especially the distinction between common prefixes, explicit directory probes, and phantom empty-directory keys.

Important coverage includes `TestDirectoryListedAsCommonPrefix`, `TestEmptyDirectorySurfacedAsMarker`, `TestNonEmptyDirectoryGetsNoPhantomMarker`, and `TestEmptyDirectoryHiddenInFlatListing`. These directly exercise `ListingCursor` and `doListFilerEntries` with a fake filer client.

Control flow builds synthetic directory/file entries under `/buckets/...`, invokes `doListFilerEntries` with different delimiter, prefix, and `prefixEndsOnDelimiter` settings, and records callback entries. It verifies regular directories are passed to delimiter handling as common-prefix candidates, empty real directories are surfaced as folder markers only during explicit `<dir>/` probes, non-empty directories emit their children instead of phantom markers, and plain flat listing hides empty directories while still returning real objects inside non-empty directories.

State and persistence are in-memory fake filer entries keyed by directory path. The tests mutate an empty directory's MIME to `FolderMimeType` through implementation behavior when surfacing it as a directory key object.

Dependencies include `testFilerClient`, `filer_pb.Entry`, `s3_constants.FolderMimeType`, and `testify/assert`. Integration point is S3 client compatibility for tools that infer directories via ListObjects under trailing-slash prefixes.

Risks: tests cover selected directory shapes but not pagination, URL encoding, versioned buckets, multipart upload folder skipping, or delimiter values other than `/`. They are precise guards against regressions that either hide legitimate empty-directory probes or expose deleted-object directory leftovers as phantom S3 keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_list_directory_test.go -->
