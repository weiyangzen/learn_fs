<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/examples/seekable_decompression_mem.c -->
# sources/compression/zstd/contrib/seekable_format/examples/seekable_decompression_mem.c

## Purpose
This example demonstrates in-memory seekable decompression for small seekable zstd files.

## Important APIs, Types, And Functions
It defines `MAX_FILE_SIZE`, allocation/file helpers, `decompressFile_orDie`, and `main`. It uses `ZSTD_seekable_initBuff` and `ZSTD_seekable_decompress`.

## Control Flow
The program reads the entire compressed file into memory, initializes the seekable object over that buffer, decompresses the requested range into an output buffer, and writes it to stdout.

## State And Persistence
State is the in-memory compressed file buffer, output range buffer, and seekable object. It persists no files.

## Dependencies And Integration Points
It depends on zstd static APIs and demonstrates the buffer-backed seekable API.

## Risks
It caps input size and requires the source buffer to remain alive while the seekable object is used. Large ranges allocate full decompressed output.

## Test Signals
Range comparisons with original data and parity with file-backed decompression validate this path.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/examples/seekable_decompression_mem.c -->
