# sources/distributed-fs/ceph-client/arch/x86/xen/irq.c

Purpose: Provides Xen PV interrupt flag/halt operations and event-channel callback forcing for the x86 paravirt IRQ layer.

Important APIs/types/functions: `xen_force_evtchn_callback()` issues a cheap hypercall so Xen rechecks pending events after callback mask changes. `xen_safe_halt()` blocks via `SCHEDOP_block`, which implicitly enables interrupts. `xen_halt()` either downs the vCPU when interrupts are disabled or calls safe halt. `xen_init_irq_ops()` installs PV IRQ ops and Xen interrupt initialization.

Control flow and state: The installed PV ops make initial save-fl and irq-disable no-ops/zero-return while interrupts are known off, mark irq-enable as a bug during early setup, and install Xen halt hooks. No private persistent state is stored in this file.

Dependencies and integration points: It depends on Xen scheduler/vCPU hypercalls, event-channel core, paravirt IRQ ops, `x86_init.irqs`, and `xen_vcpu_nr()`.

Risks and test signals: Halt and callback behavior affects idle, interrupt reenable, and pending event delivery. Test signals include PV idle wakeups, event callback after mask clear, no unexpected `BUG_func` irq-enable during early boot, and correct vCPU down behavior when halting with IRQs disabled.
