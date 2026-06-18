# sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb_iplan2p4.c

## Purpose
This file implements Atari 4 bpp drawing for the 4-plane, 2-byte-interleaved framebuffer layout used by ST low, TT mid, Falcon 16-color-style modes, and related planar configurations.

## Important APIs, types, and functions
It exports `atafb_iplan2p4_copyarea()`, `atafb_iplan2p4_fillrect()`, and `atafb_iplan2p4_linefill()`. It sets `BPL` to 4 and reuses the generic static inline planar helpers from `atafb_utils.h`. With `BPL > 2`, the helper macros expand colors into two `u32` plane words per 16-pixel group.

## Control flow
The structure mirrors the 2-plane helper. `copyarea()` splits same-parity copies from odd/even shifted copies, chooses forward or reverse direction for overlap safety, and copies full groups with direct word moves plus masked column helpers on edges. Misaligned copies carry two plane words (`pval[0]` and `pval[1]`) as they shift data between source and destination positions. `fillrect()` and `linefill()` process a leading half group, full 16-pixel groups, and a trailing half group.

## State and persistence behavior
All state is transient except for writes into framebuffer memory. The functions do not maintain hardware or driver state.

## Dependencies and integration points
The implementation depends on `atafb_utils.h` inline generation with `BPL == 4`, fbdev data structures, and the `atafb.c` dispatcher. It is part of the Atari fbdev software drawing path rather than hardware acceleration.

## Risks and edge cases
The main risk is corruption on boundary conditions: source/destination x alignment differing by 8 pixels, trailing widths not divisible by 16, reverse-overlap copies, and plane-word ordering. Since it writes multiple plane words per logical pixel group, any mismatch with `next_line` or `xres_virtual` produces visually scrambled color planes.

## Test signals
Run 4 bpp fbcon and fbtest patterns, especially scrollback, rectangle clear, stippled glyphs, color palette changes, odd x offsets, and overlapping copies across 8/16-pixel edges.
