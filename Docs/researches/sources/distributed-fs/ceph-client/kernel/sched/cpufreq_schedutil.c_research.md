# sources/distributed-fs/ceph-client/kernel/sched/cpufreq_schedutil.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/sched/cpufreq_schedutil.c` implements the `schedutil` cpufreq governor, which selects CPU frequency or performance levels from scheduler utilization, utilization clamps, IO-wait boosts, deadline bandwidth, and scheduler-class extension performance targets. The file was read as a complete 938-line source.

## Important APIs, Types, and Functions

`struct sugov_policy` stores policy-level state: cpufreq policy, tunables, update lock, rate-limit timing, cached/next frequency, slow-switch irq work/kthread state, and limit-change flags. `struct sugov_cpu` stores per-CPU hook data, IO-wait boost state, last utilization, and bandwidth minimum. Main update paths are `sugov_update_single_freq()`, `sugov_update_single_perf()`, and `sugov_update_shared()`. Frequency computation flows through `sugov_get_util()`, `sugov_effective_cpu_perf()`, `get_capacity_ref_freq()`, and `get_next_freq()`. IO boosting is managed by `sugov_iowait_boost()`, `sugov_iowait_apply()`, and `sugov_iowait_reset()`. Governor lifecycle functions are `sugov_init()`, `sugov_exit()`, `sugov_start()`, `sugov_stop()`, and `sugov_limits()`.

## Control Flow

Governor init enables fast switching if possible, allocates policy state, creates a deadline-scheduled kthread for slow-switch drivers, creates or shares sysfs tunables, and rebuilds sched domains for energy-aware scheduling. Start chooses the update callback by policy shape and driver support: shared policies use `sugov_update_shared()`, fast-switch adjust-perf policies use `sugov_update_single_perf()`, and others use `sugov_update_single_freq()`. Each CPU gets a scheduler utilization hook through `cpufreq_add_update_util_hook()`.

On scheduler updates, the governor first updates IO-wait boost and deadline-bandwidth signals. `sugov_should_update_freq()` rejects unsupported remote updates, handles policy limit changes with barriers, honors forced update requests, and enforces `rate_limit_us`. Single-frequency mode computes one CPU's util and calls fast-switch directly or queues deferred irq/kthread work. Single-performance mode calls `cpufreq_driver_adjust_perf()` when frequency invariance exists. Shared mode locks the policy, updates the triggering CPU, scans all policy CPUs, chooses max util, then fast-switches or defers. Slow-switch work reads `next_freq` under `update_lock`, clears `work_in_progress`, and invokes `__cpufreq_driver_target()` under `work_lock`.

## State and Persistence Behavior

State persists while the cpufreq policy uses schedutil. Tunables may be global or per-policy depending on governor configuration. Per-CPU `sugov_cpu` state is zeroed on start. Cached raw frequency avoids redundant driver resolution. `limits_changed` and `need_freq_update` coordinate policy limit updates across cpufreq and scheduler contexts.

## Dependencies and Integration Points

The file depends on scheduler utilization APIs (`effective_cpu_util()`, `cpu_util_cfs_boost()`, deadline bandwidth, uclamp), architecture frequency/capacity scaling, cpufreq governor and driver operations, kthreads, irq work, sysfs governor attributes, energy model sched-domain rebuilds, and optional sched-ext hooks (`scx_cpuperf_target()`, `scx_switched_all()`). It integrates with `cpufreq.c` hook installation and with `deadline.c` through deadline bandwidth signals and SCHED_DEADLINE sugov kthreads.

## Risks and Edge Cases

Fast-switch callbacks run under rq lock and must not sleep. Slow-switch work must not miss updates while `work_in_progress` is being cleared, hence the policy lock. Memory barriers between `sugov_limits()` and `sugov_should_update_freq()` protect policy limit visibility. IO-wait boost decays by tick timing and can overboost or underboost bursty IO. Shared-policy util uses max policy CPU util, so stale per-CPU state can matter after hotplug if hooks are not stopped cleanly. Deadline-bandwidth increases bypass rate limiting through `need_freq_update`.

## Test Signals

Signals include cpufreq governor selftests across fast-switch, adjust-perf, and slow-switch drivers; sysfs `rate_limit_us` read/write tests; policy min/max limit-change tests; CPU hotplug and shared-policy stress; IO-wait wakeup benchmarks checking boost and decay; deadline workload tests confirming rate-limit bypass; uclamp/EAS frequency selection tests; and lockdep coverage for rq-lock and slow-switch sleeping boundaries.
