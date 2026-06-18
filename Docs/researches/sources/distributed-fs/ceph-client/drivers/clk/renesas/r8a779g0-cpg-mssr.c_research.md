<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a779g0-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a779g0-cpg-mssr.c

## Purpose
`r8a779g0-cpg-mssr.c` is the R-Car V4H Gen4 CPG/MSSR clock description. It exposes a rich Gen4 clock tree with PLL1-PLL6 roots, S0 domain splits for VIO/VC/HSC/MM/RT/PER/CC, SV VIP/IR clocks, VIO/VC buses, CANFD/CSI/DSI/SD/MSO/RPC clocks, and module gates for ISP, AVB/TSN, CSI, display, VSP/FCP, serial, I2C, VIN, PFC, audio, and timers.

## Important APIs, Types, and Functions
Important objects are `r8a779g0_core_clks[]`, `r8a779g0_mod_clks[]`, `CPG_PLL_CONFIG_INDEX()`, `cpg_pll_configs[]`, `r8a779g0_cpg_mssr_init()`, and `r8a779g0_cpg_mssr_info`. It uses `rcar-gen4-cpg.h`, Gen4 PLL/Z/SD/RPC/OSC/MDSEL helpers, domain-specific fixed factors, and sets `.reg_layout = CLK_REG_LAYOUT_RCAR_GEN4`. No critical module array is defined in this file.

## Control Flow, State, and Persistence
Init reads mode pins, indexes the four-entry Gen4 PLL table, rejects prohibited `extal_div == 0` mode, and calls `rcar_gen4_cpg_init(cpg_pll_config, CLK_EXTALR, cpg_mode)`. The exported info advertises `30 * 32` hardware module clocks. Runtime state is the common clock graph and Gen4 CPG/MSSR hardware state; the file does not store persistent software data.

## Dependencies and Integration Points
Dependencies include `dt-bindings/clock/r8a779g0-cpg-mssr.h`, Gen4 CPG support, common CPG/MSSR infrastructure, and reset-mode-pin reads. It matches via `CONFIG_CLK_R8A779G0` and `"renesas,r8a779g0-cpg-mssr"`. Consumers include ISP, AVB0-2, TSN, CANFD, CSI4, display/DSI, FCP/VSP, VIN00-17, HSCIF/SCIF, I2C, MSIOF, SDHI0, TMU/CMT, PFC, TSC, RPC, SSI/SSIU, and watchdog modules.

## Risks and Test Signals
Risks include the large domain-split clock tree, absent critical-clock annotations, high module IDs such as TSN/SSI, and close similarity to V4M/V4H derivatives. Test V4H boot, clk summary validation for VIO/VC/HSC/PER/MM domains, VIN/CSI/display/ISP/AVB/TSN/SDHI/RPC/audio probing, and suspend/runtime PM with careful watchdog and interrupt monitoring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a779g0-cpg-mssr.c -->
