# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/Kconfig

## Purpose
This Kconfig entry exposes the Samsung S5P MFC video codec driver as `CONFIG_VIDEO_SAMSUNG_S5P_MFC`. It allows the driver to be built as a module or built-in for S5PV210/Exynos platforms, and also under `COMPILE_TEST`.

## Important APIs, Types, and Constants
The key symbol is `VIDEO_SAMSUNG_S5P_MFC`, a `tristate` named "Samsung S5P MFC Video Codec". It depends on `V4L_MEM2MEM_DRIVERS`, `VIDEO_DEV`, and either a supported Samsung architecture or compile-test coverage. It selects `VIDEOBUF2_DMA_CONTIG`, matching the driver's use of contiguous DMA-backed videobuf2 queues.

## Control Flow and State
Kconfig state controls whether the Makefile builds `s5p-mfc.o`. There is no runtime logic here, but the selected dependencies define what V4L2 and vb2 APIs are available to the source files.

## Dependencies and Integration Points
This item integrates the MFC driver into the media platform build. The dependency set is important because the driver registers V4L2 video devices, implements mem2mem streaming semantics, and allocates DMA-contiguous buffers for firmware, stream, and frame storage.

## Risks
The help text still says "MFC 5.1 and 6.x" although the source includes v7, v8, v10, and v12 tables. If maintainers rely on help text, supported hardware may be underdocumented. Missing dependencies on firmware loader, PM, or OF are not explicit here but may be pulled indirectly by the platform/media configuration.

## Test Signals
Build coverage should include native Exynos configs, `COMPILE_TEST`, module and built-in builds, and link checks that all objects from the Makefile resolve when this symbol is enabled.
