# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a77470-cpg-mssr.c

Purpose: This RZ/G1C (`r8a77470`) data file supplies Gen2 CPG core clocks, module standby clocks, critical module IDs, and mode-pin PLL setup for the generic CPG-MSSR framework.

Important APIs, types, and functions: It defines `r8a77470_core_clks`, `r8a77470_mod_clks`, `r8a77470_crit_mod_clks`, `cpg_pll_configs`, `r8a77470_cpg_mssr_init()`, and exported `r8a77470_cpg_mssr_info`.

Control flow: The central CPG-MSSR driver selects this info object. The `.init` callback reads mode pins, indexes PLL configuration from bits 14/13, and calls `rcar_gen2_cpg_init(cpg_pll_config, 2, cpg_mode)`. Core and module clock registration is then performed by generic code.

State and persistence: Tables are const init data. Runtime module-stop, reset, and core clock state are owned by the generic CPG-MSSR and Gen2 CPG layers. Critical module clocks protect RWDT and INTC-SYS.

Dependencies and integration: Depends on `renesas-cpg-mssr.h`, `rcar-gen2-cpg.h`, `rcar-rst`, and `r8a77470-cpg-mssr.h`. The module table covers G1C-specific USB channel naming, SDHI, display, serial, Ethernet, GPIO, CAN, QSPI, I2C, and audio blocks.

Risks: PLL config index 2 is explicitly invalid/prohibited in the table; if hardware straps select it, the resulting zeroed config would be dangerous unless generic code rejects it. Module IDs are sparse and hardware-specific. Critical clock protection is minimal but essential.

Test signals: Boot RZ/G1C with valid mode pins, verify Gen2 PLL rates, confirm USB/SDHI/SCIF/Ethernet module clocks, check critical RWDT/INTC-SYS behavior, and compile-test `CLK_R8A77470`.
