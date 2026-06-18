# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_draw.h

## Purpose

This header provides common bit-address, masking, endian, palette, and reversal helpers for the generic packed-pixel framebuffer drawing engines. The complete 163-line source was read.

## Important APIs, Types, and Functions

Important APIs include `fb_address_move_long()`, `fb_address_forward()`, `fb_address_backward()`, `fb_comp()`, `fb_modify_offset()`, `fb_palette()`, `fb_right()`, `fb_left()`, `struct fb_reverse`, `fb_reverse_bits_long()`, `fb_reverse_long()`, `fb_pixel_mask()`, and `fb_reverse_init()`.

## Control Flow

Drawing engines initialize `struct fb_address`, move it by bit offsets, compute masks for leading/trailing partial words, read-modify-write masked regions, fetch pseudo-palettes for true/direct color images, and use `fb_reverse_init()` to determine whether byte or pixel bit order must be reversed for the current framebuffer.

## State and Persistence Behavior

No global state exists. The helpers operate on transient address cursors and framebuffer words.

## Dependencies and Integration Points

It depends on `struct fb_info`, endian configuration, `fb_be_math()`, optional architecture bit-reverse acceleration, `FB_REV_PIXELS_IN_BYTE`, and memory-specific read/write functions supplied by including headers. It is shared by copy, fill, and imageblit templates.

## Risks and Edge Cases

Bit-direction helpers are endian-dependent, so subtle mistakes affect every generic drawing operation. Reverse-pixel support is compiled only when enabled; drivers setting `FB_NONSTD_REV_PIX_IN_B` without the symbol will not get pixel reversal. Masking and address movement must remain valid for non-word-aligned framebuffer bases.

## Test Signals

Unit-style golden tests should cover little and big endian builds, native and foreign framebuffer endian settings, reverse-pixel low-bpp modes, masked writes at every bit offset, and address movement across word boundaries.
