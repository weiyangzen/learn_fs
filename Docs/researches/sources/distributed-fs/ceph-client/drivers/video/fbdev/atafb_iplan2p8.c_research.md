# sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb_iplan2p8.c

## Purpose
This file implements Atari 8 bpp drawing for the 8-plane, 2-byte-interleaved layout used by 256-color planar modes. It provides copy, solid fill, and 1-bit image expansion for fbdev operations.

## Important APIs, types, and functions
The exported entry points are `atafb_iplan2p8_copyarea()`, `atafb_iplan2p8_fillrect()`, and `atafb_iplan2p8_linefill()`. `BPL` is set to 8 before `atafb_utils.h`, causing color expansion and masked-copy helpers to operate on four `u32` plane words per 16-pixel group.

## Control flow
`copyarea()` handles same-alignment and shifted-alignment cases separately, and chooses forward or reverse traversal for overlap safety. Full aligned groups are copied as repeated `u32` moves. Edge and shifted cases use masks and four carry words so each plane remains in the correct byte lane. `fillrect()` expands an 8-bit color into four plane masks, then fills leading, full, and trailing pixel groups. `linefill()` expands 1-bit source masks into foreground/background plane words.

## State and persistence behavior
No driver state is retained. The only durable effect is modification of framebuffer memory.

## Dependencies and integration points
This is called from `atafb.c` for 8 bpp modes. It depends on fbdev structures, the prototypes in `atafb.h`, and `atafb_utils.h` generated inline helpers.

## Risks and edge cases
The 8-plane variant has the broadest memory write footprint per pixel group, so stride errors and off-by-one calculations can overwrite adjacent lines quickly. Misaligned copies depend on four carry values and two complementary masks; regressions are likely to show as color-plane swapping, vertical streaks, or damaged edge columns.

## Test signals
Use 8 bpp console and graphics tests covering palette entries above 15, solid fills for multiple colors, glyph expansion with distinct foreground/background colors, overlapping scroll in both directions, and x coordinates/widths that begin or end on 8-pixel halves.
