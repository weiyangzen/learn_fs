# sources/compression/zstd/tests/fuzz/dictionary_decompress.c

## Purpose
This fuzz target attempts dictionary-aware decompression of arbitrary input to catch crashes and invalid memory access in dictionary decompression paths. It trains a dictionary from the fuzz input rather than fuzzing an unrelated external dictionary file.

## APIs, control flow, and state
It keeps a global `ZSTD_DCtx`. `LLVMFuzzerTestOneInput()` reserves a data prefix for compressed bytes, calls `FUZZ_train(src, size, producer)` to create a `FUZZ_dict_t`, then randomly chooses between creating a `ZSTD_DDict`, loading a dictionary into the dctx with `ZSTD_DCtx_loadDictionary_advanced()`, or referencing a prefix with `ZSTD_DCtx_refPrefix_advanced()`. It allocates a random destination size in `0..10*size`, then calls either `ZSTD_decompress_usingDDict()` or `ZSTD_decompressDCtx()`. Return errors are acceptable; sanitizer failures are findings. Non-stateful builds free the dctx after each input.

## Dependencies, risks, and test signals
Dependencies are `zstd_helpers`, `fuzz_helpers`, `fuzz_data_producer`, and optional third-party sequence producer setup macros. Risks include limited semantic assertions because arbitrary compressed data is often invalid, and very large destination choices for large inputs. The target is valuable for dictionary loader modes, dictionary header handling, and dctx reuse/reset behavior. Pass means no crash or sanitizer report.
