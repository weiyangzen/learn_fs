<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7724/irq.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7724/irq.c

## Purpose
SH7724 Solution Engine FPGA interrupt support. It maps FPGA interrupt bits to Linux IRQs, provides enable/disable callbacks, demultiplexes chained IRQs, and exports helper mapping functions.

## Important APIs, Types, and Functions
- functions: fpga2irq, get_fpga_irq, disable_se7724_irq, enable_se7724_irq, se7724_irq_demux, init_se7724_IRQ.

## Control Flow
- Machine-vector IRQ init calls this file during early boot; it creates mappings/descriptors and unmasks board interrupt sources before device probing.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.

## Dependencies and Integration Points
- headers: linux/init.h, linux/irq.h, linux/interrupt.h, linux/export.h, linux/topology.h, linux/io.h, linux/err.h, mach-se/mach/se7724.h.
- Source-tree integration: mach-se/7724; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.
- IRQ mask, polarity, and demux mistakes usually appear as lost or storming interrupts.

## Test Signals
- boot dmesg, /proc/interrupts, and interrupt-driven device probes are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-se/7724/irq.c -->
