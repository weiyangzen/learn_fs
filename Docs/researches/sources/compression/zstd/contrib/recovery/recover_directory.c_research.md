<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/recovery/recover_directory.c -->
# sources/compression/zstd/contrib/recovery/recover_directory.c

## Purpose
`recover_directory.c` recovers individual files from a concatenated multi-frame zstd file, such as output from recursive zstd compression.

## Important APIs, Types, And Functions
It defines `ZstdFrames`, `usage`, `readFile`, `computePadding`, and `main`. It uses `ZSTD_findFrameCompressedSize`, `ZSTD_createDCtx`, `ZSTD_decompressStream`, and zstd utility file-size helpers.

## Control Flow
The program reads the whole archive into memory, walks frames to count them and find max frame size, allocates an output name buffer and decompression buffer, then iterates frames. Each frame is decompressed into `${PREFIX}<padded-index>` with a reset dctx.

## State And Persistence
State includes the full compressed file in memory, a reusable decompression buffer, output filename buffer, and dctx. Persistent effects are recovered output files.

## Dependencies And Integration Points
It depends on zstd static APIs and `util.h`. It is a standalone contrib utility for disaster recovery or archive inspection.

## Risks
It loads the entire input file into memory and exits on first error. It assumes each frame maps to one desired output file and does not recover original filenames.

## Test Signals
Manual tests should create a multi-frame zstd file, run recovery, and compare each recovered file with expected frame payloads.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/recovery/recover_directory.c -->
