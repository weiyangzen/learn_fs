<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/cpu.c -->
# sources/distributed-fs/ceph-client/drivers/opp/cpu.c

## Purpose
`cpu.c` provides CPU-oriented helpers on top of the generic OPP core. It builds cpufreq frequency tables from OPP entries, frees those tables, removes OPP tables over CPU masks, and records/query CPU sharing relationships for OPP tables.

## Important APIs, Types, And Functions
Under `CONFIG_CPU_FREQ`, `dev_pm_opp_init_cpufreq_table()` allocates and fills a `struct cpufreq_frequency_table` from available OPPs. `dev_pm_opp_free_cpufreq_table()` releases it. Always-built helpers include `_dev_pm_opp_cpumask_remove_table()`, `dev_pm_opp_cpumask_remove_table()`, `dev_pm_opp_set_sharing_cpus()`, and `dev_pm_opp_get_sharing_cpus()`.

## Control Flow
`dev_pm_opp_init_cpufreq_table()` first obtains the count of available OPPs. It allocates one extra entry for `CPUFREQ_TABLE_END`, repeatedly calls `dev_pm_opp_find_freq_ceil()` with a monotonically increasing `rate`, stores kHz frequencies, and marks boost OPPs with `CPUFREQ_BOOST_FREQ`. The loop relies on OPP list ordering and the find helper updating `rate` to the matched frequency.

CPU mask removal iterates CPUs until an optional `last_cpu` stop point and calls `dev_pm_opp_remove_table()` for each resolved CPU device. Sharing setup finds the existing table for a representative CPU, adds `opp_device` entries for each other CPU, and marks the table `OPP_TABLE_ACCESS_SHARED`. Sharing query refuses unknown access mode, then returns either every `opp_dev->dev->id` in the table or only the requested CPU for exclusive tables.

## State And Persistence
The cpufreq table is caller-owned heap memory and must be freed by the matching helper. Sharing persists in the shared `opp_table->dev_list` and `shared_opp` enum until table teardown. No hardware is programmed here; the helpers only prepare data and modify table membership.

## Dependencies And Integration Points
This file depends on CPU device lookup (`get_cpu_device()`), cpumask iteration, cpufreq table structures, and OPP core internals `_find_opp_table()`, `_add_opp_dev()`, and `_dev_pm_opp_cpumask_remove_table()`. It is commonly used by CPUFreq drivers that consume DT OPP tables.

## Risks
The generated cpufreq table is a snapshot; callers must rebuild it after OPP availability or voltage/frequency changes. `dev_pm_opp_set_sharing_cpus()` logs but continues if some CPUs cannot be resolved or added, which can leave a partial sharing mask. It assumes CPU device IDs correspond to CPU numbers. Removal over masks can encounter absent CPU devices and continue, so cleanup errors are not fatal.

## Test Signals
Tests should cover cpufreq table generation order, boost flags, empty/no-table error returns, rebuild after enable/disable, shared CPU mask reporting for exclusive and shared tables, partial CPU device failures, and table teardown over policy masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/cpu.c -->
