# sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/AlluxioS3Exception.java

## Purpose
`AlluxioS3Exception` translates AWS client/service failures into Alluxio runtime exceptions with gRPC status and external error type.

## Important APIs, Types, And Functions
Static `from(AmazonClientException)` and `from(String, AmazonClientException)` create exceptions. `httpStatusToGrpcStatus` maps HTTP status codes to `io.grpc.Status`. The private constructor passes `ErrorType.External` and retryability to `AlluxioRuntimeException`.

## Control Flow
Generic `AmazonClientException` becomes `Status.UNKNOWN` with a client-exception description. `AmazonS3Exception` contributes HTTP status, S3 error code/message, and retryable flag. Optional caller-provided messages override generated descriptions.

## State And Persistence
The class has no mutable state. It encapsulates cause, status, message, error type, and retryability in the exception object.

## Dependencies And Integration Points
It is used by S3A UFS, input stream, listing, metadata, and delete paths to convert SDK failures into Alluxio's runtime error model.

## Risks
Mapping is approximate; some S3-compatible stores return nonstandard status/error combinations. Generic client failures lose detailed status.

## Test Signals
S3A UFS tests expect `AlluxioS3Exception` for listing, metadata, and rename failures. No direct exhaustive status-map test is present.
