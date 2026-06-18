<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-r2d/irq.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-r2d/irq.c

## Purpose
RTS7751R2D interrupt routing. It provides revision-specific vector/mask/IRL tables, demultiplexes external IRL interrupts, and registers board INTC descriptors.

## Important APIs, Types, and Functions
- functions: rts7751r2d_irq_demux, init_rts7751r2d_IRQ.
- integration hooks: register_intc_controller.

## Control Flow
- Machine-vector IRQ init calls this file during early boot; it creates mappings/descriptors and unmasks board interrupt sources before device probing.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- headers: linux/init.h, linux/irq.h, linux/interrupt.h, linux/io.h, mach/r2d.h.
- resource/data arrays: vectors_r2d_1, mask_registers_r2d_1, irl2irq_r2d_1, vectors_r2d_plus, mask_registers_r2d_plus, irl2irq_r2d_plus, irl2irq.
- Source-tree integration: mach-r2d; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.
- IRQ mask, polarity, and demux mistakes usually appear as lost or storming interrupts.

## Test Signals
- boot dmesg, /proc/interrupts, and interrupt-driven device probes are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-r2d/irq.c -->
