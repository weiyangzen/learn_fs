<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7790-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7790-cpg-mssr.c

## Purpose
`r8a7790-cpg-mssr.c` is the R-Car H2 Gen2 CPG/MSSR clock description. It exposes legacy Gen2 external inputs (`extal`, `usb_extal`), PLL0/PLL1/PLL3 roots, fixed CPU/bus/media clocks, SD/MMC/SSP/QSPI/RCAN clocks, and module gates for the large H2 multimedia and peripheral surface.

## Important APIs, Types, and Functions
Important symbols include `r8a7790_core_clks[]`, `r8a7790_mod_clks[]`, `r8a7790_crit_mod_clks[]`, `CPG_PLL_CONFIG_INDEX()`, `cpg_pll_configs[]`, `r8a7790_cpg_mssr_init()`, and `r8a7790_cpg_mssr_info`. The file uses Gen2 helpers and types such as `CLK_TYPE_GEN2_MAIN`, `CLK_TYPE_GEN2_PLL0`, `CLK_TYPE_GEN2_ADSP`, `CLK_TYPE_GEN2_SD*`, `CLK_TYPE_GEN2_QSPI`, `CLK_TYPE_GEN2_RCAN`, and `rcar_gen2_cpg_clk_register`.

## Control Flow, State, and Persistence
The init function reads mode pins, computes a three-bit PLL table index from MD14/MD13/MD19, selects one of eight `rcar_gen2_cpg_pll_config` entries, and calls `rcar_gen2_cpg_init(cpg_pll_config, 2, cpg_mode)`. The `2` argument reflects the Gen2 PLL0/PLL1 VCO division model used by this SoC. Module gates are declared for 12 banks. Runtime state is limited to CCF registration and hardware gate/rate registers.

## Dependencies and Integration Points
The file depends on `dt-bindings/clock/r8a7790-cpg-mssr.h`, `renesas-cpg-mssr.h`, `rcar-gen2-cpg.h`, and `rcar-rst.h`. It is matched through `"renesas,r8a7790-cpg-mssr"` in `renesas-cpg-mssr.c` and built by `CONFIG_CLK_R8A7790`. Consumers include VIN/VSP/FDP/DU, USB, Ethernet, QSPI, SDHI/MMCIF, serial/MSIOF, audio SSI/SCU, CAN, I2C, GPIO, timers, DMAC, and interrupt/watchdog infrastructure.

## Risks and Test Signals
Risks include legacy Gen2 rate-table mistakes, the PLL VCO/2 distinction, `usb_extal`/RCAN parent mismatches, and missing gates for H2-only multimedia units. RWDT (`402`) and INTC-SYS/GIC (`408`) are critical. Test signals are H2 DT boot, expected PLL and fixed-clock rates, working SDHI/MMC/QSPI/USB/Ethernet/display/video/audio, and no regressions with runtime PM or unused-clock disabling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7790-cpg-mssr.c -->
