# sources/compression/zstd/tests/fuzz/block_round_trip.c

## Purpose
This fuzz target validates raw block compression/decompression round trips.

## APIs, control flow, and state
`roundTripTest()` starts block compression with `ZSTD_compressBegin_advanced()`, calls `ZSTD_compressBlock()`, and if the block is uncompressible (`ret == 0`) copies the source directly to the result. Otherwise it calls `ZSTD_decompressBegin()` and `ZSTD_decompressBlock()`. `LLVMFuzzerTestOneInput()` reserves a prefix for randomized parameters, chooses a compression level, caps source size to `ZSTD_BLOCKSIZE_MAX`, allocates reusable `cBuf`/`rBuf`, creates contexts, and asserts decompressed size and bytes equal the input.

## Dependencies, risks, and test signals
Dependencies include `zstd_helpers`, `fuzz_third_party_seq_prod`, and the sequence producer setup/teardown macros. Risks include buffer sizing based on original input before cap, block-only semantics not including frame checksums, and global contexts under stateful fuzzing. Strong findings are zstd errors in expected-success paths, size mismatch, or byte corruption.
