# sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_metadata.go

## Purpose
`s3_sse_metadata.go` provides small metadata helpers for SSE-C IV storage and retrieval. It normalizes the current raw-IV format while preserving backward compatibility with a legacy base64-encoded IV format.

## Important APIs, Types, and Functions
The file exposes `StoreSSECIVInMetadata(metadata map[string][]byte, iv []byte)` and `GetSSECIVFromMetadata(metadata map[string][]byte) ([]byte, error)`.

## Control Flow
`StoreSSECIVInMetadata` writes non-empty IV bytes directly to the `SeaweedFSSSEIV` metadata key. `GetSSECIVFromMetadata` reads that key, returns it directly if it is exactly 16 bytes, otherwise tries base64 decoding and validates the decoded value is 16 bytes. Missing or malformed metadata produces descriptive errors.

## State and Persistence Behavior
The helper mutates the caller-provided metadata map. The stored IV becomes durable when the object entry is persisted. The current canonical storage format is raw 16-byte IV, not base64 text.

## Dependencies and Integration Points
It depends on base64, S3 constants, and AES block size constants. It is used by SSE-C upload/copy/GET paths and aligns CopyObject behavior with `putToFiler` metadata format.

## Risks and Edge Cases
Legacy compatibility accepts any base64 string decoding to 16 bytes, even if the stored byte length is not exactly the normal 24-byte base64 length. That is permissive and useful for migration. Empty IVs are not stored, so callers must enforce IV generation before persistence.

## Test Signals
Tests should verify raw IV round trips, legacy base64 IV decode, missing metadata errors, invalid base64 errors, and wrong decoded length errors.
