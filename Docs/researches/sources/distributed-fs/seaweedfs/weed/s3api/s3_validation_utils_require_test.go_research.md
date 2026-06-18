# sources/distributed-fs/seaweedfs/weed/s3api/s3_validation_utils_require_test.go

## Purpose
This test file verifies runtime behavior of SSE key commitment enforcement. It ensures SeaweedFS can remain compatible with legacy objects by default while supporting a strict mode that rejects missing commitments.

## Important APIs, Types, and Functions
Tests cover `VerifyKeyCommitment`, `ComputeKeyCommitment`, `SetRequireKeyCommitment`, and the package-level `requireKeyCommitment` atomic.

## Control Flow
Each test snapshots the previous atomic value and restores it with `t.Cleanup`. Tests explicitly set strict mode on or off, then verify missing commitment acceptance/rejection, valid commitment acceptance, and rejection of tampered key, IV, algorithm, or commitment bytes. The final test checks that the public setter updates the atomic.

## State and Persistence Behavior
State is limited to the process-wide atomic flag. The tests do not read environment variables or write metadata; they exercise the verifier directly.

## Dependencies and Integration Points
The file protects commitment checks used during SSE-S3 and SSE-KMS decryption. It indirectly validates the compatibility contract documented by `WEED_S3_REQUIRE_KEY_COMMITMENT`.

## Risks and Edge Cases
The tests use short byte slices as HMAC inputs in some cases; that is fine for commitment logic but not full AES validation. They do not cover environment-variable initialization directly. They also do not test malformed but non-empty commitment lengths separately; HMAC comparison handles that by mismatch.

## Test Signals
Passing tests signal legacy acceptance when strict mode is disabled, missing-commitment rejection when enabled, valid HMAC acceptance, tamper detection across all bound inputs, and correct setter behavior.
