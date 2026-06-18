# sources/distributed-fs/ceph-client/arch/m68k/sun3/dvma.c

## Purpose

initializes low-level Sun-3 DVMA page mappings from kernel addresses into bus-visible virtual space

## Important APIs, Types, and Functions

Source read size: 68 lines, 1290 bytes. Includes: `linux/init.h`, `linux/kernel.h`, `linux/mm.h`,
`linux/memblock.h`, `linux/list.h`, `asm/page.h`, `asm/sun3mmu.h`, `asm/dvma.h`. Defined functions:
`dvma_page`, `dvma_map_iommu`, `sun3_dvma_init`. Declared functions: `sun3_put_pte`, `return`,
`dvma_page`.

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
