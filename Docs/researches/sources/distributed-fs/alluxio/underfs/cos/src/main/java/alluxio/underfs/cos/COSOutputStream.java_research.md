# Research: sources/distributed-fs/alluxio/underfs/cos/src/main/java/alluxio/underfs/cos/COSOutputStream.java

Purpose: COS object output stream that stages writes to a local temporary file, then uploads the complete file on close. It implements `ContentHashable` to expose the uploaded object's ETag/content hash.

Important APIs and control flow: constructor validates bucket/key/client, creates a temp file under configured temp dirs, and wraps a `FileOutputStream` in `DigestOutputStream` for MD5 when available. `write` and `flush` operate on the local stream. `close` is guarded by `AtomicBoolean`, closes local output, uploads via `putObject` with content length and optional base64 MD5 metadata, stores ETag, and deletes the temp file in `finally`.

State, dependencies, integration, risks, tests: state includes temp file path, local stream, MD5 digest, closed flag, and content hash. Dependencies include Tencent COS SDK, commons-codec Base64, Alluxio temp-dir utilities. Risks include local disk pressure, temp deletion failure, no multipart upload for large files, and content hash unavailable before close.
