## sources/distributed-fs/ceph-client/include/linux/context_tracking.h

Purpose: This header declares context tracking transitions for user, guest, exception, idle, IRQ warning, and RCU watching state. It supports nohz/RCU/vtime accounting around extended quiescent states.

Important APIs, types, and functions: User tracking exports `ct_cpu_track_user`, `__ct_user_enter`, `__ct_user_exit`, `ct_user_enter`, `ct_user_exit`, `user_enter_callable`, and `user_exit_callable`. Inline wrappers `user_enter`, `user_exit`, `user_enter_irqoff`, and `user_exit_irqoff` gate calls on `context_tracking_enabled()`. `exception_enter()` and `exception_exit()` transition out of non-kernel state for exceptions unless off-stack tracking is enabled. Guest helpers enter/exit `CT_STATE_GUEST`. Idle tracking declares `ct_idle_enter`, `ct_idle_exit`, `rcu_is_watching_curr_cpu`, `ct_state_inc`, `warn_rcu_enter`, and `warn_rcu_exit`.

Control flow: Architecture entry/exit code calls the wrappers on transitions between kernel, user, guest, idle, IRQ, and exception contexts. The wrappers avoid overhead when context tracking is disabled. Warning helpers temporarily make RCU appear watching while reporting recursive RCU-not-watching conditions.

State and persistence: State lives in per-CPU `context_tracking` from `context_tracking_state.h`, including active flag, recursion, atomic state, and nesting counters. Updates are per-CPU and generally require interrupts/preemption constraints appropriate to the path.

Dependencies and integration points: It depends on scheduler state, vtime, instrumentation controls, `asm/ptrace.h`, RCU dynticks, nohz full, KVM guest transitions, exception entry code, and idle/IRQ tracking.

Risks and test signals: Risks include missing entry/exit pairs, calling IRQ-off variants with interrupts enabled, corrupting RCU watching bits, and recursion during warning paths. Test signals include nohz full workloads, RCU stall tests, KVM guest entry/exit, idle loop tests, context tracking selftests, and lockdep/RCU debug builds.
