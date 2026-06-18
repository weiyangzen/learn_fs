# sources/compression/xz/src/liblzma/lzma/lzma_encoder_presets.c

## Purpose
Maps user preset levels and the extreme flag to concrete `lzma_options_lzma` values for dictionary size, mode, match finder, nice length, and search depth.

## Important APIs, Types, And Functions
- `lzma_lzma_preset()` is the only function. It validates preset level/flags and fills `lzma_options_lzma`.

## Control Flow
The function masks the level and flags, rejects levels above 9 or unsupported flags, clears preset dictionary fields, sets default lc/lp/pb, chooses dictionary size from `dict_pow2`, then selects fast mode for levels 0-3 and normal mode for 4-9. With `LZMA_PRESET_EXTREME`, it forces normal mode/BT4 and overrides nice length/depth based on level.

## State And Persistence
No global mutable state. It writes the caller-provided options struct.

## Dependencies And Integration Points
Includes `common.h` for API types and constants. Used by higher-level preset configuration paths in applications and internal tests. `xz` needs it even in decode-only builds per file note.

## Risks
Preset choices are user-visible performance/ratio policy. Changing them can affect memory usage, compression ratio, speed, and compatibility expectations. Unsupported flag validation must reject unknown bits.

## Test Signals
Tests should verify all levels 0-9 and extreme combinations produce expected options, invalid levels/flags fail, and resulting options pass encoder validation and round-trip.
