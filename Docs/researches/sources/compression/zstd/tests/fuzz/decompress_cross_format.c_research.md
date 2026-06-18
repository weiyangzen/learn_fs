# sources/compression/zstd/tests/fuzz/decompress_cross_format.c

## Purpose
This target cross-checks standard zstd frame decompression against magicless zstd frame decompression.

## APIs, control flow, and state
The fuzzer reserves a prefix for parameter data, treats the remaining bytes as magicless compressed data, prepends `ZSTD_MAGICNUMBER` to create a standard frame candidate, and uses `ZSTD_findFrameCompressedSize()` to truncate to one frame. It then reuses a `ZSTD_DCtx` to test one-shot `ZSTD_decompressDCtx()` in `ZSTD_f_zstd1` and `ZSTD_f_zstd1_magicless` modes, followed by streaming `ZSTD_decompressStream()` in both modes. If both accept, it asserts equal decompressed size and bytes; if one accepts, the other is expected to accept in the checked direction.

## Dependencies, risks, and test signals
Dependencies are zstd static format parameter APIs and allocation helpers. State is the reusable `dctx` plus per-input buffers. Risks include assuming little-endian magic-number memory layout and very large `dstSize` selection (`0..10*size`). Test signals are cross-format accept/reject consistency and identical output for accepted frames.
