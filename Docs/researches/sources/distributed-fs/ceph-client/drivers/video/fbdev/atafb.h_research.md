# sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb.h

## Purpose
`atafb.h` is the small internal interface between `atafb.c` and the Atari framebuffer drawing helper implementations. It declares depth-specific copy, fill, and 1-bit image linefill routines for monochrome and 2/4/8-plane Atari interleaved planar formats.

## Important APIs, types, and functions
The exported helper families are `atafb_mfb_*`, `atafb_iplan2p2_*`, `atafb_iplan2p4_*`, and `atafb_iplan2p8_*`. Each family exposes `copyarea(struct fb_info *, u_long next_line, ...)`, `fillrect(struct fb_info *, u_long next_line, u32 color, ...)`, and `linefill(struct fb_info *, u_long next_line, ..., const u8 *data, u32 bgcolor, u32 fgcolor)`. The header relies on fbdev types such as `struct fb_info`, `u32`, and `u8` being available from includers.

## Control flow
`atafb.c` includes this header and dispatches generic fbdev drawing requests to one of these prototypes based on `info->var.bits_per_pixel`. The implementation files include the same header to provide definitions matching the front-end calls.

## State and persistence behavior
The header defines no state and no persistence. All state is supplied by the caller through `fb_info`, framebuffer base memory, and the `next_line` stride.

## Dependencies and integration points
This file is tightly coupled to `atafb.c`, `atafb_mfb.c`, `atafb_iplan2p2.c`, `atafb_iplan2p4.c`, and `atafb_iplan2p8.c`. Its signatures encode Atari helper assumptions: byte-addressable framebuffer memory, caller-provided line stride, and fbdev coordinate units.

## Risks and edge cases
Because this is a plain prototype header, the main risks are signature drift between the front end and helper files and missing prerequisite type includes in future users. The helpers assume clipped and mostly byte/word-aligned arguments; the header does not document those preconditions.

## Test signals
Compile coverage is the primary signal. Runtime signals come from `atafb_fillrect`, `atafb_copyarea`, and `atafb_imageblit` successfully resolving to the right helper at 1, 2, 4, and 8 bpp.
