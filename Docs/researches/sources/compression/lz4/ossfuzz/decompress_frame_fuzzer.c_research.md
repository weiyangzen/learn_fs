# sources/compression/lz4/ossfuzz/decompress_frame_fuzzer.c

## Purpose
This harness sends arbitrary bytes through LZ4 frame decompression in several option combinations to ensure malformed or partial frames do not crash the frame decoder.

## Important APIs, Types, And Functions
The local `decompress()` helper resets a `LZ4F_dctx` and calls either `LZ4F_decompress()` or static `LZ4F_decompress_usingDict()`. `LLVMFuzzerTestOneInput()` uses producer helpers to choose destination capacity and dictionary size, then toggles `LZ4F_decompressOptions_t.stableDst`.

## Control Flow
The harness consumes seeds, allocates a destination buffer up to four times input size and a zero-filled dictionary up to 64 KB, then runs four decompression attempts: no dictionary with unstable and stable destination, and dictionary with unstable and stable destination. Return values are intentionally ignored because invalid input is expected.

## State, Persistence, And Dependencies
One frame decompression context is reused across the four attempts, with explicit reset before each attempt. Dictionary contents are synthetic zero bytes. There is no persistent state beyond heap allocations.

## Integration Points
This target requires `LZ4F_STATIC_LINKING_ONLY` for dictionary decompression and links against frame internals. It exercises decoder paths that ordinary round-trip tests may not reach.

## Risks
The helper ignores consumed sizes and errors, so it is a crash-only target rather than a semantic validator. Zero-size allocations are asserted. Very large fuzz inputs can amplify allocation size through the `4 * size` capacity expression.

## Test Signals
Findings include decoder crashes, sanitizer errors, invalid memory reads under dictionary modes, and state-reset regressions between repeated decompression attempts.
