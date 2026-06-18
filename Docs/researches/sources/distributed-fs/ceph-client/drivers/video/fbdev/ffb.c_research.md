# sources/distributed-fs/ceph-client/drivers/video/fbdev/ffb.c

## Purpose
`ffb.c` is the SPARC Creator/Creator3D/Elite3D framebuffer driver. It maps FBC and DAC registers from OF resources, provides SBUS mmap/ioctl behavior, and accelerates fill, vertical copy, and monochrome image blits.

## APIs And Control Flow
`struct ffb_fbc` and `struct ffb_dac` mirror hardware registers. `struct ffb_par` stores locks, mapped registers, flags, cached fg/bg/ROP, FIFO cache, physical base, fb size, board type, and pseudo palette. Drawing paths use `FFBFifo()`, `FFBWait()`, `ffb_rop()`, `ffb_fillrect()`, `ffb_copyarea()`, and `ffb_imageblit()`. Probe maps registers, detects AFB and DAC cursor polarity, resets from graphics mode, unblanks, allocates cmap, initializes fix/var data, and registers fbdev.

## State, Dependencies, Integration, Risks
Hardware state is protected by `par->lock` and cached where useful. Dependencies include Open Firmware platform devices, UPA accessors, `sbuslib`, and fbdev SBUS ops. Risks include FIFO polling, narrow image blit reads, and console switching from graphics mode. Tests should cover AFB/FFB detection, DAC cursor polarity, blanking, accelerated and fallback drawing, mmap map offsets, ioctl helper behavior, and remove cleanup.
