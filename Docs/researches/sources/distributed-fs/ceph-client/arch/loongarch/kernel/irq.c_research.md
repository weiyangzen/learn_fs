<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/irq.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/irq.c

Purpose: implements LoongArch interrupt initialization and interrupt dispatch glue.
Important APIs and types: provides IRQ initialization, `do_vint`, `arch_show_interrupts`, `init_IRQ`, and architecture interrupt accounting hooks.
Control flow: exception vector `handle_vint` calls `do_vint` with `pt_regs`; the C path decodes pending interrupt state, dispatches to irqdomains/chained handlers, and returns through common restore code.
State and persistence: interrupt controller mappings, per-CPU interrupt state, and IRQ statistics persist in generic IRQ structures.
Dependencies and integration: integrates with ACPI/FDT irqchip discovery, Loongson interrupt controllers, generic IRQ core, SMP IPIs, and `/proc/interrupts` reporting.
Risks and test signals: wrong vector dispatch loses interrupts or loops. Signals include timer/IPI/device interrupt tests, `/proc/interrupts`, irqdomain validation, and SMP stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/irq.c -->
