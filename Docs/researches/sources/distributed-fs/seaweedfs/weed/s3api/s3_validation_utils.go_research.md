# sources/distributed-fs/seaweedfs/weed/s3api/s3_validation_utils.go

## Purpose
`s3_validation_utils.go` holds validation and commitment helpers shared by server-side encryption implementations. It can enforce HMAC key commitments, validate KMS key IDs, validate IV lengths, and validate SSE-KMS/SSE-S3 key structures.

## Important APIs, Types, and Functions
The file defines `RequireKeyCommitmentEnv`, the atomic `requireKeyCommitment`, and functions `SetRequireKeyCommitment`, `ComputeKeyCommitment`, `VerifyKeyCommitment`, `isValidKMSKeyID`, `ValidateIV`, `ValidateSSEKMSKey`, and `ValidateSSES3Key`.

## Control Flow
`init` reads `WEED_S3_REQUIRE_KEY_COMMITMENT` and enables strict mode for missing commitments. `ComputeKeyCommitment` returns HMAC-SHA256 keyed by encryption key over IV plus algorithm. `VerifyKeyCommitment` accepts missing commitments by default for legacy compatibility, rejects missing commitments in strict mode, and compares present commitments with `hmac.Equal`. KMS key validation rejects empty strings, whitespace, spaces, controls, and overlong IDs. SSE-S3 validation checks key size, algorithm, key ID, and optional IV length.

## State and Persistence Behavior
The only state is the process-wide atomic commitment requirement. Commitments themselves are stored by SSE metadata code in object or chunk metadata. This file does not persist anything directly.

## Dependencies and Integration Points
It depends on HMAC/SHA256, environment variables, S3 constants, and glog. It is used by SSE-C/KMS/S3 encryption and decryption paths to prevent IV/key/algorithm tampering and malformed metadata panics.

## Risks and Edge Cases
Default acceptance of missing commitments is compatibility-friendly but leaves legacy objects without downgrade protection unless strict mode is enabled after migration. `ValidateSSEKMSKey` only checks nil, leaving deeper field validation to serializers/KMS. KMS key validation is intentionally permissive and does not enforce ARN/UUID patterns despite regexes elsewhere.

## Test Signals
`s3_validation_utils_require_test.go` covers default missing-commitment acceptance, strict missing-commitment rejection, valid strict commitments, tampered key/IV/algorithm/commitment rejection, and runtime toggling.
