<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hardirq.h -->
# sources/distributed-fs/ceph-client/include/linux/hardirq.h

Purpose: This header defines generic hard IRQ and NMI context entry/exit helpers used by architecture IRQ paths and low-level kernel code.

Important APIs/types/functions: It declares `synchronize_irq()` and `synchronize_hardirq()`, optional NO_HZ_FULL `__rcu_irq_enter_check_tick()`, and inline `rcu_irq_enter_check_tick()`. Macros `__irq_enter()`, `__irq_enter_raw()`, `__irq_exit()`, and `__irq_exit_raw()` adjust preempt count, lockdep state, and hardirq accounting. Functions `irq_enter()`, `irq_enter_rcu()`, `irq_exit()`, and `irq_exit_rcu()` provide higher-level paths. NMI helpers `__nmi_enter()`, `nmi_enter()`, `__nmi_exit()`, and `nmi_exit()` manage lockdep, arch hooks, preempt count, context tracking, instrumentation, and ftrace.

Control flow, state, and persistence: IRQ entry increments hardirq preempt count before code runs in hardirq context; exit decrements and may process softirqs through implementation. NMI entry disables lockdep, adds NMI plus hardirq offsets, enters context tracking/tracing, and exit reverses the sequence. These helpers rely on strictly balanced entry/exit calls.

Dependencies/integration: It integrates preempt accounting, lockdep, ftrace IRQ/NMI tracing, context tracking, scheduler hardirq time accounting, vtime, and architecture hardirq definitions.

Risks and test signals: Incorrect ordering can make tracing observe inconsistent `in_nmi()`/preempt state. Unbalanced entry/exit corrupts preempt count and lockdep state. Tests/signals include lockdep IRQ state validation, ftrace NMI tracing, NO_HZ full tick checks, softirq processing after IRQ exit, and architecture build coverage for arch NMI hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hardirq.h -->
