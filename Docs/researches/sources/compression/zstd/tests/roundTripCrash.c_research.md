# sources/compression/zstd/tests/roundTripCrash.c

Purpose: This standalone test program loads a file, compresses and decompresses it with zstd, verifies exact round-trip equality, and deliberately crashes or exits on corruption. It is suitable for fuzzing and crash-focused regression detection.

Important APIs and functions: `roundTripTest()` uses `ZSTD_compress()` and `ZSTD_decompress()` with a compression level derived from an XXH32 hash of up to the first 128 bytes. `cctxParamRoundTripTest()` uses `ZSTD_CCtx`, `ZSTD_CCtx_params`, `ZSTD_CCtxParams_setParameter()`, `ZSTD_CCtx_setParametersUsingCCtxParams()`, and `ZSTD_compressStream2()` with workers and overlap settings. `roundTripCheck()` allocates buffers, dispatches the selected compression path, checks size and bytes through `checkBuffers()`, and frees buffers. File helpers determine regular-file size, reject directories, and load the input.

Control flow: `main()` requires an input file and optionally consumes `--cctxParams`. It then calls `fileCheck()`, which loads the file into memory and calls `roundTripCheck()`. Any zstd error, regenerated-size mismatch, byte mismatch, file-read failure, or allocation failure exits nonzero. In fuzzing builds, `crash()` calls `abort()` instead of `exit()`.

State and persistence: All buffers are heap-local to a single run and freed on success. No output file is written. The only persistent effect is process termination status or crash.

Dependencies and integration points: Depends on zstd static-linking declarations, `xxhash.h`, standard C file/stat APIs, and optional `FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION`. It integrates with fuzzing or test scripts that provide candidate input files.

Risks and test signals: `rBuff` is allocated with compressed-bound capacity, which is at least source size for zstd but is conceptually a decompression output buffer. The `--cctxParams` path uses multithreaded compression parameters, so builds without threading support may behave differently. Error messages precede nonzero exit or abort; success writes "no pb detected" to stderr.
