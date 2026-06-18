# sources/distributed-fs/ceph-client/arch/m68k/sun3/idprom.c

## Purpose

reads and validates the Sun IDPROM, including Ethernet address, machine type, serial, and checksum
fields

## Important APIs, Types, and Functions

Source read size: 134 lines, 4464 bytes. Includes: `linux/module.h`, `linux/kernel.h`,
`linux/types.h`, `linux/init.h`, `linux/string.h`, `asm/oplib.h`, `asm/idprom.h`, `asm/machines.h`,
`sun3.h`. Defined functions: `display_system_type`, `sun3_get_model`, `calc_idprom_cksum`,
`idprom_init`. Declared functions: `Copyright`, `prom_getproperty`, `prom_printf`, `strcpy`,
`display_system_type`. Types visible in this file: `idprom`. Exported symbols: `idprom`.

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
