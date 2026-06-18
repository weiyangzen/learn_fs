# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestRequestFactory.java

## Purpose
`TestRequestFactory` validates that `RequestFactoryImpl` builds S3 SDK request builders with expected bucket, ACL, encryption, checksum, timeout, request-preparer, multipart limit, and SSE-C completion metadata behavior.

## Important APIs, Types, and Functions
- Uses `RequestFactoryImpl.builder()` to construct factories.
- `createFactoryObjects()` creates/analyzes abort, complete MPU, copy, delete, bulk delete, directory marker, get/head, list v1/v2, list multipart, initiate MPU, and PUT request builders.
- `AWSRequestAnalyzer` inspects each built request, while `CountRequests` verifies preparer invocation count.
- `assertApiTimeouts()` validates request override `apiCallAttemptTimeout` and `apiCallTimeout`.
- Parameterized checksum test covers `CRC32`, `CRC32_C`, `SHA1`, and `SHA256`.

## Control Flow
Encryption and preparer tests build factories with encryption secrets or request preparers and exercise the common request set. ACL tests assert canned ACL propagates to PUT, COPY, and initiate-MPU requests. Multipart tests validate upload-part request creation up to a part-count limit and reject part numbers beyond it. Timeout tests verify default and configured upload timeouts apply to PUT and upload-part requests. Checksum tests verify checksum algorithm propagation to copy, put, create-MPU, and upload-part requests. SSE-C completion test builds encryption secrets, derives base64 and MD5 values, and verifies complete-MPU includes customer encryption fields.

## State and Persistence Behavior
No S3 calls are made; state is built SDK request objects and local counters. `requestsAnalyzed` is an instance counter used to compare with preparer invocations.

## Dependencies and Integration Points
The test integrates request factory construction, AWS SDK S3 request builders, S3A encryption secrets, `PutObjectOptions`, multipart upload limits, checksum configuration, and audit/request analysis tooling.

## Risks and Edge Cases
`requestsAnalyzed` accumulates within each test instance; assumptions rely on JUnit creating fresh instances. The request set in `createFactoryObjects()` must be updated when RequestFactory gains required request types.

## Test Signals
Passing confirms S3A request construction consistently applies cross-cutting options across all major S3 operation builders.
