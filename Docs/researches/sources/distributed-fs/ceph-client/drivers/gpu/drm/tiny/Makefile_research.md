# sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/Makefile

## Purpose

`tiny/Makefile` maps tiny DRM Kconfig symbols to their object files.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_DRM_APPLETBDRM) += appletbdrm.o` builds the Apple Touch Bar DRM driver.
- Other entries build arcpgu, bochs, cirrus-qemu, gm12u320, panel-mipi-dbi, pixpaper, hx8357d, ili9163, ili9225, ili9341, ili9486, mi0283qt, repaper, and sharp-memory drivers.

## Control Flow

Kbuild includes each object when the corresponding Kconfig symbol is enabled as built-in or module. The object name determines the module name for module builds.

## State and Persistence Behavior

The Makefile has no runtime state; it controls compile/link outputs.

## Dependencies and Integration Points

It integrates the tiny DRM directory with top-level Kbuild and the options declared in `tiny/Kconfig`.

## Risks and Edge Cases

- Missing or mismatched object entries cause enabled drivers not to build.
- Formatting inconsistencies, such as spacing around `pixpaper.o`, are harmless but can hide accidental changes in reviews.

## Test Signals

Build all tiny DRM entries as modules and built-ins, and verify `appletbdrm.ko` is produced when `CONFIG_DRM_APPLETBDRM=m`.
