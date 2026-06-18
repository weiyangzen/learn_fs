<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a77990-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a77990-cpg-mssr.c

## Purpose
`r8a77990-cpg-mssr.c` describes the R-Car E3 Gen3 CPG/MSSR clock provider. It exposes a compact PLL0/PLL1/PLL3-based tree with PE/S clocks, ZA/Z2/ZT/ZX outputs, SD0/SD1/SD3, RPC/RPCD2, CANFD/CSI/MSO, and a module gate table for E3's display, video, communication, storage, and audio blocks.

## Important APIs, Types, and Functions
Important definitions include `r8a77990_core_clks[]`, `r8a77990_mod_clks[]`, `r8a77990_crit_mod_clks[]`, `CPG_PLL_CONFIG_INDEX()`, `cpg_pll_configs[]`, `r8a77990_cpg_mssr_init()`, and `r8a77990_cpg_mssr_info`. It uses Gen3 helpers but follows the E3-style clock shape with PLL0 divider aliases, `CLK_TYPE_GEN3_PE`, and DT-visible clocks through `R8A77990_CLK_CPEX`.

## Control Flow, State, and Persistence
Probe through the common driver calls init, which reads mode pins, indexes the SoC-specific PLL table, and initializes Gen3 CPG state. The core and module arrays are static `__initconst` data consumed during provider setup. Runtime state is the CCF clock graph plus hardware CPG/MSSR gate/divider state; no software persistence is implemented.

## Dependencies and Integration Points
Dependencies are the E3 DT clock binding, `renesas-cpg-mssr.h`, `rcar-gen3-cpg.h`, and `rcar-rst.h`. It integrates via `CONFIG_CLK_R8A77990` and `"renesas,r8a77990-cpg-mssr"`. Consumers include SCIF/HSCIF, MSIOF, DMAC, CMT/TMU, SDHI, USB, FCP/VSP/DU/LVDS, CSI/VIN, Ethernet AVB, GPIO, CANFD, RPC-IF, I2C, PWM, thermal, SSI/SCU, watchdog, and GIC.

## Risks and Test Signals
Risks are E3-specific SD/RPC/multimedia clock differences, PLL0 divider parent mistakes, and binding ID drift. Test with E3 board boot, clk summary validation for PE/S/SD/RPC clocks, SDHI/RPC/display/video/Ethernet/USB/audio probing, runtime PM gate toggling, and preservation of critical RWDT (`402`) and INTC-AP (`408`) clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a77990-cpg-mssr.c -->
