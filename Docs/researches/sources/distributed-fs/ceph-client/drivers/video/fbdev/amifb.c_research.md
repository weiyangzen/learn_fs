# sources/distributed-fs/ceph-client/drivers/video/fbdev/amifb.c

## Purpose
`amifb.c` is the framebuffer driver for Amiga native OCS, ECS, and AGA chipsets. It translates fbdev modes into Amiga custom-chip display registers, manages planar framebuffer memory in Chip RAM, builds Copper lists for display updates and ywrap, handles palette and blanking, implements a hardware sprite cursor API, and provides custom planar drawing routines.

## Important APIs, Types, and Functions
The central private type is `struct amifb_par`, which stores decoded mode geometry, pixel clock tag, line scaling, display window coordinates, DMA fetch registers, bitplane pointers/modulos, chipset-specific register values, and cursor geometry. Global state includes chipset capability tables (`pixclock`, `maxdepth`, `maxfmode`, `chipset`), memory pointers (`videomemory`, `spritememory`, `dummysprite`), Copper list storage in `copdisplay`, vblank latches (`do_vmode_full`, `do_vmode_pan`, `do_blank`, `do_cursor`), blank/cursor state, and saved color zero.

Mode conversion is handled by `ami_decode_var()`, `ami_encode_var()`, `ami_update_par()`, `ami_build_copper()`, `ami_rebuild_copper()`, `ami_init_display()`, and `ami_update_display()`. fbdev entry points are `amifb_check_var`, `amifb_set_par`, `amifb_setcolreg`, `amifb_blank`, `amifb_pan_display`, `amifb_fillrect`, `amifb_copyarea`, `amifb_imageblit`, and `amifb_ioctl`. Custom ioctls expose `FBIOGET_FCURSORINFO`, `FBIOGET_VCURSORINFO`, `FBIOPUT_VCURSORINFO`, `FBIOGET_CURSORSTATE`, and `FBIOPUT_CURSORSTATE`.

## Control Flow
The platform driver probes `amiga-video`. Probe parses boot options, disables DMA, allocates `fb_info`, classifies the hardware as OCS/ECS/AGA, sets maximum depth/fetch mode/video memory size, derives pixel clock values from `amiga_eclock`, patches the mode database, chooses monitor specs, finds a startup mode, and allocates one Chip RAM block for framebuffer, sprite memory, dummy sprite, and Copper lists. It maps video memory write-through when possible, initializes a safe Copper list, enables display/Copper/blitter/sprite DMA, requests `IRQ_AMIGA_COPPER`, allocates a colormap, and registers the framebuffer.

Mode setting calls `ami_decode_var()` to validate and round fbdev timing, bpp, scrolling, DMA fetch limits, ywrap, and memory layout. `amifb_set_par()` then rebuilds Copper lists and sets `do_vmode_full`, so the actual hardware switch happens in `amifb_interrupt()` at Copper/vblank time. Panning similarly updates decoded offsets, recomputes bitplane pointers, and sets `do_vmode_pan`. The interrupt applies pending display changes, initializes full modes, rebuilds Copper pointer sequences, updates or flashes the hardware cursor, and processes blank/unblank requests.

Drawing is software-driven and planar-aware. For 1bpp images it expands bits into each plane with unaligned bit-copy helpers; for deeper images it calls `c2p_planar()`. Fill and copy paths operate directly on planar memory using bit-level functions that support unaligned packed operations and overlapping copies.

## State and Persistence
All state is volatile and hardware-resident. Chip RAM holds framebuffer pixels, sprite data, and Copper programs. `struct amifb_par` plus global latches describe the current and pending display state. Palette writes update Amiga color registers immediately except color zero while blanked. Hardware state persists until mode change, blanking, driver removal, or system reset; the driver does not persist settings to disk.

## Dependencies and Integration Points
The driver depends on Amiga architecture interfaces: `amiga_custom`, `amiga_chip_alloc/free`, `amiga_chip_avail`, `ZTWO_PADDR`, `ZTWO_VADDR`, `amiga_eclock`, `amiga_vblank`, `amiga_chipset`, `AMIGAHW_PRESENT`, `IRQ_AMIGA_COPPER`, and `amifb_video_off()`. It integrates with fbdev core, platform devices, user-copy ioctls, Chip RAM allocation, Amiga DMA/Copper registers, and `c2p_planar.o` from the Makefile.

## Risks and Edge Cases
This driver is highly timing-sensitive. Incorrect `min_fstrt`, monitor capabilities, or mode timing can steal DMA cycles from audio, floppy, refresh, or sprites. The vblank latch variables are global and not protected by a general lock; they depend on fbdev call serialization and interrupt-time ordering. Some cursor user-copy paths contain comments noting unchecked `get_user`/`put_user` return values, so fault handling is incomplete. `amifb_blank()` records a pending blank but returns before hardware has applied it. The driver has many chipset-specific compile-time paths; OCS only supports broadcast modes, ECS/AGA add programmable sync, and AGA adds higher depths/fetch modes. Custom bit-copy routines are performance-critical but risk subtle boundary errors with unaligned 32/64-bit accesses.

## Test Signals
Validation should include OCS, ECS, and AGA boot probes; PAL/NTSC and VGA mode selection; `monitorcap:`, `fstart:`, `inverse`, and `ilbm` boot options; mode switches across bpp and interlace/doublescan modes; ywrap and ypan scrolling; blank, hsync suspend, vsync suspend, and powerdown; palette updates including AGA high/low color writes; cursor ioctl get/set/state/flash behavior; planar fill/copy/imageblit clipping and overlap; and interrupt-driven application of pending mode and pan changes. Hardware tests should watch for audio/floppy disruption from aggressive fetch starts.
