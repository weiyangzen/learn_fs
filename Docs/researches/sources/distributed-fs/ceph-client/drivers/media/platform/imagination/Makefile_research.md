# sources/distributed-fs/ceph-client/drivers/media/platform/imagination/Makefile

## Purpose
Builds the Imagination E5010 JPEG encoder module from its core driver and hardware helper objects.

## Important APIs, Types, and Functions
Defines `e5010_jpeg_enc-objs := e5010-jpeg-enc-hw.o e5010-jpeg-enc.o` and adds the module through `obj-$(CONFIG_VIDEO_E5010_JPEG_ENC) += e5010_jpeg_enc.o`.

## Control Flow
No runtime flow. Kbuild links the hardware abstraction and V4L2 driver implementation into one module when the Kconfig symbol is enabled.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Depends on the Kconfig symbol and Kbuild media platform traversal. The object order places hardware helpers before main driver in the module object list, though both are linked together.

## Risks
Adding new source files without updating this Makefile causes unresolved references. Renaming the config or objects breaks module builds.

## Test Signals
Module build with `CONFIG_VIDEO_E5010_JPEG_ENC=m` and built-in build with `=y`.
