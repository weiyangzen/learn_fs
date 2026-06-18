# Research: sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/GCSInputStream.java

Purpose: GCS input stream optimized for skip/offset reads, avoiding slow read-and-discard behavior from the underlying stream by reopening from a requested offset.

Important APIs and control flow: constructors store bucket, key, `GoogleStorageService`, initial position, and retry policy. `read` lazily opens the stream and advances `mPos`. `read(byte[], off, len)` returns 0 for zero-length reads. `skip` returns 0 for non-positive values, uses buffered skip if enough bytes are available, otherwise closes the current stream, advances `mPos`, and reopens from that offset. `openStream` retries 404s and throws immediately for other service errors.

State, dependencies, integration, risks, tests: state includes current position and a nullable buffered input stream. Dependencies include JetS3t `GoogleStorageService`, `GSObject`, Apache HTTP status, and Alluxio retry policy. Risks include `skip` calling `mInputStream.available()` when stream is null in some call sequences, object mutation between reopen calls, and retry policy reuse across opens.
