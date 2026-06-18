<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/irq-r7780rp.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/irq-r7780rp.c

## Purpose
Interrupt routing for the R7780RP Highlander board, parallel to the R7780MP file but with the R7780RP external lines and masks. It supplies highlander_plat_irq_setup for the machine vector path in setup.c.

## Important APIs, Types, and Functions
- functions: highlander_plat_irq_setup.
- integration hooks: register_intc_controller.

## Control Flow
- Machine-vector IRQ init calls this file during early boot; it creates mappings/descriptors and unmasks board interrupt sources before device probing.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- headers: linux/init.h, linux/irq.h, linux/io.h, mach/highlander.h.
- resource/data arrays: vectors, mask_registers, irl2irq.
- Source-tree integration: mach-highlander; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.
- IRQ mask, polarity, and demux mistakes usually appear as lost or storming interrupts.

## Test Signals
- boot dmesg, /proc/interrupts, and interrupt-driven device probes are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/irq-r7780rp.c -->
