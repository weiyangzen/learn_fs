<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/sram.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/sram.S

## Purpose
Provides the OMAP1 SRAM-resident clock reprogramming routine that safely updates DPLL_CTL and ARM_CKCTL while executing from internal SRAM.

## Important APIs, Types, and Functions
Exports `omap1_sram_reprogram_clock` and size symbol `omap1_sram_reprogram_clock_sz`.

## Control Flow
The routine saves registers, computes virtual addresses for DPLL_CTL and ARM_CKCTL, optionally clears the DPLL lock bit to enter bypass, writes CKCTL and DPLL values, delays for settling, polls lock when requested, then restores registers and returns.

## State and Persistence Behavior
No software state beyond registers and stack. Hardware state is DPLL and clock-control register programming.

## Dependencies and Integration Points
Copied and called by `sram-init.c`; depends on OMAP1 IO address macros and register constants.

## Risks
Clock reprogramming from normal memory could fail while clocks/memory are unstable, hence SRAM execution. Incorrect argument order, lock polling, or address constants can hang the CPU.

## Test Signals
Compare copied size against symbol, call through `omap_sram_reprogram_clock()` for known safe rate transitions, and verify DPLL lock and timer/serial continuity after changes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/sram.S -->
