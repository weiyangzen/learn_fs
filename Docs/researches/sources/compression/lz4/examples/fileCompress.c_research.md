# sources/compression/lz4/examples/fileCompress.c

## Purpose
This example uses the higher-level `lz4file.h` API to compress and decompress a file through FILE-like wrapper functions, then verifies the round trip.

## Important APIs, Types, and Functions
It uses `LZ4_writeFile_t`, `LZ4_readFile_t`, `LZ4F_writeOpen()`, `LZ4F_write()`, `LZ4F_writeClose()`, `LZ4F_readOpen()`, `LZ4F_read()`, `LZ4F_readClose()`, `LZ4F_isError()`, and `LZ4F_getErrorName()`. Local helpers are `get_file_size()`, `compress_file()`, `decompress_file()`, and `compareFiles()`.

## Control Flow
`main()` derives `.lz4` and `.lz4.dec` filenames. `compress_file()` opens an LZ4 file writer with default preferences, reads 16 KiB chunks from input, writes each chunk, closes the writer, and reports errors. `decompress_file()` opens an LZ4 reader, repeatedly reads decompressed chunks, writes them to the output file, then closes the reader. Finally, `compareFiles()` checks decoded content against the original.

## State and Persistence
It writes a frame-formatted `<input>.lz4` file and decoded `<input>.lz4.dec`. Heap state is limited to one chunk buffer and the LZ4 file contexts.

## Dependencies and Integration Points
It depends on `lz4file.h`, which wraps the frame API around standard C `FILE*` I/O. The examples Makefile validates the produced `.lz4` with the `lz4` CLI.

## Risks
Some `fopen()` results are asserted or checked inconsistently. The error reporting in `main()` passes integer return codes to `LZ4F_getErrorName()`, which is not meaningful for local `1` failures. The ratio calculation divides by original file size and can misbehave for empty input.

## Test Signals
Success prints compression stats, `decompress : done`, and `verify : OK`; `lz4 -vt <input>.lz4` should also validate the frame.
