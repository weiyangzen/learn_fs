# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/preempt.h

Purpose: This header adapts generic preemption support for PowerPC and exposes a PowerPC-specific `need_irq_preemption()` predicate for IRQ-entry/exit preemption decisions.

Important APIs/types/functions: It includes `asm-generic/preempt.h`. With `CONFIG_PREEMPT_DYNAMIC`, it declares the static key `sk_dynamic_irqentry_exit_cond_resched` and defines `need_irq_preemption()` as a static-branch check. Otherwise it returns `IS_ENABLED(CONFIG_PREEMPTION)`.

Control flow: IRQ return or entry/exit code can call `need_irq_preemption()` to decide whether conditional rescheduling is enabled. Dynamic preemption changes update the static key so the branch can be patched efficiently.

State and persistence: The dynamic build stores state in the jump-label static key; non-dynamic builds encode the state at compile time. The header owns no runtime data beyond the external key declaration.

Dependencies and integration points: It integrates generic preempt accounting, Linux jump labels, dynamic preemption, and PowerPC interrupt entry/exit paths.

Risks and test signals: Incorrect static-key polarity would change IRQ preemption behavior globally. Build tests should cover `CONFIG_PREEMPT_DYNAMIC`, `CONFIG_PREEMPTION`, and non-preempt configs. Runtime tests include preemption model switching, IRQ return latency, scheduler selftests, and lockdep/preempt count checks.
