<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/freq.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/freq.h

## Purpose
Defines CPU-family clock/frequency-control register addresses and divisor limits used by clock initialization code.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_CPU_SH4_FREQ_H`, `FRQCR`, `VCLKCR`, `SCLKACR`, `SCLKBCR`, `IrDACLKCR`, `MSTPCR0`, `MSTPCR1`, `MSTPCR2`, `OSCCR`, `PLLCR`, `FRQCRA`, `FRQCRB`, `FCLKACR`, `FCLKBCR`, `FRQCR0`, `FRQCR2`, `FRQMR1`, plus 7 more. Register or hardware-address constants include `FRQCR`, `VCLKCR`, `SCLKACR`, `SCLKBCR`, `IrDACLKCR`, `OSCCR`, `PLLCR`, `FCLKACR`, `FCLKBCR`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_CPU_SUBTYPE_SH7722`, `CONFIG_CPU_SUBTYPE_SH7723`, `CONFIG_CPU_SUBTYPE_SH7343`, `CONFIG_CPU_SUBTYPE_SH7366`, `CONFIG_CPU_SUBTYPE_SH7757`, `CONFIG_CPU_SUBTYPE_SH7763`, `CONFIG_CPU_SUBTYPE_SH7780`, `CONFIG_CPU_SUBTYPE_SH7724`, `CONFIG_CPU_SUBTYPE_SH7734`, `CONFIG_CPU_SUBTYPE_SH7785`, `CONFIG_CPU_SUBTYPE_SH7786`, `CONFIG_CPU_SUBTYPE_SHX3`. Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 74 lines, 1995 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/freq.h -->
