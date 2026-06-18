# sources/distributed-fs/ceph-client/drivers/video/fbdev/c2p_planar.c

## Purpose
`c2p_planar.c` implements and exports `c2p_planar()`, converting 8-bit chunky pixels into standard planar framebuffer memory with separate planes.

## Important APIs, Types, and Functions
`c2p_32x8()` converts 32 chunky pixels stored in eight 32-bit words. `perm_c2p_32x8[]` defines the output plane order after transposition. `store_planar()` writes full blocks to successive planes using `dst_nextplane`, and `store_planar_masked()` merges partial edge blocks. `c2p_planar()` is GPL-exported.

## Control Flow
The function aligns `dx` to a 32-pixel destination word, computes leading and trailing masks, and processes each line as a single masked block or a leading edge, full 32-pixel blocks, and trailing edge. Each block is copied into a temporary union, transposed through `c2p_32x8()`, and stored to each requested plane.

## State and Persistence
No driver state is kept. The function writes destination framebuffer memory and performs read-modify-write for masked first/last words to preserve pixels outside the requested rectangle.

## Dependencies and Integration Points
Dependencies are `c2p.h`, `c2p_core.h`, unaligned big-endian access helpers, and module export support. It integrates with planar fbdev drawing paths where chunky software images must be converted for legacy planar framebuffers.

## Risks and Edge Cases
The implementation assumes valid caller-provided bpp in the 1-to-8 range, addressable plane memory, and compatible endian output. Invalid strides or `dst_nextplane` can corrupt unrelated planes. Boundary mask behavior should be regression-tested for `dx + width` exactly divisible by 32.

## Test Signals
Golden-vector tests should cover 1 through 8 bpp, every unaligned `dx % 32`, exact and non-exact block widths, multiple scanlines with source/destination stride padding, and preservation of untouched bits at left and right edges.
