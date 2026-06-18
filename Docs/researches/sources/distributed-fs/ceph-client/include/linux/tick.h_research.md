<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tick.h -->
# sources/distributed-fs/ceph-client/include/linux/tick.h

## Purpose
declares tick, broadcast tick, NO_HZ idle/full, CPU hotplug, suspend, and tick-dependency APIs used by timekeeping, scheduler, RCU, and clockevent code.

## Important APIs, Types, and Functions
The file is 317 lines and exports these visible symbol families: types/enums `tick_broadcast_mode`, `tick_broadcast_state`, `tick_dep_bits`; macros/constants `tick_cpu_dying`, `TICK_DEP_BIT_MAX`, `TICK_DEP_MASK_NONE`, `TICK_DEP_MASK_POSIX_TIMER`, `TICK_DEP_MASK_PERF_EVENTS`, `TICK_DEP_MASK_SCHED`, `TICK_DEP_MASK_CLOCK_UNSTABLE`, `TICK_DEP_MASK_RCU`, `TICK_DEP_MASK_RCU_EXP`, `tick_nohz_enabled`; function-like macros `arch_needs_cpu`, `tick_nohz_full_cpu`; inline helpers `tick_init`, `tick_suspend_local`, `tick_resume_local`, `tick_assert_timekeeping_handover`, `tick_freeze`, `tick_unfreeze`, `tick_irq_enter`, `hotplug_cpu__broadcast_tick_pull`, `tick_broadcast_control`, `tick_broadcast_oneshot_control`, `tick_broadcast_enable`, `tick_broadcast_disable`, `tick_broadcast_force`, `tick_broadcast_enter`, and 33 more; external prototypes `tick_init`, `tick_suspend_local`, `tick_resume_local`, `tick_cpu_dying`, `tick_assert_timekeeping_handover`, `tick_freeze`, `tick_unfreeze`, `tick_irq_enter`, `hotplug_cpu__broadcast_tick_pull`, `tick_broadcast_control`, `tick_broadcast_oneshot_control`, `tick_nohz_is_active`, `tick_nohz_tick_stopped`, `tick_nohz_tick_stopped_cpu`, and 26 more.

## Control Flow
Clockevent setup calls tick init/suspend/resume and CPU dying hooks. Idle and IRQ entry/exit paths stop or restart periodic ticks in NO_HZ idle. Full dynticks code tracks dependency bits for POSIX timers, perf, scheduler, unstable clocks, RCU, and expedited RCU; setting a dependency restarts/kicks ticks as needed.

## State and Persistence Behavior
Runtime state includes global NO_HZ enable/full masks, per-CPU stopped-tick state, broadcast mode/state, static keys, and dependency masks attached to CPUs, tasks, and signals. Disabled configs compile to stubs.

## Dependencies and Integration Points
It depends on clockchips, irq flags, percpu data, context tracking, cpumasks, scheduler state, RCU, and static keys. Direct includes are `linux/clockchips.h`, `linux/irqflags.h`, `linux/percpu.h`, `linux/context_tracking_state.h`, `linux/cpumask.h`, `linux/sched.h`, `linux/rcupdate.h`, `linux/static_key.h`.

## Risks and Edge Cases
Stopping ticks while dependencies exist can break timers, scheduler accounting, perf, or RCU quiescent-state detection. CPU hotplug and suspend handoff ordering are especially sensitive.

## Test Signals
Run NO_HZ idle/full kernel selftests, CPU hotplug loops, suspend/resume, RCU stall tests, perf/POSIX timer activity on isolated CPUs, and builds for generic clockevents on/off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tick.h -->
