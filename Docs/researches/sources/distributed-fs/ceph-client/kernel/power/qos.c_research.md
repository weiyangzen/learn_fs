# sources/distributed-fs/ceph-client/kernel/power/qos.c

## Purpose
Implements the base Power Management Quality of Service aggregation engine plus global CPU latency QoS and frequency QoS helpers. It lets kernel and user-space clients submit constraints that are aggregated into effective latency or frequency limits and optionally reported through notifiers.

## Important APIs, Types, and Functions
Core helpers are `pm_qos_read_value()`, `pm_qos_update_target()`, and `pm_qos_update_flags()`. A global `pm_qos_lock` protects constraint lists, flags lists, and notifier updates. PM QoS constraints use `struct pm_qos_constraints`, `plist_head`, `plist_node`, and action enum values `PM_QOS_ADD_REQ`, `PM_QOS_UPDATE_REQ`, and `PM_QOS_REMOVE_REQ`. Constraint type `PM_QOS_MIN` chooses the lowest priority value; `PM_QOS_MAX` chooses the highest.

When `CONFIG_CPU_IDLE` is enabled, CPU latency APIs include `cpu_latency_qos_limit()`, `cpu_latency_qos_request_active()`, `cpu_latency_qos_add_request()`, `cpu_latency_qos_update_request()`, and `cpu_latency_qos_remove_request()`. User space accesses the same aggregate through `/dev/cpu_dma_latency`. Optional `CONFIG_PM_QOS_CPU_SYSTEM_WAKEUP` adds `/dev/cpu_wakeup_latency` and `cpu_wakeup_latency_qos_limit()`.

Frequency QoS APIs include `freq_constraints_init()`, `freq_qos_read_value()`, `freq_qos_apply()`, `freq_qos_add_request()`, `freq_qos_update_request()`, `freq_qos_remove_request()`, `freq_qos_add_notifier()`, and `freq_qos_remove_notifier()`.

## Control Flow
`pm_qos_update_target()` takes the spinlock, computes the previous aggregate, normalizes default values, mutates the plist according to add/update/remove, computes and stores the new aggregate with `WRITE_ONCE`, drops the lock, emits a tracepoint, and notifies subscribers if the aggregate changed. `pm_qos_update_flags()` performs the same pattern for OR-aggregated flags.

CPU latency request operations validate handles and values, attach the request to `cpu_latency_constraints`, update the aggregate, and wake all idle CPUs if the effective latency changes. The misc-device open path allocates a request with default value; write accepts either a binary `s32` or text value and updates the request; release removes and frees it.

Frequency QoS initializes independent min and max constraint lists with opposite aggregation directions: min frequency uses `PM_QOS_MAX`, and max frequency uses `PM_QOS_MIN`. Add/update/remove operations validate active handles and then delegate to `pm_qos_update_target()`.

## State and Persistence Behavior
QoS requests are runtime constraints associated with kernel-owned request objects or open misc-device file descriptors. Closing `/dev/cpu_dma_latency` or `/dev/cpu_wakeup_latency` removes that request. Effective values are held in `target_value` and observed locklessly via `READ_ONCE`. No state persists across reboot.

## Dependencies and Integration Points
The file depends on plist, spinlocks, blocking notifiers, misc devices, user-copy helpers, debug/trace infrastructure, CPU idle wakeups, and cpufreq-style frequency constraints. CPU idle governors, cpufreq drivers, device PM, and user-space latency-sensitive applications consume these limits.

## Risks
Risks include callers updating inactive request objects, invalid negative constraints, missed notifier transitions, lock ordering with notifier callbacks, user-space ABI compatibility for binary vs text writes, and stale requests if file release paths fail. Because one global spinlock protects all PM QoS lists, expensive work must remain outside the critical section.

## Test Signals
Exercise kernel add/update/remove APIs, duplicate add/remove warnings, notifier callbacks, `/dev/cpu_dma_latency` binary and text writes, close cleanup, optional `/dev/cpu_wakeup_latency`, cpufreq min/max constraints, and tracepoints. Runtime validation should confirm idle CPUs wake when CPU latency limits tighten.
