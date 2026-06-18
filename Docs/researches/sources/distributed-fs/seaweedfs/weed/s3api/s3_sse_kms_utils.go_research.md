# sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_kms_utils.go

## Purpose
`s3_sse_kms_utils.go` contains shared helper logic for SSE-KMS data-key generation, validation, AES block creation, plaintext clearing, and construction of commitment-bearing `SSEKMSKey` metadata.

## Important APIs, Types, and Functions
The file defines `KMSDataKeyResult` and functions `generateKMSDataKey`, `clearKMSDataKey`, and `createSSEKMSKey`.

## Control Flow
`generateKMSDataKey` validates KMS key ID format and optional encryption context, obtains the global KMS provider, requests an AES-256 data key, and constructs an AES cipher from the plaintext key. If cipher creation fails, plaintext is cleared before returning. `clearKMSDataKey` zeroes the plaintext in a result. `createSSEKMSKey` packages KMS response fields plus encryption context, bucket-key flag, IV, chunk offset, and HMAC commitment over plaintext key, IV, and KMS algorithm.

## State and Persistence Behavior
The helper itself keeps no persistent state. It receives sensitive plaintext key material from KMS and expects callers to defer `clearKMSDataKey`. The returned `SSEKMSKey` carries persistent metadata fields, but not plaintext key bytes.

## Dependencies and Integration Points
The file depends on the global `kms` package, AES, shared key-ID and commitment validators, and `s3_constants`. It is used by multiple SSE-KMS encryption creation paths to keep metadata and commitment behavior consistent.

## Risks and Edge Cases
`generateKMSDataKey` uses `context.Background()` rather than request context, so KMS calls are not request-cancellable here. Context validation allows up to 2048 chars in this helper while `parseEncryptionContext` elsewhere uses 256, which may surprise callers. Global KMS provider absence returns an ordinary error that caller must map to S3 response codes.

## Test Signals
Tests should cover invalid key IDs, invalid context keys/values/counts, no global KMS provider, KMS generate failures, AES cipher failure with plaintext clearing, and commitment presence in `createSSEKMSKey`.
