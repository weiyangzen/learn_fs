<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/zstd_seekable.h -->
# sources/compression/zstd/contrib/seekable_format/zstd_seekable.h

## Purpose
`zstd_seekable.h` declares the public API and format constants for zstd's seekable format, which splits compressed data into independently compressed frames followed by a seek table.

## Important APIs, Types, And Functions
It declares `ZSTD_seekable_CStream`, `ZSTD_seekable`, `ZSTD_seekTable`, `ZSTD_frameLog`, compression APIs, raw frame-log/seek-table APIs, buffer/file/custom decompression initialization, range/frame decompression APIs, frame metadata accessors, `offsetToFrameIndex`, and custom read/seek callback types.

## Control Flow
Compression clients create/init a cstream, call `compressStream`, optionally `endFrame`, then repeat `endStream` until the current frame and seek table are flushed. Decompression clients initialize from a buffer, FILE, or callbacks, then decompress ranges or whole frames using seek-table metadata.

## State And Persistence
Opaque objects hold stream state, seek-table metadata, callback/file references, and decompressor reuse state. The persistent on-disk format stores zstd frames plus a final skippable seek table.

## Dependencies And Integration Points
It depends on `zstd.h` and C stdio. Examples, tests, and `zstdseek_compress.c` implement/use this contract.

## Risks
Compressed/decompressed frame sizes are stored in bounded fields; callers must keep backing buffers/files alive for initialized objects. API is contrib-level and less stable than core zstd.

## Test Signals
`seekable_tests.c` and examples validate compression, seek-table metadata, buffer/file/custom input, and range/frame decompression.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/zstd_seekable.h -->
