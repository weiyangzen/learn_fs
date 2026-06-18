# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/Kconfig

## Purpose
This Kconfig file declares the MediaTek JPEG codec driver option. The driver exposes hardware JPEG decode and encode functionality through the V4L2 mem2mem API.

## Important APIs, Types, And Functions
There are no C APIs. `VIDEO_MEDIATEK_JPEG` is a tristate labelled "Mediatek JPEG Codec driver". It depends on V4L2 mem2mem drivers, MediaTek IOMMU support or `COMPILE_TEST`, `VIDEO_DEV`, MediaTek architecture or `COMPILE_TEST`, and MediaTek SMI support or a compile-test case with SMI disabled. It selects `VIDEOBUF2_DMA_CONTIG` and `V4L2_MEM2MEM_DEV`.

## Control Flow And State
The symbol controls whether the objects in `mediatek/jpeg/Makefile` are built. Selected symbols guarantee the mem2mem framework and contiguous DMA allocator used by `mtk_jpeg_core.c`.

## Dependencies And Integration Points
The driver needs DMA-contiguous buffers and V4L2 mem2mem support. Its platform integration relies on OF matches in the core and child hardware files. The module name advertised to users is `mtk-jpeg`.

## Risks
The dependency expression around `MTK_SMI` allows compile testing when SMI is disabled, but real hardware paths may require SMI and IOMMU integration. If new SoC variants need additional clocks, IOMMU, or power-domain symbols, this Kconfig must reflect them to prevent runtime probe failures.

## Test Signals
Build as module and built-in under MediaTek SoC configs and under `COMPILE_TEST`. Check that `VIDEOBUF2_DMA_CONTIG` and `V4L2_MEM2MEM_DEV` are selected and that `mtk-jpeg` module objects link for all compatible variants.
