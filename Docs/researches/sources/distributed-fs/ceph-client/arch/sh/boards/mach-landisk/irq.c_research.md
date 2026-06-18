<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-landisk/irq.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-landisk/irq.c

## Purpose
LANDISK board interrupt setup. It defines the board INTC vectors and mask registers and registers them through init_landisk_IRQ.

## Important APIs, Types, and Functions
- functions: init_landisk_IRQ.
- integration hooks: register_intc_controller.

## Control Flow
- Machine-vector IRQ init calls this file during early boot; it creates mappings/descriptors and unmasks board interrupt sources before device probing.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.

## Dependencies and Integration Points
- headers: linux/init.h, linux/irq.h, linux/interrupt.h, linux/io.h, mach-landisk/mach/iodata_landisk.h.
- resource/data arrays: vectors_landisk, mask_registers_landisk.
- Source-tree integration: mach-landisk; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.
- IRQ mask, polarity, and demux mistakes usually appear as lost or storming interrupts.

## Test Signals
- boot dmesg, /proc/interrupts, and interrupt-driven device probes are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-landisk/irq.c -->
