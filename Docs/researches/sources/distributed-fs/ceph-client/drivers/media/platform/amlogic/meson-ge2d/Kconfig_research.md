
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/meson-ge2d/Kconfig

## Purpose

This Kconfig file defines `CONFIG_VIDEO_MESON_GE2D`, the build option for the Amlogic GE2D 2D graphics accelerator V4L2 mem2mem driver. GE2D provides color conversion, scaling, BitBLT, and alpha-blending hardware, though the current driver implements a narrower RGB blit/transform subset.

## Important APIs, Types, And Functions

The single tristate symbol is `VIDEO_MESON_GE2D`, prompted as `"Amlogic 2D Graphic Acceleration Unit"`. The option selects `VIDEOBUF2_DMA_CONTIG` and `V4L2_MEM2MEM_DEV`, which are required by `ge2d.c`.

## Control Flow

Kconfig allows this driver when V4L2 mem2mem infrastructure, video device support, and either Meson architecture or compile testing are enabled. The help text explains module selection and high-level hardware capability.

## State And Persistence

No runtime state is stored here. The build configuration determines whether the Makefile builds `ge2d.o`.

## Dependencies And Integration Points

The option integrates a platform V4L2 mem2mem accelerator into the media build. It depends on `V4L_MEM2MEM_DRIVERS` and `VIDEO_DEV`, aligning with the driver's V4L2 mem2mem queues, video node, and VB2 DMA-contig memory usage.

## Risks

The help text mentions scaling and color conversion hardware capabilities while `ge2d.c` documents several missing features, including scaling and YUV input support. Integrators should treat the Kconfig description as hardware capability, not full driver feature coverage.

## Test Signals

Build with `CONFIG_VIDEO_MESON_GE2D=m` and `=y` under Meson and `COMPILE_TEST`. Confirm the config selects mem2mem and DMA-contig support and produces the GE2D driver object/module.
