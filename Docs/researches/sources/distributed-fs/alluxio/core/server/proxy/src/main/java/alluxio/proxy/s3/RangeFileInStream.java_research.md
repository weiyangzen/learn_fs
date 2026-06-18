# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/RangeFileInStream.java

`RangeFileInStream` adapts an Alluxio `FileInStream` into a bounded Java `InputStream` for S3 byte-range reads. Factory construction seeks to `S3RangeSpec.getOffset(objectLength)` and caps normal `read()`/`read(byte[], int, int)` calls at `S3RangeSpec.getLength(objectLength)`.

The class stores only stream-local state: wrapped stream, allowed length, and bytes returned. It does not persist data; `close()` delegates to the Alluxio stream. It integrates with `S3ObjectTask` and `S3RestServiceHandler` for GET ranges and copy-source ranges.

Risk signals: the `read(ByteBuffer, int, int)` overload delegates directly to `FileInStream` without enforcing the range cap or updating `mReadBytes`; callers using it could read outside the requested range. Tests should cover full, open-ended, suffix, invalid, and out-of-object ranges, EOF behavior, zero-length reads, and close propagation.
