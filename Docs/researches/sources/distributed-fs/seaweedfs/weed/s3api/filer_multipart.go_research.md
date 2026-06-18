# sources/distributed-fs/seaweedfs/weed/s3api/filer_multipart.go

Purpose: implements S3 multipart upload lifecycle on SeaweedFS filer entries: initiate, complete, abort, list uploads, list parts, encryption metadata propagation, multipart ETag, composite checksums, versioning, and cleanup.

Important APIs/types: `createMultipartUpload`, `CompleteMultipartUploadResult`, `copySSEHeadersFromFirstPart`, `multipartCompletionState`, `completeMultipartResult`, `extractMultipartSSES3Info`, `completedMultipartChunk`, `applyMultipartSSES3HeadersFromUploadEntry`, `prepareMultipartCompletionState`, `completeMultipartUpload`, `abortMultipartUpload`, `listMultipartUploads`, `listObjectParts`, `MultipartEncryptionConfig`, `prepareMultipartEncryptionConfig`, `applyMultipartEncryptionConfig`, `calculateMultipartETag`, `computeCompositeChecksum`, `getEtagFromEntry`, and `validateCompletePartETag`.

Control flow: initiation creates an upload directory, stores target key/owner/metadata/content type/object-lock metadata, validates checksum algorithm, and persists explicit or bucket-default SSE metadata. Completion validates ordered parts, lists upload entries, matches ETags, rejects too-small non-final parts, remaps chunk offsets, records part boundaries, computes multipart ETag and optional composite checksum, then writes a version file, null-version object, or normal object. Writes are routed through object ownership helpers when available, otherwise an object write lock is used. Cleanup removes unused part entries and upload directory.

State and persistence: persistent state is filer entries and extended metadata for upload ID, object key, owner, ETag, version ID, multipart part count/boundaries, checksum algorithm/value, object lock, TTL expiry, and SSE metadata. Versioned buckets store content under `.versions` and update latest pointers with rollback on finalize failure.

Dependencies and integration points: AWS S3 SDK structs, filer operations, versioning helpers, conditional header checks, object routing locks, stats counters, S3 encryption helpers, checksum mappings, and `s3_constants`.

Risks: completion is a multi-step persistence transaction, so partial failures can leave stale upload data. SSE-S3 IV backfill trusts existing per-chunk metadata to avoid corruption and only fills missing metadata. Composite checksum requires every completed part to carry matching checksum metadata.
