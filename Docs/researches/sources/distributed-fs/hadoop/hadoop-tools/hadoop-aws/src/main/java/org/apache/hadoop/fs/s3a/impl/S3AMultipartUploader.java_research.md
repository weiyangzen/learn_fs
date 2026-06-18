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
