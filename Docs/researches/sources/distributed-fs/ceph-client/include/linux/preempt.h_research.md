# sources/distributed-fs/ceph-client/include/linux/preempt.h

Purpose: defines preemption count bit layout, interrupt-context predicates, preempt disable/enable primitives, nested preempt handling for RT, preempt notifiers, scoped guards, and preemption-model queries.

Important APIs and types: bit masks and offsets split `preempt_count()` into preempt, softirq, hardirq, and NMI fields plus need-resched handling. Helpers/macros include `interrupt_context_level()`, `nmi_count()`, `hardirq_count()`, `softirq_count()`, `irq_count()`, `in_nmi()`, `in_hardirq()`, `in_serving_softirq()`, `in_task()`, deprecated `in_softirq()`/`in_interrupt()`, `in_atomic()`, `preempt_disable/enable()`, notrace/no-resched variants, `preempt_check_resched()`, need-resched fold/set helpers, `preempt_disable_nested()/preempt_enable_nested()`, lock guards, `struct preempt_ops`, `struct preempt_notifier`, notifier registration APIs, and preempt model queries including dynamic model support.

Control flow: kernel code increments preempt count before critical sections and decrements on exit; on preemptible kernels `preempt_enable()` schedules if the count reaches zero and resched is pending. Interrupt and softirq entry code manipulates the corresponding count fields. PREEMPT_RT changes softirq/preempt-lock semantics and uses nested preempt disable only where CPU-local serialization is required. Preempt notifiers call registered hooks on task schedule-out/in under documented contexts.

State and persistence: state lives in per-task/arch preempt count, softirq disable count on RT, need-resched flags, and optional notifier lists. It is strictly runtime scheduler/context state.

Dependencies and integration points: depends on arch `asm/preempt.h`, scheduler preemption functions, task flags, IRQ state, lockdep, cleanup guard macros, PREEMPT_RT, PREEMPT_DYNAMIC, modules, and KVM or other users of preempt notifiers.

Risks and test signals: risks include unbalanced preempt counts, scheduling with preemption disabled, sleeping in atomic context, using deprecated context predicates for sleepability, RT semantic drift around spinlocks/softirqs, module misuse of no-resched helpers, notifier lifetime bugs, and dynamic preempt model misclassification. Test lockdep/preempt count debugging, voluntary/full/lazy/RT/none models, nested RT sections, interrupt context predicates, preempt notifier register/unregister around task switches, module builds, and stress tests for schedule-in-atomic warnings.
