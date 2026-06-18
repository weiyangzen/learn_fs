<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpufreq.h -->
# sources/distributed-fs/ceph-client/include/linux/cpufreq.h

## Purpose

`cpufreq.h` is the main kernel interface for CPU dynamic voltage/frequency scaling. It defines cpufreq policy state, driver and governor contracts, transition notifiers, frequency-table helpers, boost handling, fast switching, thermal integration flags, and OF performance-domain sharing helpers. The source was read as a complete 1,250-line file.

## Important APIs, Types, and Functions

Core types include `struct cpufreq_cpuinfo`, `struct cpufreq_policy`, `struct cpufreq_policy_data`, `struct cpufreq_freqs`, `struct freq_attr`, `struct cpufreq_driver`, `struct cpufreq_governor`, `struct gov_attr_set`, `struct governor_attr`, and `struct cpufreq_frequency_table`. Policy APIs include `cpufreq_cpu_get_raw()`, `cpufreq_cpu_policy()`, `cpufreq_cpu_get()`, `cpufreq_cpu_put()`, `cpufreq_get()`, `cpufreq_quick_get()`, `cpufreq_update_policy()`, `cpufreq_update_limits()`, fast-switch helpers, pressure access, and guard/free helpers for policy locks and references. Driver/governor APIs include `cpufreq_register_driver()`, `cpufreq_unregister_driver()`, `cpufreq_driver_target()`, `cpufreq_driver_fast_switch()`, `cpufreq_driver_adjust_perf()`, `cpufreq_register_governor()`, `cpufreq_start_governor()`, and `cpufreq_stop_governor()`. Table helpers cover iteration, validation, target resolution, efficient-frequency filtering, and sorted ascending/descending search.

## Control Flow

A cpufreq driver registers a `struct cpufreq_driver`, initializes policies per related CPU domain, verifies limits, exposes sysfs attributes, and starts a governor. Governors compute targets and invoke driver callbacks through core wrappers. Frequency transitions notify `PRECHANGE` and `POSTCHANGE`, update policy `cur`, and synchronize through `transition_lock` and `transition_wait`. Table target helpers clamp target frequencies to min/max, choose relation `L/H/C`, optionally skip inefficient entries, and retry without efficiency filtering if needed.

## State and Persistence Behavior

`struct cpufreq_policy` is the persistent in-memory state for a frequency domain: CPU masks, limits, current/suspend frequency, governor data, QoS requests, frequency table, sysfs kobject, policy list node, rwsem, fast-switch and boost flags, cached resolution, transition state, stats, driver data, thermal cooling device pointer, and notifier blocks. No file-backed persistence is owned here, but sysfs exposes mutable policy state.

## Dependencies and Integration Points

It depends on clk, CPU/core, cpumask, completions, kobjects, notifiers, OF, OPP, PM QoS, spinlocks, sysfs, and min/max helpers. Integration points include schedutil and scheduler frequency invariance, energy-aware scheduling, thermal cooling, OPP energy models, CPU hotplug, sysfs governors, architecture frequency read/scale hooks, and device-tree performance domains.

## Risks and Edge Cases

Policy locking and reference lifetimes are critical because hotplug can remove policies while readers inspect them. Fast switch callbacks run in scheduler-sensitive contexts and must avoid sleeping. Frequency table helpers assume correct sorting metadata; unsorted tables use a separate path. Efficient-frequency filtering must retry if filtering makes min/max impossible. Notifier ordering and async notification flags must match driver behavior. Disabled `CONFIG_CPU_FREQ` stubs return zeros or unsupported errors, so consumers must handle absent cpufreq.

## Test Signals

Signals include cpufreq selftests, driver registration/unregistration, policy hotplug stress, sysfs min/max/governor changes, notifier ordering traces, fast-switch scheduler tests, boost enable/disable, frequency-table target tests for ascending/descending/unsorted tables, inefficient-frequency selection tests, thermal cooling integration, OF sharing mask parsing, and builds with cpufreq disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpufreq.h -->
