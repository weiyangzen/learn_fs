# sources/compression/zstd/tests/fuzz/raw_dictionary_round_trip.c

## Purpose

`raw_dictionary_round_trip.c` validates zstd compression and decompression with raw-content dictionaries and prefixes. It splits fuzz input into source and dictionary regions, compresses with one of the raw dictionary attachment modes, decompresses with the matching mode, and asserts source recovery.

## Important APIs And Functions

The entry point is `LLVMFuzzerTestOneInput()`. `roundTripTest()` configures the shared `ZSTD_CCtx` and `ZSTD_DCtx`, using `FUZZ_setRandomParameters()`, `ZSTD_CCtx_refPrefix_advanced()`, `ZSTD_CCtx_loadDictionary_advanced()`, `ZSTD_compress2()`, `ZSTD_DCtx_refPrefix_advanced()`, `ZSTD_DCtx_loadDictionary_advanced()`, and `ZSTD_decompressDCtx()`.

The fuzz target also integrates optional sequence-producer hooks via `FUZZ_SEQ_PROD_SETUP()` and `FUZZ_SEQ_PROD_TEARDOWN()`.

## Control Flow

The fuzzer reserves input-prefix bytes for parameter production, then selects a source size inside the remaining data. Bytes after the source become the raw dictionary. It allocates decompression output sized to the source and a compressed buffer of `ZSTD_compressBound(srcSize)` minus a random zero or one byte. Checksum is disabled to allow the slightly smaller buffer in cases where frame overhead remains sufficient.

For each run, it picks either prefix reference mode or dictionary load mode. Compression must succeed. Decompression is configured with the same raw dictionary content type and then must return exactly the source size and identical bytes.

## State And Persistence

`cctx` and `dctx` are static and may persist across calls under `STATEFUL_FUZZING`; otherwise they are freed after each input. Optional third-party sequence producer state is created and destroyed per test case. Source, dictionary, compressed, and decompressed buffers are per input.

## Dependencies And Integration Points

This target depends on zstd public/experimental dictionary APIs, random parameter helpers, fuzz helper assertions, and optional third-party sequence producers. It exercises both dictionary-by-reference prefix behavior and load-method variation for raw-content dictionaries.

## Risks And Edge Cases

Key edges include empty source, empty dictionary, dictionary equal to source tail, random load methods, checksum-disabled small compressed buffers, persistent context reset behavior, and mismatched prefix/load configuration. Because dictionary memory points into the fuzzer input, reference modes also test lifetime assumptions during a single call.

## Test Signals

Valid signals are exact decompressed size and byte equality. Failures indicate dictionary attachment/load regressions, raw dictionary decode mismatch, parameter interactions that break round trips, or sequence-producer fallback issues when custom producers are enabled.
