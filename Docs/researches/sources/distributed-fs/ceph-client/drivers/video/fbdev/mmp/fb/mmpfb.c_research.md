# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/fb/mmpfb.c

## Purpose
Implements the fbdev frontend for Marvell MMP display paths. It converts fbdev pixel formats and modes into MMP display modes/windows, allocates coherent framebuffer memory, wires fb operations to overlay/path APIs, and registers `/dev/fb*` devices.

## Important APIs, Types, and Functions
- `var_to_pixfmt()` and `pixfmt_to_var()` translate between fbdev bitfields and MMP `PIXFMT_*` values.
- `fbmode_to_mmpmode()` and `mmpmode_to_fbmode()` translate between fbdev video modes and MMP display modes.
- `mmpfb_check_var()`, `mmpfb_set_par()`, `mmpfb_setcolreg()`, `mmpfb_pan_display()`, and `mmpfb_blank()` implement fbdev operations.
- `var_update()` selects a matching or best video mode, normalizes pixel format, doubles virtual Y, and updates fixed info.
- `mmpfb_set_win()` programs overlay window geometry and pitches.
- `modes_setup()` imports modes from the selected path/panel.
- `mmpfb_probe()` consumes platform data, gets path/overlay, allocates DMA coherent framebuffer memory, powers on the overlay, initializes fb_info, and registers the framebuffer.

## Control Flow
Probe requires `struct mmp_buffer_driver_mach_info` platform data. It allocates `fb_info`, initializes default format, gets a registered path by name, gets an overlay by ID, assigns the DMA fetch ID, imports panel modes if present, sizes the framebuffer, allocates coherent memory, powers the overlay if modes exist, sets up fb_info/cmap, and registers fbdev. `set_par()` normalizes the requested var, programs the path mode, overlay window, and overlay address. Panning recomputes the base physical address from offsets and updates the overlay address. Blanking toggles overlay/path power through `mmpfb_power()`.

## State and Persistence
`struct mmpfb_info` stores platform identity, current fb mode, pixel format, DMA framebuffer address and size, selected path/overlay, pseudo palette, and output format. The coherent framebuffer memory persists until driver teardown, but this source has no remove function, so release is not implemented.

## Dependencies and Integration Points
Depends on the MMP core and hardware path API from `<video/mmp_disp.h>`, Linux fbdev, platform data, and DMA coherent allocation. It relies on `mmp_ctrl.c` or another hardware provider registering paths before probe.

## Risks
The driver rejects 8bpp in `mmpfb_check_var()` even though format conversion and visual logic know about pseudocolor. It has no platform driver remove callback, so framebuffer memory and registration are not cleaned up on device removal. `mmpfb_setcolreg()` does not program pseudocolor hardware palette. `modes_setup()` returns 0 when no modelist exists, causing a large default allocation but no path mode power-on. `info->screen_buffer` is used for coherent memory rather than the more common `screen_base` field.

## Test Signals
Test path lookup failure, overlay lookup failure, panel modelist import, fb registration, mode changes across RGB/YUV formats, panning address calculation, blank/unblank overlay state, coherent framebuffer allocation size, and module/device removal behavior. Visual tests should confirm overlay pitch and pixel format programming.
