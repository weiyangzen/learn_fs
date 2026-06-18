<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/Kconfig

## Purpose

This Kconfig file defines build options for the OMAP2/OMAP3 V4L2 display driver and optional VRFB support.

## Important APIs, types, and functions

- `VIDEO_OMAP2_VOUT` enables the OMAP2/3 V4L2 display driver.
- `VIDEO_OMAP2_VOUT_VRFB` is a helper bool defaulting to enabled when `VIDEO_OMAP2_VOUT` and OMAP2 VRFB support or compile testing are available.
- The main driver depends on V4L platform drivers, MMU, framebuffer support or compile-test fallback, OMAP2/OMAP3 architecture or compile test, and `VIDEO_DEV`.
- It selects `VIDEOBUF2_DMA_CONTIG` and selects `OMAP2_VRFB` on real OMAP2/3 builds.

## Control flow

There is no runtime flow. These symbols control whether OMAP vout objects and optional VRFB object are compiled.

## State and persistence behavior

State is limited to the kernel build configuration. Runtime driver state is in the compiled source files, not this Kconfig.

## Dependencies and integration points

It integrates the OMAP display driver with the media platform menu, fbdev OMAP2 support, VRFB, vb2 DMA-contig, and compile-test infrastructure.

## Risks and edge cases

The framebuffer dependency has a special compile-test exception when `FB_OMAP2=n`, so compile coverage can include systems without the real framebuffer stack. VRFB selection differs between real hardware and compile-test paths.

## Test signals

Build with OMAP2/3 hardware configs, with `COMPILE_TEST`, with VRFB enabled/disabled where possible, and as both module and built-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/Kconfig -->
