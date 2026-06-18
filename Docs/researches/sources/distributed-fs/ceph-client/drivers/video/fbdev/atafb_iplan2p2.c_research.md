# sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb_iplan2p2.c

## Purpose
This file implements low-level fbdev drawing for Atari interleaved bitplanes with 2 planes and 2-byte interleave. It handles 2 bpp copy, rectangle fill, and monochrome glyph/image expansion into planar memory.

## Important APIs, types, and functions
The exported functions are `atafb_iplan2p2_copyarea()`, `atafb_iplan2p2_fillrect()`, and `atafb_iplan2p2_linefill()`. The file sets `BPL` to 2 before including `atafb_utils.h`, which specializes inline helpers such as `expand8_col2mask`, `expand16_col2mask`, `fill8_col`, `fill8_2col`, `fill16_col`, and `memmove32_col` for two planes.

## Control flow
`copyarea()` determines whether the copy is upward/forward or downward/reverse and whether source and destination have compatible 16-pixel alignment. Compatible copies use direct 32-bit moves for full 16-pixel groups and masked column copies for edge halves. Odd/even misaligned copies rebuild shifted plane words with masks and carry values per row. `fillrect()` fills an optional leading 8-pixel half group, a run of 16-pixel groups, and an optional trailing half group. `linefill()` expands 1-bit source data into foreground/background color planes for an optional leading half group, 16-pixel groups, and a trailing half group.

## State and persistence behavior
The functions mutate only the framebuffer memory addressed by `info->screen_base`. No persistent software state is stored. All operation state is stack-local and derived from coordinates, width, height, color, and `next_line`.

## Dependencies and integration points
The file depends on fbdev types, `atafb.h` prototypes, and `atafb_utils.h` specialization through `BPL`. It is called by `atafb.c` when the active mode is 2 bpp and not Falcon 16 bpp.

## Risks and edge cases
The implementation assumes the caller has clipped rectangles and that widths passed to monochrome source expansion are compatible with the font/image data. The copy path contains pointer arithmetic with reverse traversal and masks; off-by-one errors would show as corrupted edge columns or overlap artifacts. Casts between byte pointers and `u32 *` rely on architecture alignment tolerance matching the Atari/m68k target.

## Test signals
Exercise 2 bpp fbcon glyph drawing, rectangle clears, horizontal and vertical overlapping scrolls, unaligned x coordinates, widths crossing 8- and 16-pixel boundaries, and reverse copies where destination is below or to the right of source.
