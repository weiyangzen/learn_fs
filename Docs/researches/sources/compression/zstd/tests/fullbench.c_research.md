# sources/compression/zstd/tests/fullbench.c

## Purpose
`fullbench.c` is a standalone zstd speed analyzer. It benchmarks many compression, decompression, streaming, block-internal, and sequence APIs over generated samples or user-provided files.

## Important APIs, types, and scenarios
The benchmark framework centers on `PrepResult`, function-pointer types `PrepFunction_f`, `BenchedFunction_f`, `VerifFunction_f`, and `BenchScenario`. `kScenarios` maps numeric scenario IDs to named benchmark functions such as `compress`, `decompress`, `compress_freshCCtx`, `decompressDCtx`, `compressContinue`, streaming variants, `compress2`, multi-thread `compressStream2`, sequence compression, sequence/literal conversion, and internal literal/sequence header decode scenarios when not built as a DLL import.

## Control flow and state
Global contexts `g_zcc`, `g_zdc`, `g_cstream`, and `g_dstream` are lazily allocated in `benchMem()` and freed after each scenario. Prep functions build suitable input: compressed frames for decompression, first-block literal/sequence slices for internal decoders, generated sequence buffers for sequence APIs, copied input for normal compression, or intentionally shortened output capacity. `benchMem()` configures compression parameters on contexts, prepares data, warms the destination buffer, runs `BMK_benchTimedFn()`, tracks the best ns/run, optionally verifies output with `check_compressedSequences`, and prints MB/s.

## CLI, dependencies, and integration
`main()` parses `-b#`, `-l#`, `-P#`, `-B#`, `-i#`, help flags, pause, and `--zstd=` parameter strings for window/hash/chain/search/minMatch/targetLength/strategy/level. With no files it calls `benchSample()` using lorem or RDG-generated data; with files it calls `benchFiles()`, loading as much as memory allows via `BMK_findMaxMem()`. Dependencies include zstd public and internal headers, `benchfn`, `benchzstd`, `datagen`, `lorem`, and platform `util`.

## Risks and test signals
This is benchmark code, so global contexts and process-level state are acceptable but not thread-safe. Risks include internal API churn, skipped scenarios when prep cannot produce compressed internals, large memory allocation, and benchmark results being sensitive to CPU/load. Validation signals are no zstd errors, optional sequence verification passing, and coherent speed output for selected scenarios.
