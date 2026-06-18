# sources/distributed-fs/ceph-client/drivers/media/platform/intel/Kconfig

## Purpose
This Kconfig file introduces the Intel media platform driver menu and the `VIDEO_PXA27x` configuration symbol for the PXA27x Quick Capture Interface V4L2 capture driver. It controls whether `pxa_camera.c` can be built and encodes the compile-time dependencies required by the driver.

## Important APIs, Types, And Functions
There are no C APIs. The important configuration symbol is `VIDEO_PXA27x`, a tristate option labelled "PXA27x Quick Capture Interface driver". It depends on the media platform driver class, `VIDEO_DEV`, and either `PXA27x` or `COMPILE_TEST`. It selects `VIDEOBUF2_DMA_SG`, `SG_SPLIT`, and `V4L2_FWNODE`.

## Control Flow And State
Kconfig state determines whether the PXA camera driver is not built, built-in, or built as a module. The selected dependencies are part of the build-time state that makes the vb2 DMA-SG buffer handling and scatterlist splitting paths available.

## Dependencies And Integration Points
The file is integrated from the parent media platform Kconfig hierarchy. Its `VIDEO_PXA27x` symbol is consumed by the adjacent Makefile, which adds `pxa_camera.o` when enabled. The dependency on `PXA27x || COMPILE_TEST` keeps the driver tied to the intended platform while still allowing cross-architecture compile coverage.

## Risks
If the selected vb2 and scatterlist helpers diverge from what `pxa_camera.c` actually uses, the driver can fail to compile under valid configurations. The symbol name contains `PXA27x` casing, so Makefiles and external config fragments must match exactly. Because the driver uses both platform data and firmware-node endpoints, weakening `V4L2_FWNODE` selection would break OF probing.

## Test Signals
Useful checks are `allyesconfig`/`allmodconfig` build coverage, `COMPILE_TEST` builds on non-PXA architectures, and a target PXA configuration that enables `VIDEO_PXA27x` as both built-in and module. Kconfig linting should confirm there are no unmet direct dependencies for `VIDEOBUF2_DMA_SG`, `SG_SPLIT`, or `V4L2_FWNODE`.
