# sources/compression/lz4/programs/bench.c

## Purpose
`bench.c` implements the LZ4 command-line benchmark engine. It measures compression and decompression speed, compression ratio, dictionary effects, checksum correctness, decode-only frame speed, and synthetic lorem-ipsum input when no files are supplied.

## Important APIs, Types, And Functions
Public setters include `BMK_setNotificationLevel`, `BMK_setAdditionalParam`, `BMK_setNbSeconds`, `BMK_setBlockSize`, `BMK_setBenchSeparately`, `BMK_setDecodeOnlyMode`, and `BMK_skipChecksums`. The main public entry point is `BMK_benchFiles()`. Internally, `compressionParameters` selects no-stream, fast-stream, or HC-stream functions. `BMK_benchMem()` performs timed loops and validation. Helpers load files, choose max memory, run level ranges, and generate synthetic data.

## Control Flow
`BMK_benchFiles()` clamps levels, optionally loads the last 64 KB of a dictionary file, then benchmarks files together, separately, or synthetic data. `BMK_benchMem()` splits input into blocks, allocates compressed and result buffers, initializes compression state, times repeated compression loops and decompression loops, adapts loop counts toward one-second runs, prints progress, and verifies XXH64 checksums unless decode-only mode is active.

## State, Persistence, And Dependencies
Global settings control display level, duration, block size, separate-file mode, decode-only mode, checksum skipping, and an output-format parameter. `g_dctx` is a process-global frame decompression context and is not freed in this file. Persistent state is limited to reading input and dictionary files; benchmark results are printed.

## Integration Points
The CLI calls this module through `bench.h`. It depends on platform utilities, timing helpers, lorem generation, `xxhash.h`, `lz4.h`, `lz4hc.h`, and `lz4frame.h`. It exercises both normal and HC compression APIs, streaming dictionary attach APIs, and frame decompression for decode-only benchmarks.

## Risks
The code exits the process on many errors through `END_PROCESS()`, so it is not library-friendly. Memory sizing is complex and depends on `LZ4_MAX_INPUT_SIZE`, `maxMemory`, block count, and decode multiplier. `LZ4_isError(errcode)` is defined as `errcode == 0` for compression return values, which is local and easy to confuse with frame error semantics.

## Test Signals
Run synthetic benchmarks, multi-file benchmarks, separate-file mode, custom block sizes, dictionary benchmarks, HC level ranges, decode-only frame benchmarks with and without checksum skipping, quiet output mode, and checksum-corruption tests.
