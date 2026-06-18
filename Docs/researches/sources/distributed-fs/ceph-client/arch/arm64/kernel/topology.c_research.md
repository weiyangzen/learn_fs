## sources/distributed-fs/ceph-client/arch/arm64/kernel/topology.c

### Purpose
`topology.c` supplies ARM64 CPU frequency invariance and ACPI CPPC fast-channel counter reads using Activity Monitor Unit counters when available.

### Important APIs, Types, And Functions
Important APIs are `update_freq_counters_refs`, `freq_inv_set_max_ratio`, `arch_cpu_idle_enter`, `arch_freq_get_on_cpu`, `cpc_ffh_supported`, `cpc_read_ffh`, and `cpc_write_ffh`. It also registers cpufreq and CPU hotplug callbacks through `init_amu_fie`.

### Control Flow
Per-CPU AMU samples track previous core and constant cycle counts. Cpufreq policy creation validates AMU support for all CPUs in a policy, allocates/updates `amu_fie_cpus`, and registers `amu_scale_freq_tick` as the frequency scale source. Each tick or idle entry reads AMU deltas, applies a precomputed max-frequency/reference-frequency ratio, clamps to scheduler capacity scale, and stores `arch_freq_scale`. `arch_freq_get_on_cpu` may select an active housekeeping CPU in the same cpufreq policy if the requested CPU lacks a fresh tick. CPPC FFH reads call onto the target CPU unless IRQs are disabled and the target is local.

### State, Persistence, And Dependencies
State includes per-CPU `arch_max_freq_scale`, `cpu_amu_samples`, `arch_freq_scale`, the allocated `amu_fie_cpus` mask, cpufreq notifier registration, and topology scale source registration. No filesystem state is used.

### Integration Points
The file integrates scheduler capacity scaling, cpufreq policy lifecycle, CPU hotplug, housekeeping/nohz isolation, ACPI CPPC FFH, AMU CPU feature detection, erratum 2457168 handling, and the architected timer rate.

### Risks
AMU counters can be absent, disabled, reset, or affected by errata. Mixing CPUs with and without valid counters inside one policy can produce inconsistent scheduler scaling. Remote counter reads are unsafe with IRQs disabled. Stale nohz samples require careful fallback behavior.

### Test Signals
Run cpufreq policy creation/removal, CPU hotplug, nohz full housekeeping fallback, AMU-enabled and AMU-disabled systems, CPPC FFH reads, erratum builds, and scheduler frequency invariance validation under load.
