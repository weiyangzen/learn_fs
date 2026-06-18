# sources/compression/lz4/tests/fuzzer.c

## Purpose
`fuzzer.c` is the broad randomized regression driver for the raw LZ4 block and LZ4HC APIs. It combines deterministic unit tests, generated corpora, dictionary scenarios, streaming/ring-buffer paths, low-address buffers, malformed input, and destination-boundary checks.

## Important APIs, Types, and Functions
Major routines are `FUZ_unitTests()`, `FUZ_test()`, `FUZ_AddressOverflow()`, `FUZ_fillCompressibleNoiseBuffer()`, `FUZ_createLowAddr()`, and `main()`. It exercises default, fast, destSize, external-state, fast-reset, HC, HC destSize, streaming, dictionary attach/load, safe/fast/partial decompression, safe/fast continue, and HC continue APIs. It uses `XXH32`/`XXH64` for reference checks and directly inspects HC context cleanliness through static-linking-only internals.

## Control Flow, State, and Persistence
`main()` parses seed, count, duration, start cycle, compressibility, verbosity, and pause flags. Unless a seed/start cycle is supplied, it runs unit tests at default and optimal-min HC levels, then enters `FUZ_test()`. The randomized loop chooses block size, source offset, dictionary size, compression level, low-address placement, and corruption cases from a deterministic PRNG. State is in heap buffers, LZ4 streams, HC streams, low-address mmap or malloc buffers, checksums, and counters for compression ratios. No artifacts are persisted.

## Dependencies and Integration Points
The file depends on `platform.h`, `util.h`, `lz4.h`, `lz4hc.h`, `xxhash.h`, and `sys/mman.h` on Unix/AIX for low-address testing. It targets sanitizer and CI integration by aborting/`exit(1)` on the first invariant violation and printing seed/cycle coordinates.

## Risks and Test Signals
Covered risks include output/input overrun, too-small buffer success, exact-boundary failure handling, NULL/empty input behavior, address-space overflow on 32-bit builds, decoder shortcut OOB regressions, context dirty-state leaks, dictionary attach mismatches, ring-buffer decoder desynchronization, and HC destSize edge cases. Remaining risks are runtime cost, nondeterminism when seed is omitted, and platform differences in mmap. Signals are canary preservation, exact return sizes, checksum equality, expected failures on malformed data, and reproducible seed/cycle output.
