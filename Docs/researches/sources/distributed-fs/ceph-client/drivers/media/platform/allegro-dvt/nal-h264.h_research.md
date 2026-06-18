# sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/nal-h264.h

## Purpose

`nal-h264.h` declares C structs for H.264 SPS, PPS, VUI, and HRD syntax and provides inline mapping helpers from V4L2 codec/color controls to H.264 bitstream numeric values.

## Important APIs, Types, And Symbols

- `struct nal_h264_hrd_parameters`, `struct nal_h264_vui_parameters`, `struct nal_h264_sps`, and `struct nal_h264_pps` model H.264 syntax elements.
- Inline mapping helpers include `nal_h264_profile()`, `nal_h264_level()`, `nal_h264_full_range()`, `nal_h264_color_primaries()`, `nal_h264_transfer_characteristics()`, and `nal_h264_matrix_coeffs()`.
- Public function declarations cover SPS/PPS/filler read and write helpers plus print prototypes.

## Control Flow

The inline helpers use switch statements to convert V4L2 enum values into H.264 profile ids, level ids, color primaries, transfer characteristics, matrix coefficients, and full-range flags. The structs are consumed by `nal-h264.c` syntax walkers.

## State And Persistence

The header defines data layouts and pure conversions only. No state is stored globally or persistently.

## Dependencies And Integration Points

It depends on V4L2 control and pixel format enums. `allegro-core.c` fills these structs from current channel controls and colorimetry, then passes them to `nal_h264_write_*()`. The helpers also rely on V4L2 default color mapping macros for default transfer/ycbcr settings.

## Risks

The structs contain fixed-size arrays for HRD and slice-group data; parser code must constrain syntax counts before indexing. Some mappings default to generic values rather than returning errors, which improves tolerance but can hide unsupported color metadata. The declared `nal_h264_print_sps()` and `nal_h264_print_pps()` prototypes are not implemented in the researched object list, so callers outside this module must not rely on them unless another translation unit supplies them.

## Test Signals

Unit tests should check V4L2-to-H.264 mappings for common colorimetry and all supported profiles/levels. Build/link tests should catch accidental use of undeclared or unimplemented print helpers. Bitstream tests should verify generated SPS/PPS values match channel settings.
