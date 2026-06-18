<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/spear-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/spear-cpufreq.c

## Purpose

Provides cpufreq for ST SPEAr platforms using a DT-provided frequency table and CPU clock programming, with special parent-source selection for SPEAr1340.

## APIs, Types, And Functions

The global `spear_cpufreq` struct stores the CPU clock, transition latency, allocated table, and count. `spear1340_cpu_get_possible_parent()` selects a system clock source based on requested frequency. `spear1340_set_cpu_rate()` sets source rate and changes the parent of the CPU's system clock. `spear_cpufreq_target()` applies target rates.

## Control Flow

Platform probe gets CPU0's DT node, reads `clock-latency` and `cpufreq_tbl`, allocates a frequency table, gets `"cpu_clk"`, and registers cpufreq. Policy init installs the global table and transition latency. Targeting converts the table entry to Hz; on SPEAr1340 it chooses a possible parent, doubles the source rate, rounds it, sets the source rate, and switches parent. Other SPEAr variants directly set the CPU clock rate.

## State And Persistence

Global state retains the allocated frequency table and CPU clock. Hardware state persists in CPU clock rate and, for SPEAr1340, the parent of the CPU's system clock.

## Dependencies And Integration Points

Depends on OF CPU node properties `clock-latency` and `cpufreq_tbl`, common clock parent/rate APIs, machine compatible `st,spear1340`, and cpufreq generic initialization.

## Risks And Test Signals

There is no remove path freeing the table or clock. SPEAr1340 only supports hard-coded source ranges; unsupported rates return `-EINVAL`. Test signals include parsed DT table order, rounded source rates, parent selection at range boundaries, `clk_set_parent()` success, and `cpufreq_generic_get()` matching expected rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/spear-cpufreq.c -->
