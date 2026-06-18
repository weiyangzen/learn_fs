<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/examples/parallel_processing.c -->
# sources/compression/zstd/contrib/seekable_format/examples/parallel_processing.c

## Purpose
This example demonstrates parallel random access over a seekable zstd file by summing bytes in each frame independently.

## Important APIs, Types, And Functions
It defines `sum_job`, `sumFrame`, `sumFile_orDie`, and `main`, using `ZSTD_seekable_initFile`, `ZSTD_seekable_getNumFrames`, `ZSTD_seekable_getFrameDecompressedSize`, and `ZSTD_seekable_decompressFrame`.

## Control Flow
The program opens the seekable file, reads the frame count, creates one job per frame, and runs jobs in a zstd pool. Each job opens its own file handle and seekable object, decompresses one frame, computes a byte sum, and stores it for final aggregation.

## State And Persistence
State is per-job frame number/sum plus transient decompressed buffers. It does not modify files.

## Dependencies And Integration Points
It depends on zstd's pool and seekable decompression API. It illustrates multi-reader integration for applications that process frames independently.

## Risks
Opening the file once per job is simple but expensive. Very large frames allocate full decompressed frame buffers.

## Test Signals
Running it on a known seekable file should produce a deterministic sum; comparing with an uncompressed byte-sum validates correctness.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/examples/parallel_processing.c -->
