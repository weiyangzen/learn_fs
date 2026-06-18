# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3Exception.java

`S3Exception` is the checked S3 failure type carrying an `S3ErrorCode` and optional resource. Constructors support code-only, resource/code, wrapping another exception, and custom message/resource/code forms. Wrapping/custom forms derive a new `S3ErrorCode` with the original code/status and replacement description.

The object is transient request state consumed by `S3ErrorResponse` and `S3RestUtils` translation helpers. It does not persist data.

Risk signal: the custom message constructor does not call a superclass message constructor, so `getMessage()` can be null even though `getErrorCode().getDescription()` is set. Tests should verify cause preservation, resource mutation, code derivation, response message behavior, and code-only exceptions without resources.
