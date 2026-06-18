# sources/distributed-fs/ceph-client/lib/fonts/font.h

## Purpose
Private font-library header defining the storage wrapper for compiled bitmap font data and stable indices for built-in fonts.

## Important APIs, Types, and Functions
Defines `FONT_EXTRA_WORDS`, `struct font_data` with `extra[4]` metadata and a flexible `data[]` byte array, and numeric index macros such as `VGA8x8_IDX`, `FONT10x18_IDX`, `TER16x32_IDX`, and `TER10x18_IDX`. It includes public `linux/font.h` for `struct font_desc`.

## Control Flow
No executable control flow. Font source files include this header to wrap glyph bytes and assign `font_desc.idx` values.

## State and Persistence
No mutable state. The macros and packed struct define compile-time data layout.

## Dependencies and Integration Points
Integrates with all `font_*.c` files and common font handling code. The `struct font_data` layout lets font blobs carry extra metadata before raw glyph bytes while still exposing `data` to `struct font_desc`.

## Risks
Index values must stay aligned with font registration/lookup expectations. Changing `struct font_data` packing or `FONT_EXTRA_WORDS` would affect every compiled font object. New fonts require coordinated Kconfig, Makefile, index, and descriptor updates.

## Test Signals
Compile all font objects, verify `font_desc.idx` uniqueness, and test font lookup/selection paths for each index. Static review should confirm new fonts update this header consistently.
