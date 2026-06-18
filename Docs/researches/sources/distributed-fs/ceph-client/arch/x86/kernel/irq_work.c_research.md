# sources/distributed-fs/ceph-client/arch/x86/kernel/irq_work.c

## Purpose
Provides x86 APIC-backed irq_work delivery using a self-IPI and system-vector handler.

## Important APIs And State
Under `CONFIG_X86_LOCAL_APIC`, defines `sysvec_irq_work` and `arch_irq_work_raise()`. It updates `apic_irq_work_irqs` in per-CPU IRQ stats and emits irq vector tracepoints.

## Control Flow
`arch_irq_work_raise()` checks whether the architecture has an interrupt delivery mechanism, sends `IRQ_WORK_VECTOR` to self with `__apic_send_IPI_self()`, and waits for the APIC ICR to become idle. The vector handler EOIs the APIC, traces entry/exit, increments stats, and runs queued irq_work callbacks with `irq_work_run()`.

## Dependencies And Integration Points
Depends on local APIC, IDT system vector setup, irq_work core, tracepoints, and common IRQ stats.

## Risks And Test Signals
Risks include self-IPI unavailable or delayed, missed EOI, and deadlocks if irq_work callbacks assume wrong context. Tests include irq_work queueing from NMI/IRQ/process contexts, APIC disabled cases, tracepoint visibility, and `/proc/interrupts` IWI counter increments.
