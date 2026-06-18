# sources/compression/lz4/examples/simple_buffer.c

## Purpose
This example demonstrates the simplest block compression/decompression workflow with `LZ4_compress_default()` and `LZ4_decompress_safe()`.

## Important APIs, Types, and Functions
It uses `LZ4_compressBound()`, `LZ4_compress_default()`, and `LZ4_decompress_safe()`. Local `run_screaming()` prints an error and exits. Standard library dependencies are `malloc()`, `realloc()`, `free()`, `strlen()`, `memcmp()`, and `printf()`.

## Control Flow
`main()` defines a string, computes `src_size`, allocates a destination using `LZ4_compressBound()`, compresses, shrinks the compressed buffer with `realloc()`, allocates a regeneration buffer of the known original size, safely decompresses, frees compressed data, verifies decompressed size and byte equality, then prints the regenerated string.

## State and Persistence
State is heap allocated and freed within the process. There are no files or external state.

## Dependencies and Integration Points
It is the basic block API teaching sample in `examples/Makefile`. It also demonstrates the important integration rule that LZ4 blocks do not carry their own original size, so callers need external metadata.

## Risks
The example assumes `realloc()` failure loses the original pointer and exits, which is acceptable for a short sample but not ideal production ownership handling. It uses a known source string; real applications must store or transmit both compressed size and decompressed bound.

## Test Signals
Successful execution prints a compression ratio, decompression success, validation success, and the original string.
