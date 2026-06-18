# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/irq.h

Purpose: Declares PowerPC generic IRQ constants, per-CPU interrupt stacks, lost interrupt accounting, and architecture IRQ helper functions.

Important APIs, types, and functions: Defines `NR_IRQS`, `NR_IRQS_LEGACY`, `ppc_n_lost_interrupts`, `virq_to_hw()`, `irq_canonicalize()`, `distribute_irqs`, BookE critical/debug/mcheck stacks, hardirq/softirq stacks, `__do_IRQ()`, `irq_choose_cpu()`, and optional `arch_trigger_cpumask_backtrace()`.

Control flow: Generic IRQ code uses `__do_IRQ()` for dispatch and architecture helpers for virq/hwirq mapping and CPU target selection. Low-level exception code switches to per-CPU IRQ stacks.

State and persistence: Runtime state includes per-CPU stack pointers, lost interrupt counter, and IRQ distribution policy.

Dependencies and integration points: Depends on Linux IRQ core, cpumasks, radix-tree types, and platform interrupt controllers.

Risks: Stack pointers must be initialized before interrupt delivery. IRQ CPU selection affects affinity and load balancing. Legacy IRQ count must align with i8259 assumptions.

Test signals: SMP IRQ affinity/distribution, hardirq/softirq stack use, BookE critical/debug/mcheck interrupt stacks, virq mapping, and NMI backtrace IPI where configured.
