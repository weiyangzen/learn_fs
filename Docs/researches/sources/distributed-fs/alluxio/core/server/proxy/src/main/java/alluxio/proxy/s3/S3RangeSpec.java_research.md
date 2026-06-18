# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3RangeSpec.java

`S3RangeSpec` parses HTTP byte range headers for object GET and copy-source requests. `Factory.create` accepts `bytes=start-end`, open-ended `bytes=start-`, and suffix `bytes=-length`; malformed input returns the invalid sentinel, which means full-object behavior.

Valid specs compute an actual object offset, length, and `Content-Range` string. Suffix ranges clamp to object size. Starts beyond object size return length zero and offset zero. The class is immutable and request-local.

It integrates with `RangeFileInStream`, object GET, and copy operations. Tests should cover empty/malformed headers, start/end ranges, open-ended ranges, suffix ranges, suffix zero rejection, start greater than end, suffix larger than object, start at/beyond object size, and very large numeric values. A compatibility risk is that invalid ranges fall back to full-object reads instead of returning an S3 invalid-range error.
