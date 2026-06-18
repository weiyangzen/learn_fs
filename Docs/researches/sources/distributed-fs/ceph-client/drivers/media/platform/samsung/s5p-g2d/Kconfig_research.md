# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-g2d/Kconfig

Purpose: build configuration for the Samsung S5P/Exynos G2D 2D graphics accelerator V4L2 mem2mem driver.

Important declarations: `config VIDEO_SAMSUNG_S5P_G2D` is a tristate option. It depends on `V4L_MEM2MEM_DRIVERS`, `VIDEO_DEV`, and either `ARCH_S5PV210`, `ARCH_EXYNOS`, or `COMPILE_TEST`. It selects `VIDEOBUF2_DMA_CONTIG` and `V4L2_MEM2MEM_DEV`.

Control flow and integration: enabling this option causes the Makefile to build the `s5p-g2d` module/object from `g2d.o` and `g2d-hw.o`. The selected dependencies ensure V4L2 mem2mem and contiguous DMA buffer support are present for queueing and hardware DMA.

State and persistence: no runtime state; this is kernel build metadata.

Risks: missing architecture or mem2mem dependencies will hide the option. Selecting DMA-contig implies the runtime driver expects physically contiguous buffers or IOMMU-compatible contiguous DMA mappings.

Test signals: Kconfig visibility under Exynos/S5PV210 and `COMPILE_TEST`, module build with `CONFIG_VIDEO_SAMSUNG_S5P_G2D=m`, and dependency closure in allmodconfig-style builds.
