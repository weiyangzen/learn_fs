<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/s5pv210-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/s5pv210-cpufreq.c

## Purpose

Provides Samsung S5PC110/S5PV210 cpufreq by directly programming clock-controller and DMC memory-controller registers, regulators, and reboot/suspend-safe frequency behavior.

## APIs, Types, And Functions

Static tables describe five performance levels, per-level DVS voltages, and clock divider values. `s5pv210_set_refresh()` recomputes DMC refresh counters. `s5pv210_target()` is the central transition sequence. `check_mem_type()` restricts support to LPDDR/LPDDR2. Probe maps clock/DMC registers, gets regulators, and registers cpufreq.

## Control Flow

Probe obtains `vddarm`/`vddint`, maps the `samsung,s5pv210-clock` node and two DMC nodes, registers a reboot notifier, and registers cpufreq. Policy init gets `armclk`, DMC clocks, validates CPU0 and memory type, snapshots original DMC refresh values/rates, sets `suspend_freq`, and installs the table. Targeting serializes with `set_freq_lock`, rejects access after reboot lockout, raises voltages for upscaling, adjusts temporary DRAM refresh for bus changes, switches MFC/G3D and MSYS muxes around APLL changes, rewrites dividers and APLL PMS values, restores refresh counters, then lowers voltages for downscaling.

## State And Persistence

Global mapped bases, DMC clocks, regulators, DRAM refresh snapshots, mutex, and `no_cpufreq_access` persist for the built-in platform driver lifetime. Hardware state persists in PLL, mux, divider, MCS, ONEDRAM, DMC refresh, and regulator registers. Reboot notifier drives the CPU to 800 MHz and disables later access.

## Dependencies And Integration Points

Depends on OF node mapping, Samsung clock/DMC register layout, regulators, common clock lookup, reboot notifier, cpufreq generic suspend, and CPU0-only policy assumptions.

## Risks And Test Signals

This is high-risk sequencing: direct MMIO polling loops have no timeout, memory refresh changes must be correct, and only LPDDR/LPDDR2 are supported. Probe lacks a remove path because it is a built-in platform driver. Test signals include register mapping, DMC aliases, memory type, refresh counter readback, PLL lock/mux status completion, regulator changes, reboot transition to `SLEEP_FREQ`, and memory stability across L0/L4 transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/s5pv210-cpufreq.c -->
