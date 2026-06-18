<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/examples/seekable_compression.c -->
# sources/compression/zstd/contrib/seekable_format/examples/seekable_compression.c

## Purpose
This example shows basic streaming compression into the zstd seekable format.

## Important APIs, Types, And Functions
It defines allocation/file helpers, `compressFile_orDie`, `createOutFilename_orDie`, and `main`. It uses `ZSTD_seekable_createCStream`, `ZSTD_seekable_initCStream`, `ZSTD_seekable_compressStream`, and `ZSTD_seekable_endStream`.

## Control Flow
The program reads an input file in chunks, feeds the seekable compressor until input is consumed, flushes the stream/table with repeated `endStream` calls, and writes output to `<input>.zst`.

## State And Persistence
State is input/output FILEs, input/output buffers, and a seekable compression stream. Persistent output is the compressed seekable file.

## Dependencies And Integration Points
It depends on zstd static APIs and `zstd_seekable.h`. It is the simplest producer example for downstream users.

## Risks
It exits on errors and is not designed as a robust CLI. Frame-size choices trade random-access granularity against ratio.

## Test Signals
Output should decompress with seekable decompression examples and pass byte comparison with the source.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/examples/seekable_compression.c -->
