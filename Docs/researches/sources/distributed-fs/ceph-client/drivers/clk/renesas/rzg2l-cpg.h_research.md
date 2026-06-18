# sources/distributed-fs/ceph-client/drivers/clk/renesas/rzg2l-cpg.h

## Purpose
Defines RZ/G2L-family CPG descriptor formats and register encoding helpers. SoC-specific clock tables use this header to describe PLLs, dynamic dividers, muxes, SD muxes, DSI clocks, module gates, MSTOP associations, resets, critical resources, and PM exclusions.

## Important APIs, Types, and Functions
`struct cpg_core_clk` includes type, parent, factors, packed register config, status config, divider/mux tables, rate limits, and notifier hooks. `enum clk_types` covers SAM/G3S PLLs, dividers, muxes, SD muxes, SIPLL5, PLL5_4 mux, and DSI divider. `struct rzg2l_mod_clk` carries module ID, parent, CLK_ON offset/bit, MSTOP config, and coupled flag. `struct rzg2l_reset` maps reset bits to monitors. `struct rzg2l_cpg_info` is the full SoC contract.

## Control Flow, State, and Persistence
The header is declarative. Its macros pack offsets, shifts, widths, and status bits for `rzg2l-cpg.c`. `DEF_MOD`, `DEF_COUPLED`, `DEF_RST`, and `DEF_RST_MON` generate SoC tables.

## Dependencies, Integration Points, Risks, and Test Signals
It depends on notifier and CCF divider-table types and declares SoC info symbols plus notifier functions. Risks are compact descriptor packing errors, wrong MSTOP sharing, and reset monitor mismatches. Test build coverage, boot-time registration, SDHI/DSI rate changes, reset monitor behavior, and PM-domain filtering.
