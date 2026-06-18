<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a77995-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a77995-cpg-mssr.c

## Purpose
`r8a77995-cpg-mssr.c` provides the R-Car D3 Gen3 CPG/MSSR clock data. It is a small Gen3 provider with `extal`, PLL0/PLL1/PLL3, PE/S clocks, ZA2/Z2/ZT/ZX, SD0, RPC, CANFD/MSO, and a reduced module table for D3 display, communication, storage, audio, timer, and control peripherals.

## Important APIs, Types, and Functions
The main symbols are `r8a77995_core_clks[]`, `r8a77995_mod_clks[]`, `r8a77995_crit_mod_clks[]`, `CPG_PLL_CONFIG_INDEX()`, `cpg_pll_configs[]`, `r8a77995_cpg_mssr_init()`, and `r8a77995_cpg_mssr_info`. It uses Gen3 CPG types and `rcar_gen3_cpg_clk_register`, with `LAST_DT_CORE_CLK = R8A77995_CLK_CPEX` and 77 module gate definitions.

## Control Flow, State, and Persistence
The common driver invokes init, which reads mode pins, selects the D3 PLL table entry, and calls `rcar_gen3_cpg_init()`. Static tables are used to register the clock graph and 12-bank MSSR module space. The file does not retain mutable state; persistence is limited to hardware register settings until reset and common-clock objects while the kernel is running.

## Dependencies and Integration Points
Dependencies include `dt-bindings/clock/r8a77995-cpg-mssr.h`, `renesas-cpg-mssr.h`, Gen3 CPG support, and reset-mode-pin reads. It integrates through `CONFIG_CLK_R8A77995` and `"renesas,r8a77995-cpg-mssr"`. Consumers include TMU/CMT, SCIF/HSCIF, MSIOF, DMAC, SDHI0, USB, display/FCP/VSP/VIN, Ethernet AVB, GPIO, CANFD, RPC, I2C/IIC-DVFS, SSI/SCU, PWM, thermal, RWDT, and GIC.

## Risks and Test Signals
Risks include copying clocks from E3/V3H that D3 lacks, incorrect PLL0 divider factors, and missing reduced audio/display gates. Test by booting D3 hardware, checking SD0/RPC/CANFD/MSO rates, probing serial/I2C/SDHI/RPC/display/Ethernet/USB/audio, and verifying critical RWDT and INTC-AP gates remain on through unused-clock cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a77995-cpg-mssr.c -->
