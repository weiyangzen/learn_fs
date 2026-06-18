# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/opp2xxx.h

## Purpose
`opp2xxx.h` defines the deprecated OMAP2xxx PRCM configuration structure and the bitfield macros used by OMAP2420/2430 old-style OPP/rate tables. It is effectively a register-programming vocabulary for clock ratios, DPLL multipliers/dividers, and standard speed constants.

## Important APIs, Types, and Functions
The key type is `struct prcm_config`, with oscillator, DPLL, MPU speed, PRCM clock selector values, SDRC refresh base, and flags. Important declarations are `omap2420_rate_table[]`, conditional `omap2430_rate_table[]`, `rate_table`, and `curr_prcm_set`. Macros cover 2420 and 2430 ratio sets, boot-bypass modes, DPLL settings for 12/13/19.2 MHz references, PLL x1/x2 modes, and speed constants.

## Control Flow
The header contains no executable flow. Clock code consumes its structures/macros to select and program PRCM register sets from the SoC-specific tables.

## State and Persistence Behavior
No state is stored in the header. It declares external clock-selection state and defines constants that ultimately persist as hardware PRCM and SDRC register values.

## Dependencies and Integration Points
It integrates directly with `opp2420_data.c`, `opp2430_data.c`, and OMAP2xxx clock code. It also ties old OPP naming to PRCM hardware register layouts.

## Risks
This header is low-level and deprecated; edits can affect every OMAP2xxx rate table. Macro mistakes are hard to diagnose because symptoms can be unstable clocks, memory refresh failures, or peripheral timing issues.

## Test Signals
Build OMAP2420 and OMAP2430 configs. Validate all table rows that use changed macros by checking computed PRCM values, selected MPU/DPLL rates, and stable boot/peripheral operation.
