# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/Makefile

## Purpose
This Makefile assembles the i.MX8 ISI driver objects according to the Kconfig options.

## Important APIs, Types, and Functions
The composite object `imx8-isi.o` is built from `imx8-isi-core.o`, `imx8-isi-crossbar.o`, `imx8-isi-gasket.o`, `imx8-isi-hw.o`, `imx8-isi-pipe.o`, and `imx8-isi-video.o`. `imx8-isi-debug.o` is appended when `CONFIG_DEBUG_FS` is enabled. `imx8-isi-m2m.o` is appended when `CONFIG_VIDEO_IMX8_ISI_M2M` is enabled. `obj-$(CONFIG_VIDEO_IMX8_ISI)` controls whether the composite object is built.

## Control Flow
There is no runtime control flow. Kbuild evaluates the configuration symbols and links the selected object files into the driver.

## State and Persistence
The Makefile stores build composition only. Runtime state is in the C sources it selects.

## Dependencies and Integration Points
It depends on Kbuild composite-object conventions and the symbols from the adjacent Kconfig file. Its object list is tightly coupled to declarations in `imx8-isi-core.h`; omitting a selected source would cause unresolved symbols for crossbar, gasket, hardware, video, pipe, debugfs, or m2m functions.

## Risks and Edge Cases
Optional debugfs and m2m files must remain guarded in headers and source so both selected and unselected builds link. Changes to object names or new source files require this Makefile to stay synchronized with exported functions.

## Test Signals
Build matrix signals are the main validation: build with `CONFIG_VIDEO_IMX8_ISI=m/y`, `CONFIG_DEBUG_FS=y/n`, and `CONFIG_VIDEO_IMX8_ISI_M2M=y/n`, then check that the resulting driver links and exports the expected capture, debugfs, and mem2mem functionality.
