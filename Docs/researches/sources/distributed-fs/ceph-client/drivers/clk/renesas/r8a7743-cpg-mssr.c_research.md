# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7743-cpg-mssr.c

Purpose: This RZ/G1M and RZ/G1N (`r8a7743`/`r8a7744`) data file supplies Gen2 CPG-MSSR clock and module tables.

Important APIs, types, and functions: It defines mutable `r8a7743_core_clks`, `r8a7743_mod_clks`, `r8a7743_crit_mod_clks`, PLL config table, `r8a7743_cpg_mssr_init()`, and exported `r8a7743_cpg_mssr_info`.

Control flow: The generic CPG-MSSR core invokes `.init`. The callback reads mode pins, selects the Gen2 PLL config, and if the DT node is `renesas,r8a7744-cpg-mssr`, adjusts the ZG divider from the default to 1/5 before calling `rcar_gen2_cpg_init()`.

State and persistence: The core clock table is intentionally mutable for the RZ/G1N variant adjustment. Runtime register state is managed by the generic CPG-MSSR and Gen2 CPG libraries. Critical module clocks protect RWDT and INTC-SYS.

Dependencies and integration: Depends on OF compatibility checks, `rcar-rst`, `renesas-cpg-mssr.h`, `rcar-gen2-cpg.h`, and `r8a7743-cpg-mssr.h`. The module table spans timers, serial, USB, display, VIN, Ethernet, storage, GPIO, CAN, audio, and DMA.

Risks: Static table mutation for RZ/G1N must occur before generic registration. Module IDs are numerous and easy to misalign. `num_hw_mod_clks = 12 * 32` assumes the Gen2 MSSR register bank size.

Test signals: Boot both R8A7743 and R8A7744 compatibles, verify ZG divider difference, check critical clocks, run peripheral clock enable tests, and compare core rates to mode-pin tables.
