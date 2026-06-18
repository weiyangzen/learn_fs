# sources/distributed-fs/ceph-client/include/linux/irq-entry-common.h

## Purpose
`irq-entry-common.h` defines generic syscall/interrupt/NMI entry and exit state handling shared by architectures: lockdep IRQ state, context tracking/RCU transitions, tracing, KMSAN register cleanup, rseq notifications, deferred hrtimer rearming, and user-mode work loops.

## Important APIs, types, and functions
Important interfaces include `EXIT_TO_USER_MODE_WORK*`, architecture hooks, `enter_from_user_mode`, `exit_to_user_mode_loop`, syscall/irq exit prepare helpers, `exit_to_user_mode`, `irqentry_enter_from_user_mode`, `irqentry_exit_to_user_mode`, `irqentry_state_t`, `irqentry_enter_from_kernel_mode`, `irqentry_exit_to_kernel_mode*`, `irqentry_enter`, `irqentry_exit`, `irqentry_nmi_enter`, and `irqentry_nmi_exit`.

## Control flow
Low-level architecture entry code calls these helpers with interrupts disabled. User entries leave context tracking user state, restore lockdep/tracing, and unpoison registers. Exits process pending TIF work, validate no temporary mappings, then re-enter user tracking. Kernel entries conditionally enter/exit RCU depending on idle/EQS state and may run preempt checks before returning.

## State and persistence
State is per-CPU/per-task transient entry state: RCU watching/EQS, lockdep hardirq state, TIF work flags, rseq entry state, hrtimer deferred work, and `irqentry_state_t.exit_rcu`.

## Dependencies and integration points
It integrates with architecture `pt_regs`, context tracking, tick/nohz, lockdep, trace IRQ flags, KMSAN, rseq, static calls for preempt dynamic, and unwind state.

## Risks and test signals
Risks include wrong interrupt-disable assumptions, missing RCU transitions from idle, instrumentation in noinstr regions, unhandled TIF flags, and preempt/lockdep mismatches. Tests should include user/kernel/idle interrupt entry, NMI nesting, NO_HZ_FULL, PREEMPT_DYNAMIC, KMSAN builds, rseq exits, and hrtimer deferred rearm paths.
