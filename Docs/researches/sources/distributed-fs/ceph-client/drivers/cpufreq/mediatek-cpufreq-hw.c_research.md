# sources/distributed-fs/ceph-client/drivers/cpufreq/mediatek-cpufreq-hw.c

## Purpose

`mediatek-cpufreq-hw.c` is a MediaTek hardware-managed cpufreq driver. Instead of using OPP/regulator/PLL sequencing in software, it reads firmware-populated LUTs from MMIO performance domains and switches performance states by writing hardware registers or, on hybrid DVFS variants such as MT8196, per-CPU FDVFS registers.

## Important APIs, types, and functions

- `struct mtk_cpufreq_variant` holds register offsets, an optional variant init hook, and an `is_hybrid_dvfs` flag.
- `struct mtk_cpufreq_priv` stores the device, variant, and optional FDVFS mapping.
- `struct mtk_cpufreq_domain` stores one cpufreq domain's table, register bases, requested resource, mapping, and OPP count.
- `mtk_cpu_create_freq_table()` reads up to 32 LUT rows, extracts `LUT_FREQ`, stops at a repeated frequency, and terminates the cpufreq table.
- `mtk_cpu_resources_init()` maps the domain selected by `performance-domains`, with an index adjustment for hybrid DVFS.
- `mtk_cpufreq_hw_target_index()`, `mtk_cpufreq_hw_fast_switch()`, and `mtk_cpufreq_hw_get()` implement cpufreq callbacks.
- `mtk_cpufreq_register_em()` registers an Energy Model using power data read from `REG_EM_POWER_TBL`.

## Control flow

Probe first checks that every present CPU has a `"cpu"` regulator available, preventing cpufreq registration before supplies exist. It selects variant data from device-tree compatible strings, performs variant init if needed, stores private data, and registers the cpufreq driver. Policy init maps the correct MMIO domain through `of_perf_domain_get_sharing_cpumask()`, builds a table from the LUT, sets transition latency from hardware, enables the cpufreq hardware block, and polls for CPUFreq/SVS hardware readiness.

Target changes either write the table index to `REG_FREQ_PERF_STATE` or, with FDVFS, convert target kHz to the 26 kHz divider units expected by the FDVFS register and write one register per real CPU in the policy. Fast switch uses the same writes after selecting the closest table index. Energy Model registration exposes firmware-provided power rows for scheduler/thermal use.

## State and persistence behavior

Per-policy domain mappings are explicitly requested and mapped at init, then unmapped and released at exit. The cpufreq table is device-managed but tied to the domain data. Hardware state persists in performance-state, enable, and FDVFS registers. The driver enables the hardware block during policy lifetime and writes zero to pause it on exit. There is no dedicated suspend/resume callback.

## Dependencies

The driver depends on device-tree `performance-domains`, ordered MMIO resources matching domain indexes, variant-compatible register layouts, firmware-populated LUT/status/power/latency registers, CPU regulators, cpufreq fast-switch support, and Energy Model APIs.

## Risks and edge cases

- In `mtk_cpu_resources_init()`, errors after `ioremap()` during table creation return without unmapping/releasing the region, so probe-failure cleanup is incomplete on that path.
- LUT parsing stops on the first repeated frequency; malformed LUTs can truncate valid states or produce zero OPPs.
- FDVFS fast-switch writes `target_freq` rather than the selected table frequency, so callers must pass a value acceptable to hardware rounding.
- `mtk_cpufreq_get_cpu_power()` decrements `i` after the loop; requests below the first table frequency can underflow.
- Poll timeout distinguishes missing CPUFreq hardware from missing SVS only through current status bits; SVS timeout is logged but not fatal.

## Test signals

Validation should include probe deferral until CPU regulators exist, correct domain mapping for each `performance-domains` entry, table contents matching hardware LUTs, successful hardware enable/status polling, fast-switch operation, FDVFS writes on MT8196, Energy Model power readings, and clean region release on policy exit. Thermal cooling registration should also observe `CPUFREQ_IS_COOLING_DEV`.
