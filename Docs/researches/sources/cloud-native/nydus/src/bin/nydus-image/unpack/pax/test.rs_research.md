# sources/cloud-native/nydus/src/bin/nydus-image/unpack/pax/test.rs

## Purpose
`pax/test.rs` unit-tests `ChunkReader`, the streaming adapter that turns RAFS blob chunks into regular-file tar data for unpacking.

## Important APIs, Types, And Functions
`MockBlobReader` implements `BlobReader` over an in-memory `Vec<u8>`. `MockChunkInfo` implements enough of `BlobChunkInfo` to describe chunk offsets, sizes, blob index, and compression state. Tests are `test_read_chunk`, `test_read_chunk_smaller_buffer`, `test_read_chunk_larger_buffer`, `test_read_chunk_zero_buffer`, and `test_read_chunk_compress`. Helpers `create_default_chunk_reader` and `create_compress_chunk_reader` construct readers for uncompressed multi-chunk and gzip-compressed single-chunk cases.

## Control Flow
The default reader concatenates two 256-byte chunks and provides two metadata entries. Tests read with buffers equal to, smaller than, larger than, and zero relative to chunk boundaries to verify cursor carryover and EOF behavior. The compressed test compresses four 256-byte blocks with gzip, marks the metadata compressed, and verifies decompressed output across multiple reads.

## State And Persistence
All state is in memory. `MockBlobReader` stores source bytes and metrics; `MockChunkInfo` stores static metadata. The tests do not write files or use real backends.

## Dependencies And Integration Points
The tests depend on `BlobReader`, `BlobChunkInfo`, `BackendMetrics`, `nydus_utils::compress`, and the private `ChunkReader` from `pax.rs`. They exercise the same `Read` interface used by `tar::Builder::append` for regular file payloads.

## Risks
Several trait methods are left as `todo!()` because current tests do not call them; future `ChunkReader` changes could accidentally hit those paths and panic. `MockBlobReader::try_read` uses `clone_from_slice` into the full destination buffer, which assumes the selected data slice length equals the buffer length; it works for these offsets/sizes but is not a general short-read mock. Tests do not cover backend read errors, missing blob indexes, missing compressors, encrypted chunks, batch chunks, or CRC validation.

## Test Signals
The file itself is the test signal for chunk-boundary read correctness and decompression. Passing tests indicate that `ChunkReader` can stream contiguous uncompressed chunks and one compressed chunk into arbitrary caller buffer sizes.
