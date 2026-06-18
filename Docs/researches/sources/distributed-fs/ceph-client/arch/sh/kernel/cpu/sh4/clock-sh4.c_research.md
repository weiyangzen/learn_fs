# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/clock-sh4.c

## Purpose
`clock-sh4.c` implements generic SH4 clock operations for non-SH4A processors by decoding `FRQCR`.

## Important APIs, Types, And Functions
It defines IFC/BFC/PFC divisor tables, four `sh4_*_clk_ops`, and `arch_init_clk_ops()`.

## Control Flow
Clock callbacks read `FRQCR` and use low three-bit fields for module, bus, and CPU divisors. `master_clk_init()` multiplies the input rate by the peripheral divisor. `arch_init_clk_ops()` returns the callback set by index.

## State And Persistence
The file is stateless aside from clock rate updates in `struct clk`; `FRQCR` is the hardware source of truth.

## Dependencies And Integration Points
It integrates with the SH clock framework and setup files for SH7750/SH7760-class non-SH4A CPUs. Timer and serial drivers rely on the derived rates.

## Risks
Generic SH4 ratios do not apply to SH4A, which is why the Makefile excludes this file under `CONFIG_CPU_SH4A`. Wrong selection breaks baud and timekeeping globally.

## Test Signals
Boot clock logs, stable timer calibration, and serial baud tests on SH7750/SH7760 hardware validate this file.
