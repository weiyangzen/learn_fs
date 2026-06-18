<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/sh7785lcr.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/sh7785lcr.h

Purpose: provides the SH7785LCR board device address map.

Important APIs/types/functions: NOR_FLASH_ADDR, NOR_FLASH_SIZE, PLD_BASE_ADDR, PLD_PCICR, PLD_LCD_BK_CONTR, PLD_LOCALCR, PLD_POFCR, PLD_LEDCR, PLD_SWSR.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/sh7785lcr.h -->
