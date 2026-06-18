# sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_utils.go

## Purpose
`s3_sse_utils.go` provides the shared AES-CTR IV offset calculation used by SSE-C, SSE-KMS, and SSE-S3. It enables safe range and multipart decryption without reusing the same counter block for different byte positions.

## Important APIs, Types, and Functions
The file exposes `calculateIVWithOffset(baseIV []byte, offset int64) ([]byte, int)`.

## Control Flow
The helper validates that `baseIV` is 16 bytes, copies it, computes `blockOffset = offset / 16` and `skip = offset % 16`, then adds the block offset to the last eight bytes of the IV as a big-endian counter. It returns the derived IV and the number of intra-block bytes the caller must discard from the CTR stream.

## State and Persistence Behavior
The helper is stateless and does not mutate the input IV. Derived IVs are often used transiently for range reads or stored in chunk metadata by higher-level SSE code depending on encryption mode.

## Dependencies and Integration Points
It depends only on glog and is called by SSE-C offset streams, SSE-KMS chunk/range handling, and SSE-S3 multipart helpers. The behavior is covered by CTR-specific tests.

## Risks and Edge Cases
Invalid IV length logs an error and returns the original IV with skip 0, leaving security/correctness enforcement to callers. Negative offsets are not explicitly rejected and would produce surprising arithmetic. Counter overflow beyond the last eight bytes is not surfaced as an error.

## Test Signals
`s3_sse_ctr_test.go` verifies skip calculations, block-aligned and non-block-aligned offsets, range simulations, and reader-based decryption behavior.
