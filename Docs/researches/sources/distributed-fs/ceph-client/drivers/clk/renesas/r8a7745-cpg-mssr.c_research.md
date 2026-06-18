# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7745-cpg-mssr.c

Purpose: This file provides RZ/G1E (`r8a7745`) Gen2 CPG-MSSR tables and PLL initialization data.

Important APIs, types, and functions: It defines `r8a7745_core_clks`, `r8a7745_mod_clks`, `r8a7745_crit_mod_clks`, a four-entry effective PLL config table, `r8a7745_cpg_mssr_init()`, and `r8a7745_cpg_mssr_info`.

Control flow: The generic CPG-MSSR driver uses this info object for the matching SoC. The `.init` callback reads mode pins, selects a PLL config from bits 14/13, and calls `rcar_gen2_cpg_init(cpg_pll_config, 3, cpg_mode)`, reflecting PLL0 VCO/3 behavior for this SoC.

State and persistence: This source is mostly const init data. Runtime state is in generic CPG-MSSR registers and Gen2 CPG helpers. RWDT and INTC-SYS are listed as critical module clocks.

Dependencies and integration: Depends on Gen2 CPG helper code, CPG-MSSR core, `rcar-rst`, and `r8a7745-cpg-mssr.h`. Module entries cover the reduced RZ/G1E peripheral set.

Risks: PLL0 multiplier semantics differ from adjacent Gen2 files, so the `3` divider argument is important. Sparse module coverage must match silicon capabilities. Wrong critical clock IDs can destabilize watchdog or interrupt handling.

Test signals: Boot RZ/G1E, validate PLL0/PLL1/PLL3 rates from mode pins, verify SDHI/MMC, USB, serial, display, and Ethernet clocks, and confirm RWDT/INTC-SYS are protected from disable.
