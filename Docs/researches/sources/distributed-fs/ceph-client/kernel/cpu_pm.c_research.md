# sources/distributed-fs/ceph-client/kernel/cpu_pm.c

## Purpose
`cpu_pm.c` provides a raw notifier-chain API for CPU and CPU-cluster low-power entry/exit. It lets low-level platform code notify drivers that per-CPU or cluster-local hardware state may be lost and must be saved/restored with interrupts disabled.

## Important APIs, types, and functions
The file owns `cpu_pm_notifier`, a `raw_notifier_head` plus `raw_spinlock_t`. Public APIs are `cpu_pm_register_notifier()`, `cpu_pm_unregister_notifier()`, `cpu_pm_enter()`, `cpu_pm_exit()`, `cpu_cluster_pm_enter()`, and `cpu_cluster_pm_exit()`. Internal helpers `cpu_pm_notify()` and `cpu_pm_notify_robust()` call raw notifier chains and translate notifier return values with `notifier_to_errno()`.

When `CONFIG_PM` is enabled, `cpu_pm_suspend()` and `cpu_pm_resume()` are registered as syscore suspend/resume operations by `cpu_pm_init()`. Suspend runs CPU then cluster entry notifications; resume runs cluster then CPU exit notifications.

## Control flow
Register/unregister calls take the raw spinlock with IRQ save/restore and update the notifier chain. Entry calls use `raw_notifier_call_chain_robust()` under the raw lock so a failing entry callback receives the matching failure event for already-called notifiers. Exit calls use `raw_notifier_call_chain()` under RCU read lock rather than the raw lock. Platform code is expected to call the entry/exit APIs on the affected CPU with interrupts disabled and with correct nesting.

## State and persistence behavior
State is limited to the in-kernel notifier chain and lock. There is no on-disk persistence or sysfs state. Robust entry notifications may partially execute callbacks and then issue failure notifications when a notifier returns an error.

## Dependencies and integration points
This module integrates with CPU idle/power-management platform code, syscore suspend/resume, interrupt-controller drivers, local timer drivers, floating-point/co-processor context code, and any driver that registers a CPU PM notifier. It deliberately uses raw notifiers and raw spinlock locking because idle-task notification paths must not block under PREEMPT_RT.

## Risks and edge cases
Ordering is strict: cluster entry must follow per-CPU entry for all CPUs in the power domain, and cluster exit must precede per-CPU exit. Callers must avoid double entry on the same CPU before exit. Notifier callbacks run with interrupts disabled and must not sleep. Exit notifications are not robust, so failed restore-style callbacks are only reflected by notifier return aggregation. A callback that assumes normal spinlocks can block on RT kernels would be unsafe in this path.

## Test signals
Test by registering synthetic notifiers that record event ordering, inject failures in `CPU_PM_ENTER` and `CPU_CLUSTER_PM_ENTER`, verify robust failure callbacks, exercise syscore suspend/resume ordering, and run on PREEMPT_RT-style configurations to catch sleeping callbacks. Platform idle paths should validate IRQ-disabled preconditions and no duplicate entry without exit.
