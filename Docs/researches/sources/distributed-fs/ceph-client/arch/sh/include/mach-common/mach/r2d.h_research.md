<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/r2d.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/r2d.h

Purpose: provides the Renesas RTS7751R2D board FPGA/IRQ/resource map.

Important APIs/types/functions: PA_BCR, PA_IRLMON, PA_CFCTL, PA_CFPOW, PA_DISPCTL, PA_SDMPOW, PA_RTCCE, PA_PCICD, PA_VOYAGERRTS, Copyright, rts7751r2d_irq_demux.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/r2d.h -->
