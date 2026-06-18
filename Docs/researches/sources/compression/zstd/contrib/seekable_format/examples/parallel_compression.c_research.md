<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/examples/parallel_compression.c -->
# sources/compression/zstd/contrib/seekable_format/examples/parallel_compression.c

## Purpose
This example compresses independent frames in parallel and then writes a seekable zstd file with a generated seek table.

## Important APIs, Types, And Functions
It defines `state`, `job`, pending-list helpers, `compressFrame`, `finishFrame`, `compressFile_orDie`, and `main`. It uses zstd thread pool APIs, `ZSTD_compress`, `XXH64`, and raw seekable-table APIs `ZSTD_seekable_createFrameLog`, `ZSTD_seekable_logFrame`, and `ZSTD_seekable_writeSeekTable`.

## Control Flow
The main loop reads fixed-size frame chunks, submits jobs to a pool, and each job compresses/checksums its chunk. Completion inserts jobs into an ordered pending list protected by a mutex; contiguous completed IDs are flushed to output and logged. After joining workers, the seek table is serialized.

## State And Persistence
Runtime state includes output file, mutex, next frame ID, pending list, frame log, and per-job buffers. Persistent output is `<input>.zst` or stdout.

## Dependencies And Integration Points
It integrates zstd's pool/threading, xxHash, and seekable-format raw table API.

## Risks
Jobs call `exit` on failure from worker threads. Frame size must fit zstd compress bound into 32-bit table fields. Pending list ordering is essential for valid output.

## Test Signals
A produced file should be readable by seekable decompression examples/tests and preserve input bytes.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/examples/parallel_compression.c -->
