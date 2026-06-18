<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a779f0-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a779f0-cpg-mssr.c

## Purpose
`r8a779f0-cpg-mssr.c` describes the R-Car S4-8 Gen4 CPG/MSSR clock tree. It provides EXTAL/EXTALR, PLL1/2/3/5/6 roots, S0 and segmented MM/RT/PER/HSC/CC fixed factors, SD0, RPC, MSO, R/OSC, and module gates for serial, I2C, MSIOF, PCIe, SDHI, timers, watchdog, PFC, Ethernet switch/SerDes, and UFS.

## Important APIs, Types, and Functions
Key definitions are `r8a779f0_core_clks[]`, `r8a779f0_mod_clks[]`, `r8a779f0_crit_mod_clks[]`, `CPG_PLL_CONFIG_INDEX()`, `cpg_pll_configs[]`, `r8a779f0_cpg_mssr_init()`, and `r8a779f0_cpg_mssr_info`. It uses Gen4 fixed PLL helper macros such as `DEF_GEN4_PLL_F9_24` and `DEF_GEN4_PLL_V9_24`, Gen4 SD/RPC/OSC/MDSEL helpers, and `CLK_REG_LAYOUT_RCAR_GEN4`.

## Control Flow, State, and Persistence
The init function reads mode pins, indexes the four-entry PLL table from MD14/MD13, rejects the prohibited row where `extal_div` is zero, and calls `rcar_gen4_cpg_init()`. The module table covers `28 * 32` hardware module clocks, reflecting high-numbered S4-8 module IDs. State is declarative CCF registration and hardware gate/divider state.

## Dependencies and Integration Points
Dependencies are `dt-bindings/clock/r8a779f0-cpg-mssr.h`, Gen4 CPG support, the common CPG/MSSR core, and reset-mode-pin reading. It integrates through `CONFIG_CLK_R8A779F0` and `"renesas,r8a779f0-cpg-mssr"`. Consumers include HSCIF/SCIF, I2C, MSIOF, PCIe, SDHI0, system DMAC, TMU/CMT, PFC, TSC, R-Switch2, Ethernet SerDes, UFS, watchdog, and RPC.

## Risks and Test Signals
Risks include wrong domain-specific S0 divisor parentage, high module-bank sizing, prohibited mode handling, and rates for Ethernet/UFS/PCIe clocks. Test S4-8 boot, `clk_summary` for S0* domain clocks and RPC/SD/MSO, probe PCIe/UFS/Ethernet switch/serial/I2C/SDHI, verify RWDT critical module `907`, and exercise suspend/runtime PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a779f0-cpg-mssr.c -->
