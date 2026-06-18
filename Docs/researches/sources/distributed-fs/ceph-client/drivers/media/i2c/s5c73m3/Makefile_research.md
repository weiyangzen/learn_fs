# sources/distributed-fs/ceph-client/drivers/media/i2c/s5c73m3/Makefile

## Purpose
This Makefile defines how the Samsung S5C73M3 camera driver is built. It combines the core I2C/V4L2 implementation, SPI firmware transport, and control implementation into one `s5c73m3` module when `CONFIG_VIDEO_S5C73M3` is enabled.

## Important APIs, Types, and Functions
The build contract is `s5c73m3-objs := s5c73m3-core.o s5c73m3-spi.o s5c73m3-ctrls.o` and `obj-$(CONFIG_VIDEO_S5C73M3) += s5c73m3.o`. There are no runtime APIs in this file, but it is the link boundary that lets `s5c73m3-core.c` call symbols exported by the local SPI and controls translation units.

## Control Flow
Kbuild compiles the three object files and links them into `s5c73m3.o`. The module entry point is the I2C driver declared in `s5c73m3-core.c`; `s5c73m3-spi.c` contributes helper registration and SPI transfer functions, and `s5c73m3-ctrls.c` contributes `s5c73m3_init_controls()`.

## State and Persistence
The file stores no runtime state. Its only persistent effect is build composition under the kernel configuration system.

## Dependencies and Integration Points
It integrates with Kconfig symbol `CONFIG_VIDEO_S5C73M3` and the Linux media I2C driver build. The object ordering means unresolved cross-file symbols must match declarations in `s5c73m3.h`.

## Risks and Edge Cases
Removing one object silently breaks link-time availability of core helper functions. Splitting the driver into multiple modules would require changing this file and the internal symbol visibility because these objects currently share one module namespace.

## Test Signals
The main signal is a successful kernel build with `CONFIG_VIDEO_S5C73M3=m` or `y`, producing a module that includes I2C probe/remove, SPI helper registration, and V4L2 control setup without unresolved symbols.
