# sources/compression/lz4/ossfuzz/compress_frame_fuzzer.c

## Purpose
This harness fuzzes `LZ4F_compressFrame()` with randomized frame preferences and possibly undersized output buffers. If compression succeeds, it requires the compressed frame to decompress exactly back to the input.

## Important APIs, Types, And Functions
`LLVMFuzzerTestOneInput()` uses `FUZZ_dataProducer_create()`, `FUZZ_dataProducer_preferences()`, `FUZZ_getRange_from_uint32()`, `LZ4F_compressFrameBound()`, `LZ4F_compressFrame()`, `LZ4F_isError()`, and `FUZZ_decompressFrame()`.

## Control Flow
The producer consumes control bytes from the end of the fuzz input to choose preferences and a destination-capacity seed. The remaining bytes are treated as payload. The destination size is selected from `[0, compressBound]`. Compression errors are accepted; successful frames are decompressed and compared with `memcmp`.

## State, Persistence, And Dependencies
State is per-input heap allocation for the producer, compressed buffer, and round-trip buffer. Frame decompression state is hidden inside `FUZZ_decompressFrame()`. There is no persistent corpus mutation or file state.

## Integration Points
The target links against liblz4 frame APIs and common fuzz helpers. It complements `round_trip_frame_fuzzer.c`, which always allocates enough output and expects compression success.

## Risks
The source pointer passed to compression remains the original `data`, while `size` is reduced after consuming producer bytes, so control bytes are still in the prefix of the compressed payload and only the tail of the input length is considered. Zero-size malloc behavior is asserted non-null, which can vary by C library.

## Test Signals
Useful findings include crashes on small output capacities, invalid successful frames, frame preference edge cases, checksum modes, and mismatches after decompression.
