# sources/compression/zstd/tests/fuzz/decompress_dstSize_tooSmall.c

## Purpose
This target verifies behavior when decompression destination capacity is smaller than the original input size.

## APIs, control flow, and state
It uses global `ZSTD_CCtx` and `ZSTD_DCtx`. For each input it compresses data into a buffer sized by `ZSTD_compressBound(size)`, chooses or derives a destination capacity smaller than `size`, and calls decompression APIs to ensure they fail safely rather than writing past the destination. It uses `FUZZ_dataProducer_t` for parameter choices.

## Dependencies, risks, and test signals
Dependencies are zstd one-shot compression/decompression APIs and fuzz helpers. State is reusable contexts, freed when not stateful. The important signal is that undersized destinations produce zstd errors or safe behavior under sanitizers. Risks are low coverage for exact boundary sizes unless corpus generation explores them.
