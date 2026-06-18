# sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/display_gx.c

## Purpose
`display_gx.c` programs the AMD Geode GX display controller for `gxfb`.

## APIs And Control Flow
`gx_frame_buffer_size()` discovers VRAM from GLIU MSRs without VSA2 or VSA virtual registers with VSA2. `gx_line_delta()` returns 8-byte aligned pitch. `gx_set_mode()` unlocks the display controller, disables timing/FIFO/compression, sets DCLK, configures FIFO priority, framebuffer offset, pitch, line size, graphics/video enable, pixel format, horizontal/vertical timings, writes final config, calls `gx_configure_display()`, and relocks. `gx_set_hw_palette_reg()` writes RGB888 palette entries.

## State, Dependencies, Integration, Risks
State is hardware register state accessed through `gxfb_par`. Dependencies include `gxfb.h`, CS5535/VSA helpers, MSRs, and GX video-output functions. Risks are validated-mode assumptions, fixed FIFO priority, VSA/non-VSA discovery differences, and unsupported bpp values beyond 8/16/32. Tests should cover both VRAM discovery paths, pitch alignment, all bpp formats, high-resolution stability, palette writes, and register lock sequencing.
