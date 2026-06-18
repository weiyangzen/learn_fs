# sources/distributed-fs/ceph-client/kernel/time/tick-sched.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/tick-sched.c` implements NO_HZ idle/full dynticks and scheduler tick emulation. It manages per-CPU tick hrtimers, jiffies catch-up, idle sleep accounting, tick dependency tracking, full-dynticks kicks, next-event calculation, tick stop/restart, IRQ idle transitions, and CPU hotplug cleanup. The complete 1716-line source was read.

## Important APIs, Types, and Functions

Important external functions include `tick_get_tick_sched`, `tick_nohz_dep_set`, `tick_nohz_dep_clear`, `tick_nohz_dep_set_cpu`, `tick_nohz_dep_clear_cpu`, `tick_nohz_dep_set_task`, `tick_nohz_dep_clear_task`, `tick_nohz_dep_set_signal`, `tick_nohz_dep_clear_signal`, `__tick_nohz_task_switch`, `tick_nohz_full_setup`, `tick_nohz_cpu_hotpluggable`, `tick_nohz_init`, `tick_nohz_is_active`, `tick_nohz_tick_stopped`, `tick_nohz_tick_stopped_cpu`, `get_cpu_idle_time_us`, `get_cpu_iowait_time_us`, `get_jiffies_update`, `tick_nohz_idle_stop_tick`, `tick_nohz_idle_retain_tick`, `tick_nohz_idle_enter`, `tick_nohz_irq_exit`, `tick_nohz_idle_got_tick`, `tick_nohz_get_next_hrtimer`, `tick_nohz_get_sleep_length`, `tick_nohz_get_idle_calls_cpu`, `tick_nohz_idle_restart_tick`, `tick_nohz_idle_exit`, `tick_irq_enter`, `tick_setup_sched_timer`, `tick_sched_timer_dying`, `tick_clock_notify`, `tick_oneshot_notify`, and `tick_check_oneshot_change`. Key state is per-CPU `struct tick_sched`, `last_jiffies_update`, `tick_nohz_full_mask`, `tick_nohz_full_running`, and global/per-CPU/task/signal tick dependency masks.

## Control Flow

The per-CPU scheduler tick hrtimer runs `tick_nohz_handler`. It updates jiffies through `tick_sched_do_timer`, performs process accounting when IRQ regs are available, and either restarts for the next period or stops if NO_HZ has disabled the tick. Jiffies updates use a fast 64-bit acquire check or 32-bit seqcount check, then serialize under `jiffies_lock` and update `last_jiffies_update`, `tick_next_period`, load average, and wall time.

Idle entry sets `TS_FLAG_INIDLE` and starts idle accounting. The idle governor can call `tick_nohz_get_sleep_length`, which computes the next timer event, honors RCU/arch/irq_work/local timer softirq needs, limits the timekeeping CPU by `timekeeping_max_deferment`, and caches the result. `tick_nohz_idle_stop_tick` sets timer bases idle, hands off `tick_do_timer_cpu` if needed, records accounting stats, and programs either the per-CPU hrtimer or clockevent for the next real deadline. IRQ entry/exit and idle exit stop idle accounting, update stale jiffies, and restart or keep stopped the tick depending on NO_HZ full dependencies.

For NO_HZ full, dependency setters mark global, CPU, task, or signal dependencies and kick affected full-dynticks CPUs through IRQ work. On task switch, a stopped full-dynticks CPU rechecks current task/signal dependencies and restarts if needed.

## State and Persistence Behavior

All state is in memory and per-CPU/global. `struct tick_sched` stores flags, scheduler tick hrtimer, last/next tick deadlines, idle accounting times, cached timer expiration data, idle call counters, dependency masks, and clock-change notification bits. State persists across idle cycles and is partially preserved across CPU dying cleanup for cumulative idle/iowait counters. Boot parameters `nohz=` and `skew_tick=` affect runtime behavior.

## Dependencies and Integration Points

Dependencies include hrtimers, clockevents, jiffies/timekeeping, timer wheel idle APIs, RCU, irq_work, scheduler context tracking, load average, vmstat, softlockup watchdog, CPU hotplug, NO_HZ full masks, POSIX CPU timer dependencies, perf/scheduler tick dependencies, and tracepoints. It integrates with `tick-common.c` for tick device state and `tick_do_timer_cpu`, with `tick-oneshot.c` for event programming, with timer wheel code for next timer deadlines, and with POSIX CPU timers through `tick_nohz_dep_set_task/signal`.

## Risks and Edge Cases

Stopping the tick can stall jiffies if the timekeeping CPU sleeps without handoff, so `TS_FLAG_DO_TIMER_LAST` and `TICK_DO_TIMER_NONE` are critical. Local pending timer softirqs, RCU needs, irq_work, arch hooks, and reschedule requests must prevent tick stop. NO_HZ full must restart the tick when dependencies appear, including POSIX CPU timers and perf events. Stale cached `timer_expires_base` must be cleared after use. Hrtimer and lowres paths differ in whether `sched_timer` or the clockevent is programmed. Idle/iowait accounting is documented as potentially observing backward values because remote iowait counters are unsynchronized.

## Test Signals

Strong signals include NO_HZ idle/full boot tests, cpuidle sleep-length validation, jiffies progression under long idle and stop-machine/VMEXIT stalls, POSIX CPU timer and perf dependencies on nohz_full CPUs, CPU hotplug and dying cleanup, suspend/resume idle accounting, softirq-pending tick-stop warnings, highres and lowres configurations, and tracepoint checks for tick stop/restart reasons.
