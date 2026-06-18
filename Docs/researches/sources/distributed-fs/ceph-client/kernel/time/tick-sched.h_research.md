# sources/distributed-fs/ceph-client/kernel/time/tick-sched.h

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/tick-sched.h` defines the private tick scheduling data structures and flags shared by NO_HZ, high-resolution tick, generic tick device, and broadcast code. The complete 124-line header was read.

## Important APIs, Types, and Functions

The header defines `enum tick_device_mode`, `struct tick_device`, `TS_FLAG_INIDLE`, `TS_FLAG_STOPPED`, `TS_FLAG_IDLE_ACTIVE`, `TS_FLAG_DO_TIMER_LAST`, `TS_FLAG_NOHZ`, `TS_FLAG_HIGHRES`, and `struct tick_sched`. It declares `tick_get_tick_sched`, `tick_setup_sched_timer`, `tick_sched_timer_dying` or its stub, and `__tick_broadcast_oneshot_control` or its stub.

## Control Flow

There is no executable control flow beyond config-dependent inline stubs. The data definitions shape runtime flow in `tick-common.c`, `tick-broadcast.c`, `tick-oneshot.c`, and `tick-sched.c`: each CPU has a tick device mode, and each CPU's `tick_sched` flags determine whether it is in idle, has stopped the tick, uses NO_HZ, or runs a high-resolution scheduler tick.

## State and Persistence Behavior

The header owns no storage but defines per-CPU persistent state fields. `struct tick_sched` retains scheduler tick hrtimer state, last/next tick times, idle and iowait sleep accounting, cached next timer deadlines, idle counters, dependency masks, and clock-change notification state across idle transitions.

## Dependencies and Integration Points

It depends on `linux/hrtimer.h` and, for broadcast declarations, on tick broadcast configuration. The header is included by `tick-internal.h` and is the structural contract between tick scheduler implementation and the rest of the tick subsystem.

## Risks and Edge Cases

Flag semantics are tightly coupled to interrupt-disabled sections. Misinterpreting `TS_FLAG_INIDLE` versus `TS_FLAG_IDLE_ACTIVE` can break idle accounting during IRQ entry. `TS_FLAG_STOPPED` controls whether the scheduler tick must be restarted. `TS_FLAG_DO_TIMER_LAST` is part of safe jiffies handoff after a timekeeping CPU enters NO_HZ idle.

## Test Signals

Compile coverage for oneshot and non-oneshot configs validates the stubs. Runtime NO_HZ idle/full tests, high-resolution tick tests, broadcast enter/exit tests, and CPU hotplug tests validate that the fields are updated consistently.
