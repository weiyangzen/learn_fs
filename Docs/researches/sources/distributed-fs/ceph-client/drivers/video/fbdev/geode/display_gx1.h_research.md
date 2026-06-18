# sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/display_gx1.h

## Purpose
`display_gx1.h` defines GX1 display-controller APIs, register offsets, and bitfields.

## APIs And Control Flow
It declares `gx1_gx_base()`, `gx1_frame_buffer_size()`, and `gx1_dc_ops`. Constants cover config I/O registers, memory controller bank/base registers, DC unlock/general/timing/output config bits, framebuffer/cursor/video offsets, line delta, buffer size, timings, palette, and diagnostics.

## State, Dependencies, Integration, Risks
The header has no runtime state and is consumed by `display_gx1.c` and GX1 core code. It depends on `struct geode_dc_ops` from `geodefb.h`. Risks are silent hardware misprogramming from incorrect masks/shifts and duplicate palette register defines. Tests include build coverage, register audit against hardware docs, and runtime mode/palette programming.
