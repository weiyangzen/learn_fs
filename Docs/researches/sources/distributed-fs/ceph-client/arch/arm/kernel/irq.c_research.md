# sources/distributed-fs/ceph-client/arch/arm/kernel/irq.c

Purpose: supplies ARM interrupt initialization, generic first-level IRQ dispatch, IRQ stack setup, `/proc/interrupts` architecture rows, and platform/cache controller initialization hooks.

Important APIs/types/functions: `handle_IRQ`, `init_IRQ`, `arch_show_interrupts`, `arch_probe_nr_irqs`, and optional `do_softirq_own_stack`. `irq_err_count` records bad IRQs; per-CPU `irq_stack_ptr` exists under `CONFIG_IRQSTACKS`.

Control flow: `init_IRQ` allocates IRQ stacks, selects DT irqchip init or machine descriptor `init_irq`, initializes L2 cache controller support when configured, and initializes UniPhier cache support. Runtime `handle_IRQ` validates IRQ numbers, maps to `irq_desc`, and calls `handle_irq_desc` or `ack_bad_irq`.

State and persistence: per-CPU IRQ stack pointers persist after boot; `irq_err_count` is reported. Machine descriptor choices determine boot-time IRQ topology.

Dependencies and integration: integrates with irqchip, machine descriptors, FIQ/IPI reporting, softirq stacks, outer cache/L2X0, DT, sparse IRQ, and reboot code include dependencies.

Risks: invalid IRQ decoding must not crash; missing IRQ stack allocation degrades safety; machine descriptor vs DT selection must match platform firmware. Test signals include boot IRQ init logs, `/proc/interrupts`, bad IRQ accounting, SMP IPI rows, and IRQ stack/softirq stress.
