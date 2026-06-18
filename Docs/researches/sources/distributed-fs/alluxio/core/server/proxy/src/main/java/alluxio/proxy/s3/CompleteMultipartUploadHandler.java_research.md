# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/CompleteMultipartUploadHandler.java

## Purpose
`CompleteMultipartUploadHandler` handles S3 `CompleteMultipartUpload` requests in the proxy. It parses the request body, validates uploaded parts, merges part files into the final object, records ETag/upload metadata, cleans temporary multipart state, and returns an XML result.

## Important APIs, Types, and Functions
The outer class extends Jetty `AbstractHandler` and implements `handle`. It owns metadata filesystem `mMetaFs`, an executor pool sized by `PROXY_S3_COMPLETE_MULTIPART_UPLOAD_POOL_SIZE`, keepalive settings, and the S3 URI prefix. The inner `CompleteMultipartUploadTask` implements `Callable<CompleteMultipartUploadResult>` with key methods `call`, `prepareForCreateTempFile`, `parseCompleteMultipartUploadRequest`, `validateParts`, `removePartsDirAndMPMetaFile`, `cleanupTempPath`, and `checkIfComplete`.

## Control Flow, State, and Persistence
`handle` ignores non-matching paths, non-POST requests, and requests without `uploadId`. For matching requests it extracts the S3 user from authorization, parses bucket/object/upload ID, reads the XML body, submits a task, optionally sends whitespace keepalives while the future runs, then serializes success or S3 error XML. The task validates bucket and upload metadata, parses ordered parts, lists and sorts temporary part files, enforces minimum size for all but the last part, creates a temporary object with upload/tag/content-type xAttrs, streams all parts through an MD5 `DigestOutputStream`, persists the ETag xAttr, renames the temp object over the target with multipart S3 syntax options, deletes the parts directory and metadata file, and cancels the multipart cleaner. On exception it checks whether a concurrent retry already completed the same upload ID and returns that ETag if present. Temporary object cleanup runs in `finally`.

## Dependencies and Integration Points
The handler integrates Jetty request handling, Alluxio `FileSystem`, S3 path utilities, XML parsing/serialization with Jackson `XmlMapper`, proxy access logging, S3 metrics timers, multipart cleaner, Alluxio xAttrs, write type selection, and rename semantics.

## Risks
Keepalive mode may commit HTTP status before the task outcome, so S3 errors after whitespace flushing can be encoded in the body with an already-OK status. `validateParts` ignores requested ETags and returns all uploaded parts, not just requested parts, after validating presence and size. Multipart completion races are handled by upload-ID xAttr idempotency but still depend on rename atomicity and xAttr propagation. The executor is created per handler and there is no explicit shutdown here. Parsing bucket/object by first slash assumes a valid S3 path after prefix stripping.

## Test Signals
High-value tests include successful multipart completion, missing upload ID metadata, invalid XML, invalid part order, missing part, too-small non-final part, retry/idempotency after prior successful rename, cleanup of temp object after failure, cleaner cancellation, keepalive response behavior, and preservation of tag/content-type xAttrs.
