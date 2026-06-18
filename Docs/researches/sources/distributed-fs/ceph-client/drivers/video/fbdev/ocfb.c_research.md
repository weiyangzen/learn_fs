# sources/distributed-fs/ceph-client/drivers/video/fbdev/ocfb.c

## Purpose

`ocfb.c` is a platform fbdev driver for the OpenCores VGA/LCD 2.0 controller. It allocates a coherent framebuffer, maps controller registers, programs timing and framebuffer base registers, supports 8/16/24/32-bpp packed-pixel modes, and exposes a simple fbdev device with color-register support. The source was read as a complete 428-line file.

## Important APIs, Types, and Functions

The key device state is `struct ocfb_dev`, embedding `struct fb_info`, register base, endianness flag, coherent framebuffer physical/virtual addresses, and a pseudo palette. Important functions are `ocfb_setup()` for boot option parsing, `ocfb_readreg()`/`ocfb_writereg()` for endian-aware register I/O, `ocfb_setupfb()` for hardware programming, `ocfb_setcolreg()` for palette/pseudo-palette updates, `ocfb_init_fix()`, `ocfb_init_var()`, `ocfb_probe()`, and `ocfb_remove()`. `ocfb_ops` uses `FB_DEFAULT_IOMEM_OPS` plus `.fb_setcolreg`.

## Control Flow

Init parses `ocfb` options in built-in mode and registers a platform driver matching `opencores,ocfb`. Probe allocates `ocfb_dev`, selects a video mode with `fb_find_mode()` and a 640x480@60 default, initializes `var`/`fix`, maps MMIO, allocates coherent framebuffer memory sized by line length and yres, clears it, calls `ocfb_setupfb()` to disable output, write framebuffer base, detect register endianness, program horizontal/vertical timing and total lengths, set color depth and burst length, and enable output. It then marks `FBINFO_FOREIGN_ENDIAN` if needed, allocates the cmap, and registers the framebuffer. Remove unregisters, frees cmap and DMA memory, disables display, and clears driver data.

## State and Persistence Behavior

State is per-platform-device and devm-managed except coherent framebuffer memory/cmap which are explicitly freed. Hardware state includes OCFB timing registers, framebuffer base address, control bits, palette entries, and enabled/disabled output. Framebuffer contents live in coherent DMA memory for the lifetime of the fbdev device; no storage persists across remove.

## Dependencies and Integration Points

The driver depends on platform devices, device tree matching, MMIO resource mapping, coherent DMA allocation, fbdev mode helpers, and framebuffer console/userspace through standard fbdev ops. It has a `mode_option` module parameter/boot option for initial mode selection.

## Risks and Edge Cases

`ocfb_setupfb()` assumes timing fields are nonzero before subtracting one; invalid or unusual mode timings could underflow register fields. Register endianness is detected by writing/reading `OCFB_VBARA`, which depends on a stable framebuffer physical address and readable register. `ocfb_setcolreg()` writes pseudo-palette entries for all regnos below cmap length even though truecolor pseudo palettes are conventionally 16 entries; callers normally limit truecolor regnos but the local guard is `info->cmap.len`. DMA allocation size is based on the chosen mode and can fail on high resolutions.

## Test Signals

Device-tree probe with big- and little-endian register mappings, initial mode parsing, successful coherent allocation and screen clear, 8-bpp palette writes to hardware, truecolor pseudo-palette writes, remove disabling display, and framebuffer console smoke at each supported bpp are useful signals.
