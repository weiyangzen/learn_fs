# sources/distributed-fs/ceph-client/include/linux/sched/idle.h

Purpose: declares idle-state helpers and polling-thread flag operations used to avoid unnecessary reschedule IPIs.

Important APIs and types: `enum cpu_idle_type`, `wake_up_if_idle()`, `current_set_polling_and_test()`, `current_clr_polling_and_test()`, `current_clr_polling()`, and low-level polling bit setters/clearers are the main symbols.

Control flow: idle loops mark the current task as polling, test `TIF_NEED_RESCHED`, and clear polling before leaving idle. Memory barriers pair with remote `resched_curr()` so reschedule state is visible and IPIs are not lost.

State and persistence: state is the current thread-info polling flag and need-resched state. It is transient per idle-loop entry.

Dependencies and integration points: depends on `sched.h`, thread-info flags, preempt folding, and architecture bitops. It integrates scheduler idle handling with interrupt/IPI avoidance.

Risks and test signals: risks include missing barriers causing lost wakeups, incorrect fallback when `TIF_POLLING_NRFLAG` is absent, and arch bitop instrumentation differences. Test idle wake latency, NOHZ idle, reschedule IPIs, PREEMPT configs, and architectures with/without polling flags.
