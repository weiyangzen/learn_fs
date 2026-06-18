# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/Makefile

## Purpose

This Makefile maps fbdev core Kconfig symbols to built-in and modular objects. It defines the aggregate `fb.o` composition and independently built helper modules for drawing, file operations, DDC, and svgalib. The complete 37-line source was read.

## Important APIs, Types, and Functions

`obj-$(CONFIG_FB_CORE) += fb.o` creates the core aggregate. `fb-y` always includes `fb_info.o`, `fbmem.o`, `fbcmap.o`, `modedb.o`, `fbcvt.o`, and `fb_cmdline.o`; additional objects include `fb_backlight.o`, `fbmon.o`, `fb_defio.o`, `fb_chrdev.o`, `fb_procfs.o`, `fbsysfs.o`, fbcon/rotation/logo objects, and optional tileblit. Standalone objects map `CONFIG_FB_CFB_*`, `CONFIG_FB_IOMEM_FOPS`, `CONFIG_FB_SYS_*`, `CONFIG_FB_SYSMEM_FOPS`, `CONFIG_FB_SVGALIB`, and `CONFIG_FB_DDC`.

## Control Flow

There is no runtime flow. Kbuild expands selected config symbols into object lists, links `fb.o`, and builds helper modules or built-ins depending on tristate settings.

## State and Persistence Behavior

No runtime state exists. The durable contract is build composition: exported APIs from these files are available only when their corresponding symbols are selected.

## Dependencies and Integration Points

The Makefile integrates with `core/Kconfig`, fbcon configuration, logo configuration, and drivers that call generic helper functions such as `cfb_fillrect()`, `fb_io_read()`, `fb_deferred_io_init()`, or `fb_ddc_read()`.

## Risks and Edge Cases

Risks are build drift: adding source files without Makefile entries, missing optional objects from `fb-y`, or helper symbols not matching exported APIs. Conditional `ifdef CONFIG_FB` adds `fb_backlight.o` and `fbmon.o` only when the broader fbdev config is active, which must remain aligned with Kconfig expectations.

## Test Signals

Build with core as built-in and module-like tristate helpers, framebuffer console on/off, logo on/off, rotation on/off, and each generic helper selected independently. Inspect generated object lists and exported symbols.
