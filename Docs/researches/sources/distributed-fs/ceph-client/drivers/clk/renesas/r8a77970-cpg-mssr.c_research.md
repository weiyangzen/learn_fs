<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a77970-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a77970-cpg-mssr.c

## Purpose
`r8a77970-cpg-mssr.c` describes the R-Car V3M Gen3 CPG/MSSR clock tree. It is a smaller Gen3 provider with PLL0/PLL1/PLL3 roots, Z2/ZTR/ZT/ZX and S1/S2 clocks, one SDHI channel, RPC/RPCD2, CANFD/MSO/CSI dividers, and a V3M-oriented module gate map.

## Important APIs, Types, and Functions
Important objects include `r8a77970_core_clks[]`, `r8a77970_mod_clks[]`, `r8a77970_crit_mod_clks[]`, `cpg_pll_configs[]`, `r8a77970_cpg_mssr_init()`, custom `r8a77970_cpg_clk_register()`, and `r8a77970_cpg_mssr_info`. This file defines V3M-specific SD clock types handled by a custom registrar before delegating other clocks to `rcar_gen3_cpg_clk_register`.

## Control Flow, State, and Persistence
Init reads mode pins, indexes a four-entry PLL config table from MD14/MD13, and calls `rcar_gen3_cpg_init()`. During clock registration, `r8a77970_cpg_clk_register()` intercepts `CLK_TYPE_R8A77970_SD0H` and `CLK_TYPE_R8A77970_SD0`, picks divider tables and shifts, and registers divider-table clocks at `CPG_SD0CKCR`; all other core clocks use the generic Gen3 registrar. State is framework registration and hardware register values only.

## Dependencies and Integration Points
The file depends on `dt-bindings/clock/r8a77970-cpg-mssr.h`, Gen3 CPG helpers, the common CPG/MSSR framework, reset-mode-pin support, and common clock divider APIs. It integrates through `CONFIG_CLK_R8A77970` and `"renesas,r8a77970-cpg-mssr"`. Consumers include timers, serial/MSIOF, SYS-DMAC, SDHI0, USB, FDP/VSP/VIN, Ethernet AVB, GPIO, CANFD, RPC-IF, I2C, RWDT, and INTC-AP.

## Risks and Test Signals
The custom SD divider path is the main risk: wrong shift/table/parent handling can break SDHI0 rates. The smaller module set also makes copy-paste from larger Gen3 SoCs risky. Test V3M boot, SDHI0 frequency changes, RPC/CAN/Ethernet/USB/video capture paths, clk summary parent/rate checks, and critical RWDT/GIC preservation during clock pruning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a77970-cpg-mssr.c -->
