<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/zstdseek_compress.c -->
# sources/compression/zstd/contrib/seekable_format/zstdseek_compress.c

## Purpose
`zstdseek_compress.c` implements seekable-format compression and raw seek-table serialization.

## Important APIs, Types, And Functions
It defines `framelogEntry_t`, `ZSTD_frameLog`, `ZSTD_seekable_CStream`, frame-log allocation/free helpers, `ZSTD_seekable_create/freeCStream`, `ZSTD_seekable_initCStream`, `ZSTD_seekable_logFrame`, `ZSTD_seekable_compressStream`, `ZSTD_seekable_endFrame`, `ZSTD_seekable_writeSeekTable`, and `ZSTD_seekable_endStream`.

## Control Flow
Initialization resets frame counters, validates max frame size, configures checksum, and initializes zstd cstream. `compressStream` limits input to the current frame budget, updates compressed/decompressed sizes and optional XXH64 checksum, and ends the frame when full. `endFrame` flushes zstd, logs frame metadata, and resets for the next frame. `writeSeekTable` streams a skippable seek table incrementally, preserving position across small output buffers. `endStream` finishes the final frame then writes the table.

## State And Persistence
The cstream stores a zstd stream, frame log vector, current frame sizes, checksum state, max frame size, and seek-table write cursor. Persistent output is zstd frames followed by the serialized seek table.

## Dependencies And Integration Points
It depends on zstd static APIs, `zstd_errors.h`, `mem.h`, xxHash, and `zstd_seekable.h`. Examples and tests call both high-level streaming and raw frame-log APIs.

## Risks
Frame counts and sizes are bounded by `ZSTD_SEEKABLE_MAXFRAMES` and 32-bit fields. Incremental table writing is offset-sensitive. Empty input still logs an empty frame, which tests expect to begin with a zstd magic header.

## Test Signals
`seekable_tests.c` validates round trip, table metadata, malformed input behavior, empty compression, and repeated range reads; parallel compression example exercises raw frame-log serialization.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/zstdseek_compress.c -->
