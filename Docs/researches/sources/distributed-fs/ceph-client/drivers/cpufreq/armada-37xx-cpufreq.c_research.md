# sources/distributed-fs/ceph-client/drivers/cpufreq/armada-37xx-cpufreq.c

## Purpose

This Armada 37xx helper programs north-bridge DVFS and optional AVS voltage tables, creates OPPs for the supported CPU load levels, and then registers a `cpufreq-dt` platform device to provide normal cpufreq operation.

## Important APIs, types, and functions

`struct armada37xx_cpufreq_state` stores the `cpufreq-dt` device, CPU device, PM regmap, and suspend snapshots. `struct armada_37xx_dvfs` maps base CPU frequencies to four divider values and calculated AVS values. Important helpers include `armada_37xx_cpu_freq_info_get()`, `armada37xx_cpufreq_dvfs_setup()`, `armada37xx_cpufreq_avs_configure()`, `armada37xx_cpufreq_avs_setup()`, `armada37xx_cpufreq_enable_dvfs()`, `armada37xx_cpufreq_disable_dvfs()`, and suspend/resume callbacks passed through `cpufreq_dt_platform_data`.

## Control flow, state, and persistence

The late initcall locates syscon regmaps for peripheral clock, north-bridge PM, and optionally AVS, disables DVFS, gets CPU0's clock parent rate, selects the matching divider profile, calculates AVS values, programs VSET registers, programs all four load-level register fields, adds dynamic OPPs with frequencies and voltages, enables hardware DVFS, and registers `cpufreq-dt`. Suspend saves NB DVFS registers; resume disables DVFS, restores saved load/config registers, and writes `NB_DYN_MOD` last because it re-enables DVFS and makes other fields read-only. Runtime persistence is hardware NB/AVS register state plus dynamically added OPPs.

## Dependencies and integration points

The driver depends on syscon/regmap compatibles for Armada 3700 clock, PM, and AVS blocks, CPU clocks, OPP core, and the generic `cpufreq-dt` driver. It integrates with `cpufreq-dt` by creating the platform device and supplying suspend/resume hooks.

## Risks and test signals

Risk areas are unsupported parent clock rates, AVS voltage calculation edge cases, DVFS enable ordering, missing AVS syscon behavior, and failure cleanup that must remove only OPPs already added. Test signals include OPP table contents for four load levels, correct voltage values for 600/800/1000/1200 MHz bases, frequency switching through `cpufreq-dt`, suspend/resume register restoration, and no CPU lockups when transitioning from lower load levels back to L0.
