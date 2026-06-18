# sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb_utils.h

## Purpose
`atafb_utils.h` provides performance-critical memory and planar color helpers for Atari framebuffer drawing. It contains m68k inline assembly replacements for common memory operations and C inline functions specialized by the `BPL` macro for interleaved planar formats.

## Important APIs, types, and functions
General helpers include `fb_memclear_small()`, `fb_memclear()`, `fb_memset255()`, `fb_memmove()`, and `fast_memmove()`. When `BPL` is defined, the header adds color expansion tables (`four2long`, `two2word`) and helpers such as `expand8_col2mask()`, `expand8_2col2mask()`, `fill8_col()`, `fill8_2col()`, `expand16_col2mask()`, `expand16_2col2mask()`, `fill16_col()`, and `memmove32_col()`.

## Control flow
The memory functions choose small unrolled paths or larger aligned block paths and use forward or reverse copying depending on address order. The planar helpers expand a logical color into byte or word masks for the active number of planes, fill packed plane words for 8- or 16-pixel groups, and copy selected columns with masks that preserve untouched planes or half groups.

## State and persistence behavior
The header defines static constant lookup tables and inline functions only. It persists no mutable driver state. Callers persist effects by writing framebuffer memory.

## Dependencies and integration points
This file is included by `atafb_mfb.c` and by the `atafb_iplan2p*.c` files after setting `BPL`. The inline assembly is m68k-specific and assumes the compiler accepts the register constraints and instruction syntax used here.

## Risks and edge cases
The assembly is difficult to audit, architecture-specific, and sensitive to alignment, count underflow, and compiler constraint behavior. `fast_memmove()` assumes a size divisible by 16. The `BPL`-conditional helpers must only be used after defining supported values 2, 4, or 8; otherwise helper expansion would not match the framebuffer layout.

## Test signals
Compile on the target m68k configuration, run framebuffer copy/fill tests for small and large sizes, verify overlapping forward and reverse `fb_memmove()`, and compare planar helper output against known bitplane layouts for 2/4/8 bpp colors and glyph masks.
