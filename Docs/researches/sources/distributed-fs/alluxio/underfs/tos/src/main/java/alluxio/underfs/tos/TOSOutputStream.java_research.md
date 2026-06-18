# sources/distributed-fs/alluxio/underfs/tos/src/main/java/alluxio/underfs/tos/TOSOutputStream.java

## Purpose
`TOSOutputStream` is the non-streaming TOS upload path. It buffers the complete object in a local temporary file, calculates an MD5 when available, and uploads the file to TOS on close.

## APIs and Control Flow
The constructor validates bucket, key, and client, creates a UUID temp file under Alluxio temp dirs, initializes an MD5 `MessageDigest`, and wraps file output in a `DigestOutputStream` when possible. Writes and flushes delegate to the local output stream. `close()` uses an `AtomicBoolean` to make the method idempotent, closes the local stream, opens a buffered input stream from the temp file, sets content length and content MD5 metadata, uploads with `putObject`, stores the returned ETag, and deletes the temp file in `finally`.

## State, Dependencies, and Integration
State includes bucket, key, temp file, TOS client, local stream, digest, close flag, and optional content hash. It implements `ContentHashable` so callers can retrieve the ETag. `TOSUnderFileSystem.createObject` chooses this class when streaming upload is disabled.

## Risks and Test Signals
The class is marked not thread-safe despite an atomic close guard; concurrent writes and close are unsafe. Temp-file delete failure is logged but not raised. SDK errors are converted to `AlluxioTosException`. `TOSOutputStreamTest` covers constructor I/O failure, write delegation, flush, upload failure, delete-on-close, and ETag exposure, but uses heavy static/constructor mocking.
