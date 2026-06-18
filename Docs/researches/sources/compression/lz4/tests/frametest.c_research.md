# sources/compression/lz4/tests/frametest.c

## Purpose
`frametest.c` is the randomized and deterministic test driver for the `lz4frame` API. It verifies one-shot frames, streaming compression/decompression, dictionaries, checksums, skippable frames, custom allocators, context size accounting, and decoder recovery after errors.

## Important APIs, Types, and Functions
Key entry points are `unitTests()`, `fuzzerTests()`, `test_lz4f_decompression()`, `test_lz4f_decompression_wBuffers()`, `bug1227()`, and `main()`. It exercises `LZ4F_compressFrame`, `LZ4F_compressBegin`, `LZ4F_compressUpdate`, `LZ4F_uncompressedUpdate`, `LZ4F_flush`, `LZ4F_compressEnd`, `LZ4F_getFrameInfo`, `LZ4F_decompress`, `LZ4F_decompress_usingDict`, `LZ4F_createCDict`, `LZ4F_compressFrame_usingCDict`, `LZ4F_cctx_size`, and `LZ4F_dctx_size`. `Test_alloc_state` tracks custom allocator live bytes.

## Control Flow, State, and Persistence
The unit phase allocates a 2 MB compressible-noise buffer, computes an XXH64 reference checksum, and executes fixed API edge cases. The fuzzer phase builds a 9 MB corpus and loops by count or duration, deriving source windows, preferences, flush behavior, and corruption patterns from a deterministic PRNG. Contexts are reused but reset after errors. State is in heap buffers, LZ4F contexts, custom allocator bookkeeping, global display/pause flags, and PRNG seeds; no durable data is written.

## Dependencies and Integration Points
The file includes `lz4frame.h` multiple times, including static-linking declarations, to validate header safety. It integrates `lz4file.h` write helpers, `lz4.h` constants, and `xxhash` checksums. CLI flags (`-i`, `-T`, `-s`, `-t`, `-P`, `-v`, `-q`, `--no-prompt`) make failures reproducible by seed and test number.

## Risks and Test Signals
Important risks covered include incomplete headers, wrong content size checks, checksum failures, overrun on small dst buffers, stale decompression context state after errors, dictionary regression, allocator accounting drift, and skippable-frame parsing. Some paths intentionally ignore the exact error from noisy input because sanitizer safety is the goal. Strong signals are checksum equality, sentinel-byte preservation, exact input consumption, expected `LZ4F_ERROR_frameHeader_incomplete`, and seeded reproduction.
