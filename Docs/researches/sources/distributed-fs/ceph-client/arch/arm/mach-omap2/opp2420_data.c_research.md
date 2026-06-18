# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/opp2420_data.c

## Purpose
`opp2420_data.c` provides deprecated OMAP2420 PRCM rate tables for legacy clock code. Each table row describes a validated combination of crystal rate, DPLL rate, MPU rate, clock divider register values, SDRC refresh setting, and availability flags.

## Important APIs, Types, and Functions
The exported data is `const struct prcm_config omap2420_rate_table[]`. It uses macros from `opp2xxx.h`, SDRC refresh constants from `sdrc.h`, and `RATE_IN_242X` from clock code.

## Control Flow
No function executes locally. OMAP2 clock initialization scans the sorted table from fastest to slowest and chooses an applicable PRCM set based on SoC, oscillator, and supported flags. Boot-bypass rows provide low-rate fallback.

## State and Persistence Behavior
The file holds immutable clock configuration data. Runtime state is external, notably `rate_table`, `curr_prcm_set`, PRCM registers, and SDRC refresh timing programmed by clock code.

## Dependencies and Integration Points
It depends on `opp2xxx.h`, `sdrc.h`, and `clock.h`. It integrates with OMAP2420 clock rate selection, SDRAM controller refresh programming, and platform support for H4/Nokia-era boards.

## Risks
The format is deprecated and missing voltage data and 19.2 MHz sets. A wrong divider or SDRC refresh value can cause immediate instability, memory corruption, or failed frequency changes. Table order matters because fastest entries are preferred.

## Test Signals
Build OMAP2420 support and boot with 12/13 MHz oscillators. Verify selected MPU/DPLL rates, SDRC refresh values, and stable operation under clock changes if enabled. Look for boot regressions on N800/N810-class configurations due to missing 19.2 MHz handling.
