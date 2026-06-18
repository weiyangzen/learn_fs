# sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/Makefile

Purpose: maps STM32 media Kconfig symbols to build artifacts.

Important build rules: `CONFIG_VIDEO_STM32_CSI` builds `stm32-csi.o`; `CONFIG_VIDEO_STM32_DCMI` builds `stm32-dcmi.o`; `CONFIG_VIDEO_STM32_DCMIPP` descends into `stm32-dcmipp/`; and `CONFIG_VIDEO_STM32_DMA2D` builds the composite `stm32-dma2d.o` from `dma2d/dma2d.o` plus `dma2d/dma2d-hw.o`.

Control flow and integration: the file is consumed by kbuild after Kconfig selection. The DMA2D object composition separates V4L2/mem2mem policy from register programming, while DCMIPP has its own subdirectory Makefile for multi-entity composition.

State and risks: no runtime state. Risks are object-list drift when adding new source files, missing subdirectory traversal for DCMIPP, or mismatched module names expected by Kconfig help and userspace. Test signals are clean modular and built-in builds for each STM32 media symbol and link checks for `stm32-dma2d-objs`.
