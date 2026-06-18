# sources/distributed-fs/alluxio/underfs/tos/src/main/java/alluxio/underfs/tos/AlluxioTosException.java

## Purpose
`AlluxioTosException` translates Volcengine `TosException` failures into Alluxio runtime exceptions with gRPC status codes and `ErrorType.External`.

## APIs and Control Flow
`from(TosException)` and `from(String, TosException)` map the HTTP status code from the TOS exception to a gRPC `Status`, derive a default message from TOS code and message, and construct a retryable `AlluxioTosException`. `httpStatusToGrpcStatus` maps common HTTP statuses to `INVALID_ARGUMENT`, `UNAUTHENTICATED`, `PERMISSION_DENIED`, `NOT_FOUND`, `UNIMPLEMENTED`, `ABORTED`, `FAILED_PRECONDITION`, `OUT_OF_RANGE`, `INTERNAL`, `UNAVAILABLE`, `DEADLINE_EXCEEDED`, or `UNKNOWN`.

## State, Dependencies, and Integration
The class is immutable after construction and stores no additional fields beyond its superclass. It is used by TOS streams, the UFS, and the factory when SDK calls fail.

## Risks and Test Signals
All converted exceptions are marked retryable, including client-side or permission failures that may not be usefully retried. The default message builds `code:message`, which can degrade if either field is null. No listed test directly verifies HTTP-to-gRPC status mappings.
