# sources/distributed-fs/ceph-client/kernel/sched/cpufreq.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/sched/cpufreq.c` provides the scheduler-to-cpufreq callback hook used by governors such as `schedutil`. It stores per-CPU `update_util_data` pointers and exposes helpers to install, remove, and validate scheduler utilization update callbacks. The file was read as a complete 75-line source.

## Important APIs, Types, and Functions

`DEFINE_PER_CPU(struct update_util_data __rcu *, cpufreq_update_util_data)` is the central per-CPU hook pointer. `cpufreq_add_update_util_hook()` sets the callback function in caller-provided data and publishes it with RCU. `cpufreq_remove_update_util_hook()` clears the pointer. `cpufreq_this_cpu_can_update()` checks whether the current CPU can update a policy directly or, for drivers with `dvfs_possible_from_any_cpu`, through a still-installed local scheduler hook.

## Control Flow

Governor startup calls `cpufreq_add_update_util_hook()` for each CPU in a policy after ensuring no hook is already installed. Scheduler hot paths later call `cpufreq_update_util()` from RCU-sched read-side critical sections, which dereference this pointer and invoke `data->func`. Governor stop clears hooks and must synchronize RCU before freeing hook storage. `cpufreq_this_cpu_can_update()` is used by schedutil before calculating or committing frequency changes to avoid stale remote/offline CPU requests.

## State and Persistence Behavior

State is one RCU-protected callback pointer per CPU. The pointed-to storage is governor-owned, usually per-CPU schedutil state. No data persists beyond governor policy lifetime.

## Dependencies and Integration Points

The file depends on scheduler internals, RCU, per-CPU storage, `struct cpufreq_policy`, and cpufreq driver policy masks. It is exported GPL-only for governors and integrates directly with `cpufreq_schedutil.c`.

## Risks and Edge Cases

Installing over an existing hook or installing a null callback is rejected by warnings and no-op returns. Removal does not wait for readers; callers must use `synchronize_rcu()` or RCU callbacks before freeing. Remote DVFS updates must be suppressed when the local CPU is going offline and has no scheduler hook.

## Test Signals

Signals include governor start/stop tests that verify hook install/remove and RCU synchronization; CPU hotplug tests for remote DVFS policies; WARN coverage for duplicate/null hooks; and schedutil workloads proving `cpufreq_update_util()` still receives callbacks after policy transitions.
