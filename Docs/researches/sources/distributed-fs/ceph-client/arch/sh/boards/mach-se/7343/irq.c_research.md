<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7343/irq.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7343/irq.c

## Purpose
SH7343 Solution Engine CPLD interrupt domain. It demultiplexes CPLD status bits, creates a linear irq_domain, initializes generic-chip mask handling, and hooks init_7343se_IRQ.

## Important APIs, Types, and Functions
- functions: se7343_irq_demux, se7343_domain_init, se7343_gc_init, init_7343se_IRQ.
- integration hooks: irq_domain, generic_handle_domain_irq.

## Control Flow
- Machine-vector IRQ init calls this file during early boot; it creates mappings/descriptors and unmasks board interrupt sources before device probing.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.

## Dependencies and Integration Points
- headers: linux/init.h, linux/irq.h, linux/interrupt.h, linux/irqdomain.h, linux/io.h, linux/sizes.h, mach-se/mach/se7343.h.
- Source-tree integration: mach-se/7343; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.
- IRQ mask, polarity, and demux mistakes usually appear as lost or storming interrupts.

## Test Signals
- boot dmesg, /proc/interrupts, and interrupt-driven device probes are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7343/irq.c -->
