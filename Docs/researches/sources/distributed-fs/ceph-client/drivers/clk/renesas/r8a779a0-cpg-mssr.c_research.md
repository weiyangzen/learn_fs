<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a779a0-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a779a0-cpg-mssr.c

## Purpose
`r8a779a0-cpg-mssr.c` is the R-Car V3U Gen4 CPG/MSSR clock provider. It defines Gen4 PLL-derived roots, Z0/Z1/ZG CPU/GPU clocks, S1/S3 divisions, SD0, RPC, CANFD/CSI/DSI/MSO dividers, OCO/R selection, and module gates for high-bandwidth video, ISP, Ethernet AVB, display, CSI, VIN, and peripheral blocks.

## Important APIs, Types, and Functions
Important symbols are `r8a779a0_core_clks[]`, `r8a779a0_mod_clks[]`, `r8a779a0_crit_mod_clks[]`, `CPG_PLL_CONFIG_INDEX()`, `cpg_pll_configs[]`, `r8a779a0_cpg_mssr_init()`, and `r8a779a0_cpg_mssr_info`. It uses Gen4 helpers from `rcar-gen4-cpg.h`, including Gen4 PLL/Z/SD/RPC/OSC/MDSEL support, and marks `.reg_layout = CLK_REG_LAYOUT_RCAR_GEN4`.

## Control Flow, State, and Persistence
Init reads MD14/MD13 mode pins, indexes a four-entry Gen4 PLL table, and calls `rcar_gen4_cpg_init(cpg_pll_config, CLK_EXTALR, cpg_mode)`. The table contains a prohibited row but this init path does not perform the explicit `extal_div` rejection used by later Gen4 files. The module table spans `15 * 32` hardware module clocks. State is common-clock registration plus Gen4 CPG/MSSR hardware registers.

## Dependencies and Integration Points
Dependencies include `dt-bindings/clock/r8a779a0-cpg-mssr.h`, `rcar-gen4-cpg.h`, `renesas-cpg-mssr.h`, reset-mode-pin support, and common clock infrastructure. It matches through `CONFIG_CLK_R8A779A0` and `"renesas,r8a779a0-cpg-mssr"`. Consumers include ISP/ISPCS, AVB0-5, CANFD, CSI4, DU/DSI, FCP/VSP, VIN00-37, SDHI0, HSCIF/SCIF, I2C, MSIOF/MSI, TMU/TPU, RPC-IF, PFC, and watchdog.

## Risks and Test Signals
Risks include Gen4 register-layout mismatches, unvalidated prohibited strap handling, large VIN/ISP module coverage errors, and wrong PLL20/21/30/31/ZG parentage. Test V3U boot, clk summary rates for Z/S/SD/RPC/DSI/CANFD/CSI, ISP/VIN/display/AVB/SDHI/RPC probing, watchdog critical gate behavior (`907`), and suspend/runtime PM with Gen4 layout operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a779a0-cpg-mssr.c -->
