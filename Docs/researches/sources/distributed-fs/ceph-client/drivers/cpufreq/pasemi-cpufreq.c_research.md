# sources/distributed-fs/ceph-client/drivers/cpufreq/pasemi-cpufreq.c

## Purpose

`pasemi-cpufreq.c` implements CPUFreq support for PA Semi PWRficient systems. It exposes five A-states, reads their frequencies from SDCPWR configuration registers, and switches all online CPUs by writing SDC ASR registers.

## Important APIs, types, and functions

- `pas_freqs` contains A0-A4 table rows; turbo A5/A6 are intentionally excluded.
- `get_astate_freq()`, `get_cur_astate()`, and `get_gizmo_latency()` read SDCPWR registers to determine table frequencies, current state, and transition latency.
- `set_astate()` writes a CPU's ASR register with IRQs disabled.
- `check_astate()` and `restore_astate()` are exported helper-style functions used by platform idle/power paths to observe or restore the current A-state.
- `pas_cpufreq_cpu_init()` maps SDC/Gizmo resources from device tree, fills the table, initializes current frequency, and calls `cpufreq_generic_init()`.
- `pas_cpufreq_target()` updates `current_astate`, writes every online CPU, and updates `ppc_proc_freq`.

## Control flow

Module init only registers the driver on `PA6T-1682M` or `pasemi,pwrficient` machines. CPU init reads CPU `clock-frequency`, maps the SDC ASR window and Gizmo power registers, fills the frequency table by reading each A-state's configuration register, reads the current A-state for the policy CPU, updates PowerPC global processor frequency, and initializes cpufreq. Target changes are global: the selected A-state is written for every online CPU.

## State and persistence behavior

State is global MMIO mappings plus `current_astate`. The driver deliberately does not unmap resources after the system reaches running state because CPU hotplug is not supported. Hardware A-state persists in SDCPWR/SDCASR registers, and `restore_astate()` uses cached `current_astate` when returning from power savings. `ppc_proc_freq` is updated on init and target changes.

## Dependencies

The driver depends on PA Semi device-tree compatibles (`1682m-sdc`, `pasemi,pwrficient-sdc`, `1682m-gizmo`, `pasemi,pwrficient-gizmo`), PowerPC MMIO helpers, hard SMP processor IDs, `ppc_proc_freq`, and platform power-management code using `check_astate()`/`restore_astate()`.

## Risks and edge cases

- Only one set of global mappings exists; multiple policies or hotplug are not supported.
- `pas_cpufreq_cpu_init()` can be invoked per policy, but mapping globals are not protected against repeated initialization.
- Frequencies are derived from register low bits times 100 MHz, which assumes hardware encoding remains stable.
- Target changes update all online CPUs regardless of policy CPU mask.

## Test signals

Tests should verify table rows match SDCPWR A-state configuration, current state reads correctly, target writes affect all online CPUs, `ppc_proc_freq` tracks selected state, idle restore paths call `restore_astate()`, and module unload before `SYSTEM_RUNNING` unmaps resources.
