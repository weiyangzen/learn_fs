<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/SkippableFrame.h -->
# sources/compression/zstd/contrib/pzstd/SkippableFrame.h

## Purpose
`SkippableFrame.h` declares pzstd's small metadata frame placed before each zstd frame to enable parallel decompression.

## Important APIs, Types, And Functions
`SkippableFrame` exposes `kSize`, the constructor, `tryRead`, `data`, and `frameSize`. Constants include zstd skippable magic `0x184D2A50` and a 4-byte content-size field.

## Control Flow
Callers construct a header with the compressed frame size, write `data()`, and later call `tryRead` on 12 bytes from input to recover the next frame size.

## State And Persistence
The object is a fixed-size byte array plus numeric frame size. Persisted output is embedded in pzstd streams as skippable frames.

## Dependencies And Integration Points
It depends on pzstd `ByteRange`. It is central to `Pzstd.cpp` compression output and decompression frame discovery.

## Risks
The format is pzstd-specific and only backward-compatible as a zstd skippable frame. Consumers must still handle normal zstd streams without these headers.

## Test Signals
Pzstd round-trip and fallback tests validate that headers are generated and interpreted correctly.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/SkippableFrame.h -->
