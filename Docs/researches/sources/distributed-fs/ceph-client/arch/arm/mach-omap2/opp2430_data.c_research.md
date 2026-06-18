# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/opp2430_data.c

## Purpose
`opp2430_data.c` provides deprecated OMAP2430 PRCM rate tables for the old OMAP2xxx clock path. It captures ratio configurations for 2430, including differences from 2420 such as no phase synchronizers and a different IVA/modem domain layout.

## Important APIs, Types, and Functions
The exported object is `const struct prcm_config omap2430_rate_table[]`. Rows use `R1`, `R2`, `M4`, `M5A`, `M5B`, and boot-bypass macros from `opp2xxx.h`, plus SDRC refresh constants and `RATE_IN_243X`.

## Control Flow
The clock layer selects an entry based on oscillator and desired/available rate, assuming the table is sorted fastest to slowest. Rows include fast and slow variants and bypass fallbacks.

## State and Persistence Behavior
Only immutable configuration data lives here. Runtime state exists in PRCM register programming, SDRC settings, and the selected current PRCM set tracked by clock code.

## Dependencies and Integration Points
It depends on `opp2xxx.h`, `sdrc.h`, and `clock.h`. It integrates with OMAP2430 clock init and any platform code relying on old-style OPP/rate selection.

## Risks
The table lacks voltage data and 19.2 MHz sys_clk sets. Incorrect ratios can affect MPU, DSP/IVA, GFX, L3/L4, USB, modem, and SDRC timing. Adding rows without preserving sort order can select an unintended slower or unstable operating point.

## Test Signals
Build and boot OMAP2430 targets with supported oscillators. Confirm MPU/DPLL rates, modem divider programming, SDRC refresh timing, and low-power bypass behavior. Stress memory and peripherals after rate selection.
