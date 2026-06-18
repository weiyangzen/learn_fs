# sources/compression/lz4/ossfuzz/round_trip_stream_fuzzer.c

## Purpose
This harness fuzzes streaming compression and decompression for both fast LZ4 and HC LZ4, including prefix mode, external dictionary mode, loaded dictionaries, and attached dictionary streams.

## Important APIs, Types, And Functions
It defines cursor structs and `state_t` to hold fast and HC compression streams, a decode stream, input, compressed output, round-trip output, seed, and HC level. It uses `LZ4_createStream()`, `LZ4_createStreamHC()`, `LZ4_createStreamDecode()`, `LZ4_resetStream_fast()`, `LZ4_resetStreamHC_fast()`, `LZ4_compress_fast_continue()`, `LZ4_compress_HC_continue()`, `LZ4_decompress_safe_continue()`, `LZ4_loadDict()`, `LZ4_loadDictHC()`, `LZ4_attach_dictionary()`, and `LZ4_attach_HC_dictionary()`.

## Control Flow
`LLVMFuzzerTestOneInput()` consumes a deterministic seed, creates state, then runs eight round-trip modes. Each mode resets streams to the same seed, may trim a dictionary prefix into the expected output, compresses random chunk sizes, immediately decompresses each emitted block, and finally compares the rebuilt data against the original.

## State, Persistence, And Dependencies
State is explicit in `state_t` and is recreated per fuzz input. Some modes copy input into a second buffer and alternate source addresses to force external dictionary behavior. No file state is used.

## Integration Points
This is the deepest OSS-Fuzz coverage for streaming APIs in `lz4.c` and `lz4hc.c`, including static-linking-only attach APIs.

## Risks
`state_create()` asserts `state.cstream` twice and never asserts `state.cstreamHC`, so HC stream allocation failure would not be caught at the intended point. Random chunk size can be zero; compression APIs must handle that consistently. Output buffer sizing uses a margin rather than exact proof.

## Test Signals
Signals include stream reset bugs, dictionary attach/load mismatches, ext-dict boundary errors, decompression continuation failures, and corruption after alternating source buffers.
