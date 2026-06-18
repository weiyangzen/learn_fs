# sources/distributed-fs/ceph-client/drivers/clk/renesas/r7s9210-cpg-mssr.c

Purpose: This file describes the RZ/A2 (`r7s9210`) CPG/MSSR clock topology, including early timer clocks, core clocks, module clocks, and custom RZ/A2 clock registration.

Important APIs, types, and functions: It defines `r7s9210_early_core_clks`, `r7s9210_early_mod_clks`, `r7s9210_core_clks`, `r7s9210_mod_clks`, `r7s9210_update_clk_table()`, `rza2_cpg_clk_register()`, `r7s9210_cpg_mssr_info`, and `r7s9210_cpg_mssr_early_init()`.

Control flow: `CLK_OF_DECLARE_DRIVER()` calls `cpg_mssr_early_init()` for `renesas,r7s9210-cpg-mssr`, allowing early OSTM clocks. The CPG-MSSR core later consumes `r7s9210_cpg_mssr_info`. Custom registration updates divider tables from `CPG_FRQCR` and extal rate, then registers main/PLL fixed-factor clocks.

State and persistence: Init-only `cpg_mode` and mutable `r7s9210_core_clks` divider fields reflect EXTAL/FRQCR hardware state. Module clock state is handled by the generic MSSR core using RZ/A standby register layout.

Dependencies and integration: Depends on `renesas-cpg-mssr.h`, DT bindings, CCF, and generic CPG-MSSR infrastructure. Early module clocks support timers before the full driver is ready.

Risks: Illegal FRQCR values trigger `BUG_ON(1)`. Divider tables are mutated at init, so they must not be treated as const. EXTAL > 12 MHz is used as a mode heuristic. `num_hw_mod_clks` includes nonexistent STBCR0 intentionally.

Test signals: Boot RZ/A2, verify early OSTM clocks, compare FRQCR-derived I/G/B/P rates, check module clock gating for SCIF/USB/Ethernet/SDHI, and compile-test `CLK_R7S9210`.
