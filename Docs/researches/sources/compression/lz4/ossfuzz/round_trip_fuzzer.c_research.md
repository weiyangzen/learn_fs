# sources/compression/lz4/ossfuzz/round_trip_fuzzer.c

## Purpose
This harness validates raw LZ4 block compression, full decompression, and partial decompression under multiple dictionary pointer configurations.

## Important APIs, Types, And Functions
It uses `LZ4_compress_default()`, `LZ4_decompress_safe()`, `LZ4_decompress_safe_partial()`, and `LZ4_decompress_safe_partial_usingDict()` with no dictionary, small and large prefix dictionaries, and small and large external dictionaries.

## Control Flow
The producer chooses a partial-output size. Compression is done into a buffer preceded by a large prefix area. Full decompression must match the input. Then six partial-decompression variants decode exactly `partialCapacity` bytes and compare that prefix with the original.

## State, Persistence, And Dependencies
The harness allocates one compressed buffer with prefix space, one external dictionary buffer, one full round-trip buffer, and separate partial buffers for each variant. State is not retained between inputs.

## Integration Points
This is the success-path counterpart to `decompress_fuzzer.c`, proving that valid compressed blocks remain decodable across partial and dictionary APIs.

## Risks
The prefix buffers are allocated but not initialized before being offered as dictionaries; for this compressed data they should not be referenced, but the setup may still exercise decoder assumptions. Zero partial capacity leads to `malloc(0)` assertions. Dictionary content is unrelated to the block unless generated references require it.

## Test Signals
Signals include compression failure despite bounded output, full round-trip corruption, partial decode length mismatch, and dictionary-mode partial decode regressions.
