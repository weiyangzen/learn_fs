<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-dreamcast/mach/dma.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-dreamcast/mach/dma.h

Purpose: provides the Dreamcast DMA channel and register map.

Important APIs/types/functions: G2_NR_DMA_CHANNELS, PVR2_CASCADE_CHAN, G2_CASCADE_CHAN, PVR2_DMA_BASE, PVR2_DMA_ADDR, PVR2_DMA_COUNT, PVR2_DMA_MODE, PVR2_DMA_LMMODE0, PVR2_DMA_LMMODE1.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-dreamcast/mach/dma.h -->
