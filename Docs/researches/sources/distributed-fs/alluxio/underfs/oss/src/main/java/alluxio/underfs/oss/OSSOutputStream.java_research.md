# sources/distributed-fs/alluxio/underfs/oss/src/main/java/alluxio/underfs/oss/OSSOutputStream.java

## Purpose
`OSSOutputStream` is the non-streaming OSS write path: it buffers all bytes to a local temporary file and uploads the completed file on close.

## Important APIs, Types, And Functions
The constructor validates bucket/key/client, chooses a temp path from configured tmp dirs, and wraps a local file stream in an MD5 `DigestOutputStream` when possible. `write`, `flush`, `close`, and `getContentHash` form the public behavior.

## Control Flow
Writes go to local disk. `close` is guarded by an `AtomicBoolean`; it closes the local stream, builds metadata including Base64 MD5 if available, calls `putObject`, stores the returned ETag, and deletes the temp file.

## State And Persistence
State includes bucket, key, temp file, OSS client, local stream, MD5 digest, closed flag, and content hash. Persistence is local until close, then remote in OSS.

## Dependencies And Integration Points
It depends on Aliyun OSS `putObject`, Alluxio temp-dir selection, Commons Codec Base64, and `ContentHashable`. `OSSUnderFileSystem.createObject` uses it when streaming upload is disabled.

## Risks
Large writes require local disk space. Failure during close may leave temp files or partial remote state. Content hash is only available after successful upload.

## Test Signals
`OSSOutputStreamTest` verifies constructor guards, write forwarding, close failure/success, flush forwarding, upload call, deletion, and content hash behavior.
