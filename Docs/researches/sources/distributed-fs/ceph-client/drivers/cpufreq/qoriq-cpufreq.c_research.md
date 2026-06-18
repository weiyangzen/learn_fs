<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/qoriq-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/qoriq-cpufreq.c

## Purpose

Implements cpufreq for Freescale/NXP QorIQ SoCs by switching the CPU clock parent among available parent clocks.

## APIs, Types, And Functions

`struct cpu_data` stores parent clock pointers and the allocated frequency table. `get_bus_freq()` derives platform bus frequency from DT or a named clock for latency calculation. `set_affected_cpus()` finds CPUs sharing the same clock. `freq_table_redup()` invalidates duplicate rates and `freq_table_sort()` sorts entries descending.

## Control Flow

Platform probe refuses known erratum A-008083 clockgens, then registers cpufreq. Policy init gets the CPU node and CPU clock, enumerates its parents through `clk_hw`, builds a parent-indexed frequency table, removes duplicates, sorts it, computes shared CPUs, stores driver data, and sets transition latency to 12 platform clocks. Targeting sets the CPU clock parent based on the selected table entry.

## State And Persistence

Per-policy allocated state retains parent clock pointers and the frequency table until exit. Hardware state persists as the CPU clock parent selection. No direct register writes are performed here.

## Dependencies And Integration Points

Depends on OF CPU nodes, clock parents, `clk_set_parent()`, platform bus frequency properties/clocks, cpufreq cooling flag, and platform-device creation under name `qoriq-cpufreq`.

## Risks And Test Signals

The table assumes parent clock rates are valid and fixed enough for cpufreq policy use. Error paths collapse many failures to `-ENODEV`. Test signals include blacklist behavior, table ordering/deduplication, related CPU mask for shared clocks, transition latency, and parent-clock readback after target changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/qoriq-cpufreq.c -->
