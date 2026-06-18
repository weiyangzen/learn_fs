# sources/compression/zstd/tests/fuzz/block_decompress.c

## Purpose
This libFuzzer target throws arbitrary input at `ZSTD_decompressBlock()` to ensure block decompression rejects or handles malformed raw blocks without crashing.

## APIs, control flow, and state
`LLVMFuzzerTestOneInput()` creates a `FUZZ_dataProducer_t` from the input only to randomize allocation behavior, ensures a reusable `rBuf` of `ZSTD_BLOCKSIZE_MAX`, creates/reuses `ZSTD_DCtx`, calls `ZSTD_decompressBegin()`, and invokes `ZSTD_decompressBlock(dctx, rBuf, neededBufSize, src, size)`. In non-`STATEFUL_FUZZING` builds it frees `dctx` after each input; `rBuf` remains process-global unless grown/replaced.

## Dependencies, risks, and test signals
Dependencies are zstd static APIs, `fuzz_helpers`, and `fuzz_data_producer`. The target intentionally ignores decompression return errors, treating only sanitizer/assert crashes as findings. Risks are persistent globals under stateful fuzzing and the block API requiring initialized history. A pass means no crash, assert, or sanitizer finding for the input.
