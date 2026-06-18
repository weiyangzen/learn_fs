# sources/distributed-fs/ceph-client/drivers/cpufreq/p4-clockmod.c

## Purpose

`p4-clockmod.c` exposes Pentium 4/Xeon and related Intel ACPI clock-modulation duty cycles as cpufreq states. It is a throttling driver, not true voltage/frequency scaling, and it intentionally avoids module autoloading because platform-specific SpeedStep or ACPI cpufreq drivers are usually better.

## Important APIs, types, and functions

- Duty-cycle enum values map to IA32 thermal-control modulation states, with `DC_DISABLE` representing full speed.
- `cpufreq_p4_setdc()` writes `MSR_IA32_THERM_CONTROL`, checks thermal status, applies N44/O17 errata by avoiding 12.5% and 25% duty cycles, and enables/disables modulation.
- `p4clockmod_table` contains duty-cycle cpufreq entries from 12.5% through 100%, with reserved/invalid rows.
- `cpufreq_p4_get_frequency()` detects stock frequency through `speedstep-lib` helpers and marks constant loops where TSC is invariant under throttling.
- `cpufreq_p4_cpu_init()` sets sibling policy masks, detects errata steppings, may recalibrate on early desktop P4, fills the table from `stock_freq`, and sets high transition latency.

## Control flow

`late_initcall(cpufreq_p4_init)` requires Intel `X86_FEATURE_ACC` and ACPI capability, then registers cpufreq. Policy init fills a global table from the detected stock frequency and invalidates low duty cycles on errata CPUs. Target changes iterate all logical CPUs in the policy sibling mask and write the selected duty-cycle control bits to each CPU's thermal-control MSR. `.get` reads the current modulation bits and returns stock frequency scaled by duty cycle or full stock frequency when disabled.

## State and persistence behavior

Global state includes `has_N44_O17_errata[]`, `stock_freq`, and the mutated frequency table. Duty-cycle settings persist per logical CPU in `MSR_IA32_THERM_CONTROL` until another target or external thermal control changes them. There is no suspend/resume state handling. The driver sets `CPUFREQ_CONST_LOOPS` for processors where loop calibration should not scale with clock modulation.

## Dependencies

The driver depends on x86 MSR access, Intel ACPI clock modulation feature detection, SpeedStep frequency helpers, topology sibling masks, and cpufreq generic table verification. It intentionally has no `MODULE_DEVICE_TABLE`.

## Risks and edge cases

- Clock modulation reduces duty cycle without lowering voltage; it can hurt performance/power efficiency and should not be confused with real DVFS.
- `stock_freq` and `p4clockmod_table` are global, so heterogeneous systems are not represented.
- Thermal throttling can already be active; the driver only logs it and still writes modulation.
- Errata invalidation is per policy CPU, but the table is global and may affect all policies after one errata CPU initializes.

## Test signals

Validation should confirm the driver does not autoload, warns when better EST/SpeedStep drivers exist, exposes valid duty-cycle states, avoids errata low states, writes all SMT siblings, and reports current frequency from thermal-control MSR bits. Thermal stress should ensure hardware throttling interactions do not corrupt cpufreq state.
