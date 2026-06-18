<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpu_pm.h -->
# sources/distributed-fs/ceph-client/include/linux/cpu_pm.h

## Purpose

`cpu_pm.h` defines notifier events used when CPUs or CPU power domains enter and leave low-power states that may reset local or cluster hardware context. The source was read as a complete 100-line file.

## Important APIs, Types, and Functions

`enum cpu_pm_event` defines `CPU_PM_ENTER`, `CPU_PM_ENTER_FAILED`, `CPU_PM_EXIT`, `CPU_CLUSTER_PM_ENTER`, `CPU_CLUSTER_PM_ENTER_FAILED`, and `CPU_CLUSTER_PM_EXIT`. When `CONFIG_CPU_PM` is enabled, it declares notifier registration plus `cpu_pm_enter()`, `cpu_pm_exit()`, `cpu_cluster_pm_enter()`, and `cpu_cluster_pm_exit()`. Disabled builds provide zero-return stubs.

## Control Flow

Platform idle, suspend, and hotplug code calls CPU events on the affected CPU with interrupts disabled. Once all CPUs in a shared power domain have been notified, cluster events notify drivers that global context may be lost. Exit and failed-enter notifications restore or unwind state.

## State and Persistence Behavior

Notifier registrations persist in the CPU PM notifier chain. The header itself owns no context; registered drivers are responsible for saving/restoring per-CPU and cluster hardware state.

## Dependencies and Integration Points

It depends on `linux/kernel.h` and `linux/notifier.h`. Integration points include cpuidle low-level entry macros, architecture suspend/hotplug paths, interrupt controller drivers, timer/counter drivers, cache/FPU context code, and SoC power-domain management.

## Risks and Edge Cases

Notifications must run with interrupts disabled and on the affected CPU for per-CPU events. Failing to send failed-enter events can leave drivers thinking state was lost. Cluster events must be ordered after per-CPU events. Disabled-config stubs mean callers cannot rely on notifier side effects in all builds.

## Test Signals

Signals include low-power entry/exit tests with notifier ordering instrumentation, suspend/resume on platforms that power down CPU domains, hotplug play-dead flows, failure-injection for failed enter notifications, and builds with `CONFIG_CPU_PM=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpu_pm.h -->
