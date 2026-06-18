<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/gpio.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/gpio.h

## Purpose
Defines SH architecture declarations and macros for `gpio` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Key macros/constants include `_CPU_SH3_GPIO_H`, `PORT_PACR`, `PORT_PBCR`, `PORT_PCCR`, `PORT_PDCR`, `PORT_PECR`, `PORT_PFCR`, `PORT_PGCR`, `PORT_PHCR`, `PORT_PJCR`, `PORT_PKCR`, `PORT_PLCR`, `PORT_PMCR`, `PORT_PPCR`, `PORT_PRCR`, `PORT_PSCR`, `PORT_PTCR`, `PORT_PUCR`, plus 23 more. Register or hardware-address constants include `PORT_PACR`, `PORT_PBCR`, `PORT_PCCR`, `PORT_PDCR`, `PORT_PECR`, `PORT_PFCR`, `PORT_PGCR`, `PORT_PHCR`, `PORT_PJCR`, `PORT_PKCR`, `PORT_PLCR`, `PORT_PMCR`, plus 6 more.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_CPU_SUBTYPE_SH7720`, `CONFIG_CPU_SUBTYPE_SH7721`, `CONFIG_CPU_SUBTYPE_SH7709`. Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 78 lines, 2108 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/gpio.h -->
