# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/Kconfig

## Purpose

This Kconfig file exposes the Amlogic C3 Image Signal Processor driver as `VIDEO_C3_ISP`. The driver provides a V4L2/media-controller ISP pipeline for processing raw images and writing results to memory.

## Important APIs, Types, And Symbols

- `VIDEO_C3_ISP` is a tristate symbol.
- Dependencies are `ARCH_MESON || COMPILE_TEST`, `VIDEO_DEV`, and `OF`.
- It selects `MEDIA_CONTROLLER`, `V4L2_FWNODE`, `VIDEO_V4L2_SUBDEV_API`, `VIDEOBUF2_DMA_CONTIG`, `VIDEOBUF2_VMALLOC`, and `V4L2_ISP`.

## Control Flow

When dependencies are satisfied, users can build the C3 ISP as a module or built-in. The sibling Makefile aggregates multiple C3 ISP objects into `c3-isp.o`.

## State And Persistence

The `.config` setting is the only state here. Runtime state is in the C3 ISP C files and shared header.

## Dependencies And Integration Points

The selected symbols match the implementation: media graph entities, V4L2 subdevs, fwnode parsing, DMA-contig capture buffers, vmalloc metadata/parameter buffers, and the V4L2 ISP API are all used by the driver family.

## Risks

If dependencies are incomplete, compile or link failures will appear in broad build testing. The help text says "outputing", a spelling issue only. The symbol depends on OF, so non-device-tree use is intentionally excluded.

## Test Signals

Compile with `CONFIG_VIDEO_C3_ISP=m` under `ARCH_MESON` and `COMPILE_TEST`. Runtime signals include media-controller entity registration and successful ISP capture video node creation.
