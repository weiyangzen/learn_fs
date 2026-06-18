<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a774e1-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a774e1-cpg-mssr.c

## Purpose
`r8a774e1-cpg-mssr.c` provides the RZ/G2H CPG/MSSR data. It is a broad Gen3 clock provider with PLL0/1/2/3/4 roots, CPU/video/display/system fixed factors, four SDHI clock pairs, RPC, CANFD/CSI/MSO/HDMI dividers, and the largest RZ/G2 module gate set in this group.

## Important APIs, Types, and Functions
The important definitions are `r8a774e1_core_clks[]`, `r8a774e1_mod_clks[]`, `r8a774e1_crit_mod_clks[]`, `cpg_pll_configs[]`, `r8a774e1_cpg_mssr_init()`, and `r8a774e1_cpg_mssr_info`. It uses the same Gen3 macros as R-Car H3-style drivers: `DEF_GEN3_Z` for `z`, `z2`, and `zg`, `DEF_GEN3_SDH/SD` for SDHI, `DEF_DIV6P1` for programmable peripheral clocks, and `MOD_CLK_ID()` for audio submodule parentage.

## Control Flow, State, and Persistence
Initialization reads mode pins, decodes the four mode bits into a 16-entry PLL table, rejects entries where `extal_div` is zero, and calls `rcar_gen3_cpg_init(cpg_pll_config, CLK_EXTALR, cpg_mode)`. The common CPG/MSSR driver then uses the core and module arrays to publish clock providers and manage module stop gates. The driver has no persistent storage; all lasting effects are framework registrations and CPG/MSSR register programming.

## Dependencies and Integration Points
It depends on the RZ/G2H clock binding header, Gen3 CPG support, the CPG/MSSR core, and reset-mode-pin access. The module table feeds GPU, FDP/VCP/VDP, timers, serial/MSIOF, DMAC, SDHI, PCIe, USB, audio DMAC/SSI/SCU, thermal, PWM, FCP/VSP, CSI, DU/HDMI/LVDS, VIN, Ethernet AVB, SATA, GPIO, CAN, RPC-IF, and I2C consumers. RWDT and GIC clocks are critical.

## Risks and Test Signals
Risks include H3/RZ-G2H table drift, incorrect multimedia module coverage, and PLL strap errors causing rate damage. HDMI and SDHI divider parentage are common integration-sensitive areas. Test with RZ/G2H board boot, clk summary rate comparison against hardware manuals, SD/PCIe/USB/display/audio/video/Ethernet exercises, suspend/resume, and unused-clock disable runs that preserve RWDT and INTC-AP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a774e1-cpg-mssr.c -->
