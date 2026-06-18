<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/examples/seekable_decompression.c -->
# sources/compression/zstd/contrib/seekable_format/examples/seekable_decompression.c

## Purpose
This example extracts a byte range from a seekable zstd file using file-backed random access.

## Important APIs, Types, And Functions
It defines allocation/file helpers, `fseek_orDie`, `decompressFile_orDie`, and `main`. It uses `ZSTD_seekable_create`, `ZSTD_seekable_initFile`, and `ZSTD_seekable_decompress`.

## Control Flow
The program opens a seekable file, initializes a seekable decompressor, allocates an output buffer for the requested range, decompresses from start offset to end offset, and writes bytes to stdout.

## State And Persistence
State is a FILE handle, seekable object, and output buffer. It writes decompressed bytes to stdout only.

## Dependencies And Integration Points
It integrates the public file-based seekable decompression API with standard stdio.

## Risks
Large requested ranges allocate full output size. It assumes valid numeric offsets and exits on first error.

## Test Signals
Comparing extracted ranges with the original uncompressed file validates correctness.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/examples/seekable_decompression.c -->
