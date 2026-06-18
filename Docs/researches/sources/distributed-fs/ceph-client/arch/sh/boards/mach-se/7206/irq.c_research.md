<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7206/irq.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7206/irq.c

## Purpose
SH7206 Solution Engine custom external IRQ controller support. It defines register addresses, enable/disable/eoi callbacks, installs irq_chip behavior, and sets interrupt sense/priority during init_se7206_IRQ.

## Important APIs, Types, and Functions
- functions: disable_se7206_irq, enable_se7206_irq, eoi_se7206_irq, make_se7206_irq, init_se7206_IRQ.

## Control Flow
- Machine-vector IRQ init calls this file during early boot; it creates mappings/descriptors and unmasks board interrupt sources before device probing.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.

## Dependencies and Integration Points
- headers: linux/init.h, linux/irq.h, linux/io.h, linux/interrupt.h, mach-se/mach/se7206.h.
- Source-tree integration: mach-se/7206; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.

## Test Signals
- boot dmesg, /proc/interrupts, and interrupt-driven device probes are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7206/irq.c -->
