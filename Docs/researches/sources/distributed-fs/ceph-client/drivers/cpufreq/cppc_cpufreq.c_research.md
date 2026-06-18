# sources/distributed-fs/ceph-client/drivers/cpufreq/cppc_cpufreq.c

## Purpose

This generic ACPI CPPC cpufreq driver maps cpufreq frequency requests to CPPC performance controls. It also supports optional scheduler frequency invariance from CPPC feedback counters, boost, CPPC sysfs controls, shared performance domains, and an artificial energy model on heterogeneous ARM64 systems.

## Important APIs, types, and functions

The driver uses `struct cppc_cpudata` from ACPI CPPC core as policy private data. Core paths are `cppc_cpufreq_get_cpu_data()`, `cppc_cpufreq_cpu_init()`, `cppc_cpufreq_set_target()`, `cppc_cpufreq_fast_switch()`, `cppc_cpufreq_update_perf_limits()`, `cppc_cpufreq_get_rate()`, `cppc_cpufreq_set_boost()`, and `cppc_cpufreq_cpu_exit()`. With `CONFIG_ACPI_CPPC_CPUFREQ_FIE`, `struct cppc_freq_invariance`, `cppc_scale_freq_tick()`, PCC work handling, and `topology_set_scale_freq_source()` update `arch_freq_scale`. Sysfs attributes include frequency-domain CPUs, auto-select, auto activity window, EPP value, and perf-limited.

## Control flow, state, and persistence

Late init requires valid ACPI `_CPC`, initializes FIE and efficiency-class data, then registers the cpufreq driver. Policy init allocates CPPC data, reads `_PSD`, performance caps, and current perf controls, sets policy min to lowest nonlinear and max to highest or nominal depending on boost, applies sharing masks for `CPUFREQ_SHARED_TYPE_ANY`, enables fast-switch when CPPC permits it, programs desired perf to highest, and starts FIE for the policy. Target/fast-switch convert requested kHz to desired performance, recompute min/max performance bounds from policy limits, and call `cppc_set_perf()`. Get-rate samples feedback counters twice and falls back to desired perf when counters are invalid or idle. Exit lowers desired perf to lowest and frees CPPC data.

## Dependencies and integration points

The driver depends on ACPI CPPC methods, ACPI processor IDs, `_PSD`, scheduler topology frequency-scale hooks, optional PCC-safe kthread work, cpufreq core, CPU hotplug semantics, and optional ARM64 energy model registration from MADT GICC efficiency classes. It is the generic fallback for systems exposing standards-based CPPC rather than vendor-specific drivers like AMD pstate.

## Risks and test signals

Risks include CPPC firmware returning zero or inconsistent counters, sleeping PCC accesses from tick context, shared-domain policy misclassification, boost max updates not refreshing limits by themselves, artificial EM cost modeling inaccuracies, and sysfs writes that alter autonomous selection or EPP unexpectedly. Test signals include successful policy creation from `_CPC/_PSD`, frequency requests reflected in CPPC desired perf, correct frequency-invariance values under load, cpufreq boost toggling, sysfs read/write behavior, CPU hotplug cleanup, and suspend/idle cases where get-rate falls back cleanly.
