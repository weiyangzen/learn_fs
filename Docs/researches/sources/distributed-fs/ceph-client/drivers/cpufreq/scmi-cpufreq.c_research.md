<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/scmi-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/scmi-cpufreq.c

## Purpose

Implements cpufreq over ARM SCMI Performance Protocol domains, using firmware-provided OPPs, frequency set/get operations, fast channels when available, performance limit notifications, and energy-model data.

## APIs, Types, And Functions

`struct scmi_data` stores domain id, OPP count, CPU device, OPP sharing mask, limit notifier, and frequency QoS request. Main callbacks are `scmi_cpufreq_init()`, `scmi_cpufreq_set_target()`, `scmi_cpufreq_fast_switch()`, `scmi_cpufreq_get_rate()`, `scmi_cpufreq_exit()`, and `scmi_cpufreq_register_em()`. Helpers discover domain ids from `clocks` or `power-domains` and compute sharing CPUs.

## Control Flow

SCMI driver probe verifies the SCMI device is referenced by CPUs, obtains the performance protocol handle, optionally registers a dummy clock provider, and registers cpufreq. Policy init gets the CPU device/domain, allocates state and masks, finds SCMI and OPP sharing CPUs, adds firmware OPPs when not already present, builds a cpufreq table, sets any-CPU DVFS, latency, fast-switch support, transition delay, and a max-frequency QoS request, then subscribes to performance-limit notifications. Target and fast-switch send `perf_ops->freq_set()`, synchronous flag false or true respectively.

## State And Persistence

Per-policy state owns dynamic OPPs, cpufreq table, QoS limit request, notifier registration, and sharing mask. Firmware owns actual performance-domain state. Limit notifications update the policy max constraint through `freq_qos_update_request()`.

## Dependencies And Integration Points

Depends on SCMI Performance Protocol ops, OF CPU domain references, OPP framework, PM QoS, energy model, cpufreq cooling/boost, and optional common clock provider compatibility.

## Risks And Test Signals

`freq_set` for normal target is asynchronous, so observed frequency may lag requests. Incorrect domain-sharing discovery can duplicate OPPs or split policies. Test signals include SCMI protocol probe, generated OPP count, transition latency/rate limit, fast-switch availability, limit notification QoS updates, EM registration with power scale, and firmware `freq_get()` matching requested OPPs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/scmi-cpufreq.c -->
