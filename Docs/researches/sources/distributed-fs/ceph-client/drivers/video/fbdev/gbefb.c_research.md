# sources/distributed-fs/ceph-client/drivers/video/fbdev/gbefb.c

## Purpose
`gbefb.c` drives the SGI GBE framebuffer. It programs GBE PLL/timing/DMA registers, supports CRT and 1600SW defaults, and hides tiled scanout behind a linear CPU/user view.

## APIs And Control Flow
`struct gbefb_par` stores active var, timing, WC cookie, and validity. Global state tracks GBE registers, framebuffer memory, DMA/physical addresses, tile table, revision, pseudo palette, cmap cache, and mode options. Probe maps MMIO, allocates a coherent tile table, maps or allocates framebuffer memory, sets write-combine attributes, fills tile entries, resets GBE, finds/checks a mode, and registers fbdev. `gbefb_set_par()` computes timing, turns GBE off, programs PLL/timing/WID/tile DMA registers, initializes gamma/cmap, and turns GBE on. `gbefb_mmap()` remaps each 64KB tile separately.

## State, Dependencies, Integration, Risks
Dependencies include `video/gbe.h`, DMA APIs, MIPS cache attributes, platform devices, and fbdev CFB helpers. Risks include the tile linearization divisibility constraint, global single-device state, polling timeouts during power sequencing, and mmap tile-boundary correctness. Tests should cover 8/16/32 bpp, rejected divisibility cases, tile mmap ranges, CRT vs LCD setup, cmap FIFO behavior, blanking, and probe unwind.
