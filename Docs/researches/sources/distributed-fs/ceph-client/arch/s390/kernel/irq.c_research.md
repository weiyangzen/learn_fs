# sources/distributed-fs/ceph-client/arch/s390/kernel/irq.c

Purpose: handles s390 external and I/O interrupt entry, interrupt accounting display, external interrupt handler registration, and interrupt subclass reference management.

Important APIs and state: per-CPU `irq_stat` tracks arch interrupt subclasses. `do_io_irq()` and `do_ext_irq()` are noinstr entry points. `show_interrupts()` backs `/proc/interrupts`; `arch_dynirq_lower_bound()` reserves base IRQs. `register_external_irq()` and `unregister_external_irq()` maintain an RCU hlist hash of external interrupt handlers. `irq_subclass_register()` and `irq_subclass_unregister()` manage CR0 subclass bits with refcounts.

Control flow: interrupt entry saves/restores irq regs, enters generic irqentry/RCU accounting, handles idle exit accounting, updates user-mode timer state and BEAR last-break data, then dispatches on async stack when needed. I/O entry loops on pending interrupts on LPAR and selects thin vs regular I/O based on lowcore TPI info. External entry copies lowcore external parameters and calls the registered handler chain for the code.

Dependencies and integration: integrates generic IRQ, `/proc/interrupts`, CIO/AIRQ init, clock comparator work, lowcore, irqentry, vtime, async stacks, RCU, and control-register subclass management. CPU-MF, virtio, IUCV, PCI, AP, and other facilities register external handlers here.

Risks and test signals: stack switching, idle accounting, RCU lifetime of handlers, and subclass refcount underflow are sensitive. Test with `/proc/interrupts`, external IRQ register/unregister users, CPU hotplug, timer-heavy idle workloads, LPAR pending I/O loops, and lockdep/RCU diagnostics.
