# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_fillrect.h

## Purpose

This header implements generic packed-pixel rectangle fill and invert operations for fbdev drawing helpers. It supports copy and XOR raster operations, arbitrary bpp up to the word size, endian conversion, low-bpp reverse pixel order, and optimized static-pattern paths for power-of-two bpp modes. The complete 279-line source was read.

## Important APIs, Types, and Functions

Important functions and types include `fb_invert_offset()`, `struct fb_pattern`, `fb_pattern_get()`, `fb_pattern_get_reverse()`, `fb_pattern_static()`, `fb_pattern_rotate()`, `pixel_to_pat()`, `bitfill()`, `bitinvert()`, `fb_fillrect_static()`, `fb_rotate()`, `fb_fillrect_rotating()`, and the entry `fb_fillrect(struct fb_info *p, const struct fb_fillrect *rect)`.

## Control Flow

The entry point converts the requested color to a repeated word pattern, initializes framebuffer address and reversal state, adjusts for rectangle x/y and line length, then chooses static or rotating pattern fill depending on bpp alignment. Copy fills overwrite masked/full words; XOR fills invert only the bits selected by the pattern. Each line advances by the framebuffer line length in bits.

## State and Persistence Behavior

There is no global state. It mutates framebuffer memory and uses temporary pattern/address state.

## Dependencies and Integration Points

The header depends on `fb_draw.h`, memory-specific read/write accessors, fbdev visual/bpp fields, `fb_be_math()`, and caller-provided `struct fb_fillrect`. It is used by `cfbfillrect.c` and system-memory equivalents.

## Risks and Edge Cases

Risks include color pattern generation for unusual bpp values such as 3, 6, 12, or 24, endian shifts on big-endian builds, XOR behavior with masks, and off-by-one errors at rectangle edges. The helper expects valid rectangle geometry; wrappers do not clip.

## Test Signals

Use randomized golden tests for copy and XOR fills across bpp values, all x bit offsets, odd widths/heights, foreign endian settings, reverse-pixel low-bpp modes, and 32/64-bit word sizes.
