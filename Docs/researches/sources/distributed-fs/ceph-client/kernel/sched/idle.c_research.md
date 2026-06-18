# sources/distributed-fs/ceph-client/kernel/sched/idle.c

## Purpose
Implements the generic idle thread loop and the idle scheduling class. It connects scheduler idle-task selection to cpuidle governors, tick/nohz management, CPU hotplug death, suspend-to-idle, polling idle, livepatch state updates, and injected idle residency.

## APIs, Control Flow, and State
Externally visible functions include `sched_idle_set_state()`, `cpu_idle_poll_ctrl()`, `default_idle_call()`, `play_idle_precise()`, `cpu_startup_entry()`, `cpu_in_idle()`, and the `DEFINE_SCHED_CLASS(idle)` instance. Optional boot parameters `nohlt` and `hlt` control `cpu_idle_force_poll` when `CONFIG_GENERIC_IDLE_POLL_SETUP` is enabled. The main control path is `cpu_startup_entry()` setting `PF_IDLE` and repeatedly calling `do_idle()`. `do_idle()` enters tickless idle, loops until `need_resched()`, handles offline CPUs through `cpuhp_report_idle_dead()` and `arch_cpu_idle_dead()`, flushes deferred RCU no-cb wakeups, then chooses polling idle or `cpuidle_idle_call()`. `cpuidle_idle_call()` either uses suspend-to-idle/deepest-state logic, asks the cpuidle governor, or falls back to `default_idle_call()`. Exiting idle propagates preemption state, restarts nohz accounting, flushes SMP call functions, schedules away from the idle task, and updates livepatch state.

State is per-CPU and transient: polling bits on the idle task, `rq` idle state, tick/nohz state, cpuidle selected state/residency, `PF_IDLE`, and injected-idle hrtimer state. The idle sched class never migrates idle tasks, warns if they are dequeued/scheduled incorrectly, updates idle runtime and deadline-server idle accounting, and marks scheduler-ext idle transitions.

## Dependencies and Integration Points
Depends on cpuidle, clockevents broadcast idle, RCU dynticks, CPU hotplug, scheduler core, livepatch, hrtimers, tracepoints, and architecture hooks (`arch_cpu_idle_*`). Integration points include tick stopping/restarting, suspend-to-idle QoS latency, cpuidle governors, PREEMPT need-resched propagation, `SCHED_CLASS(idle)` callbacks, and `play_idle_precise()` users that temporarily force a kernel thread into controlled idle.

## Risks and Test Signals
The main risks are missed reschedule/timer events around interrupt-disabled idle entry, polling-bit ordering bugs, tick/nohz imbalance, CPU hotplug dead-loop mistakes, cpuidle governor misuse during s2idle, and illegal sleeps from the idle thread. Test signals include suspend-to-idle/resume cycles, CPU hotplug stress, NO_HZ_FULL and tick-broadcast tests, idle residency/cpuidle trace validation, livepatch while idle, lockdep/RCU stall testing, and RT/kthread callers of `play_idle_precise()`.
