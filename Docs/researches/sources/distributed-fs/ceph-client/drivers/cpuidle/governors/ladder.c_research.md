<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governors/ladder.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/governors/ladder.c

## Purpose

`ladder.c` implements the legacy cpuidle ladder governor. It promotes or demotes one state at a time based on the previous residency and fixed promotion/demotion counters.

## Important APIs, Types, And Functions

Per-CPU `struct ladder_device` holds `struct ladder_device_state` entries with promotion/demotion thresholds and counters. `ladder_enable_device()` initializes thresholds from state exit latencies and sets the initial state. `ladder_select_state()` enforces latency constraints and updates promotion/demotion counters. `ladder_reflect()` records the actual entered state.

## Control Flow

Selection starts from `dev->last_state_idx`, treats polling state 0 specially, and immediately returns state 0 when latency requirement is zero. If the last adjusted residency exceeds the promotion threshold for enough consecutive selections and the next state fits the latency constraint, it promotes. If the state is disabled, violates latency, or under-runs the demotion threshold, it demotes.

## State And Persistence Behavior

The governor persists per-CPU counters across idle entries and resets them when devices are enabled. The governor rating is raised from 10 to 25 when nohz is disabled, making ladder preferable for periodic tick systems.

## Dependencies And Integration Points

It depends on cpuidle device residency accounting, PM QoS latency, tick nohz status, and governor registration.

## Risks And Test Signals

Risks include slow adaptation to workload changes, poor choices with tickless idle, and state index assumptions when state 0 is polling. Test with nohz on/off, PM QoS constraints, state disables, and workloads alternating short and long idle intervals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governors/ladder.c -->
