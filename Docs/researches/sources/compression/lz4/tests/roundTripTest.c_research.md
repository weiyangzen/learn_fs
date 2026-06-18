# sources/compression/lz4/tests/roundTripTest.c

## Purpose
`roundTripTest.c` is a file-oriented round-trip validator intended for fuzzing workflows such as AFL. It reads one file, compresses it, decompresses it, and aborts on any corruption so fuzzing infrastructure records failures as crashes.

## Important APIs, Types, and Functions
Key functions are `roundTripTest()`, `roundTripCheck()`, `fileCheck()`, `loadFile()`, `getFileSize()`, `isDirectory()`, `select_clevel()`, and `main()`. Compression dispatches through a `compressFn`: levels at or above `LZ4HC_CLEVEL_MIN` use `LZ4_compress_HC`, while lower selected levels use `LZ4_compress_fast`. `XXH32` selects a deterministic compression level when the CLI level is zero.

## Control Flow, State, and Persistence
`main()` parses an optional `-#` level and a filename. `fileCheck()` gets file size, allocates a source buffer even for empty files, loads the full file, and calls `roundTripCheck()`. The compressed and result buffers are allocated at `LZ4_COMPRESSBOUND(srcSize)`. `roundTripTest()` compresses, safely decompresses, validates decompressed size, and scans for the first differing byte. State is heap-local and freed after each check; the input file is only read.

## Dependencies and Integration Points
The file uses `lz4.h`, `lz4hc.h`, `xxhash.h`, libc file I/O, and platform-specific stat variants for MSVC versus POSIX. It is a simple fuzz harness around public block APIs.

## Risks and Test Signals
Risks include `fclose(NULL)` if `fopen()` fails after `isDirectory()` is called, size truncation when very large files exceed `int`-based LZ4 APIs, and only one file processed per invocation. Strong signals are abort-on-corruption behavior, deterministic level selection from input bytes, exact decompressed size, and byte-position reporting for silent decoding differences.
