# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/fb/Makefile

## Purpose
Builds the MMP framebuffer frontend object.

## Important APIs, Types, and Functions
- `obj-$(CONFIG_MMP_FB) += mmpfb.o`.

## Control Flow
Kbuild compiles `mmpfb.c` when `CONFIG_MMP_FB` is enabled.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Connects the fbdev frontend to the kernel build under the MMP display subsystem.

## Risks
None beyond config dependency correctness.

## Test Signals
Build with `CONFIG_MMP_FB=m/y` and ensure `mmpfb.o` is emitted.
