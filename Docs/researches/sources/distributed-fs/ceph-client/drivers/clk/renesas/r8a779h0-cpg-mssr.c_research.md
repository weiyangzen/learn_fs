<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a779h0-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a779h0-cpg-mssr.c

## Purpose
`r8a779h0-cpg-mssr.c` describes the R-Car V4M Gen4 CPG/MSSR clock topology. It provides EXTAL/EXTALR, PLL1-PLL6 roots, C0-C3 Z clocks, S0 domain splits, IMP/VIO/VC source and bus clocks, SD0, RPC, CANFD/CSI/DSI/MSO, and module gates for ISP, AVB/RGMII, CSI, display, VSP/FCP, serial, I2C, VIN, timers, PFC, audio, and watchdog-related modules.

## Important APIs, Types, and Functions
Important definitions include `r8a779h0_core_clks[]`, `r8a779h0_mod_clks[]`, `CPG_PLL_CONFIG_INDEX()`, `cpg_pll_configs[]`, `r8a779h0_cpg_mssr_init()`, and `r8a779h0_cpg_mssr_info`. It uses Gen4 PLL helpers, domain fixed-factor definitions, Gen4 SD/RPC/OSC/MDSEL helpers, and `CLK_REG_LAYOUT_RCAR_GEN4`. Like `r8a779g0`, it has no explicit critical module clock array.

## Control Flow, State, and Persistence
Init reads MD14/MD13 mode pins, indexes a four-entry PLL table, rejects the prohibited row, and initializes Gen4 CPG state using `CLK_EXTALR`. The module table declares a `30 * 32` hardware module space and includes high-numbered audio modules. Runtime state is held in common-clock registrations and Gen4 CPG/MSSR hardware registers; nothing is persisted across reboot.

## Dependencies and Integration Points
Dependencies are `dt-bindings/clock/r8a779h0-cpg-mssr.h`, `rcar-gen4-cpg.h`, `renesas-cpg-mssr.h`, and reset-mode-pin support. It integrates through `CONFIG_CLK_R8A779H0` and `"renesas,r8a779h0-cpg-mssr"`. Consumers include ISP, AVB/RGMII, CANFD, CSI4, display/DSI, FCP/VSP, HSCIF/SCIF, I2C, MSIOF, SDHI0, VIN, TMU/CMT, PFC, TSC, RPC, SSI/SSIU, IMP/VIO/VC blocks, and watchdog.

## Risks and Test Signals
Risks include V4M-specific IMP/VIO/VC clock routing, high module IDs, missing critical-clock protections, and close-but-not-identical V4H clock names. Test V4M boot, clk summary for ZC/S0/IMP/VIO/VC domains, SDHI/RPC/CSI/VIN/display/AVB/audio/serial/I2C probing, runtime PM, suspend/resume, and watchdog/interrupt stability during unused-clock pruning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a779h0-cpg-mssr.c -->
