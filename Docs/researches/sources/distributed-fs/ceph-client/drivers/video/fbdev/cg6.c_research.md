# sources/distributed-fs/ceph-client/drivers/video/fbdev/cg6.c

## Purpose
`cg6.c` is the fbdev driver for Sun CGsix/GX/TGX accelerated 8-bit framebuffers. It maps the Brooktree DAC, FBC, TEC, THC, FHC, ROM/RAM regions, initializes the accelerator/display controller, provides hardware fill/copy/monochrome image operations, and exposes legacy SBUS mmap/ioctl compatibility.

## Important APIs, Types, and Functions
Core types include `struct cg6_tec`, `struct cg6_thc`, `struct cg6_fbc`, `struct bt_regs`, and `struct cg6_par`. fbdev callbacks include `cg6_setcolreg()`, `cg6_blank()`, `cg6_fillrect()`, `cg6_copyarea()`, `cg6_imageblit()`, `cg6_sync()`, and `cg6_pan_display()`. Initialization helpers are `cg6_bt_init()`, `cg6_chip_init()`, `cg6_init_fix()`, and `cg6_unmap_regs()`.

## Control Flow
`cg6_probe()` allocates fb state, fills OF var info, computes framebuffer size with optional double-buffer multiplier, maps all hardware blocks, sets acceleration flags and fbops, maps RAM, initializes DAC/FBC/TEC/THC state, unblanks video, allocates/sets colormap, registers the framebuffer, and stores driver data. Drawing operations lock, wait for FBC idle via `cg6_sync()`, program FBC registers, and trigger rectangle, blit, or font rendering.

## State and Persistence
Per-device state stores mapped hardware blocks, spinlock, blanked flag, and IO-space ID. Hardware state includes DAC palette, accelerator mode/clip/ALU registers, cursor position, timing/video bits, FHC revision/workaround settings, and VRAM. The driver hides the hardware cursor when switching out of graphics mode through pan-display handling.

## Dependencies and Integration Points
The file depends on OF platform resources, SBUS helpers, `sbuslib.h`, Sun fbio constants, generic `cfb_imageblit()` fallback for deep images, and fbdev hardware-acceleration flags. It binds `cgsix` and `cgthree+`.

## Risks and Edge Cases
Accelerator register programming is timing-sensitive; `cg6_sync()` has a finite polling limit but callers do not surface timeout details. Old FHC revisions require hardware workarounds. The monochrome imageblit path packs source bytes manually and must match font bit ordering. Double-buffer sizing multiplies smem length by four based on an OF property.

## Test Signals
Signals include correct GX/GX+/TGX/TGX+ identification, palette changes, blank/unblank video bit behavior, accelerated fill/copy/text rendering correctness, fallback for images with depth greater than one, mmap of all CG6 regions, no hangs in `cg6_sync()`, and correct remove cleanup of every mapped block.
