# sources/compression/lz4/ossfuzz/compress_fuzzer.c

## Purpose
This harness fuzzes basic LZ4 block compression with destination buffers ranging from zero to the compression bound. It verifies round trips for successful compression and for `LZ4_compress_destSize()`.

## Important APIs, Types, And Functions
`LLVMFuzzerTestOneInput()` calls `LZ4_compressBound()`, `LZ4_compress_default()`, `LZ4_compress_destSize()`, `LZ4_decompress_safe()`, `FUZZ_dataProducer_retrieve32()`, and `FUZZ_getRange_from_uint32()`.

## Control Flow
The first producer value selects destination capacity. The remaining producer size becomes the effective input size. Regular compression may fail when the destination is too small; success must decompress to the full effective size. If `dstCapacity > 0`, `compress_destSize()` must succeed, update `compressedSize`, and decompress to exactly that prefix.

## State, Persistence, And Dependencies
Only per-call heap buffers and the producer are allocated. There is no shared state or filesystem behavior.

## Integration Points
This is the basic block-compressor OSS-Fuzz target and exercises the same block format later consumed by `decompress_fuzzer.c` and round-trip tests.

## Risks
Like other producer-based harnesses, control bytes are not advanced out of the `data` pointer, only out of the size. Zero-byte input and zero-byte output rely on platform malloc behavior because the harness asserts returned pointers. `size_t` inputs are narrowed to `int` in LZ4 calls, so practical fuzzing depends on OSS-Fuzz input-size limits.

## Test Signals
Strong signals are compression crashes, successful output that cannot decode, `destSize` returning non-positive for positive capacity, and corruption in decoded prefixes.
