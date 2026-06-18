# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3RestExceptionMapper.java

`S3RestExceptionMapper` is the Jersey `ExceptionMapper<Throwable>` for the older S3 REST resource. It delegates all uncaught throwables to `S3ErrorResponse.createErrorResponse(e, "")`.

The mapper is stateless and has no persistence. It intentionally passes an empty resource because this fallback has no direct bucket/object context.

Tests should verify provider registration and mappings for `S3Exception`, Alluxio status/runtime exceptions, IO exceptions, and generic throwables. Risks are empty resource fields and generic plain-text fallback responses, both of which can affect strict S3 clients.
