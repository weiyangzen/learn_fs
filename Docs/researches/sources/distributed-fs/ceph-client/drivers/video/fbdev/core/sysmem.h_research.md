# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/sysmem.h

## Purpose
`sysmem.h` provides normal-memory framebuffer access primitives for shared fbdev drawing templates.

## APIs And Control Flow
`struct fb_address` stores an aligned word address and bit offset. `fb_address_init()` aligns `p->screen_buffer` down to an unsigned-long boundary and computes the bit displacement. `fb_write_offset()` and `fb_read_offset()` perform word stores/loads at offsets from that aligned base.

## State, Dependencies, Integration, Risks
The helpers are inline and stateless, depending on the caller's `struct fb_info`. They integrate with generic blit templates included by system-memory wrappers. Risks include using these helpers for MMIO mappings and subtle word-boundary behavior with unaligned `screen_buffer` values. Tests should cover unaligned bases, 32/64-bit word builds, and packed blits crossing word boundaries.
