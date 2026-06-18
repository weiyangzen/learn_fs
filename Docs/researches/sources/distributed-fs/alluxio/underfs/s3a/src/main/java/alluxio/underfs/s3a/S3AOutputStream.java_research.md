# sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/S3AOutputStream.java

## Purpose
`S3AOutputStream` is the non-streaming S3 write path that uploads a local temporary file on close.

## Important APIs, Types, And Functions
The constructor validates inputs, selects a temp file, initializes MD5 digesting, and stores a `TransferManager`. Public methods implement `write`, `flush`, `close`, `getContentHash`, with protected `getUploadPath` and `getTransferManager`.

## Control Flow
Writes are buffered to local disk. `close` closes the local stream, builds `ObjectMetadata` with MD5 and optional AES256 SSE, submits a `PutObjectRequest` to `TransferManager.upload`, waits for completion, records ETag, and deletes the temp file.

## State And Persistence
State includes bucket, key, temp file, transfer manager, local output stream, digest, closed flag, and content hash. Data is local until close then persisted in S3.

## Dependencies And Integration Points
It depends on AWS SDK v1 transfer manager, Commons Codec Base64, Alluxio temp-dir utilities, and `ContentHashable`. `S3AUnderFileSystem.createObject` uses it when streaming upload is disabled.

## Risks
Large writes consume local disk. Interrupted or failed uploads can leave temp files or incomplete remote operations. `close` must remain idempotent.

## Test Signals
`S3AOutputStreamTest` verifies write/flush delegation, upload-on-close, content hash after close, and mocked transfer manager interaction.
