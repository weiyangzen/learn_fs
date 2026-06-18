# sources/compression/lz4/tests/fullbench.c

## Purpose
`fullbench.c` is an executable speed analyzer for LZ4 block, HC, dictionary, and frame APIs. It reads real input files, chunks them, runs selected compressors and decompressors repeatedly, reports throughput and ratios, and verifies decompressed data with checksums.

## Important APIs, Types, and Functions
`fullSpeedBench()` is the main benchmark engine. Descriptor tables `compDescArray` and `decDescArray` map CLI-selectable numeric IDs to local wrappers around `LZ4_compress_default`, `LZ4_compress_destSize`, `LZ4_compress_fast`, external-state/streaming variants, HC variants, `LZ4F_compressFrame`, `LZ4F_compressUpdate`, safe/fast dictionary decompressors, partial decompressors, and frame decompressors. `chunkParameters` stores per-chunk original and compressed buffers and sizes.

## Control Flow, State, and Persistence
`main()` parses options such as `-c#`, `-d#`, `-i#`, `-B#`, `-l`, and `--no-prompt`, then passes filenames to `fullSpeedBench()`. Each file is opened, sized with `UTIL_getFileSize()`, limited by `BMK_findMaxMem()`, read into memory, split by `g_chunkSize`, and benchmarked for `g_nbIterations` timed loops. Compression output is later regenerated with default LZ4 for decompression tests. Global LZ4 stream/context objects are reused between iterations where APIs require state.

## Dependencies and Integration Points
It uses `platform.h`, `util.h`, `lz4.h`, `lz4hc.h`, `lz4frame.h`, and `xxhash.h`. It intentionally defines `LZ4_malloc`, `LZ4_calloc`, and `LZ4_free` to exercise `LZ4_USER_MEMORY_FUNCTIONS` builds. Non-DLL builds also benchmark hidden force-ext-dict entry points.

## Risks and Test Signals
Benchmark numbers are sensitive to CPU scheduling, clock granularity, file size, and memory pressure. Some partial decompression wrappers opt out of checksum validation because they intentionally decode less than the full output. Correctness signals include nonzero compression sizes, exact decompressed sizes, XXH32 equality for checked paths, and frame input-consumption checks. Resource risks include large allocations up to the memory cap and process exits on benchmark failures.
