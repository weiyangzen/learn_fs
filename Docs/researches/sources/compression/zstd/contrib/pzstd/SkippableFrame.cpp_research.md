<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/SkippableFrame.cpp -->
# sources/compression/zstd/contrib/pzstd/SkippableFrame.cpp

## Purpose
This file implements pzstd's 12-byte skippable-frame header used to prefix each independently compressed frame with its compressed size.

## Important APIs, Types, And Functions
It implements `SkippableFrame::SkippableFrame(uint32_t size)` and static `SkippableFrame::tryRead(ByteRange bytes)`.

## Control Flow
The constructor writes little-endian magic, payload-size field, and next-frame size into the fixed array. `tryRead` validates byte count, magic, and payload-size field, returning the encoded frame size or `0` when the bytes are not a pzstd header.

## State And Persistence
State is the frame-size field and a 12-byte array embedded in the object. The bytes become persistent only when `writeFile` writes them to an output stream.

## Dependencies And Integration Points
It depends on `mem.h` little-endian helpers and `Range`. Compression writes these headers; decompression uses them to split frames for parallelism.

## Risks
A legitimate following frame size of zero is indistinguishable from invalid/missing header. Sizes are limited to 32 bits, constraining frame sizing.

## Test Signals
Round-trip pzstd tests exercise writing/reading headers; fallback decompression behavior covers invalid header paths.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/SkippableFrame.cpp -->
