# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_part_sse.go

Purpose: implements the UploadPartCopy slow path for destination SSE and multipart checksum cases. It streams source plaintext into the existing `putToFiler` upload pipeline so destination parts receive correct encryption metadata and checksums instead of raw-copying bytes and corrupting reads.

Important APIs include `isTransientFilerError`, `uploadEntryHasSSE`, `uploadEntryHasChecksum`, `sourceEntryHasSSE`, `openSourcePlaintextReader`, `openSSES3SourcePlaintextReader`, `applyRange`, `applyDestSSEHeadersToCopyRequest`, `applyDestChecksumHeaderToCopyRequest`, `fakeContentRequest`, `copyObjectPartViaReencryption`, and `writeEmptyCopyPart`. `errCopySourceSSEUnsupported` marks unsupported SSE-C/SSE-KMS source plaintext extraction for UploadPartCopy.

Control flow begins in `CopyObjectPartHandler` when upload entry SSE/checksum or source SSE is detected. `copyObjectPartViaReencryption` opens a plaintext reader for the requested source range, clones the original request into a fake PUT body, stages destination SSE and checksum headers from the multipart upload entry, and invokes `putToFiler` with a generated part path. Empty copy ranges without checksum are written as zero-byte parts directly.

State and persistence include multipart upload entries under `.uploads`, request headers that carry staged SSE-KMS/SSE-S3 configuration, generated part objects, and response metadata from `putToFiler`. SSE-S3 source reads can use per-chunk metadata through `buildMultipartSSES3Reader` or legacy entry-level metadata fallback. SSE-KMS upload entries require key ID, bucket-key flag, encryption context, and base IV in `Extended`.

Dependencies include gRPC status codes, `filer_pb`, S3 constants/error mapping, SSE-S3/KMS helpers, `getEncryptedStreamFromVolumes`, `createEncryptedChunkReader`, `putToFiler`, and checksum helpers. Integration is intentionally with normal upload code rather than bespoke part-writing so encryption and checksums remain consistent with PutObjectPart.

Risks: SSE-C and SSE-KMS source plaintext extraction in this slow path returns NotImplemented, so some source/destination combinations are explicitly unsupported for UploadPartCopy. Incorrect upload-entry metadata yields internal errors. Range skipping on decrypted streams can be expensive for large offsets. Tests cover checksum staging and SSE detection helpers indirectly, but end-to-end SSE UploadPartCopy requires broader integration coverage.
