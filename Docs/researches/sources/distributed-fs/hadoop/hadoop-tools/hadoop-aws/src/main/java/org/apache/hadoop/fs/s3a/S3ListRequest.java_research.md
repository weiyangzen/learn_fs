# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ListRequest.java

## Purpose
`S3ListRequest` is a version-independent wrapper around AWS S3 ListObjects v1 and v2 request types.

## Important APIs, Types, and Functions
Static constructors `v1(ListObjectsRequest)` and `v2(ListObjectsV2Request)` create the wrapper. Accessors are `isV1()`, `getV1()`, `getV2()`, and `toString()`.

## Control Flow and State
The private constructor stores exactly one request slot by convention. `isV1()` dispatches all behavior. `toString()` formats bucket, prefix, delimiter, max keys, and requester-pays value from the active request.

## State and Persistence Behavior
State is immutable references to AWS SDK request objects. The wrapper persists no remote state and performs no validation that the active request is non-null beyond factory discipline.

## Dependencies and Integration Points
Dependencies are AWS SDK `ListObjectsRequest` and `ListObjectsV2Request`. It is used by S3A listing code to abstract over list API versions while preserving useful debug logging.

## Risks and Test Signals
Risks include null requests accepted by static factories, misuse of the inactive getter, and behavior drift between v1/v2 request fields. Tests should cover v1/v2 dispatch, string formatting, requester-pays propagation, and null-request handling expectations.
