# sources/distributed-fs/ceph-client/include/linux/sched.h

Purpose: declares `task_struct`, task states, scheduling entities, scheduler entry points, wakeup/affinity APIs, reschedule helpers, task flags, and migrate-disable machinery used throughout the kernel.

Important APIs and types: task state constants, `struct task_struct`, `struct sched_entity`, `struct sched_rt_entity`, `struct sched_dl_entity`, `struct sched_avg`, `struct sched_statistics`, `struct uclamp_se`, `struct wake_q_node`, PF/PFA task flags, `schedule*()`, `io_schedule*()`, `wake_up_process()`, `wake_up_state()`, `set_cpus_allowed_ptr()`, scheduler policy setters, `cond_resched*()`, thread-flag helpers, and `migrate_disable()/migrate_enable()` form the main surface.

Control flow: tasks update `__state` through barrier-aware macros before sleeping, wakeups test compatible states and set runnable state, scheduling classes consume embedded fair/RT/deadline/ext entities, and affinity/migration APIs coordinate CPU masks with runqueue locks. Cond-resched paths add voluntary scheduling points, while migrate-disable pins current execution until the nesting counter returns to zero.

State and persistence: `task_struct` is the kernel’s live per-task state container: scheduling state, CPU masks, signal/parentage, credentials, MM/files/fs pointers, timers, accounting, tracing/debug state, cgroup hooks, fault counters, and architecture thread state. It persists only for task lifetime and is heavily config-dependent.

Dependencies and integration points: integrates scheduler core with MM, signals, credentials, pid namespaces, cgroups, RCU, futexes, perf, tracing, BPF, seccomp, block I/O, POSIX timers, NUMA balancing, and arch thread code.

Risks and test signals: high-risk areas are memory barriers in sleep/wakeup, task state reporting ABI, `task_struct` layout assumptions, PREEMPT_RT saved-state handling, affinity races, lazy TLB/membarrier interactions, proxy-exec blocked-on state, and migrate-disable imbalance. Test with scheduler selftests, lockdep/RCU/KCSAN, fork/exit/exec stress, CPU hotplug, RT configs, cgroup movement, signal-heavy workloads, and BPF/perf/tracing builds.
