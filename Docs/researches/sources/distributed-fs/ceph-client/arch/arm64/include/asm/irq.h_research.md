## sources/distributed-fs/ceph-client/arch/arm64/include/asm/irq.h

Purpose: declares arm64 IRQ controller entry hooks and backtrace support.

Important APIs/types/functions: exports `arch_trigger_cpumask_backtrace`, `set_handle_irq`, `set_handle_fiq`, and `nr_legacy_irqs`.

Control flow: platform IRQ code registers top-level IRQ/FIQ handlers; exception entry calls the registered handler with pt_regs. Backtrace code can request cross-CPU stack dumps.

State and persistence: registered IRQ/FIQ handler pointers persist after interrupt controller initialization.

Dependencies and integration: depends on generic IRQ, cpumasks, interrupt controllers, SMP backtrace, and exception entry.

Risks: missing or duplicate handler registration prevents interrupt delivery. Test signals are interrupt controller boot, IPI/backtrace tests, FIQ paths, and warning paths for legacy IRQ count.
