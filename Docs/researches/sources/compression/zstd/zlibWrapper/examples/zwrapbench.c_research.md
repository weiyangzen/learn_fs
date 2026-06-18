<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/examples/zwrapbench.c -->
# sources/compression/zstd/zlibWrapper/examples/zwrapbench.c

## Purpose
`zwrapbench.c` is a benchmark and validation command-line tool for comparing native Zstandard, native zlib, and the Zstandard zlib wrapper under multiple usage styles. It can benchmark synthetic data or one or more input files, optionally with a dictionary, and reports compression ratio plus compression/decompression speed.

## Important APIs, Types, and Functions
The file defines `blockParam_t` to track each independently compressed block and `BMK_compressor` to select benchmark mode: native `ZSTD_CCtx`, native `ZSTD_CStream`, native zlib, zlib through the wrapper, and context-reuse variants. `BMK_benchMem()` is the central benchmark loop. `BMK_benchCLevel()` runs the selected level range across all implementations. `BMK_loadFiles()`, `BMK_benchFileTable()`, and `BMK_syntheticTest()` prepare inputs. `main()` parses flags including `-D`, `-b`, `-e`, `-i`, `-B`, verbosity, and recursion when file-list support is compiled in.

## Control Flow
`main()` builds the file table, dictionary path, compression level range, block size, and run duration, then calls `BMK_benchFiles()`. File mode loads inputs into a bounded memory buffer; synthetic mode generates random data with `RDG_genBuffer()`. `BMK_benchCLevel()` then iterates through compressor families. `BMK_benchMem()` splits inputs into blocks, allocates compressed and regenerated buffers, repeatedly compresses blocks until the timing window closes, then repeatedly decompresses and checks the regenerated buffer with `XXH64`.

## State and Persistence
Global state controls display level, block size, iteration duration, compressibility, and hidden additional parameters. The benchmark keeps all test data in memory and writes no benchmark outputs other than terminal output. It mutates the wrapper's process-global switches via `ZWRAP_useZSTDcompression()` and `ZWRAP_setDecompressionType()`, so benchmark modes are process-global rather than thread-local.

## Dependencies and Integration Points
The tool depends on Zstandard internals (`ZSTD_STATIC_LINKING_ONLY`), zlib API calls from the wrapper header, `datagen`, `xxhash`, `timefn`, and local utility helpers. It is an integration exercise for `zstd_zlibwrapper.c`: wrapper modes call normal `deflate*()` and `inflate*()` entry points after toggling wrapper behavior.

## Risks
The benchmark assumes in-memory workloads and may reduce input size when memory is unavailable, which can make large-file results less representative. The wrapper toggles are not thread-safe, although this tool is single-threaded. Dictionary reuse paths intentionally change behavior after the first block for wrapper/ZSTD modes, so comparisons should be read as specific API-usage scenarios rather than pure codec comparisons. `while (!cCompleted | !dCompleted)` uses bitwise OR on booleans, which works but is easy to misread.

## Test Signals
The strongest built-in test signal is checksum validation after decompression. It also tests dictionary paths, stream and one-shot ZSTD APIs, zlib and wrapper deflate/inflate APIs, context creation/reset/reuse, block sizing, file loading, and synthetic data generation.
<!-- END_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/examples/zwrapbench.c -->
