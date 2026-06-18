# sources/distributed-fs/ceph-client/include/linux/sched/signal.h

Purpose: defines signal-handling structures embedded in tasks and thread groups, plus helpers for signal pending state, wakeups, alternate stacks, process iteration, and rlimit access.

Important APIs and types: `struct sighand_struct`, `struct signal_struct`, `struct pacct_struct`, `struct thread_group_cputimer`, `struct core_state`, signal flags, `flush_signals()`, `dequeue_signal()`, `kernel_dequeue_signal()`, force/send/kill helpers, notify-signal helpers, signal-pending helpers, `fault_signal_pending()`, `signal_wake_up()`, restore-sigmask helpers, alternate signal stack helpers, process/thread iteration macros, pid accessors, `lock_task_sighand()`, and rlimit helpers are central.

Control flow: signal code dequeues pending signals under `siglock`, wakes tasks by setting thread flags and scheduler states, handles fatal/interruptible wait decisions, manages saved signal masks around interrupted syscalls, and iterates thread groups/process lists under RCU/tasklist constraints.

State and persistence: `sighand_struct` and `signal_struct` hold shared signal actions, pending signals, group exit/stop state, POSIX timers, process accounting, child/reaped stats, rlimits, tty/session IDs, OOM metadata, and exec credential locks. This state persists for thread-group lifetime.

Dependencies and integration points: integrates scheduler tasks with signals, ptrace/jobctl, POSIX timers, credentials, pid namespaces, coredump, OOM, procfs/rusage, cgroups, tty, and MM fault handling.

Risks and test signals: risks include locking mistakes around `siglock`, RCU-unsafe process iteration, missed `TIF_NOTIFY_SIGNAL` kicks, fatal signal checks in fault retry paths, alternate-stack boundary errors, and rlimit races. Test signal delivery, ptrace stops, group exit, exec under signals, POSIX CPU timers, signalfd, alternate stacks, wait/reparenting, and signal-heavy stress with lockdep/RCU.
