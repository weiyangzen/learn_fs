# sources/distributed-fs/ceph-client/drivers/video/fbdev/sbuslib.h

Purpose: public-private interface for SBUS framebuffer helper routines. It declares the SBUS mmap table shape, mmap sentinel constants, exported helper prototypes, compat ioctl prototype, and convenience macros for initializing `struct fb_ops` in SBUS drivers.

Important APIs/types/functions: `struct sbus_mmap_map` maps a user-visible offset (`voff`) to physical offset (`poff`) and size. `SBUS_MMAP_FBSIZE(n)` encodes sizes as multiples of framebuffer size, while `SBUS_MMAP_EMPTY` marks empty entries. Function declarations cover var initialization, mmap helper, ioctl helper, and compat ioctl. `FB_DEFAULT_SBUS_OPS(prefix)` expands to fb read/write, cfb drawing, prefixed ioctl/mmap callbacks, and optional compat ioctl.

Control flow: no runtime flow exists here. The macros determine which function pointers an SBUS driver's `fb_ops` receives at compile time. Under CONFIG_COMPAT, ioctl macro expansion includes `.fb_compat_ioctl = sbusfb_compat_ioctl`; otherwise only the native prefixed ioctl is assigned.

State and persistence: no direct state. The map table structure describes persistent static tables normally owned by individual SBUS framebuffer drivers, and the macros encode a standard operations contract.

Dependencies and integration: consumed by SPARC/SBUS fbdev drivers and implemented by `sbuslib.c`. It assumes fbdev core drawing helpers (`fb_io_read`, `fb_io_write`, `cfb_fillrect`, `cfb_copyarea`, `cfb_imageblit`) are available wherever the macros are used.

Risks: macro expansion requires drivers to define functions named `prefix_sbusfb_ioctl` and `prefix_sbusfb_mmap`; mismatches become compile errors. Size sentinels rely on unsigned/negative conversion conventions that must match `sbusfb_mmapsize`. Using default cfb drawing may be inappropriate for unusual framebuffer layouts unless the driver overrides it.

Test signals: compile SBUS drivers with and without CONFIG_COMPAT, verify macro-generated fb_ops fields point to the expected prefixed functions, and mmap tables using positive, empty, and framebuffer-relative sizes.
