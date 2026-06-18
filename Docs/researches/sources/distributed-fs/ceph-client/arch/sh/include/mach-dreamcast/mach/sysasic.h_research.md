<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-dreamcast/mach/sysasic.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-dreamcast/mach/sysasic.h

Purpose: provides the Dreamcast System ASIC hardware event IRQ definitions.

Important APIs/types/functions: HW_EVENT_IRQ_BASE, HW_EVENT_VSYNC, HW_EVENT_MAPLE_DMA, HW_EVENT_GDROM_DMA, HW_EVENT_G2_DMA, HW_EVENT_PVR2_DMA, HW_EVENT_GDROM_CMD, HW_EVENT_AICA_SYS, HW_EVENT_EXTERNAL, Copyright, systemasic_irq_init.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-dreamcast/mach/sysasic.h -->
