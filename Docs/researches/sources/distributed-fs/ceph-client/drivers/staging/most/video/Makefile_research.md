# sources/distributed-fs/ceph-client/drivers/staging/most/video/Makefile

## Purpose
Kbuild recipe for the Mostcore V4L2 component.

## Important APIs, Types, And Functions
Maps `CONFIG_MOST_VIDEO` to `most_video.o` and defines `most_video-objs := video.o`.

## Control Flow
Kbuild compiles `video.c` into the composite `most_video` module or built-in object when `MOST_VIDEO` is enabled.

## State And Persistence
No runtime state. Build output names are determined by this file.

## Dependencies And Integration Points
Consumes the `MOST_VIDEO` Kconfig symbol and integrates with the kernel module build.

## Risks
The build unit has only one source file, so missing exports or V4L2 API changes surface directly as compile/link errors.

## Test Signals
Kernel build with `CONFIG_MOST_VIDEO=m` should produce `most_video.ko` containing `video.o`; `modinfo` should show metadata from `video.c`.
