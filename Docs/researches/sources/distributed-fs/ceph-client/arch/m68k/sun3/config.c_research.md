# sources/distributed-fs/ceph-client/arch/m68k/sun3/config.c

## Purpose

sets Sun-3 machdep callbacks, model strings, memory/device setup, and reboot/interrupt/time hooks
during platform configuration

## Important APIs, Types, and Functions

Source read size: 221 lines, 5450 bytes. Includes: `linux/types.h`, `linux/kernel.h`, `linux/mm.h`,
`linux/seq_file.h`, `linux/tty.h`, `linux/console.h`, `linux/init.h`, `linux/memblock.h`,
`linux/platform_device.h`, `linux/linkage.h`, `asm/oplib.h`, `asm/setup.h`; plus 14 more. Defined
functions: `sun3_get_hardware_list`, `sun3_init`, `sun3_reboot`, `sun3_halt`, `sun3_bootmem_alloc`,
`config_sun3`, `sun3_sched_init`, `sun3_platform_init`. Declared functions: `sun3_sched_init`,
`prom_init`, `m68k_setup_node`, `pr_info`, `sun3_enable_irq`, `platform_device_register_simple`.
External symbols referenced/declared: `availmem`.

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
