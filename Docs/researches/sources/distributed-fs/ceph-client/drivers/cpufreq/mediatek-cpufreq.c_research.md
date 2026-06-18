# sources/distributed-fs/ceph-client/drivers/cpufreq/mediatek-cpufreq.c

## Purpose

`mediatek-cpufreq.c` is MediaTek's software DVFS cpufreq driver. It uses CPU OPP tables, CPU/intermediate clocks, and one or two regulators per cluster to change CPU frequency safely. It supports SoC-specific voltage constraints, optional SRAM voltage tracking, and optional CCI frequency coordination.

## Important APIs, types, and functions

- `struct mtk_cpufreq_platform_data` provides voltage shift limits, max voltages, SRAM bounds, and CCI support per SoC.
- `struct mtk_cpu_dvfs_info` stores a cluster's CPU mask, CPU/CCI devices, regulators, CPU and intermediate clocks, OPP notifier, current voltage/frequency, and tracking parameters.
- `mtk_cpufreq_voltage_tracking()` enforces `Vsram - Vproc` shift constraints while stepping voltage up or down.
- `mtk_cpufreq_set_target()` is the main transition sequence: raise voltage if needed, reparent CPU to intermediate clock, change ARM PLL rate, reparent back, then lower voltage if allowed.
- `mtk_cpufreq_opp_notifier()` reacts to OPP voltage adjustments and disabled current OPPs.
- `mtk_cpu_dvfs_info_init()` acquires devices, clocks, regulators, OPP tables, intermediate voltage, and notifier state for one sharing domain.
- `mtk_cpufreq_driver_init()` matches machine compatibles, registers an internal platform driver, then creates a `"mtk-cpufreq"` platform device carrying SoC data.

## Control flow

Module init matches the machine compatible table and creates a platform device because cpufreq drivers historically lacked direct DT binding. Probe iterates present CPUs, skips CPUs already covered by a sharing mask, allocates `mtk_cpu_dvfs_info`, initializes hardware resources, and appends each domain to `dvfs_info_list`. It then registers the cpufreq driver. Policy init looks up the domain for the policy CPU, converts OPPs into a cpufreq table, copies the sharing mask, and stores `policy->clk` and `driver_data`.

During a target transition, the driver locks `reg_lock`, resolves the target OPP voltage, optionally raises it to at least boot voltage until the CCI driver is bound, scales voltage up to the maximum of intermediate and target voltage, switches the CPU clock to a stable intermediate parent, changes the original PLL rate, switches back, and scales voltage down to the final target when safe. Error paths try to restore previous voltage or clock parent/rate.

## State and persistence behavior

Each DVFS domain persists in `dvfs_info_list` for platform device lifetime. Regulator and clock handles are explicitly enabled during init and disabled/put only on probe failure; the platform driver has no remove callback, so normal operation assumes built-in lifetime. `pre_vproc` caches the last set voltage for faster transitions, while `current_freq` is used by OPP notifiers. Device links track CCI readiness and are auto-removed on consumer cleanup.

## Dependencies

Dependencies include CPU device-tree OPP v2 tables with sharing data, CPU clocks named `"cpu"` and `"intermediate"`, optional `"proc"` and `"sram"` regulators, optional `mediatek,cci` phandle, regulator voltage constraints, common clock reparenting/rate APIs, OPP notifier infrastructure, and SoC-compatible platform data.

## Risks and edge cases

- `dev_err_probe(cpu_dev, ...)` is used when `cpu_dev` may be NULL, which is questionable because there is no device to log against.
- Voltage tracking has many rollback paths; regulator failures can leave Vproc/Vsram at intermediate values if the rollback itself fails.
- CCI readiness raises CPU voltage to boot voltage as a crash-prevention workaround, but may reduce power efficiency until supplier binding completes.
- OPP disable notification calls back into `cpufreq_driver_target()` while OPP lists are changing; locking and notifier ordering are important.
- The driver registers a platform device in module init and has no platform-driver remove path for releasing `dvfs_info_list` on normal unload beyond module exit unregistering the device/driver.

## Test signals

Tests should cover all compatible SoC voltage constraints, OPP table parsing, regulator enable/disable failure paths, SRAM tracking up/down steps, intermediate-clock parent switching, CCI unavailable-to-bound transitions, OPP voltage adjustment, current OPP disable fallback, thermal cooling registration, and repeated frequency sweeps under load.
