<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a774b1-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a774b1-cpg-mssr.c

## Purpose
`r8a774b1-cpg-mssr.c` is the RZ/G2N clock description for the Renesas CPG/MSSR framework. It provides Gen3-style external inputs, PLL roots, fixed S0/S1/S2/S3 divisions, SDHI clocks, RPC clocks, div6 peripheral clocks, and a large module-stop gate table tailored to the RZ/G2N peripheral set.

## Important APIs, Types, and Functions
Important symbols are `r8a774b1_core_clks[]`, `r8a774b1_mod_clks[]`, `r8a774b1_crit_mod_clks[]`, `CPG_PLL_CONFIG_INDEX()`, `cpg_pll_configs[]`, `r8a774b1_cpg_mssr_init()`, and `r8a774b1_cpg_mssr_info`. The source uses Gen3 helpers such as `DEF_GEN3_Z`, `DEF_GEN3_SDH`, `DEF_GEN3_SD`, `CLK_TYPE_GEN3_MAIN`, `CLK_TYPE_GEN3_RPCSRC`, `CLK_TYPE_GEN3_RPC`, and `rcar_gen3_cpg_clk_register`.

## Control Flow, State, and Persistence
Probe enters through the shared CPG/MSSR driver and runs `r8a774b1_cpg_mssr_init()`. The init reads CPG mode pins, derives a PLL table index from MD14/MD13/MD19/MD17, validates that `extal_div` is nonzero, then initializes Gen3 CPG state with `CLK_EXTALR` as the external R-clock source. The module table covers 12 MSSR banks (`12 * 32` hardware module clocks). There is no file-local mutable state after init; gate and reset effects live in hardware and common framework data.

## Dependencies and Integration Points
The file depends on RZ/G2N clock DT bindings, the common CPG/MSSR driver, Gen3 CPG helper code, and reset-mode-pin reading. It is matched by the SoC compatible in `renesas-cpg-mssr.c` and compiled through the Renesas clock Makefile/Kconfig path. The clock consumers include serial, MSIOF, DMA, SDIF, PCIe, USB3/USB2, video capture/display, Ethernet AVB, SATA, GPIO, CAN, RPC-IF, I2C, and audio blocks.

## Risks and Test Signals
The main risks are SoC-variant mismatches with close RZ/G2M/R-Car M3 tables, invalid PLL strap handling, and missing gate entries for blocks present in RZ/G2N device trees. Critical RWDT and INTC-AP clocks must remain protected. Good tests are booting an RZ/G2N board, checking clk summary parentage/rates, probing SDHI/SATA/PCIe/USB/display/audio/Ethernet, and verifying runtime PM can gate noncritical modules without hanging interrupt or watchdog infrastructure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a774b1-cpg-mssr.c -->
