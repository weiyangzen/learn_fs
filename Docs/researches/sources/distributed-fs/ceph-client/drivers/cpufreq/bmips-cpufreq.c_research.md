# sources/distributed-fs/ceph-client/drivers/cpufreq/bmips-cpufreq.c

## Purpose

This driver provides cpufreq support for Broadcom BMIPS5000/BMIPS5200 MIPS SoCs by changing CPU clock divider bits in the Broadcom mode register. It builds a frequency table from the high-precision timer frequency and a platform-specific multiplier.

## Important APIs, types, and functions

`struct cpufreq_compat` binds CPU compatible strings to BMIPS type, clock multiplier, and number of frequency entries. `bmips_cpufreq_get_freq_table()` allocates descending divide-by-two entries. `bmips_cpufreq_get()` reads `read_c0_brcm_mode()`, extracts the divider, and returns kHz. `bmips_cpufreq_target_index()` writes divider state through `change_c0_brcm_mode()`. `bmips_cpufreq_driver_init()` detects a supported CPU node and registers the cpufreq driver.

## Control flow, state, and persistence

At module init, the driver scans for supported CPU compatibles and stores the selected static compatibility entry in global `priv`. Policy init allocates and installs the table, using `cpufreq_generic_init()` with a fixed transition latency. Runtime target operations use the table entry's `driver_data` as the divider. Exit frees the per-policy frequency table. Persistent state is only the CPU mode-register divider until reset or another writer changes it.

## Dependencies and integration points

The driver depends on MIPS `mips_hpt_frequency`, Broadcom C0 mode register helpers, OF CPU compatible nodes, and cpufreq generic frequency-table handling. It has no regulator or OPP integration.

## Risks and test signals

Risks include incorrect HPT-to-CPU multiplier assumptions, unsupported BMIPS variants sharing compatible strings, direct mode-register manipulation on SMP systems, and no explicit locking beyond cpufreq serialization. Test signals are a correct frequency table, initial frequency matching hardware divider, successful transitions across all divide-by-two entries, and stable timer/accounting behavior after divider changes.
