# sources/compression/lz4/examples/print_version.c

## Purpose
This trivial example prints the linked LZ4 library version number.

## Important APIs, Types, and Functions
The only LZ4 API used is `LZ4_versionNumber()` from `lz4.h`. `main()` ignores its arguments and calls `printf()`.

## Control Flow
Execution is a single call to `printf("Hello World ! LZ4 Library version = %d\n", LZ4_versionNumber())`, then return zero.

## State and Persistence
There is no state and no persistent output beyond stdout.

## Dependencies and Integration Points
It is built by `examples/Makefile` and provides a minimal compile/link smoke test for `lz4.h` and the linked library.

## Risks
It validates only that the symbol is available and callable; it does not confirm ABI compatibility beyond returning an integer.

## Test Signals
`make test` runs it first. Expected output contains `LZ4 Library version =` followed by a numeric version.
