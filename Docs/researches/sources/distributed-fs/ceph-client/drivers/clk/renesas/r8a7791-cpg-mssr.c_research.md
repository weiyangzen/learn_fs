<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7791-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7791-cpg-mssr.c

## Purpose
`r8a7791-cpg-mssr.c` defines the R-Car M2-W/M2-N Gen2 CPG/MSSR clock provider. It supplies Gen2 PLL/fixed-factor core clocks, SD/QSPI/RCAN clocks, and a module gate map for serial, display/video, audio, USB, Ethernet, CAN, I2C, GPIO, timers, and DMA blocks.

## Important APIs, Types, and Functions
Core definitions are in `r8a7791_core_clks[]`; module gates are in `r8a7791_mod_clks[]`; critical gates are in `r8a7791_crit_mod_clks[]`. Init data is selected by `CPG_PLL_CONFIG_INDEX()` and `cpg_pll_configs[]`, while `r8a7791_cpg_mssr_info` exports the tables and `rcar_gen2_cpg_clk_register`. This file also includes `<linux/of.h>` and uses `of_device_is_compatible()` for M2-N compatibility handling.

## Control Flow, State, and Persistence
Probe runs `r8a7791_cpg_mssr_init()`, reads mode pins, selects one of eight PLL configurations, and calls `rcar_gen2_cpg_init()`. The control flow includes device-tree compatible checks so the same data can serve the closely related `r8a7793` path registered by `renesas-cpg-mssr.c`. State is not persisted by the driver; it publishes CCF clocks and lets the common CPG/MSSR code operate hardware gates.

## Dependencies and Integration Points
Dependencies include the R-Car M2 binding header, `rcar-gen2-cpg.h`, `renesas-cpg-mssr.h`, OF matching, and reset-mode-pin reads. Build/match integration includes both `"renesas,r8a7791-cpg-mssr"` and `"renesas,r8a7793-cpg-mssr"` data references. Consumers include VCP/VPC/JPU/FDP/VSP/DU/VIN, SDHI/MMCIF, QSPI, USB, audio, I2C/IIC, CAN, Ethernet AVB, timers, serial, and GPIO.

## Risks and Test Signals
Risks are M2-W versus M2-N/R-Car M2 variant drift, Gen2 PLL table mistakes, and gate IDs that differ from H2/E2. Critical RWDT and INTC-SYS clocks must not be disabled. Test on both compatible variants where possible, compare clk summary rates with expected strap modes, probe SDHI/MMC/QSPI/display/video/audio/USB/Ethernet, and run unused-clock disable plus suspend/resume tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7791-cpg-mssr.c -->
