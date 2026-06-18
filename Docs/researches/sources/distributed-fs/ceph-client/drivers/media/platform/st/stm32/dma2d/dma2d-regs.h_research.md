# sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/dma2d/dma2d-regs.h

Purpose: defines the STM32 DMA2D register map, bitfields, color mode constants, hardware limits, and default dimensions used by the DMA2D V4L2 mem2mem driver.

Important constants: control register fields include operation modes `CR_M2M`, `CR_M2M_PFC`, `CR_M2M_BLEND`, `CR_R2M`, interrupt enables, abort/suspend/start bits, and mode masks. Status/clear flags cover configuration, transfer complete, access, watermark, transfer complete, and transfer error conditions. Address/offset/pixel-format registers are defined for foreground, background, and output layers. `MAX_WIDTH`/`MAX_HEIGHT` are 2592, defaults are 240x320 with `DEFAULT_SIZE` 307200, and color mode constants include ARGB8888, ARGB4444, and A4.

Control flow and integration: `dma2d-hw.c` uses these definitions to program MMIO registers; `dma2d.c` uses size limits and defaults for V4L2 format negotiation. The constants are a hardware ABI and must match STM32 DMA2D documentation.

State and risks: no runtime state. Risks are stale or incorrect bit definitions causing silent register misprogramming, partial color-mode coverage relative to `enum dma2d_cmode`, and default size assumptions that must match default pixel format/depth. Test signals are compile-time use across both DMA2D source files, hardware register dumps, interrupt flag clear tests, and format conversion validation across all advertised formats.
