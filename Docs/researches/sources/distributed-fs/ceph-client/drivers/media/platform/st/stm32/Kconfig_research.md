# sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/Kconfig

Purpose: declares STM32 media platform driver configuration symbols for CSI, DCMI, DCMIPP, and DMA2D. It controls which drivers are built and which media/V4L2 helper subsystems are selected.

Important symbols: `VIDEO_STM32_CSI` builds the STM32 Camera Serial Interface bridge and selects media controller plus V4L2 fwnode support. `VIDEO_STM32_DCMI` builds the Digital Camera Memory Interface capture driver and selects vb2 DMA-contig, media controller, and V4L2 fwnode. `VIDEO_STM32_DCMIPP` builds the Digital Camera Memory Interface Pixel Processor pipeline and selects media controller, vb2 DMA-contig, V4L2 subdev API, and V4L2 fwnode. `VIDEO_STM32_DMA2D` builds the Chrom-Art Accelerator mem2mem driver and selects vb2 DMA-contig and V4L2 mem2mem.

Control flow and integration: each symbol depends on the appropriate media driver class (`V4L_PLATFORM_DRIVERS` or `V4L_MEM2MEM_DRIVERS`), `VIDEO_DEV`, and either `ARCH_STM32` or `COMPILE_TEST`. These options feed the adjacent Makefile and govern module names such as `stm32-csi`, `stm32-dcmi`, `stm32-dcmipp`, and `stm32-dma2d`.

State and risks: Kconfig has no runtime state but shapes build-time dependency availability. Risks are missing selected helpers for vb2, fwnode graph parsing, media-controller links, or mem2mem scheduling, and compile-test paths masking runtime-only clock/reset/DMA/DT requirements. Test signals are `allyesconfig`, `allmodconfig`, `COMPILE_TEST`, and targeted builds with each symbol disabled, modular, and built-in.
