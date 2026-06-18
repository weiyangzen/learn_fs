# sources/distributed-fs/ceph-client/drivers/video/fbdev/c2p.h

## Purpose
`c2p.h` declares the public chunky-to-planar conversion entry points used by framebuffer drivers that need to copy 8-bit chunky image data into planar or interleaved-planar framebuffers.

## Important APIs, Types, and Functions
The exported declarations are `c2p_planar()` and `c2p_iplan2()`. Both accept destination/source pointers, destination x/y offsets, width/height, line strides, and bits per pixel. `c2p_planar()` also receives `dst_nextplane`; `c2p_iplan2()` is specialized for two-byte interleave.

## Control Flow
There is no implementation here. Consumers include the header and link against `c2p_planar.c` or `c2p_iplan2.c`, where the conversion loops split rectangles into aligned full and masked partial blocks.

## State and Persistence
The functions declared here are stateless. They transform caller-provided source memory into caller-provided framebuffer memory and maintain no global data.

## Dependencies and Integration Points
The header depends only on `<linux/types.h>`. It forms the source-level contract between generic fbdev drawing paths and the C2P implementation modules.

## Risks and Edge Cases
The API trusts callers to provide valid dimensions, strides, bpp, and addressable memory. Misstated bpp or stride can corrupt framebuffer memory because the implementations do no broad validation.

## Test Signals
Build/link tests should verify both symbols resolve. Functional tests should compare known chunky input patterns against expected planar/interleaved output for aligned rectangles and unaligned left/right edges.
