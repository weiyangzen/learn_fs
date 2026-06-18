<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7780/irq.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7780/irq.c

## Purpose
SH7780 Solution Engine external interrupt register setup. It programs interrupt control/priority/mask registers in init_se7780_IRQ.

## Important APIs, Types, and Functions
- functions: init_se7780_IRQ.

## Control Flow
- Machine-vector IRQ init calls this file during early boot; it creates mappings/descriptors and unmasks board interrupt sources before device probing.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.

## Dependencies and Integration Points
- headers: linux/init.h, linux/irq.h, linux/interrupt.h, linux/io.h, mach-se/mach/se7780.h.
- Source-tree integration: mach-se/7780; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.

## Test Signals
- boot dmesg, /proc/interrupts, and interrupt-driven device probes are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7780/irq.c -->
