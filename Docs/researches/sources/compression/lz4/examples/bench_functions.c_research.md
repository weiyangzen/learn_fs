# sources/compression/lz4/examples/bench_functions.c

## Purpose
This example explains and benchmarks the public compression/decompression call stack around `LZ4_compress_default()`. It demonstrates `LZ4_compress_fast()`, `LZ4_compress_fast_extState()`, `LZ4_decompress_safe()`, and deprecated `LZ4_decompress_fast()`.

## Important APIs, Types, and Functions
It includes `lz4.h` with `LZ4_DISABLE_DEPRECATE_WARNINGS`. Local helpers are `run_screaming()`, `usage()`, `CHECK`, and `bench()`. Function IDs select benchmark cases. `bench()` uses `LZ4_stream_t` for ext-state compression, `clock()` timing, `memcmp()` verification, and a recursive retry when timer resolution is too low.

## Control Flow
`main()` parses an optional iteration count, builds two static input strings, allocates destination and known-good compressed buffers, then validates each API against the known-good result. It runs two suites: normal text and highly compressible text. Each suite times compression variants and decompression variants, then prints a formatted table of total seconds, iterations per second, nanoseconds per iteration, and percentage of default.

## State and Persistence
All state is process-local heap or stack memory. No files are read or written. The only persistent effect is stdout.

## Dependencies and Integration Points
It integrates with `examples/Makefile` as the `bench_functions` binary and depends on LZ4 block APIs. It uses POSIX feature macros for `time.h` behavior and locale formatting.

## Risks
It compares full `max_dst_size` in warm-up checks for some compression paths, so zero-initialized buffers and deterministic output matter. `clock()` is low resolution on some platforms; the recursive iteration multiplier can grow until the assert guard. The program intentionally uses deprecated unsafe decompression to teach differences; that should not be copied into untrusted-input code.

## Test Signals
Successful execution prints benchmark sections for both source classes and exits zero. Any mismatch in compressed or decompressed output calls `run_screaming()` and exits with a failure code.
