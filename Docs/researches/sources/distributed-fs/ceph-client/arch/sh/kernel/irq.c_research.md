# sources/distributed-fs/ceph-client/arch/sh/kernel/irq.c

Purpose: implements SH IRQ entry glue, interrupt statistics, optional IRQ/softirq stacks, IRQ initialization, and hotplug IRQ migration.

Important APIs and control flow: `ack_bad_irq()` increments `irq_err_count`. `arch_show_interrupts()` prints NMI and ERR lines for `/proc/interrupts`. With IRQ stacks, `irq_ctx_init()` initializes per-CPU hard/soft IRQ thread-info stacks; `handle_one_irq()` switches to the hardirq stack before `generic_handle_irq()` unless already on it; `do_softirq_own_stack()` runs softirqs on their own stack. `do_IRQ()` sets irq regs, enters irq context, demuxes `irq_lookup()`, handles and finishes the IRQ, exits, and restores regs. `init_IRQ()` calls platform setup, machine-vector setup, `intc_finalize()`, and initializes CPU0 IRQ stacks.

State, dependencies, and risks: state includes `irq_err_count`, per-CPU IRQ stack arrays, platform/machine-vector IRQ demux hooks, and interrupt controller setup. Dependencies include generic IRQ core, SH INTC, softirq stack helpers, and CPU hotplug. Risks include stack switching assembly clobbers, demux returning ignored IRQs, affinity migration during hotplug, and missing stack init on secondary CPUs. Test signals are `/proc/interrupts`, nested interrupt load, softirq stress, hotplug migration, and bad-vector logging.
