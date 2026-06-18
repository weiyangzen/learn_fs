<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/governor.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/governor.c

## Purpose

`governor.c` implements genpd governor policies for deciding whether devices may suspend, whether domains may power down, and which idle state to use. CPU-domain support additionally considers cpuidle timers, CPU latency QoS, online CPU masks, and pending IPIs.

## Important APIs, types, and functions

Important functions are `default_suspend_ok()`, `dev_update_qos_constraint()`, `update_domain_next_wakeup()`, `_default_power_down_ok()`, `default_power_down_ok()`, `cpu_power_down_ok()`, and `cpu_system_power_down_ok()`. Exported governor instances are `simple_qos_governor`, `pm_domain_always_on_gov`, and, with CPU idle, `pm_domain_cpu_gov`.

## Control flow

Runtime suspend calls `suspend_ok()` before device suspend. The default policy reads resume-latency QoS, subtracts measured suspend/resume latency, folds in child constraints, and caches the result. Domain power-off calls `power_down_ok()`, which aggregates next wakeups, invalidates parent caches when constraints change, and walks from deepest to shallowest state until latency and residency requirements pass. CPU domains add hrtimer, global/per-CPU latency, online CPU, and IPI checks.

## State and persistence behavior

The governor updates `gpd_timing_data` cache fields and `genpd_governor_data` fields such as max off time, cached state index, next wakeup, next hrtimer, and residency reflection flags. It writes `genpd->state_idx`; actual usage/rejected accounting is performed by the core after transitions.

## Dependencies and integration points

It depends on PM domains, PM QoS, hrtimer, cpuidle, CPU masks, and ktime. Device drivers influence it through runtime PM, PM QoS, measured latencies, and `dev_pm_genpd_set_next_wakeup()`.

## Risks and edge cases

Stale cache invalidation can choose wrong states, zero QoS means no suspend while no-constraint QoS means unrestricted, min-residency depends on fresh wakeup hints, CPU decisions can be invalidated by IPIs, and provider state arrays must be ordered shallow-to-deep.

## Test signals

Test zero/no-constraint QoS, child constraint aggregation, latency cache updates, min-residency state selection, QoS-change invalidation, deep-to-shallow fallback, CPU hrtimer and IPI rejection, and debugfs residency counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/governor.c -->
