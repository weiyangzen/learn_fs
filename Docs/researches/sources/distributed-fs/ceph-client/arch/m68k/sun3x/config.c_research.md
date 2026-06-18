# sources/distributed-fs/ceph-client/arch/m68k/sun3x/config.c

## Purpose

sets Sun-3x machine callbacks and model/reset behavior for the 68030 Sun platform variant

## Important APIs, Types, and Functions

Source read size: 76 lines, 1435 bytes. Includes: `linux/types.h`, `linux/mm.h`, `linux/seq_file.h`,
`linux/console.h`, `linux/init.h`, `asm/machdep.h`, `asm/irq.h`, `asm/sun3xprom.h`,
`asm/sun3ints.h`, `asm/setup.h`, `asm/oplib.h`, `asm/config.h`; plus 2 more. Defined functions:
`sun3_leds`, `sun3x_get_hardware_list`, `config_sun3x`. Declared functions: `sun3x_prom_init`.

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
