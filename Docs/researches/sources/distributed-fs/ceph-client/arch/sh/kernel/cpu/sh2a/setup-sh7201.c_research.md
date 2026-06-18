<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-sh7201.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-sh7201.c

Purpose: declares SH7201 interrupt table and core platform devices.

Important APIs/types/functions: large INTC vector/group/priority/mask tables, SCIF0-7, CMT/MTU2 resources, `sh7201_devices_setup()`, `plat_irq_setup()`, `plat_early_device_setup()`.

Control flow: arch initcall adds serial/timer devices; early setup enables required clocks and registers early devices; IRQ setup registers the INTC descriptor.

State and persistence: state is platform-device registry, interrupt controller registers, and clock-gating bits.

Dependencies/integration: integrates sh-sci, CMT/MTU2, INTC, and early console/timer infrastructure.

Risks: vector/resource mismatches break specific serial ports or timer channels.

Test signals: boot with each SCIF, CMT/MTU interrupts, and early console.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-sh7201.c -->
