# sources/distributed-fs/ceph-client/drivers/clk/renesas/renesas-cpg-mssr.h

## Purpose
Defines the common data model used by Renesas CPG/MSSR SoC clock-description files and the common backend. It captures core clock descriptors, module clock descriptors, register-layout variants, public runtime state shared with custom clock registration, and the top-level `cpg_mssr_info` contract consumed by `renesas-cpg-mssr.c`.

## Important APIs, Types, and Functions
`struct cpg_core_clk` describes input, fixed-factor, DIV6, fixed-rate, and custom core clocks. `struct cpg_mssr_pub` exposes MMIO bases, notifier chain, RMW lock, and clock array to custom clock registration code. `struct mssr_mod_clk` describes packed module clocks. `enum clk_reg_layout` selects Gen2/Gen3, RZ/A, Gen4, or RZ/T2H register maps. `struct cpg_mssr_info` collects early clocks, normal clocks, module clocks, critical IDs, PM core clocks, and callbacks.

## Control Flow, State, and Persistence
This header is declarative. Macros such as `DEF_INPUT`, `DEF_FIXED`, `DEF_DIV6P1`, `DEF_MOD`, and `DEF_MOD_STB` create static descriptors. Packing macros translate sparse hardware numbering into dense indexes used by the backend and DT provider.

## Dependencies, Integration Points, Risks, and Test Signals
It depends on Linux notifier and CCF divider-table types, exports many per-SoC `cpg_mssr_info` symbols, and declares `cpg_mssr_early_init()` plus `mssr_mod_nullify()`. Risks are descriptor/index mismatches and incorrect layout selection. Test via all SoC table builds, two-cell DT clock lookup, and boot logs free of unsupported clock type or invalid index errors.
