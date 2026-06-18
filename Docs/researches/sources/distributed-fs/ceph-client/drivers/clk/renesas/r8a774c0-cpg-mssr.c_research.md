<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a774c0-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a774c0-cpg-mssr.c

## Purpose
`r8a774c0-cpg-mssr.c` describes the compact RZ/G2E (`r8a774c0`) CPG/MSSR clock tree. Compared with larger Gen3 SoCs, it exposes a smaller topology built around `extal`, PLL0/PLL1/PLL3-derived fixed factors, PE/S clocks, SD clocks for SD0/SD1/SD3, RPC, CANFD/CSI/MSO dividers, and a module table for the reduced multimedia/peripheral set.

## Important APIs, Types, and Functions
Key objects are `r8a774c0_core_clks[]`, `r8a774c0_mod_clks[]`, `r8a774c0_crit_mod_clks[]`, `CPG_PLL_CONFIG_INDEX()`, `cpg_pll_configs[]`, `r8a774c0_cpg_mssr_init()`, and `r8a774c0_cpg_mssr_info`. It uses Gen3 CPG helpers but a different core-tree shape from `r8a774a1`: PLL0 divider aliases (`pll0d4`, `pll0d6`, `pll0d8`, `pll0d20`, `pll0d24`), `CLK_TYPE_GEN3_PE`, and no `extalr` input in the core definition list.

## Control Flow, State, and Persistence
The common driver consumes `r8a774c0_cpg_mssr_info`, registers the static core/module tables, and calls `r8a774c0_cpg_mssr_init()`. Init reads CPG mode pins, indexes the SoC-specific Gen3 PLL table, and calls `rcar_gen3_cpg_init()` to establish shared PLL/rate state. Unlike many larger Gen3 files, this init path does not explicitly reject a prohibited table entry because the table is defined for the valid strap combinations used here. State remains in CCF objects and hardware clock/gate registers.

## Dependencies and Integration Points
Dependencies are `dt-bindings/clock/r8a774c0-cpg-mssr.h`, `renesas-cpg-mssr.h`, `rcar-gen3-cpg.h`, and `rcar-rst.h`. The module clocks serve SCIF/HSCIF, MSIOF, DMAC, CMT/TMU, SDIF, USB, FDP/VSP/FCP, CSI/VIN/DU/LVDS, Ethernet AVB, GPIO, CAN, RPC, I2C, SSI, and SCU consumers. RWDT (`402`) and INTC-AP (`408`) are marked critical.

## Risks and Test Signals
Risks center on the specialized PLL/fixed-factor tree, absent SD2, and variant-specific multimedia gates. A wrong parent can silently overclock SDHI, CSI, or RPC. Test signals include boot on RZ/G2E hardware, expected PE/S/SD/RPC rates in clk summary, successful SD0/SD1/SD3 probing, working CANFD/RPC/display/video paths, and no clock-disable induced loss of watchdog or interrupt delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a774c0-cpg-mssr.c -->
