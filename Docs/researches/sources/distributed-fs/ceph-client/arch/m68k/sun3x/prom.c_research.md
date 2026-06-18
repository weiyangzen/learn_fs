# sources/distributed-fs/ceph-client/arch/m68k/sun3x/prom.c

## Purpose

wraps Sun-3x PROM calls for device tree-like firmware queries, console operations, reboot/halt, and
memory/device discovery

## Important APIs, Types, and Functions

Source read size: 164 lines, 3668 bytes. Includes: `linux/types.h`, `linux/kernel.h`, `linux/tty.h`,
`linux/console.h`, `linux/init.h`, `linux/mm.h`, `linux/string.h`, `asm/page.h`, `asm/setup.h`,
`asm/traps.h`, `asm/sun3xprom.h`, `asm/idprom.h`; plus 3 more. Defined functions: `sun3x_halt`,
`sun3x_reboot`, `sun3x_prom_write`, `sun3x_prom_init`, `sun3x_debug_setup`, `prom_getintdefault`,
`prom_getbool`, `prom_printf`, `prom_halt`, `prom_get_idprom`. Declared functions: `volatile`,
`idprom_init`, `pr_warn`, `register_console`. Types visible in this file: `linux_romvec`.

## Control Flow and Behavior

control flow is entered from platform setup, firmware service wrappers, or generic
timekeeping/machdep hooks

## State and Persistence

persistent state includes PROM vectors, installed machdep callbacks, RTC register values, and
DVMA/IOMMU state for data movers

## Dependencies and Integration Points

integrates with Sun-3x PROM firmware, m68k machine setup, generic timekeeping, reset paths, and
device drivers

## Risks and Test Signals

firmware ABI and clock register mistakes can block boot or skew time; Sun-3x boot, clock read/write,
PROM console, and DMA tests are signals
