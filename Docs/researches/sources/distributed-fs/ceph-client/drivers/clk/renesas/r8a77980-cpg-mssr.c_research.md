<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a77980-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a77980-cpg-mssr.c

## Purpose
`r8a77980-cpg-mssr.c` provides the R-Car V3H Gen3 CPG/MSSR data. It defines a mid-sized Gen3 clock tree with EXTAL/EXTALR, PLL1/PLL2/PLL3, S0-S3, SD source and SD0, RPC/RPCD2, CANFD/CSI/MSO dividers, OSC/R, and module gates for V3H's capture, display, communication, and control peripherals.

## Important APIs, Types, and Functions
Key symbols are `r8a77980_core_clks[]`, `r8a77980_mod_clks[]`, `r8a77980_crit_mod_clks[]`, `CPG_PLL_CONFIG_INDEX()`, `cpg_pll_configs[]`, `r8a77980_cpg_mssr_init()`, and `r8a77980_cpg_mssr_info`. It uses standard Gen3 helper types and `rcar_gen3_cpg_clk_register`, with `LAST_DT_CORE_CLK = R8A77980_CLK_OSC` limiting the DT-visible core range.

## Control Flow, State, and Persistence
Initialization reads mode pins, selects one of four Gen3 PLL configurations using MD14/MD13, and calls `rcar_gen3_cpg_init(cpg_pll_config, CLK_EXTALR, cpg_mode)`. The module clock list spans 12 MSSR banks and is consumed by the common CPG/MSSR code. The file is declarative and keeps no persistent software state after init.

## Dependencies and Integration Points
Dependencies include `dt-bindings/clock/r8a77980-cpg-mssr.h`, `renesas-cpg-mssr.h`, `rcar-gen3-cpg.h`, and `rcar-rst.h`. It matches through `CONFIG_CLK_R8A77980` and `"renesas,r8a77980-cpg-mssr"`. Consumers include TMU/CMT, SCIF/HSCIF, MSIOF, DMAC, SDHI0, USB, FCP/VSP, CSI/VIN, DU/LVDS, Ethernet AVB, GPIO, CANFD, RPC, I2C, PWM, thermal, RWDT, and INTC-AP.

## Risks and Test Signals
Risks include assuming larger H3/M3 SDHI or multimedia availability, wrong PLL mode table entries, and clock ID mismatches with V3H DT bindings. Test on V3H hardware, validate SD0/RPC/CANFD/MSO/CSI rates in clk summary, probe capture/display/Ethernet/USB/serial/I2C, and verify watchdog/interrupt critical clocks under suspend and unused-clock disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a77980-cpg-mssr.c -->
