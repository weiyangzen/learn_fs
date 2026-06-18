# sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/display_gx1.c

## Purpose
`display_gx1.c` implements Geode GX1 display-controller operations.

## APIs And Control Flow
`gx1_read_conf_reg()` accesses GX1 config ports under a spinlock. `gx1_gx_base()` derives the GX base. `gx1_frame_buffer_size()` maps memory-controller registers to compute framebuffer memory above the graphics base. `gx1_set_mode()` unlocks DC registers, blanks/disables timing, disables FIFO/compression, sets DCLK through `vid_ops`, programs framebuffer offsets, line delta, buffer size, panel output, timing registers, final configs, calls `configure_display()`, and relocks. `gx1_set_hw_palette_reg()` writes RGB666 palette values. `gx1_dc_ops` exports these hooks.

## State, Dependencies, Integration, Risks
State is in `geodefb_par` plus the global config-register spinlock. Dependencies include `geodefb.h`, `display_gx1.h`, port I/O, MMIO, and `video_cs5530.o`. Risks include hardware assumptions in DIMM-size calculation, commented gaps for DCLK divider and pixel/line doubling, and palette quantization. Tests should cover config locking, memory-size detection, 8bpp and non-8bpp mode setup, palette writes, and clock-settle timing.
