# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/Kconfig

## Purpose
This Kconfig fragment defines the build-time configuration for the i.MX8 Image Sensor Interface driver and its optional memory-to-memory support.

## Important APIs, Types, and Functions
`config VIDEO_IMX8_ISI` is a tristate option for the main ISI V4L2 driver. It depends on `ARCH_MXC || COMPILE_TEST`, `HAS_DMA && PM`, and `VIDEO_DEV`. It selects `MEDIA_CONTROLLER`, `V4L2_FWNODE`, `VIDEO_V4L2_SUBDEV_API`, and `VIDEOBUF2_DMA_CONTIG`, and conditionally selects `V4L2_MEM2MEM_DEV` when `VIDEO_IMX8_ISI_M2M` is enabled. `config VIDEO_IMX8_ISI_M2M` is a bool dependent on the main driver.

## Control Flow
There is no runtime flow. At configuration time, enabling `VIDEO_IMX8_ISI` makes the ISI module or built-in driver available. Enabling `VIDEO_IMX8_ISI_M2M` includes additional mem2mem sources in the Makefile and enables real m2m registration functions instead of inline no-op stubs from `imx8-isi-core.h`.

## State and Persistence
The file contributes Kconfig symbols to the kernel configuration. Those symbols persist in `.config` and determine which driver objects are built.

## Dependencies and Integration Points
The fragment integrates with the media platform Kconfig tree, V4L2 core, media controller, fwnode parsing, videobuf2 DMA-contig memory allocator, runtime/system PM, and optional V4L2 mem2mem core.

## Risks and Edge Cases
The main option requires `PM`, so compile-test coverage without PM is intentionally excluded. `VIDEO_IMX8_ISI_M2M` is not tristate; it follows the main driver linkage and only toggles extra functionality. Missing selected dependencies would surface as link errors in ISI video, pipe, or m2m code.

## Test Signals
Build tests should cover `VIDEO_IMX8_ISI=m`, `VIDEO_IMX8_ISI=y`, compile-test builds on non-MXC architectures, and both enabled/disabled `VIDEO_IMX8_ISI_M2M` paths. Runtime tests should verify the module exposes capture support without m2m and both capture plus mem2mem nodes when m2m is selected.
