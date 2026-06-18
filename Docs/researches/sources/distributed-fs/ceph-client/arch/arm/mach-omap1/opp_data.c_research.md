<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/opp_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/opp_data.c

## Purpose
Provides the static OMAP1 MPU clock rate table used by legacy clock/cpufreq code to program DPLL and divider registers for supported SoCs and crystals.

## Important APIs, Types, and Functions
Defines `omap1_rate_table[]`, a sentinel-terminated array of `struct mpu_rate` entries.

## Control Flow
No active control flow in this file. Consumers scan entries by SoC flag and crystal rate, then program `CKCTL` and `DPLL_CTL` with the selected values.

## State and Persistence Behavior
Read-only data persists in kernel memory. Hardware state changes happen in clock code that uses the table.

## Dependencies and Integration Points
Depends on `clock.h` flag definitions and `opp.h` structure layout.

## Risks
The table encodes hardware timing policy. Incorrect flag coverage or divider values can overclock/underclock subsystems, break SDRAM timing assumptions, or select unsupported rates for a board crystal.

## Test Signals
For each supported crystal and SoC class, verify table lookup selects expected MPU/DPLL rates and that clock reprogramming keeps timers, serial, and memory stable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/opp_data.c -->
