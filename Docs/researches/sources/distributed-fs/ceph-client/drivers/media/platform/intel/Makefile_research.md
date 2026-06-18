# sources/distributed-fs/ceph-client/drivers/media/platform/intel/Makefile

## Purpose
This Makefile connects the Intel platform media Kconfig symbol to the PXA camera driver object. It is intentionally small: when `CONFIG_VIDEO_PXA27x` is enabled, `pxa_camera.o` is compiled into the media platform build.

## Important APIs, Types, And Functions
There are no APIs or functions. The relevant build rule is `obj-$(CONFIG_VIDEO_PXA27x) += pxa_camera.o`.

## Control Flow And State
The only state is build configuration state from Kconfig. The object is built as built-in or module according to the tristate value of `CONFIG_VIDEO_PXA27x`.

## Dependencies And Integration Points
This file depends on the parent kernel media build system including the directory. It maps directly to `drivers/media/platform/intel/pxa_camera.c` and to the `VIDEO_PXA27x` symbol defined in the adjacent Kconfig file.

## Risks
Because the driver is a single object, there are no local ordering risks. The main risk is symbol drift: if the Kconfig symbol or source filename changes, this Makefile must be updated with it. A typo here silently omits the driver from builds even if Kconfig is enabled.

## Test Signals
Run a configured kernel build with `CONFIG_VIDEO_PXA27x=m` and verify that `pxa_camera.ko` is produced. Built-in coverage should verify `pxa_camera.o` is linked when `CONFIG_VIDEO_PXA27x=y`.
