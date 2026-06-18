# sources/distributed-fs/ceph-client/drivers/cpufreq/amd-pstate.c

## Purpose

This is the AMD Processor P-State cpufreq driver. It uses ACPI CPPC data and either AMD CPPC MSRs or ACPI shared-memory CPPC calls to control performance limits, desired performance, boost, preferred-core ranking, energy-performance preference, floor performance, suspend/resume restoration, and runtime switching among disabled, passive, active EPP, and guided modes.

## Important APIs, types, and functions

The main global state is `current_pstate_driver`, `cppc_state`, `amd_pstate_prefcore`, `dynamic_epp`, and optional DMI `quirks`. Static calls select MSR or shared-memory backends for `amd_pstate_update_perf()`, `amd_pstate_set_epp()`, `amd_pstate_get_epp()`, `amd_pstate_cppc_enable()`, and `amd_pstate_init_perf()`. Important helpers include `freq_to_perf()`, `perf_to_freq()`, `amd_pstate_update_min_max_limit()`, `amd_pstate_update_freq()`, `amd_pstate_adjust_perf()`, `amd_pstate_init_freq()`, `amd_pstate_init_boost_support()`, `amd_pstate_init_prefcore()`, and `amd_pstate_set_floor_perf()`. It exports mode/status and EPP helpers used by the test module.

## Control flow, state, and persistence

`amd_pstate_init()` runs as a device initcall, checks AMD vendor, CPPC support, `_CPC`, existing cpufreq drivers, DMI quirks, boot parameters, default mode, and static-call backend selection before registering either `amd_pstate_driver` or `amd_pstate_epp_driver`. Per-CPU init allocates `struct amd_cpudata`, reads CPPC caps and current request state, computes frequency limits, enables CPPC, initializes boost/floor/perf caches, and registers QoS requests in passive/guided mode. Passive mode uses target/fast-switch/adjust_perf paths to program desired performance. Active mode uses `setpolicy`, keeps desired performance autonomous, and drives EPP plus min/max bounds. Mode changes are serialized by `amd_pstate_driver_lock` through `mode_state_machine`.

The persistent runtime state is mostly hardware CPPC request MSRs or shared-memory CPPC controls, cached in `amd_cpudata->cppc_req_cached`, `cppc_req2_cached`, and `perf`. Offline, suspend, and exit paths deliberately reset CPPC request and floor performance toward BIOS values so kexec and firmware handoff preserve sane minimums. Dynamic EPP registers a platform-profile device and optional power-supply notifier per CPU; cleanup removes those resources.

## Dependencies and integration points

The driver depends on ACPI CPPC (`cppc_*` APIs), x86 MSRs, AMD CPU feature helpers, DMI, cpufreq core, freq QoS, scheduler ITMT/preferred-core support, power-supply notifications, platform profile, tracepoints from `amd-pstate-trace.h`, and CPU subsystem sysfs. It provides global `/sys/devices/system/cpu/amd_pstate/*` controls and per-policy attributes such as max frequency, lowest nonlinear frequency, highest perf, prefcore ranking, EPP preferences, and floor frequency when supported.

## Risks and test signals

Risk centers on stale cached CPPC request values, incorrect static-call backend selection, mode transitions racing with cpufreq policies, firmware tables reporting invalid perf/frequency values, and restore paths that write inappropriate min/floor values around suspend or kexec. Preferred-core support must coordinate with AMD HFI and scheduler ITMT. Test signals include `amd-pstate-ut`, active/passive/guided mode switching through sysfs, cpufreq fast-switch behavior, boost toggling, suspend/resume and CPU hotplug, EPP behavior on AC/DC power, platform-profile changes, tracepoints, and validation that cpufreq limits remain within CPPC-derived min/max/nominal/highest values.
