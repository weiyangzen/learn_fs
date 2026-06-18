# sources/compression/zstd/tests/fuzz/zstd_frame_info.c

## Purpose

`zstd_frame_info.c` fuzzes zstd helper functions that inspect compressed-frame metadata. It intentionally feeds arbitrary input to fast metadata APIs to ensure they handle invalid, empty, truncated, and valid frame data safely.

## Important APIs And Functions

The entry point calls `ZSTD_getFrameContentSize()`, `ZSTD_getDecompressedSize()`, `ZSTD_findFrameCompressedSize()`, `ZSTD_getDictID_fromFrame()`, `ZSTD_findDecompressedSize()`, `ZSTD_decompressBound()`, `ZSTD_frameHeaderSize()`, `ZSTD_isFrame()`, `ZSTD_getFrameHeader()`, and `ZSTD_getFrameHeader_advanced()` with `ZSTD_f_zstd1`.

## Control Flow

For zero-size input, the source pointer is set to `NULL` before calling metadata helpers. All helper return values are ignored except for avoiding crashes; a local `ZSTD_FrameHeader` receives parsed header results where applicable.

## State And Persistence

This target has no persistent state and performs no allocation. It only uses stack state for the frame header.

## Dependencies And Integration Points

It depends on `fuzz_helpers.h` and `zstd_helpers.h`, which enable zstd static APIs. It complements decompression fuzzers by covering metadata-only code paths commonly used for preflight sizing, dictionary ID discovery, and frame identification.

## Risks And Edge Cases

Edges include NULL source with zero size, magicless data, skippable frames, truncated headers, concatenated frames, unknown content size, malformed frame descriptors, and very large size calculations. Since return values are not cross-validated here, logical consistency is checked in other targets such as `simple_decompress.c`.

## Test Signals

The expected signal is no crash, assertion, or sanitizer finding across all helper calls. Valid-frame corpus entries are useful for reaching deeper header parsing, while malformed short inputs stress bounds checks.
