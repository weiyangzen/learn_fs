## sources/distributed-fs/ceph-client/arch/mips/ath25/ar2315_regs.h

Purpose: defines AR2315+ interrupt numbers, physical address map, reset/control register offsets, bitfields, PLL fields, SDRAM fields, and local bus register constants used by `ar2315.c` and related platform code.

Important definitions: CPU IRQ assignments include `AR2315_IRQ_MISC`, `AR2315_IRQ_WLAN0`, and `AR2315_IRQ_LCBUS_PCI`. Misc IRQ hardware numbers include UART, SPI, AHB/APB, timer, GPIO, and watchdog. Address constants define SPI flash, WMAC, PCI, SDRAM, reset, UART, and PCI external windows. Register fields cover cold/warm resets, AHB arbitration, endian control, interface control, interrupt status/mask, watchdog, AHB error reports, PLL/CPU/AMBA clocks, SDRAM geometry, and local bus DMA/status.

Control flow: none; consumers use these macros for MMIO calculations, bit extraction, and IRQ mapping.

State and persistence: none directly. The constants name persistent hardware registers.

Dependencies and integration: included by `ar2315.c`, `early_printk.c`, and any AR2315 low-level code. It pairs with the `ATH25_REG_MS()` bitfield helper from `devices.h`.

Risks: typo risk is significant in register headers. One macro, `AR2315_RESET_SYSTEM`, references `RESET_COLD_*` names rather than the local `AR2315_RESET_COLD_*` names, although the implementation uses `AR2317_RESET_SYSTEM` for reset. Duplicate or stale hardware comments could mislead future driver work.

Test signals: compile coverage for all referenced macros, plus runtime validation of memory detection, clock frequency, PCI, UART, and interrupt dispatch. Register-level tests are hardware boot/probe behavior.
