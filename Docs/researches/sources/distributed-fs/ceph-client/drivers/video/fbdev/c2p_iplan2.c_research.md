# sources/distributed-fs/ceph-client/drivers/video/fbdev/c2p_iplan2.c

## Purpose
`c2p_iplan2.c` implements and exports `c2p_iplan2()`, converting 8-bit chunky pixels into interleaved planar framebuffer memory with two bytes of interleave. It supports 2, 4, or 8 planar bits per pixel.

## Important APIs, Types, and Functions
`c2p_16x8()` performs the core conversion of 16 chunky pixels in four 32-bit words. `perm_c2p_16x8[]` maps converted word order to output order. `store_iplan2()` writes full converted blocks; `store_iplan2_masked()` preserves untouched edge bits with `comp()`. `c2p_iplan2()` is exported with `EXPORT_SYMBOL_GPL`.

## Control Flow
The exported function computes the destination byte offset from `dy`, `dst_nextline`, and the 16-pixel-aligned part of `dx`. Each scanline is split into a possible single masked block, or leading masked block, full 16-pixel blocks, and trailing masked block. Temporary `pixels[]` are filled from source, transposed, and written as big-endian 32-bit output words.

## State and Persistence
The conversion is stateless except for modifying destination framebuffer memory. Partial writes preserve existing destination bits through read-modify-write masks, so destination contents matter at unaligned edges.

## Dependencies and Integration Points
The file depends on `c2p.h`, `c2p_core.h`, `linux/unaligned.h`, export/module infrastructure, and `memcpy()/memset()`. Drivers with interleaved planar formats call it directly or via generic helper paths.

## Risks and Edge Cases
Input arguments are trusted. Invalid `bpp`, strides, or dimensions can overrun memory. Edge masks depend on `dx % 16` and `(dst_idx + width) % 16`; zero-width or exact-boundary behavior should be guarded by callers or tests. The output assumes big-endian planar bit order.

## Test Signals
Compare output against golden interleaved-planar buffers for 2, 4, and 8 bpp, including `dx` offsets from 0 to 15, widths smaller than one block, exact 16-pixel multiples, and multi-line stride padding.
