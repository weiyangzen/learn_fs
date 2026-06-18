# sources/distributed-fs/ceph-client/include/linux/posix-timers.h

Purpose: defines kernel POSIX timer and CPU-timer internals, clockid encoding helpers, timer reference management, and CPU timer lifecycle hooks.

Important APIs and types: clock helpers create process/thread CPU clock IDs and convert file descriptors to dynamic clock IDs. `struct cpu_timer` wraps timerqueue node/head, PID, expiry list, firing/nanosleep flags, and handling task. `struct k_itimer` is the main POSIX timer object with hash/list nodes, timer id, clock id, signal target, clock operations pointer, spinlock, status, overrun accounting, signal sequence fields, interval, pid/process pointer, embedded sigqueue, rcuref, and real/cpu/alarm timer union. APIs initialize CPU timer containers, enqueue/dequeue CPU timers, rearm itimers, initialize/send/deliver sigqueue, free timers, handle prctl controls, run/exit CPU timers, set CPU timers, and update CPU rlimits.

Control flow: timer creation allocates `k_itimer`, initializes signal queue and clock-specific storage, inserts it into process timer state, and arms hrtimer/cpu timer/alarm timer backends. Expiry queues signals, manages overrun counters and sequence numbers, and uses rcuref to keep timer memory alive while sigqueue delivery is in flight. CPU timers are queued in per-task or per-signal `posix_cputimers` timerqueues and processed from scheduler/task-work hooks.

State and persistence: state is runtime per-task/per-signal timer state: timerqueues, next-event caches, active/expiry flags, timer hash/list membership, signal ownership, references, overruns, and backend timer objects. POSIX timers are process lifetime objects and do not persist across exec/exit beyond normal kernel semantics.

Dependencies and integration points: integrates with hrtimers, alarmtimers, timerqueue, signals, PIDs, task_struct/signal_struct, RCU, rcuref, spinlocks, CPU accounting, rlimits, task work, and dynamic POSIX clocks. Disabled `CONFIG_POSIX_TIMERS` and task-work configs provide empty stubs.

Risks and test signals: risks include reference leaks or premature frees during signal delivery, CPU timer dequeue/enqueue races, overrun sequence mistakes, invalid encoded clock IDs, task exit cleanup bugs, and nanosleep vs regular timer confusion. Test timer_create/delete, periodic overrun accounting, process and thread CPU timers, rlimit CPU timer updates, signal delivery under deletion races, clockfd timers, nanosleep timers, and POSIX_TIMERS-disabled builds.
