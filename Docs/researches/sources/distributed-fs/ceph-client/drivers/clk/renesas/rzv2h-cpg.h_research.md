# sources/distributed-fs/ceph-client/drivers/clk/renesas/rzv2h-cpg.h

## Purpose
Defines packed descriptors and SoC-info contracts for the RZ/V2H-family CPG backend. It captures PLL, dynamic divider, static mux, fixed module-status, module-clock, MSTOP, and reset metadata used by `rzv2h-cpg.c`.

## Important APIs, Types, and Functions
`struct pll` packs PLL offset, `has_clkn`, instance, and optional limits. `struct ddiv` packs divider offset, shift, width, monitor bit, and no-RMW flag. `struct smuxed` and `struct fixed_mod_conf` describe static muxes and status-capable fixed factors. `struct cpg_core_clk` uses these as a union. `struct rzv2h_mod_clk` records parent, critical/no-PM flags, ON and monitor indexes, MSTOP data, and external-clock mux index. `struct rzv2h_cpg_info` collects clocks, resets, and MSTOP capacity.

## Control Flow, State, and Persistence
The file is declarative. Macros build static SoC tables, and `BUS_MSTOP()` packs a register index plus bit mask for runtime reference counting.

## Dependencies, Integration Points, Risks, and Test Signals
It depends on bitfield/integer types and Renesas PLL limit structures. Risks are dense module ID mismatches, wrong ON indexes, and wrong MSTOP bits. Test all exported DT clock IDs, static mux/divider writes, reset xlate, critical clocks, and no-PM module filtering.
