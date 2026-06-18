<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/rcpufreq_dt.rs -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/rcpufreq_dt.rs

## Purpose

Rust implementation of the generic `cpufreq-dt` driver. It builds OPP-backed cpufreq policies from DT/firmware nodes, CPU clocks, optional regulators, and OPP sharing data.

## APIs, Types, And Functions

`CPUFreqDTDevice` owns the OPP table, cpufreq table, cpumask, optional OPP config token, and CPU clock. `CPUFreqDTDriver` implements `opp::ConfigOps`, `cpufreq::Driver`, and `platform::Driver`. Helper functions discover exact `cpu0-supply`/`cpu-supply` regulator names.

## Control Flow

Policy init gets the CPU device, creates a cpumask, optionally configures regulator names, determines OPP sharing via `operating-points-v2` or legacy OPP sharing, loads OPPs from OF or existing dynamic tables, validates OPP count, applies fallback sharing to all CPUs if needed, sets transition latency and suspend frequency, installs the cpufreq table, sets the CPU clock, copies the final cpumask to the policy, and returns an `Arc` holding resources. Targeting looks up the selected table frequency and calls `opp_table.set_rate()`.

## State And Persistence

State is owned by the `Arc<CPUFreqDTDevice>` stored as policy data; RAII ownership keeps the OPP table, freq table, config token, cpumask, and clock alive while C cpufreq holds raw references. Online/offline are lightweight and intentionally preserve policy data. Hardware state is managed by OPP/clock/regulator frameworks.

## Dependencies And Integration Points

Integrates with Rust kernel abstractions for CPU devices, cpufreq, OPP, cpumasks, platform drivers, C strings, and OF matching on `operating-points-v2`. It registers energy model data through OPP and supports boost flags.

## Risks And Test Signals

Safety relies on lifetime assumptions around C-visible cpufreq table and clock references, documented with `unsafe` comments. Test signals include successful OF match, OPP loading or `EPROBE_DEFER`, correct sharing cpumask, regulator-name config, transition latency fallback, `opp_table.set_rate()` success, suspend frequency, and stable hotplug online/offline without freeing policy data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/rcpufreq_dt.rs -->
