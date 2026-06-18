<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/Kconfig

## Purpose

This Kconfig file defines build-time options for the TI DaVinci VPIF V4L2 display and capture drivers.

## Important APIs, types, and functions

- `VIDEO_DAVINCI_VPIF_DISPLAY` builds the VPIF display stack for DM6467/DA850/OMAPL138-class SoCs.
- `VIDEO_DAVINCI_VPIF_CAPTURE` builds the VPIF capture stack for the same family.
- Both options depend on V4L platform drivers, V4L2 video device support, DaVinci architecture or compile testing, and I2C.
- Display selects `VIDEOBUF2_DMA_CONTIG`, and auto-selects ADV7343/THS7303 subdrivers when media subdriver autoselection is enabled.
- Capture selects `VIDEOBUF2_DMA_CONTIG` and `V4L2_FWNODE`.

## Control flow

There is no runtime flow. Selecting either symbol controls which objects the Makefile compiles and which dependent media components are made available.

## State and persistence behavior

Kconfig state is stored in the kernel build configuration. It does not affect runtime persistence beyond deciding whether the drivers are built-in, modules, or omitted.

## Dependencies and integration points

This file integrates the DaVinci VPIF drivers with the kernel media Kconfig hierarchy and ensures vb2 DMA-contig and relevant I2C/media subdevice infrastructure are present.

## Risks and edge cases

If dependencies are too broad, compile-test builds may miss missing platform data assumptions. If dependencies are too narrow, valid DT or board-file systems may be unable to enable the driver. The help text notes each mode builds two modules: common `vpif.ko` plus capture or display-specific module.

## Test signals

Build `allyesconfig`, `allmodconfig`, and `COMPILE_TEST` configurations with both symbols as modules and built-ins. Verify selected subdrivers and generated modules match the help text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/Kconfig -->
