# sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_ctr_test.go

## Purpose
This test file validates the shared AES-CTR IV offset logic used by SSE-C, SSE-KMS, and SSE-S3 range and multipart paths. It specifically guards non-block-aligned range decryption.

## Important APIs, Types, and Functions
The production API under test is `calculateIVWithOffset(baseIV []byte, offset int64) ([]byte, int)`. Tests are `TestCalculateIVWithOffset`, `TestCTRDecryptionWithNonBlockAlignedOffset`, `TestCTRRangeRequestSimulation`, and `TestCTRDecryptionWithIOReader`.

## Control Flow
Tests generate keys, IVs, and deterministic plaintext, encrypt full buffers with AES-CTR, then simulate reads from many offsets. For each offset, they derive an adjusted IV and skip value, start ciphertext reads at the block-aligned offset, decrypt, discard skip bytes, and compare with the original plaintext slice.

## State and Persistence Behavior
There is no persistent state. Random keys/IVs and plaintext/ciphertext buffers live only within the test process.

## Dependencies and Integration Points
The test depends on Go AES/CTR and the shared helper in `s3_sse_utils.go`. It protects S3 range-request behavior and multipart chunk decryption in all server-side encryption modes that use CTR.

## Risks and Edge Cases
The tests cover positive offsets but not negative offsets or IV counter overflow. Subtest names derived from runes are not very descriptive for large offsets, but failures still include offset values. The tests model the caller-side requirement that ciphertext fetches begin at the block boundary, not at the requested byte offset.

## Test Signals
Passing tests signal that skip equals `offset % 16`, block-aligned offsets need no skip, non-aligned offsets decrypt correctly after discarding intra-block bytes, and range reads across block boundaries match plaintext exactly.
