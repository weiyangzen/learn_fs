# sources/distributed-fs/ceph-client/arch/m68k/sun3/intersil.c

## Purpose

implements access to the Sun-3 Intersil RTC for hardware clock read/write operations

## Important APIs, Types, and Functions

Source read size: 70 lines, 1708 bytes. Includes: `linux/kernel.h`, `linux/rtc.h`, `asm/errno.h`,
`asm/intersil.h`, `asm/machdep.h`, `sun3.h`. Defined functions: `sun3_hwclk`. Declared functions:
`local_irq_save`, `local_irq_restore`. Key macros/defines: `STOP_VAL`, `START_VAL`.

## Control Flow and Behavior

control flow is driven by platform initialization, machdep callbacks, interrupt entry, or driver
DMA/clock requests depending on the file

## State and Persistence

persistent state is hardware register state, installed callbacks, cached IDPROM/RTC data, or
MMU/DVMA mappings as appropriate

## Dependencies and Integration Points

integrates with asm/machdep.h, Sun-3 PROM/oplib, sun3.h prototypes, m68k traps, generic
IRQ/timekeeping, and device drivers

## Risks and Test Signals

hardware register ordering and firmware assumptions are the main risks; Sun-3 defconfig boot, PROM
diagnostics, clock, IRQ, and device I/O tests are signals
