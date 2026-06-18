# sources/distributed-fs/ceph-client/drivers/video/fbdev/sunxvr1000.c

## Purpose
`sunxvr1000.c` is a minimal Open Firmware platform fbdev driver for Sun XVR-1000 (`SUNW,gfb`) framebuffers on sparc64. It exposes the firmware-provided framebuffer as a packed-pixel fbdev device without mode setting or acceleration.

## Important APIs, Types, and Functions
`struct gfb_info` stores `fb_info`, OF node, framebuffer mapping, physical base, width, height, depth, size, and a 16-entry pseudo palette. Important functions are `gfb_get_props()`, `gfb_setcolreg()`, `gfb_set_fbinfo()`, `gfb_probe()`, and `gfb_init()`. `gfb_ops` uses default IOMEM fb operations plus `fb_setcolreg`.

## Control Flow
The device initcall checks `fb_get_options("gfb")` and registers a platform driver. `gfb_probe()` allocates `fb_info`, reads `width`, `height`, and optional `depth` from the OF node, uses resource 6 as framebuffer memory, fixes line length at 16384 bytes, maps only `line_length * height`, fills `fix` and `var`, allocates a 256-entry cmap, registers the framebuffer, and stores drvdata. `gfb_setcolreg()` only updates the truecolor pseudo palette for the first 16 entries.

## State and Persistence
State is limited to runtime fbdev structures, the framebuffer mapping, cmap, and pseudo palette. Hardware state is whatever firmware already configured; the driver does not program timings or hardware registers. There is no persistence beyond device lifetime.

## Dependencies and Integration Points
The driver depends on OF platform resources/properties, `of_ioremap()`, fbdev IOMEM helpers, and early device init. It integrates with firmware-provided display setup and fbdev clients such as fbcon.

## Risks and Edge Cases
The driver assumes resource 6 is the framebuffer and that a 16384-byte pitch is correct. Missing width/height is fatal, but unexpected depth values are mostly passed through. There is no remove callback, dynamic mode validation, hardware blanking, EDID, or acceleration. Error cleanup covers allocation and mapping but registered devices rely on system lifetime.

## Test Signals
Test on OF nodes named `SUNW,gfb`, verify resource 6 mapping, visible output at firmware mode, correct pseudo-palette colors for 24/32 bpp, behavior with missing width/height, and boot option disabling through `fb_get_options("gfb")`.
