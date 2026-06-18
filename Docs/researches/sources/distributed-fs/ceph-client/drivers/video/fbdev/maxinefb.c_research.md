# sources/distributed-fs/ceph-client/drivers/video/fbdev/maxinefb.c

## Purpose
Implements the DECstation 5000/xx "Maxine" onboard framebuffer driver. It registers a fixed 1024x768 8bpp pseudocolor framebuffer, controls the Inmos IMS332 RAMDAC palette and cursor RAM, and exposes default fbdev sysmem/IOMEM operations.

## Important APIs, Types, and Functions
- `maxinefb_defined` and `maxinefb_fix` describe the fixed mode and memory layout.
- `maxinefb_ims332_write_register()` and `maxinefb_ims332_read_register()` access IMS332 registers through architecture-specific physical addresses.
- `maxinefb_setcolreg()` converts 16-bit fbdev color components to 8-bit DAC values and writes palette registers.
- `maxinefb_init()` validates machine type, clears framebuffer memory, erases cursor RAM, initializes `fb_info`, allocates a 256-entry cmap, and registers the framebuffer.
- `maxinefb_exit()` unregisters the framebuffer.

## Control Flow
Module init first honors `fb_get_options("maxinefb")`; disabled options return `-ENODEV`. It then requires `mips_machtype == MACH_DS5000_XX`. On matching hardware, it clears part of the framebuffer, sets the fixed physical start, clears 512 cursor RAM entries, populates the static `fb_info`, allocates a color map, and calls `register_framebuffer()`.

## State and Persistence
Uses one static `struct fb_info` and static mode structures. Hardware palette and cursor RAM persist in device registers until changed. The driver does not dynamically allocate private state beyond the cmap.

## Dependencies and Integration Points
Depends on MIPS boot machine type constants and `video/maxinefb.h` address/register definitions. Integrates with fbdev through `fb_ops`, `FB_DEFAULT_IOMEM_OPS`, color map allocation, and module init/exit.

## Risks
The driver performs direct volatile physical memory accesses without `ioremap`, matching old platform conventions but risky outside the exact platform. It clears only `0x1ffff` bytes despite a 1024x768 framebuffer length. `maxinefb_ims332_read_register()` is non-static while not declared here, so external users may rely on it. Failure after `fb_alloc_cmap()` but before registration is not fully cleaned up.

## Test Signals
Validation requires booting on `MACH_DS5000_XX`, seeing registration of a 1024x768x8 framebuffer, palette changes through fbdev colormap operations, and hidden hardware cursor after init. Non-Maxine machines should return `-EINVAL`; disabled options should return `-ENODEV`.
