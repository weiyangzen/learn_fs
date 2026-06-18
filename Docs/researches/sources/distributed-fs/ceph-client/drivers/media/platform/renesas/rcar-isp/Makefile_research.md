# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-isp/Makefile

## Purpose
This Makefile builds the R-Car ISP Channel Selector driver.

## Important APIs, Types, And Functions
It declares `rcar-isp-objs = csisp.o` and adds `rcar-isp.o` to `obj-*` when `CONFIG_VIDEO_RCAR_ISP` is enabled.

## Control Flow
Kbuild compiles `csisp.c` into the composite object `rcar-isp.o`. If the config is modular, the resulting module is `rcar-isp.ko`; if built-in, it is linked into the kernel image.

## State And Persistence
No runtime state is present. The file only affects build graph composition.

## Dependencies And Integration Points
It integrates with the Kconfig symbol in the same directory and the kernel media platform build tree.

## Risks
Because only `csisp.o` is listed, future split files must be added here or they will not build. A mismatch between Kconfig help text and object name would confuse module loading, but currently they align.

## Test Signals
Build `CONFIG_VIDEO_RCAR_ISP=y` and `m`, verify `csisp.o` is included once, and confirm `modinfo rcar-isp.ko` when modular.
