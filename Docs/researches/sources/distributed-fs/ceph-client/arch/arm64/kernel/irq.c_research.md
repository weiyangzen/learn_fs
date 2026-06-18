# sources/distributed-fs/ceph-client/arch/arm64/kernel/irq.c

Purpose: Initializes arm64 IRQ infrastructure, per-CPU IRQ stacks, optional shadow call stacks, root IRQ/FIQ handlers, and softirq-on-own-stack support.

Important APIs and state: per-CPU `nmi_contexts`, `irq_stack_ptr`, and optional `irq_shadow_call_stack_ptr` hold interrupt execution context. `handle_arch_irq` and `handle_arch_fiq` are `__ro_after_init` function pointers initialized to panic defaults. APIs include `set_handle_irq()`, `set_handle_fiq()`, `init_IRQ()`, and `do_softirq_own_stack()`.

Control flow: `init_IRQ()` allocates IRQ stacks, allocates IRQ shadow call stacks when enabled, calls `irqchip_init()`, and adjusts DAIF/PMR state for priority masking. Root handlers can be installed only once; otherwise registration returns `-EBUSY`.

Dependencies and integration: depends on irqchip drivers, stacktrace/vmap stack helpers, shadow call stack allocation, softirq stack assembly helper `call_on_irq_stack()`, NUMA early CPU-to-node mapping, and GIC priority masking cpufeatures.

Risks and test signals: risks include missing IRQ stack allocation, double root handler registration, priority mask left blocking wakeups, and SCS stack exhaustion. Test with boot IRQ init, interrupt flood, softirq stress, FIQ handler registration where available, vmap stack debug, and priority masking configurations.
