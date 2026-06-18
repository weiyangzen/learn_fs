# sources/cloud-native/nydus/rafs/src/mock/mock_chunk.rs

## Purpose
`mock_chunk.rs` defines a test-oriented chunk metadata object that implements both generic `BlobChunkInfo` and v5-specific `BlobV5ChunkInfo`. It lets RAFS metadata and IO-vector tests exercise chunk access without loading a real bootstrap or blob metadata.

## Important APIs, Types, And Functions
`MockChunkInfo` stores digest, blob index, chunk index, file offset, compressed and uncompressed offsets and sizes, flags, and CRC32. `MockChunkInfo::mock` constructs a chunk with caller-provided offsets and sizes while leaving other fields at defaults. The `BlobChunkInfo` implementation exposes digest, id, compression/encryption/batch status, CRC32 behavior, downcast support, blob index, compressed offsets/sizes, and uncompressed offsets/sizes. The `BlobV5ChunkInfo` implementation exposes v5 chunk index, file offset, flags, and a base trait view.

## Control Flow
Tests or mock inodes construct `MockChunkInfo` directly, optionally mutate private fields from the module's tests, and pass it through `MockInode` into `rafsv5_alloc_bio_vecs` or other code that expects trait objects. Calls are simple accessors; no IO or validation is performed.

## State And Persistence
All state is in-memory test data. No persistent metadata is read or written. CRC32 is only reported when the `HAS_CRC32` flag is set. Encryption and batch status always return false regardless of flags other than compression and CRC32.

## Dependencies And Integration Points
The mock depends on `nydus_utils::digest::RafsDigest`, `storage::device::{BlobChunkInfo, BlobChunkFlags}`, and `storage::device::v5::BlobV5ChunkInfo`. It is used by `mock_inode.rs` and tests that need v5 chunk behavior.

## Risks
The mock intentionally under-models production chunks: it never reports encryption or batch chunks, does not validate offsets, and defaults digest/blob/index fields unless tests set them. Tests relying on this mock should not be interpreted as coverage for encrypted, batch, zran, or malformed chunk metadata.

## Test Signals
The unit test builds a chunk, sets digest/blob/index/compression fields, checks base and v5 trait accessors, verifies downcasting, compressed and uncompressed end helpers, and confirms file offset propagation.
