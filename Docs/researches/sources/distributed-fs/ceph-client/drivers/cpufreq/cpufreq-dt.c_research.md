# sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq-dt.c

## Purpose

This is the generic device-tree OPP cpufreq driver. It builds cpufreq policies from CPU clocks, regulators, and OPP tables, then changes CPU rate through the OPP core.

## Important APIs, types, and functions

`struct private_data` stores the CPU device, sharing CPU mask, cpufreq table, static-OPP flag, regulator token, and list node. Important functions are `dt_cpufreq_early_init()`, `cpufreq_init()`, `set_target()`, `dt_cpufreq_release()`, `dt_cpufreq_probe()`, `dt_cpufreq_remove()`, and exported `cpufreq_dt_pdev_register()`. `find_supply_name()` handles `cpu-supply` and legacy `cpu0-supply`.

## Control flow, state, and persistence

Probe pre-initializes every present CPU so errors such as regulator or OPP probe deferral happen before registering cpufreq. Early init skips CPUs already covered by another private data entry, allocates a sharing mask, sets OPP regulators, obtains sharing from OPP v2 or legacy OPP state, adds static OPP tables for all shared CPUs, checks that the OPP table is non-empty, initializes a cpufreq table, and links the private data. Policy init finds the relevant private data, gets the CPU clock, copies the sharing mask to `policy->cpus`, installs the cpufreq table, sets suspend frequency and transition latency, and enables any-CPU DVFS. Target calls `dev_pm_opp_set_rate()` with selected frequency in Hz. Remove unregisters cpufreq and releases tables, static OPPs, regulators, masks, and list nodes.

## Dependencies and integration points

The driver depends on CPU device nodes, common clock framework, OPP core, regulator framework, cpufreq generic table verification, thermal cooling device registration, energy-model registration with OPP, software boost, and optional platform data for governor-per-policy, suspend/resume, and intermediate target hooks. It is instantiated either by `cpufreq-dt-platdev.c` or explicit platform-device registration from SoC setup drivers.

## Risks and test signals

Risks include incorrect OPP sharing masks, regulator naming compatibility, duplicated OPP table initialization, static versus dynamic OPP cleanup mistakes, and global driver callback mutation from platform data affecting all instances. Test signals include successful probe deferral behavior, valid frequency tables, regulator voltage changes through OPP, correct shared policies, cooling and EM registration, suspend frequency behavior, and clean remove/unload.
