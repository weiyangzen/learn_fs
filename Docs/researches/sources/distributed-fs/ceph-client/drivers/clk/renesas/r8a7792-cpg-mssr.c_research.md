<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7792-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7792-cpg-mssr.c

## Purpose
`r8a7792-cpg-mssr.c` is the R-Car V2H Gen2 CPG/MSSR data file. It defines a smaller Gen2 clock tree focused on imaging/video use cases, with PLL roots, QSPI, `z/zg/zx/zs`, bus clocks, SD/RCAN/R/OSC clocks, and a module table for video, display, capture, serial, storage, GPIO, I2C, CAN, audio, timers, and DMA.

## Important APIs, Types, and Functions
The key objects are `r8a7792_core_clks[]`, `r8a7792_mod_clks[]`, `r8a7792_crit_mod_clks[]`, `CPG_PLL_CONFIG_INDEX()`, `cpg_pll_configs[]`, `r8a7792_cpg_mssr_init()`, and `r8a7792_cpg_mssr_info`. It uses the Gen2 helper stack via `rcar-gen2-cpg.h` and `rcar_gen2_cpg_clk_register`, with `DEF_BASE` entries for Gen2 PLLs/QSPI/RCAN and fixed-factor definitions for bus/media clocks.

## Control Flow, State, and Persistence
The init path reads CPG mode pins, derives the PLL config from MD14/MD13, selects one of four `rcar_gen2_cpg_pll_config` rows, and calls `rcar_gen2_cpg_init(cpg_pll_config, 2, cpg_mode)`. The shared CPG/MSSR code consumes `num_hw_mod_clks = 12 * 32` and the module list to operate stop/reset bits. There is no persistent state beyond registered clocks and programmed hardware registers.

## Dependencies and Integration Points
Dependencies are the `r8a7792` clock binding, the common CPG/MSSR framework, Gen2 CPG helper code, and reset-mode-pin access. Integration is through `CONFIG_CLK_R8A7792` and the `"renesas,r8a7792-cpg-mssr"` compatible. Notable consumers include JPU, VSP, DU, VIN, PCIe, USB, SDHI, QSPI, I2C, GPIO, CAN, SSI/SCU, serial/MSIOF, timers, watchdog, and interrupt controller clocks.

## Risks and Test Signals
Risks include overgeneralizing from other Gen2 SoCs, because V2H has fewer SD/audio/display modules and different PLL mode indexing. Wrong gate IDs can leave camera/display blocks unclocked. Tests should cover V2H boot, clk summary rate validation, video capture/display pipelines, SDHI/QSPI/USB/PCIe, CAN/I2C/GPIO, audio if present, and preservation of RWDT/INTC-SYS critical gates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7792-cpg-mssr.c -->
