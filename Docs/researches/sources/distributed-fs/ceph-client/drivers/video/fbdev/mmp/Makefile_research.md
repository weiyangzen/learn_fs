# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/Makefile

## Purpose
Builds the Marvell MMP display framework root object and descends into hardware, panel, and framebuffer subdirectories when `CONFIG_MMP_DISP` is enabled.

## Important APIs, Types, and Functions
- `obj-$(CONFIG_MMP_DISP) += mmp_disp.o hw/ panel/ fb/`.
- `mmp_disp-y += core.o` links the registry framework implementation.

## Control Flow
Kbuild compiles `core.o` into `mmp_disp.o` and builds child directories under the same config gate.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Connects `core.c` and the MMP subdirectories to the kernel build.

## Risks
All child directories are visited under the root config, but their own object inclusion still depends on nested configs. Misconfigured dependencies can compile panel/fb code without usable platform devices.

## Test Signals
Build with `CONFIG_MMP_DISP=m/y` and verify `mmp_disp.o` plus configured children are produced.
