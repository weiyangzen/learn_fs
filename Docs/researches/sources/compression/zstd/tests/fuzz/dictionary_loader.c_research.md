# sources/compression/zstd/tests/fuzz/dictionary_loader.c

## Purpose
This target fuzzes dictionary loading paths by trying to use fuzz input as dictionary data for compression and decompression.

## APIs, control flow, and state
It defines helper functions `compress()` and `decompress()`. `compress()` creates a fresh `ZSTD_CCtx`, then either calls `ZSTD_CCtx_refPrefix_advanced()` or `ZSTD_CCtx_loadDictionary_advanced()` before `ZSTD_compress2()`. `decompress()` mirrors the choice with `ZSTD_DCtx_refPrefix_advanced()` or `ZSTD_DCtx_loadDictionary_advanced()`, then calls `ZSTD_decompressDCtx()`. `LLVMFuzzerTestOneInput()` uses `FUZZ_dataProducer_reserveDataPrefix()` so the prefix is source data and the suffix controls dictionary sizes, load method, content type, and prefix mode; it then asserts successful decompression size and byte equality when compression succeeds.

## Dependencies, risks, and test signals
Dependencies are zstd dictionary APIs and fuzz helpers. The target stresses dictionary validation more than compression ratio. Risks include many invalid dictionaries causing shallow coverage unless seeded with generated dictionaries. Findings include crashes, zstd assertions, and inconsistent successful round trips.
