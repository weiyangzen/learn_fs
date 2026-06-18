# sources/distributed-fs/ceph-client/drivers/video/fbdev/controlfb.c

## Purpose

This file implements fbdev support for the PowerMac "control" display adapter. It discovers the Open Firmware node, maps framebuffer/control/cmap registers, probes installed VRAM banks, chooses a Mac video mode and color depth, programs timing/RADACAL/clock registers, and exposes pan/blank/mmap/color operations. The complete 1018-line source was read.

## Important APIs, Types, and Functions

Private state is split between `struct fb_par_control`, which represents a desired/applied mode, and `struct fb_info_control`, which embeds `struct fb_info` and tracks cmap registers, control registers, framebuffer mapping, VRAM bank selection, total VRAM, and cached pseudo-palette. Key functions include `controlfb_setcolreg()`, `set_control_clock()`, `set_screen_start()`, `control_set_hardware()`, `find_vram_size()`, `read_control_sense()`, `calc_clock_params()`, `control_var_to_par()`, `control_par_to_var()`, `controlfb_check_var()`, `controlfb_set_par()`, `controlfb_pan_display()`, `controlfb_blank()`, `controlfb_mmap()`, `control_setup()`, `init_control()`, `control_of_init()`, and `control_init()`.

## Control Flow

`device_initcall(control_init)` parses `video=controlfb:` options, finds the `control` OF node, and calls `control_of_init()`. OF init enforces a single global instance, obtains framebuffer and register resources, maps the big-endian framebuffer aperture and control registers, maps a hard-coded RADACAL cmap register page, probes VRAM banks, then calls `init_control()`. Initialization chooses cmode/vmode from boot options, NVRAM, or monitor sense fallback, initializes `fb_info`, computes virtual height from VRAM, applies the selected mode with `fb_set_var()`, and registers the framebuffer.

Mode conversion aligns horizontal resolution, virtual width, and x offset to 32-byte hardware boundaries, chooses mode/radacal values by color depth and VRAM size, validates memory footprint including `CTRLFB_OFF`, computes CUDA clock parameters and sixteen timing registers, and maps fb var fields back to normalized values. Hardware programming turns display off, sends clock parameters via CUDA IIC when available, writes RADACAL registers, writes vertical/horizontal timing registers, pitch/mode/vram/start/refresh/intr registers, then turns the display on. Pan display only updates start address if bounds pass. Mmap maps framebuffer cached write-through and optional MMIO noncached only when acceleration flags allow it.

## State and Persistence Behavior

State includes a global `control_fb`, `default_vmode`, `default_cmode`, current `p->par`, pseudo-palette entries, VRAM bank/attribute state, and mapped resource metadata. Hardware-visible state includes display control/timing registers, RADACAL color/clock settings, monitor sense lines, framebuffer start address, and VRAM bank select. NVRAM is read for default video mode/color mode if reachable; the driver does not write persistent settings.

## Dependencies and Integration Points

The driver is specific to 32-bit PowerMac/PPC behavior but compiles stubs for some accessors when unavailable. It depends on Open Firmware address translation, PCI resource layout, NVRAM, ADB CUDA for clock programming, `macmodes.c` helpers, BootX text update hooks, fbdev core, and architecture cache/pgprot functions. It integrates with fbcon through `register_framebuffer()`, pan/blank ioctls, and palette operations.

## Risks and Edge Cases

Risks include single-device global state, hard-coded cmap physical address `0xf301b000`, direct VRAM write probes that assume non-existent banks ignore writes, architecture-specific cache invalidation, and `control_set_hardware()` avoiding full reprogramming when only offsets differ. CUDA clock setting is compiled out without `CONFIG_ADB_CUDA`, so timing can depend on firmware defaults. `controlfb_setcolreg()` populates pseudo-palette entries from the register number rather than the requested RGB values for direct-color modes, which matches old code style but should be validated. Cleanup unregisters resources only on failed init or never-registered teardown; there is no module exit because this is initcall-style built-in code.

## Test Signals

Test OF discovery failure, single-instance rejection, VRAM bank probing for 2 MiB bank 1, 2 MiB bank 2, and 4 MiB combinations, NVRAM/default/monitor-sense mode selection, fallback to 640x480x8, mode validation for 8/16/32 bpp and oversized virtual screens, pan alignment, blank modes, mmap framebuffer versus MMIO offsets, palette writes, CUDA clock programming, and BootX text update behavior.
