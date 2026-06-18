# Research: sources/distributed-fs/alluxio/underfs/cos/src/main/java/alluxio/underfs/cos/AlluxioCosException.java

Purpose: COS-specific runtime exception adapter converting Tencent COS SDK exceptions into Alluxio runtime exceptions with gRPC status and retryability metadata.

Important APIs and control flow: `from(CosClientException)` delegates to `from(null, cause)`. The overload defaults to `Status.UNKNOWN` and client error text, but if the cause is `CosServiceException`, maps the HTTP status code via `httpStatusToGrpcStatus` and uses COS error code/message. The private constructor passes `ErrorType.External` and `cause.isRetryable()` to `AlluxioRuntimeException`.

State, dependencies, integration, risks, tests: no persistent state. Dependencies include COS SDK exceptions, gRPC `Status`, `ErrorType`, and HTTP status constants. Integration point is object operations that catch `CosClientException`. Risk: unmapped COS-specific status codes become UNKNOWN; retryability relies on SDK classification.
