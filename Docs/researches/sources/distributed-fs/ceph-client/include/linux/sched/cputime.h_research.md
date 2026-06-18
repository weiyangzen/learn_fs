# sources/distributed-fs/ceph-client/include/linux/sched/cputime.h

Purpose: declares task and thread-group CPU time accounting helpers, adjusted cputime APIs, POSIX CPU timer integration, and paravirtual steal-time hooks.

Important APIs and types: `task_cputime()`, `task_gtime()`, `task_cputime_scaled()`, `task_cputime_adjusted()`, `thread_group_cputime_adjusted()`, `cputime_adjust()`, `thread_group_cputime()`, `thread_group_sample_cputime()`, `get_running_cputimer()`, group accounting helpers, `prev_cputime_init()`, `task_sched_runtime()`, and optional paravirt steal-clock static calls are central.

Control flow: tick/accounting paths accumulate per-task user/system/guest time, optionally update active POSIX thread-group cputimers, and expose adjusted monotonic values to proc/resource/timer consumers. Generic virtual CPU accounting may compute live values instead of reading stored fields.

State and persistence: state lives in `task_struct`, `signal_struct`, `prev_cputime`, and atomic thread-group counters. It persists for task/thread-group lifetime and is folded into exit accounting.

Dependencies and integration points: depends on `sched/signal.h`, POSIX timers, virtual CPU accounting, scaled cputime arch support, and paravirt steal time. It bridges scheduler runtime accounting with procfs, rusage, and CPU timers.

Risks and test signals: risks include non-monotonic adjusted time, accounting after `__exit_signal()`, active timer races, guest/steal time drift, and config fallback differences. Test CPU timer expiry, `/proc` stat fields, rusage, virtual accounting configs, paravirt guests, and thread exit while timers are active.
