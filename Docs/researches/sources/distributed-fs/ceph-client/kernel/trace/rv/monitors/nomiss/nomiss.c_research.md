# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nomiss/nomiss.c

## Purpose

This module implements the `nomiss` hybrid-automata monitor for deadline tasks and deadline servers. It checks that supported deadline entities move through ready, running, sleeping, idle, and throttled states without missing their deadline plus a configurable tardiness threshold.

## Important APIs, Types, and Functions

The monitor is `RV_MON_PER_OBJ` with `HA_TIMER_WHEEL` and a `struct sched_dl_entity *` target. `deadline_thresh` is a module parameter defaulting to `TICK_NSEC`. Core HA callbacks are `ha_get_env()`, `ha_reset_env()`, `ha_verify_invariants()`, `ha_convert_inv_guard()`, `ha_verify_guards()`, `ha_setup_invariants()`, and `ha_verify_constraint()`. Trace handlers include `handle_dl_replenish()`, `handle_dl_throttle()`, `handle_dl_server_stop()`, `handle_sched_switch()`, `handle_sys_enter()`, and `handle_sched_wakeup()`.

## Control Flow

On enable, the module initializes DA/HA storage, pre-allocates deadline task and server storage through `init_storage(false)`, and attaches deadline, scheduler, syscall, task creation, and process-exit tracepoints. Deadline replenish resets the clock; throttle is allowed only under defer or constrained-deadline guard conditions depending on the current state; ready and running states arm timers until `dl_deadline + deadline_thresh`. `sched_switch` maps blocked deadline tasks to suspend, incoming deadline tasks to switch-in, and server execution/idle transitions to server-specific events. Syscall entry detects policy transitions into or out of `SCHED_DEADLINE` and creates or resets per-task storage.

## State and Persistence Behavior

State is per deadline entity in HA storage and keyed by task PID or per-CPU negative server IDs from `deadline.h`. Clock state is stored in HA environments, with timers armed for ready/running states and canceled when leaving them. The monitor has no disk persistence; state is rebuilt on enable and destroyed on disable.

## Dependencies and Integration Points

The file depends on generated `nomiss.h`, `rv/ha_monitor.h`, `monitors/deadline/deadline.h`, deadline scheduler tracepoints, syscall tracepoints, task lifecycle tracepoints, and `rv_trace.h` event declarations. It registers as a child of `rv_deadline`.

## Risks and Edge Cases

The monitor must avoid allocation from deadline-server tracepoints, hence the up-front storage creation. Syscall policy parsing races with task lookup and policy changes, mitigated with RCU lookup but still approximate. Server handling depends on whether `next->dl_server` is directly available or has to be resolved by CPU. Disabling detaches RCU-heavy task/syscall probes first to reduce teardown latency.

## Test Signals

Test signals include running deadline workloads with controlled replenish/throttle paths, toggling `deadline_thresh`, policy transitions through both scheduler syscalls, task fork/exit while enabled, sched-ext server builds, and trace output for `event_nomiss`, `error_nomiss`, and `error_env_nomiss`.
