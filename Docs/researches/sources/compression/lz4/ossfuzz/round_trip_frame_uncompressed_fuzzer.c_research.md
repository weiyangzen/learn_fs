# sources/compression/lz4/ossfuzz/round_trip_frame_uncompressed_fuzzer.c

## Purpose
This target fuzzes the frame API sequence that mixes compressed updates with an explicitly uncompressed block segment, then verifies the whole frame round trips.

## Important APIs, Types, And Functions
The file uses `LZ4F_createCompressionContext()`, `LZ4F_compressBegin()`, `LZ4F_compressUpdate()`, `LZ4F_uncompressedUpdate()`, `LZ4F_compressEnd()`, `LZ4F_decompress()`, and `LZ4F_freeCompressionContext()`. It also includes `lz4frame_static.h` for the uncompressed-update API.

## Control Flow
`compress_independent_block_mode()` builds producer-driven preferences and forces independent block mode. `compress_round_trip()` consumes seeds to choose an uncompressed slice, emits a frame header, compresses bytes before the slice, writes the slice uncompressed, compresses bytes after it, ends the frame, then loops `LZ4F_decompress()` until completion and compares against the original.

## State, Persistence, And Dependencies
State is the producer, compression context, decompression context, compressed buffer, and round-trip buffer. There is no filesystem persistence.

## Integration Points
This target exercises a frame static API not covered by simple `LZ4F_compressFrame()` fuzzers and specifically requires block-independent frames.

## Risks
The decompression helper advances `dstPtr` without explicit final size comparison; corruption is caught by full `memcmp`, but overrun protection depends on `LZ4F_decompress()` respecting capacity. As with other producer harnesses, size is reduced but `data` is not pointer-advanced. The producer is freed inside `compress_round_trip()`, so callers must not reuse it.

## Test Signals
Useful signals include uncompressed block encoding crashes, invalid mixed frames, decompression loop stalls, and corruption around the uncompressed slice boundaries.
