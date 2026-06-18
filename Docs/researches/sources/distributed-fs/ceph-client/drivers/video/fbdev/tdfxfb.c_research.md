# sources/distributed-fs/ceph-client/drivers/video/fbdev/tdfxfb.c

## Purpose
`tdfxfb.c` is the PCI fbdev driver for 3Dfx Banshee, Voodoo3, and Voodoo5 display controllers. It programs VGA and 3Dfx video registers, exposes mode validation and panning, supports palette and truecolor pseudo-palette handling, optionally accelerates drawing, optionally provides a hardware cursor, and can create bit-banged I2C/DDC buses.

## Important APIs, Types, and Functions
The driver uses `struct tdfx_par` and `struct banshee_reg` from `include/video/tdfx.h`. Important functions include low-level VGA/MMIO helpers, `banshee_make_room()`, `banshee_wait_idle()`, `do_calc_pll()`, `do_write_regs()`, `do_lfb_size()`, `tdfxfb_check_var()`, `tdfxfb_set_par()`, `tdfxfb_setcolreg()`, `tdfxfb_blank()`, `tdfxfb_pan_display()`, optional `tdfxfb_fillrect()`, `tdfxfb_copyarea()`, `tdfxfb_imageblit()`, `tdfxfb_cursor()`, I2C/DDC setup helpers, `tdfxfb_probe()`, `tdfxfb_remove()`, and module option parsing.

## Control Flow
Probe removes conflicting apertures, enables PCI, allocates fbdev state, identifies the chip and max pixel clock, requests/maps register BAR0, calculates framebuffer size from DRAM registers, requests/maps framebuffer BAR1 with write-combining, reserves I/O BAR2 for VGA ports, optionally creates I2C/DDC buses and picks an EDID-derived mode, falls back to `640x480@60`, maximizes virtual height, allocates cmap, and registers the framebuffer. Mode set validates bpp, monitor limits, pitch, memory, pixel clock, and interlace constraints, computes PLL/timing/VGA/3Dfx register images, writes them via `do_write_regs()`, and updates `fix` metadata. Runtime drawing uses 2D engine commands when `CONFIG_FB_3DFX_ACCEL` is enabled, otherwise generic cfb helpers.

## State and Persistence
Runtime state includes MMIO base, VGA I/O base, write-combining cookie, max clock, 16-entry truecolor palette, optional I2C channel state, fbdev cmap, and hardware cursor memory carved from the end of VRAM. Hardware state includes VGA sequencer/CRTC/attribute/graphics registers, PLL, DAC, 2D engine state, cursor pattern, panning start, and palette. No disk persistence exists.

## Dependencies and Integration Points
Dependencies include PCI, aperture handoff, arch write-combining APIs, VGA register definitions, `video/tdfx.h`, fbdev mode/EDID helpers, optional `CONFIG_FB_3DFX_ACCEL`, and optional `CONFIG_FB_3DFX_I2C`. It integrates with fb boot options, module parameters `hwcursor`, `mode_option`, and `nomtrr`, and fbcon acceleration hooks.

## Risks and Edge Cases
Busy-wait loops for FIFO/idle have no timeout. Some acceleration paths assume dimensions below 4096 and contain endian-sensitive host-to-screen transfers. Cursor memory reduces `smem_len` and must remain aligned. Big-endian mode uses `MISCINIT0` byte-swapping bits. I2C GPIO operations read-modify-write shared registers. Probe error paths must undo WC, I/O regions, MMIO mappings, framebuffer mappings, and optional I2C.

## Test Signals
Test Banshee, Voodoo3, and Voodoo5 probe paths, memory-size detection, 8/16/24/32 bpp modes, pixel-clock rejection, panning and `nopan`, blank states including sync control, accelerated fill/copy/mono image blit, hardware cursor enable/disable/update, DDC EDID probing, `nomtrr`, unload cleanup, and fault injection around BAR requests and URB-like I2C failures.
