# sources/compression/zstd/tests/fuzz/dictionary_stream_round_trip.c

## Purpose
This target validates streaming compression/decompression round trips when dictionaries are involved.

## APIs, control flow, and state
It defines stream buffer helpers and uses global `ZSTD_CCtx`, `ZSTD_DCtx`, `cBuf`, `rBuf`, and `bufSize`. The compression path feeds selected chunk sizes through `ZSTD_compressStream2()`/end semantics with dictionary parameters; the decompression path reads back through streaming APIs with the matching dictionary. `LLVMFuzzerTestOneInput()` reserves bytes for the data producer, sizes buffers, chooses dictionary and streaming parameters, and asserts regenerated content matches input.

## Dependencies, risks, and test signals
Dependencies are zstd streaming/dictionary APIs, `zstd_helpers`, and `fuzz_data_producer`. Risks include chunk-size choices hiding edge cases and global buffers under stateful fuzzing. Pass signals are no zstd errors on expected-success paths and exact round-trip equality.
