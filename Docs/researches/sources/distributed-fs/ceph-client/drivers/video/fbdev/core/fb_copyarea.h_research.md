# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_copyarea.h

## Purpose

This header implements the generic packed-pixel area-copy engine used by I/O-memory and system-memory fbdev helpers. It handles overlapping copies, bit-aligned and unaligned sources/destinations, native or foreign endian framebuffers, optional reverse pixel order within bytes, and 32/64-bit word operations. The complete 405-line source was read.

## Important APIs, Types, and Functions

Important helpers include `fb_copy_offset_masked()`, `fb_copy_offset()`, `fb_copy_aligned_fwd()`, `fb_copy_aligned_rev()`, `fb_copy_aligned()`, `fb_copy_fwd()`, `fb_copy_rev()`, `fb_copy()`, and the entry point `fb_copyarea(struct fb_info *p, const struct fb_copyarea *area)`. It relies on `struct fb_address`, `struct fb_reverse`, `fb_address_forward()`, `fb_address_backward()`, `fb_pixel_mask()`, `fb_reverse_long()`, `fb_modify_offset()`, and memory-specific `fb_read_offset()`/`fb_write_offset()`.

## Control Flow

The entry point initializes source and destination bit addresses from `screen_base`, adjusts them by source/destination coordinates and line length, chooses reverse-copy direction when destination overlaps after source in memory, and then calls `fb_copy()`. The copy engine chooses aligned fast paths when source and destination bit offsets match, otherwise it merges adjacent source words into destination words while preserving leading/trailing masked bits. Reverse copy mirrors the process from the end of each line to avoid corrupting overlapping regions.

## State and Persistence Behavior

No global state is kept. The engine mutates framebuffer memory and uses transient bit-address cursors and masks.

## Dependencies and Integration Points

The header depends on `fb_draw.h` for endian and bit helpers and on a memory accessor header such as `cfbmem.h` or `sysmem.h`. It is included into wrapper C files so the same algorithm can target I/O or system memory.

## Risks and Edge Cases

This is performance-sensitive bit arithmetic. Risks include off-by-one errors at word boundaries, incorrect reverse direction for overlapping copies, source reads at offset `-1` in unaligned paths requiring the initial aligned cursor to make that safe, low-bpp reverse-pixel combinations, and 24 bpp or other non-power-of-two bpp widths. The implementation assumes callers provide valid rectangles within framebuffer bounds or that upper layers clipped them.

## Test Signals

Use pixel-level golden tests for 1/2/4/8/15/16/24/32 bpp, x offsets crossing word boundaries, same-line and multi-line overlaps in both directions, foreign-endian framebuffers, reverse-pixel low-bpp modes, 32-bit and 64-bit builds, and randomized copy rectangles compared with a byte/bit reference model.
