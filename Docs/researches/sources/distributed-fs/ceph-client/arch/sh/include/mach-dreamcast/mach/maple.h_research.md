<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-dreamcast/mach/maple.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-dreamcast/mach/maple.h

Purpose: provides the Dreamcast Maple bus constants and function codes.

Important APIs/types/functions: MAPLE_PORTS, MAPLE_PNP_INTERVAL, MAPLE_MAXPACKETS, MAPLE_DMA_ORDER, MAPLE_DMA_SIZE, MAPLE_DMA_PAGES, MAPLE_BASE, MAPLE_DMAADDR, MAPLE_TRIGTYPE.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-dreamcast/mach/maple.h -->
