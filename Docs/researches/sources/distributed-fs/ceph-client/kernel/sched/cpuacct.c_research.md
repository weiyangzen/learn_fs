# sources/distributed-fs/ceph-client/kernel/sched/cpuacct.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/sched/cpuacct.c` implements the legacy CPU accounting cgroup controller. It tracks aggregate and per-CPU CPU usage for each accounting cgroup, exposes legacy cgroup files such as `cpuacct.usage`, `cpuacct.usage_percpu`, `cpuacct.usage_all`, and `cpuacct.stat`, and receives charge callbacks from scheduler/cputime code. The file was read as a complete 365-line source.

## Important APIs, Types, and Functions

`enum cpuacct_stat_index` distinguishes user and system accounting buckets. `struct cpuacct` embeds `cgroup_subsys_state` plus per-CPU `cpuusage` and `kernel_cpustat` storage. `cpuacct_css_alloc()` and `cpuacct_css_free()` create and free controller state. `cpuacct_cpuusage_read()` and `cpuacct_cpuusage_write()` are the low-level per-CPU readers/resetters, with rq locking on 32-bit platforms for safe 64-bit access. User-visible cftype handlers include `cpuusage_read()`, `cpuusage_write()`, `cpuacct_percpu_seq_show()`, `cpuacct_all_seq_show()`, and `cpuacct_stats_show()`. Runtime entry points are `cpuacct_charge()` for elapsed execution time and `cpuacct_account_field()` for user/system/irq/softirq cpustat fields.

## Control Flow

At cgroup creation, the root cgroup reuses global `kernel_cpustat` and a static per-CPU root usage counter; children allocate separate per-CPU usage and cpustat arrays. Reads iterate all possible CPUs and sum or print per-CPU values. `cpuacct.stat` builds `task_cputime`, adjusts it through `cputime_adjust()`, and reports clock ticks. Writes only accept `0` and reset all per-CPU counters except the root cgroup.

At runtime, `cpuacct_charge()` is called with the target CPU rq locked and walks from the task's cpuacct cgroup to the root, adding nanoseconds to each ancestor's per-CPU `cpuusage`. `cpuacct_account_field()` adds a specific cpustat field to each non-root ancestor; the root is updated by the caller.

## State and Persistence Behavior

All state is in per-CPU kernel memory associated with cgroup lifetime. Counters are monotonically increasing unless reset through `cpuacct.usage` write on non-root cgroups. There is no persistence across reboot or cgroup destruction.

## Dependencies and Integration Points

The controller depends on cgroup core APIs, per-CPU allocation, `kernel_cpustat`, scheduler rq locking, task CSS lookup, and cputime adjustment helpers from `cputime.c`. It integrates with legacy cgroup v1 cpuacct files and with scheduler accounting hooks reached through `cgroup_account_cputime*()`.

## Risks and Edge Cases

32-bit platforms require rq locking around 64-bit per-CPU reads/writes. Root cgroup reset is explicitly rejected to protect global kernel cpustat. Reads cover possible CPUs rather than online CPUs, so offline CPU historical counters remain visible. Hierarchical charging assumes parent links remain valid during accounting. `cpuacct.stat` uses adjusted cputime, so it may differ from raw nanosecond usage files.

## Test Signals

Signals include cgroup v1 cpuacct smoke tests for every exposed file; reset tests that accept only zero and do not reset root; parent-child hierarchy charge tests; CPU hotplug/offline counter visibility checks; 32-bit or KCSAN-style race coverage around concurrent read/update; and workload comparisons against `/proc/stat` and task cputime totals.
