# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7742-cpg-mssr.c

Purpose: This RZ/G1H (`r8a7742`) data file describes Gen2 CPG core clocks, module standby clocks, critical module clocks, and PLL initialization for the generic Renesas CPG-MSSR driver.

Important APIs, types, and functions: It defines clock IDs, `r8a7742_core_clks`, `r8a7742_mod_clks`, `r8a7742_crit_mod_clks`, PLL config table `cpg_pll_configs`, `r8a7742_cpg_mssr_init()`, and exported `r8a7742_cpg_mssr_info`.

Control flow: The central CPG-MSSR driver selects this `cpg_mssr_info` for the matching compatible. Its `.init` callback reads mode pins with `rcar_rst_read_mode_pins()`, selects a PLL config using bits 14/13/19, and calls `rcar_gen2_cpg_init()`. The generic core registers listed core and module clocks.

State and persistence: All live clock state is held by generic CPG-MSSR and Gen2 CPG code. This file provides const init tables. Critical module clocks keep RWDT and INTC-SYS enabled.

Dependencies and integration: Depends on `renesas-cpg-mssr.h`, `rcar-gen2-cpg.h`, `rcar-rst`, and `r8a7742-cpg-mssr.h`. Module clocks cover display, video, USB, storage, serial, audio, GPIO, CAN, Ethernet, and DMA blocks.

Risks: Large module tables are offset-sensitive; a wrong module ID gates the wrong hardware. PLL config index must match MODEMR encoding. Critical clock omissions can break watchdog or interrupt controller operation.

Test signals: Boot RZ/G1H, compare PLL/core rates with mode pins, verify RWDT and INTC-SYS stay enabled, exercise representative module clocks such as SDHI, USB, VIN, DU, SCIF, and Ethernet.
