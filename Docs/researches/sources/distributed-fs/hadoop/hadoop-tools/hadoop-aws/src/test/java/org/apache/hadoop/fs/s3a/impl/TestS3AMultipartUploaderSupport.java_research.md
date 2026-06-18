# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestS3AMultipartUploaderSupport.java

## Purpose
`TestS3AMultipartUploaderSupport` unit-tests helper methods and payload classes used by S3A's multipart uploader part handles, including checksum capture.

## Important APIs, Types, and Functions
- Tests `S3AMultipartUploader.buildPartHandlePayload()`, `parsePartHandlePayload()`, and `extractChecksum()`.
- Uses `PartHandlePayload` accessors for path, upload ID, part number, ETag, length, checksum algorithm, and checksum.
- Builds AWS SDK `UploadPartResponse` instances with checksum fields.

## Control Flow
Round-trip tests serialize and parse payloads with normal length, length beyond integer range, and checksum metadata. Validation tests reject missing ETag, negative length, empty payload, corrupted header, missing checksum algorithm, and missing checksum. Checksum extraction tests verify CRC32, CRC32C, SHA1, SHA256, and no-checksum responses.

## State and Persistence Behavior
All state is in byte arrays and SDK response objects. No filesystem or network operations occur.

## Dependencies and Integration Points
The test protects multipart uploader handle compatibility, upload response checksum integration, and validation used when completing multipart uploads through Hadoop's multipart uploader API.

## Risks and Edge Cases
Payload header format is a compatibility contract; changing it can break persisted part handles. Checksum algorithm names returned by `extractChecksum()` must match downstream complete-MPU expectations.

## Test Signals
Passing confirms part handles round-trip safely, reject malformed inputs, handle large part lengths, and capture per-part checksum metadata when available.
