# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_etag_test.go

Purpose: verifies copy ETag semantics, especially for multipart objects whose S3 ETag is stored in extended metadata and cannot be recovered from the file's MD5 alone.

Important coverage includes `TestCopyEntryETagPrefersStoredExtendedETag`, `TestCopyEntryETagFallsBackToFilerETag`, `TestValidateConditionalCopyHeadersUsesStoredExtendedETag`, and helper `newCopyETagTestEntry`.

Control flow builds synthetic filer entries with attributes and optional `ExtETagKey`. It asserts `copyEntryETag` returns stored extended ETags when present and falls back to `filer.ETagEntry`/MD5-derived values otherwise. Conditional header tests create copy requests with `X-Amz-Copy-Source-If-Match` and `If-None-Match`, proving the source conditional path compares against the stored S3 ETag.

State and persistence are in-memory filer entries and HTTP request headers. The stored ETag lives in `Entry.Extended`, while the fallback MD5 lives in `Entry.Attributes.Md5`.

Dependencies include `s3_constants.ExtETagKey`, `s3err`, `httptest`, and a test helper for decoding MD5 hex. Integration point is both CopyObject and UploadPartCopy conditional validation, plus `finalizeCopyDestination`, which stores the destination ETag.

Risks: tests do not create real multipart objects, but they isolate the core correctness property: do not recompute or lose multipart ETags during copy or conditional matching.
