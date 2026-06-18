<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/sc520_freq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/sc520_freq.c

## Purpose

Provides cpufreq support for AMD Elan SC520 by toggling the CPU control register between 100 MHz and 133 MHz modes.

## APIs, Types, And Functions

`sc520_freq_table` contains the two hardware encodings. `sc520_freq_get_cpu_frequency()` reads the mapped CPUCTL register and decodes bits 1:0. `sc520_freq_target()` writes the selected encoding with interrupts disabled. `sc520_freq_driver` wires generic table verify, target, get, and init.

## Control Flow

Module init checks AMD family/model support, maps `MMCR_BASE + OFFS_CPUCTL`, and registers cpufreq. Policy init repeats capability checks, sets 1 ms latency, and installs the table. Targeting masks CPUCTL low bits and writes the selected value. Exit unregisters and unmaps.

## State And Persistence

The global `cpuctl` pointer stores the MMIO mapping. Hardware state persists in CPUCTL clock-speed bits.

## Dependencies And Integration Points

Depends on x86 CPU matching, fixed SC520 MMCR address, `ioremap`, and cpufreq table APIs.

## Risks And Test Signals

Only two encodings are valid; unexpected register values log an error and report 100 MHz. Test signals include MMIO mapping success, cpufreq table visibility, CPUCTL readback after target, and correct cleanup on module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/sc520_freq.c -->
