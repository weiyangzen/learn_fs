# sources/distributed-fs/ceph-client/drivers/video/fbdev/ep93xx-fb.c

## Purpose
`ep93xx-fb.c` drives the EP93xx integrated raster framebuffer using platform data, DMA write-combined framebuffer memory, controller MMIO, and a pixel clock.

## APIs And Control Flow
`struct ep93xx_fbi` stores platform callbacks, clock, resource/MMIO base, and pseudo palette. Core routines are `ep93xxfb_set_pixelmode()`, `ep93xxfb_set_timing()`, `ep93xxfb_set_par()`, `ep93xxfb_check_var()`, `ep93xxfb_mmap()`, `ep93xxfb_blank()`, `ep93xxfb_setcolreg()`, video memory allocation/free, probe, and remove. Probe allocates fb_info/cmap/DMA memory, maps registers, finds a video mode, runs board setup, validates mode, gets/enables the clock, programs hardware, and registers fbdev.

## State, Dependencies, Integration, Risks
State spans `fb_info`, hardware timing/pixel registers, the hardware LUT, pseudo palette, and board callbacks. Dependencies are platform data, DMA APIs, clocks, and fbdev helpers. A notable risk is `ep93xxfb_check_var()` writing pixel mode using `info->var` rather than the candidate `var`, causing check-time side effects. Tests should cover bpp modes, min/max clamping, mmap bounds, blank sequencing, setup/teardown callbacks, and the bit-27 DMA address bug parameter.
