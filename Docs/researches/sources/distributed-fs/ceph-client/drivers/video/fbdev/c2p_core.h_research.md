# sources/distributed-fs/ceph-client/drivers/video/fbdev/c2p_core.h

## Purpose
`c2p_core.h` contains shared bit-transpose primitives for fast chunky-to-planar conversion. It is intended to be included by concrete conversion implementations and assumes big-endian bit ordering.

## Important APIs, Types, and Functions
Internal helpers include `_transp()`, `get_mask()`, `transp8()`, `transp4()`, `transp4x()`, and `comp()`. The transpose helpers operate on arrays of 32-bit words and are parameterized by block dimensions. `comp()` merges a newly converted partial word with an existing framebuffer word using a mask.

## Control Flow
The concrete converters call a series of transpose stages that exchange bit groups between words. `get_mask()` selects canonical bit masks for 1, 2, 4, 8, or 16-bit groups, while invalid compile-time constants trigger `BUILD_BUG()`.

## State and Persistence
There is no persistent state. All operations mutate caller-supplied temporary arrays during a conversion block.

## Dependencies and Integration Points
The header depends on `linux/build_bug.h` and Linux integer types through includers. It is included by `c2p_planar.c` and `c2p_iplan2.c`, and its big-endian assumption aligns with those files' use of unaligned big-endian loads/stores.

## Risks and Edge Cases
The transpose sequences are subtle and rely on exact masks, word order, and endian semantics. Porting to little-endian output or changing store order requires golden-vector tests. `BUILD_BUG()` only protects constant invalid cases; dynamic misuse could be harder to diagnose if wrappers are changed.

## Test Signals
Golden output vectors for 1, 2, 4, and 8 bpp planar formats, plus masked partial-block cases, are the strongest signals. Compiler coverage should include optimization levels that inline these helpers.
