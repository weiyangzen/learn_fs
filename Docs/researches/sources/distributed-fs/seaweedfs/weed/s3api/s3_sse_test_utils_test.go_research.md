# sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_test_utils_test.go

## Purpose
This test utility file provides reusable helpers for SSE-C and SSE-KMS tests. It generates deterministic customer keys, configures request headers, sets up a local KMS provider, builds test metadata, and provides assertion helpers for response headers.

## Important APIs, Types, and Functions
Important test-only types are `TestKeyPair` and `TestSSEKMSKey`. Helpers include `GenerateTestSSECKey`, `SetupTestSSECHeaders`, `SetupTestSSECCopyHeaders`, `SetupTestKMS`, `SetupTestSSEKMSHeaders`, `CreateTestMetadata`, `CreateTestMetadataWithSSEC`, `CreateTestMetadataWithSSEKMS`, `CreateTestHTTPRequest`, `CreateTestHTTPResponse`, `SetupTestMuxVars`, `AssertSSECHeaders`, `AssertSSEKMSHeaders`, corrupted metadata creators, and `GenerateTestData`.

## Control Flow
SSE-C helpers derive a 32-byte deterministic key from a seed, base64-encode it, compute base64 MD5, and set the expected S3 request headers. KMS setup creates a local KMS provider, installs it globally, creates a test key, and returns cleanup that resets the global provider and closes it. Metadata helpers populate maps with the same keys production code expects.

## State and Persistence Behavior
Most helpers are in-memory. `SetupTestKMS` mutates global KMS provider state and must be paired with cleanup. No filesystem or filer persistence is used.

## Dependencies and Integration Points
The file depends on Gorilla mux, local KMS provider, KMS global provider, S3 constants, SSE serialization helpers, and Go HTTP test utilities. It supports many SSE tests by hiding repetitive setup.

## Risks and Edge Cases
Because helpers mutate global KMS state, tests using them must avoid parallel interference or always defer cleanup. `CreateTestMetadataWithSSEKMS` ignores serialization errors and stores both raw encrypted data key and serialized context, so malformed test keys could hide setup failures. The deterministic SSE-C keys are suitable for tests only.

## Test Signals
This file is not a test target by itself, but failures in dependent SSE-C/KMS tests often indicate these helpers no longer match production header or metadata conventions.
