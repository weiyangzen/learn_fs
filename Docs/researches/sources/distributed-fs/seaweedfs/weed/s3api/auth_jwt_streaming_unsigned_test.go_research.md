# sources/distributed-fs/seaweedfs/weed/s3api/auth_jwt_streaming_unsigned_test.go

Purpose: Regression tests for JWT bearer authentication on requests classified as `STREAMING-UNSIGNED-PAYLOAD-TRAILER`.

Important APIs, types, and functions: `TestJWTStreamingUnsignedAuth` exercises `getRequestAuthType`, `AuthenticateRequest`, and `authenticateJWTWithIAM` through a `MockIAMIntegration`. `TestJWTStreamingUnsignedChunkedReader` uses streaming payload test helpers to verify body decoding does not require a SigV4 seed signature for bearer-token uploads.

Control flow and state: The auth test creates IAM with memory store, attaches a JWT-auth mock, forces auth enabled, sets unsigned-streaming and bearer headers, verifies request classification remains unsigned-streaming, and expects the JWT identity. The reader test adds a bearer header to an unsigned streaming request and runs the chunked reader path.

State and persistence behavior: Uses transient in-memory IAM state and resets the shared memory store around the first test to avoid cross-test identity leakage.

Dependencies and integration points: Depends on `MockIAMIntegration` from STS tests, streaming body helpers from the S3 test suite, and `s3err`.

Risks and test signals: Covers a subtle dispatch bug: unsigned-streaming describes payload framing, not authentication type. JWT requests with checksum trailers must authenticate via IAM integration and must not be downgraded to anonymous or incorrectly verified as SigV4 streaming.
