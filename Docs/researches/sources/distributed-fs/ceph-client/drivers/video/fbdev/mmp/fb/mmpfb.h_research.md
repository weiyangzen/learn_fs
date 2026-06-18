# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/fb/mmpfb.h

## Purpose
Defines the private state for the Marvell MMP fbdev frontend and its default framebuffer allocation size.

## Important APIs, Types, and Functions
- `struct mmpfb_info` stores device pointer, fb_info, current output mode, pixel format, framebuffer CPU/DMA addresses, selected overlay/path, access mutex, pseudo palette, and output format.
- `MMPFB_DEFAULT_SIZE` reserves enough memory for two 1920x1080 32bpp buffers.

## Control Flow
The header is consumed by `mmpfb.c`; `struct mmpfb_info` is allocated as the private area of `fb_info`.

## State and Persistence
All frontend runtime state for an MMP framebuffer instance persists in `struct mmpfb_info` while the platform device is bound.

## Dependencies and Integration Points
Includes `<video/mmp_disp.h>` for path/overlay/mode types and `<linux/fb.h>` for fbdev structures.

## Risks
The `access_ok` mutex is initialized in probe but not heavily used in the current frontend, so it may give a false sense of synchronization. `fb_size` is an `int`, which is adequate for the default size but less robust for larger buffers.

## Test Signals
Compile the framebuffer frontend and verify private data allocation, DMA address assignment, and pseudo palette writes.
