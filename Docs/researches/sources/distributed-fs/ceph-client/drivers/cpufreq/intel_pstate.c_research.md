# sources/distributed-fs/ceph-client/drivers/cpufreq/intel_pstate.c

## Purpose

`intel_pstate.c` is Intel's native CPU frequency scaling driver for modern x86 processors. It supports two cpufreq operating modes: the active `intel_pstate` driver, which owns policy selection through scheduler utilization callbacks and direct P-state/HWP programming, and the passive `intel_cpufreq` driver, which exposes Intel hardware to ordinary cpufreq governors. It handles legacy PERF_CTL P-states, Hardware P-states (HWP), HWP Energy Performance Preference (EPP), turbo limits, ACPI limits, hybrid CPU capacity scaling, and runtime sysfs mode changes.

The file is intentionally self-contained because it coordinates CPU model identification, MSR programming, scheduler hooks, cpufreq policy callbacks, HWP notifications, Energy Model registration for hybrid systems, and global `/sys/devices/system/cpu/intel_pstate/` controls.

## Important APIs, types, and functions

- `struct cpudata` is per-CPU persistent driver state: policy, scheduler update hook, P-state limits, APERF/MPERF samples, EPP cache, HWP request/capability cache, HWP boost state, ACPI `_PSS` data, hybrid capacity data, and HWP notification work.
- `struct pstate_data`, `struct vid_data`, `struct sample`, `struct global_params`, and `struct pstate_funcs` separate hardware limits, Atom VID encoding, utilization samples, global sysfs limits, and CPU-model-specific callbacks.
- `intel_pstate` and `intel_cpufreq` are the two `struct cpufreq_driver` instances. Active mode uses `.setpolicy`; passive mode uses `.target`, `.fast_switch`, and HWP `.adjust_perf`.
- `intel_pstate_init()` is the `device_initcall()` entry point. It rejects unsupported/vendor-managed platforms, selects HWP or PERF_CTL operation, applies early-parameter choices, allocates `all_cpu_data`, exposes sysfs, and registers the selected cpufreq driver.
- `intel_pstate_setup()` parses `intel_pstate=` early parameters: `disable`, `active`, `passive`, `no_hwp`, `no_cas`, `force`, `hwp_only`, `per_cpu_perf_limits`, and ACPI `_PPC` support when enabled.
- `intel_pstate_set_policy()`, `intel_pstate_update_util()`, `intel_pstate_adjust_pstate()`, and `intel_pstate_set_pstate()` implement active PERF_CTL control.
- `intel_pstate_hwp_set()`, `intel_cpufreq_hwp_update()`, `intel_cpufreq_adjust_perf()`, and HWP interrupt helpers program `MSR_HWP_REQUEST`, track `MSR_HWP_CAPABILITIES`, and react to firmware-reported performance changes.
- Sysfs handlers manage `status`, `no_turbo`, `min_perf_pct`, `max_perf_pct`, `hwp_dynamic_boost`, `energy_efficiency`, and per-policy HWP EPP attributes.

## Control flow and integration

Initialization first checks for Intel vendor, platform out-of-band power management, HWP support, and CPU model tables. With HWP, the file can use HWP on any Intel CPU advertising the feature, subject to EPP or DEC safety checks. Without HWP, it falls back to explicit model matches and validates the P-state MSRs. It then registers either active `intel_pstate` or passive `intel_cpufreq`, while sysfs `status` can switch between active/passive or turn the non-HWP driver off.

CPU policy init allocates or reuses `struct cpudata`, enables HWP if active, reads MSR-derived min/max/turbo limits, initializes ACPI performance limits, and sets cpufreq policy bounds. Active mode installs a scheduler utilization hook unless HWP active mode does not need dynamic boost. The hook samples APERF/MPERF/TSC at `INTEL_PSTATE_SAMPLING_INTERVAL`, accounts for IO-wait boost, computes a target P-state from busy fraction and previous average performance, clamps it through policy/global limits, and writes `MSR_IA32_PERF_CTL`.

Passive mode lets the cpufreq governor choose target frequencies. Normal target calls wrap transitions with `cpufreq_freq_transition_begin/end`; fast-switch and adjust-perf paths write local MSRs directly when allowed. With HWP, passive mode updates min/max/desired performance fields in `MSR_HWP_REQUEST`; without HWP, it writes PERF_CTL target ratios.

HWP notification interrupts queue delayed work to refresh HWP capabilities, policy maximums, and hybrid capacity scaling. Hybrid systems use CPPC or model scaling factors to translate performance levels to frequency, register lightweight Energy Model perf domains, and set architecture CPU capacity for scheduler asymmetry. If HWP is disabled on a hybrid CPU, the driver warns because that setup is known to be problematic.

## State and persistence behavior

Global mutable state includes `all_cpu_data`, selected `intel_pstate_driver`, `global` performance percentages, HWP mode flags, EPP defaults, hybrid scaling state, and sysfs kobjects. Per-CPU state persists across policy life and CPU hotplug until driver cleanup; offline CPUs have HWP min/max forced to the lowest performance to avoid constraining siblings. Suspend marks CPUs suspended, disables HWP interrupts, and resume re-enables HWP/request state when online callbacks did not already do so.

Hardware state persists in MSRs: `MSR_PM_ENABLE`, `MSR_HWP_REQUEST`, `MSR_HWP_INTERRUPT`, `MSR_HWP_STATUS`, `MSR_IA32_PERF_CTL`, `MSR_IA32_POWER_CTL`, APERF/MPERF, platform info, turbo ratio, Atom ratio/VID, and config TDP registers. The driver caches selected HWP request/capability values because scheduler callbacks and sysfs writes can race with direct MSR updates. Locks used for serialization include `intel_pstate_driver_lock`, `intel_pstate_limits_lock`, `hybrid_capacity_lock`, and `hwp_notify_lock`.

## Dependencies

The driver depends on x86 MSR and CPU model infrastructure, cpufreq core, scheduler cpufreq hooks, tracing, frequency QoS, ACPI processor/CPPC when configured, thermal HWP interrupt integration, Energy Model support for hybrid systems, and CPU topology/cache metadata. Correct behavior also depends on firmware not retaining exclusive P-state control unless `force` is used, valid HWP capability MSRs, correct ACPI `_PSS`/`_PPC`/PCCH data on systems that expose platform limits, and sane BIOS turbo/HWP defaults.

## Risks and edge cases

- Mode switching through sysfs unregisters and re-registers cpufreq drivers; cleanup must remove scheduler hooks and per-CPU allocations without racing hotplug.
- HWP request updates are shared between scheduler boost, sysfs EPP writes, passive governor paths, and suspend/offline paths. Stale cached request bits can leak undesired desired/min/max values.
- ACPI platform detection intentionally avoids systems with firmware-owned P-state control. `force` can bypass parts of this protection and may conflict with SMM/firmware.
- Hybrid scaling is subtle: wrong scaling factors or CPPC values can produce incorrect capacity, Energy Model cost, or frequency reporting.
- APERF/MPERF sampling skips unchanged counters and assumes local callbacks. Remote execution or NOHZ behavior can reduce responsiveness.
- Turbo and global percentage limits are coupled to `turbo_pstate`; invalid MSR data can make percentage math and sysfs limits misleading.
- HWP-notify work updates policy limits asynchronously; missed interrupt masking or work cancellation on offline/suspend can leave stale limits until the next policy refresh.

## Test signals

Build coverage should include HWP and non-HWP x86 configurations, ACPI/CPPC variants, and Energy Model enabled/disabled. Runtime signals include successful driver selection, correct `status` transitions, sysfs limit clamping, EPP attribute behavior, CPU hotplug, suspend/resume with HWP enabled, HWP notify interrupt handling, turbo disable/enable behavior, and cpufreq trace samples. Performance validation should compare active versus passive modes, fast-switch versus normal target paths, IO-wait boost response, and hybrid scheduler capacity on systems with P/E cores.
