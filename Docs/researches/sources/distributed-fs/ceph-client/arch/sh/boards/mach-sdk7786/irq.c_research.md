<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/irq.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/irq.c

## Purpose
SDK7786 IRQ initialization. It initializes FPGA-backed interrupt routing using mach/fpga.h and mach/irq.h definitions.

## Important APIs, Types, and Functions
- functions: sdk7786_init_irq.

## Control Flow
- Machine-vector IRQ init calls this file during early boot; it creates mappings/descriptors and unmasks board interrupt sources before device probing.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- headers: linux/irq.h, mach/fpga.h, mach/irq.h.
- Source-tree integration: mach-sdk7786; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- boot dmesg, /proc/interrupts, and interrupt-driven device probes are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/irq.c -->
