# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/HttpChannelEOFException.java

Purpose: normalized EOFException for HTTP channel termination conditions such as no response and OpenSSL errors.

Important APIs/types: extends `EOFException`; constructor accepts path, error, and cause, uses `error` as message, and initializes cause.

Control flow: exception translation or HTTP error handling wraps low-level channel failures into this type so retry policies can match EOF semantics.

State and persistence behavior: standard exception message/cause only. The `path` parameter is not stored in this class.

Dependencies and integration points: used by S3A retry policies and HTTP client exception translation across shaded/unshaded client libraries.

Risks: dropping the path from the message can reduce diagnostics unless callers include path in the error string.

Test signals: retry tests should verify low-level no-response/channel EOF failures are represented as `EOFException` subclasses with original causes.
