# sources/distributed-fs/ceph-client/include/linux/irqflags.h

## Purpose
`irqflags.h` wraps architecture local IRQ flag operations with lockdep, tracing, debug checks, critical timing, hrtimer/posix timer/irq_work context markers, and scoped cleanup guards.

## Important APIs, types, and functions
It declares or stubs lockdep hard/soft IRQ helpers, trace IRQ flag helpers, per-CPU trace state, hardirq enter/exit/threaded markers, timer/irq_work lockdep context helpers, raw `local_irq_*` wrappers, traced `local_irq_*` wrappers, `safe_halt`, `irqs_disabled`, `irqs_disabled_flags`, and `DEFINE_LOCK_GUARD_0` guards for `irq` and `irqsave`.

## Control flow
Callers save/disable/restore/enable IRQs. With tracing enabled, wrappers record transitions only when state changes, then call raw arch operations. Debug restore checks catch bogus restores. Lockdep context helpers mark whether callbacks run as hardirq-like or softirq-like contexts.

## State and persistence
State is per-CPU hardirq trace counters and per-task softirq/irq_config trace fields. There is no persistent state.

## Dependencies and integration points
It depends on arch IRQ flag primitives, percpu access, type checking, cleanup guards, lockdep, IRQ flag tracing, preempt/irqsoff tracers, and debug IRQ flags.

## Risks and test signals
Risks include trace state diverging from hardware IRQ flags, bogus restore warnings, PREEMPT_RT softirq-context differences, and using raw APIs where traced APIs are required. Tests should cover trace-enabled/disabled builds, lockdep IRQ state, nested save/restore, safe halt, timer/irq_work context markers, and scoped guard cleanup.
