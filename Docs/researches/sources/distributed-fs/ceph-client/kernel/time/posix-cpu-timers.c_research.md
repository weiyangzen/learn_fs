# sources/distributed-fs/ceph-client/kernel/time/posix-cpu-timers.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/posix-cpu-timers.c` implements POSIX CPU clocks and CPU-time-backed POSIX timers. It supports per-thread and per-process `CPUCLOCK_PROF`, `CPUCLOCK_VIRT`, and `CPUCLOCK_SCHED` clock IDs, process/thread CPU timer creation, CPU-clock nanosleep, `RLIMIT_CPU`, `RLIMIT_RTTIME`, and the handoff between scheduler tick accounting and POSIX timer signal delivery. The complete 1670-line source was read for this report.

## Important APIs, Types, and Functions

Primary exported or externally used functions include `posix_cputimers_group_init`, `update_rlimit_cpu`, `thread_group_sample_cputime`, `posix_cpu_timers_exit`, `posix_cpu_timers_exit_group`, `run_posix_cpu_timers`, `set_process_cpu_timer`, `clear_posix_cputimers_work`, and `posix_cputimers_init_work`. The file publishes `clock_posix_cpu`, `clock_process`, and `clock_thread` as `struct k_clock` implementations. Important internal helpers are `pid_for_clock`, `cpu_clock_sample`, `cpu_clock_sample_group`, `thread_group_start_cputime`, `posix_cpu_timer_create`, `arm_timer`, `disarm_timer`, `posix_cpu_timer_set`, `posix_cpu_timer_del`, `posix_cpu_timer_get`, `collect_posix_cputimers`, `check_thread_timers`, `check_process_timers`, `posix_cpu_timer_rearm`, and `do_cpu_nanosleep`. Key state is in `struct posix_cputimers`, `struct posix_cputimer_base`, `struct cpu_timer`, `struct k_itimer`, `struct thread_group_cputimer`, and per-task or per-signal tick dependency masks.

## Control Flow

Clock access starts by decoding and validating CPU clock IDs through `pid_for_clock`, which constrains nonzero thread clocks to the caller's thread group and process clocks to process TGIDs. `clock_gettime` through the `k_clock` vtable samples either the individual task (`task_cputime`, `task_sched_runtime`) or the thread-group atomic cputime store. Process timer setup may call `thread_group_start_cputime` to synchronize group totals and enable process-wide cputime accounting before arming timers.

Timer set/disarm paths lock the target task sighand, remove any existing timerqueue node, sample current CPU time, convert relative expirations to absolute CPU-time deadlines, then enqueue the timer in the appropriate per-task or per-signal timerqueue. Scheduler tick interrupts call `run_posix_cpu_timers`, which first uses `fastpath_timer_check` against cached `nextevt` values. On expiry it collects due timers into a private firing list under sighand lock, releases sighand, then locks each timer and calls `cpu_timer_fire`. Interval timers are rearmed later from signal delivery through `posix_cpu_timer_rearm`. CPU-clock nanosleep uses a stack `k_itimer` marked `nanosleep`, sleeps the task, and stores restart state if interrupted.

## State and Persistence Behavior

There is no file-backed persistence. Runtime state is per-task and per-signal: timerqueue heads, cached next expiration values, `timers_active`, `expiry_active`, cputime atomic snapshots, timer status, overrun counters, firing flags, and `pid` references. The code deliberately keeps process-wide cputime accounting disabled until a process timer, itimer, or rlimit needs it. Tick dependencies are set while CPU timers require scheduler ticks and cleared when all cached expirations become inactive. During exit, timerqueue nodes are detached but surviving POSIX timer objects may remain addressable until deletion and RCU/reference cleanup complete.

## Dependencies and Integration Points

The file depends on scheduler cputime accounting, signal locking and delivery, PID lookup, `timerqueue`, POSIX timer core helpers in `posix-timers.c`, restart blocks, hrtimer nanosleep copyout, rlimits, deadline scheduling overrun handling, and NO_HZ tick dependency APIs from the tick subsystem. It integrates with `kernel/time/posix-timers.c` via the `struct k_clock` callbacks, with `include/linux/posix-timers.h` for `struct k_itimer`, with signal delivery via `posix_timer_queue_signal`, and with `tick-sched.c` through `tick_dep_set_task`, `tick_dep_set_signal`, and matching clear calls.

## Risks and Edge Cases

Major risks are races between timer expiry, deletion, rearming, task exit, and signal delivery. The `firing` and `handling` fields, `TIMER_RETRY`, RCU protection, sighand locking, and optional task-work mutex are all there to avoid losing a timer signal or freeing a timer while expiry runs. CPU-clock IDs are subtle because PID 0 means current thread/process and process clocks may be looked up through the caller's thread PID for `clock_gettime`. `SIGEV_NONE` timers are never queued and require synthetic forwarding during gettime. RLIMIT soft-limit updates intentionally move the soft limit forward one second/usec interval to avoid continuous signal storms. NO_HZ full correctness depends on setting tick dependencies whenever CPU timers need time to elapse.

## Test Signals

Useful test signals include POSIX CPU timer syscall tests for per-thread and per-process clocks; interval overrun tests; timer set/delete races while signals are pending; CPU-clock `clock_nanosleep` interruption and restart coverage; `ITIMER_PROF` and `ITIMER_VIRTUAL` behavior; `RLIMIT_CPU` and `RLIMIT_RTTIME` soft/hard signal behavior; task-exit cleanup under active timers; and NO_HZ full tests that verify CPU timers keep the tick running only while necessary.
