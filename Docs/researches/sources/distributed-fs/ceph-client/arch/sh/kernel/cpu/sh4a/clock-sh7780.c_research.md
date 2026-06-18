# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7780.c

## Purpose
`clock-sh7780.c` implements SH7780 clock ops and registers an additional SHYWAY on-chip clock.

## Important APIs, Types, And Functions
Important objects are IFC/BFC/PFC/CFC divisor tables, master/module/bus/CPU callbacks, `arch_init_clk_ops()`, `shyway_clk_recalc()`, `sh7780_shyway_clk`, `lookups`, and `arch_clk_init()`.

## Control Flow
Legacy ops decode `FRQCR` fields for core clocks. `arch_clk_init()` registers the SHYWAY clock and lookup after the common clock setup path.

## State And Persistence
State consists of calculated `struct clk` rates and hardware `FRQCR`; no software persistence exists.

## Dependencies And Integration Points
It is selected for SH7780 and feeds clock rates to the SH7780 platform setup and any driver requesting `shyway_clk`.

## Risks
SH7780 has distinct CFC/SHYWAY ratios; using generic SH4A assumptions can break bus/interconnect timing. Like SH7763, it lacks full MSTP mapping.

## Test Signals
Clock rate dumps, timer/serial accuracy, and successful SHYWAY lookup registration validate behavior.
