<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a774a1-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a774a1-cpg-mssr.c

## Purpose
`r8a774a1-cpg-mssr.c` describes the RZ/G2M (`r8a774a1`) Clock Pulse Generator and Module Standby/Software Reset clock topology. It exports the SoC's DT-visible core clocks, internal PLL-derived parents, SD/RPC/div6 special clocks, module gate clocks, and critical always-on gates to the shared Renesas CPG/MSSR framework.

## Important APIs, Types, and Functions
The main data objects are `enum clk_ids`, `r8a774a1_core_clks[]`, `r8a774a1_mod_clks[]`, `r8a774a1_crit_mod_clks[]`, `cpg_pll_configs[]`, `r8a774a1_cpg_mssr_init()`, and `r8a774a1_cpg_mssr_info`. Clock definitions use `DEF_INPUT`, `DEF_BASE`, `DEF_FIXED`, `DEF_GEN3_Z`, `DEF_GEN3_SDH`, `DEF_GEN3_SD`, `DEF_DIV6P1`, and `DEF_MOD`. The exported `struct cpg_mssr_info` selects `rcar_gen3_cpg_clk_register`.

## Control Flow, State, and Persistence
The file is mostly declarative. During probe, the common `renesas-cpg-mssr` driver calls `r8a774a1_cpg_mssr_init()`, which reads mode pins with `rcar_rst_read_mode_pins()`, indexes the 16-entry PLL table from MD14/MD13/MD19/MD17, rejects prohibited strap combinations with `-EINVAL`, and calls `rcar_gen3_cpg_init(cpg_pll_config, CLK_EXTALR, cpg_mode)`. Runtime state is the common-clock registrations plus hardware CPG/MSSR register state; this driver does not persist state across reboot.

## Dependencies and Integration Points
It depends on `dt-bindings/clock/r8a774a1-cpg-mssr.h`, `renesas-cpg-mssr.h`, `rcar-gen3-cpg.h`, and reset-mode-pin support from `rcar-rst.h`. It integrates through the compatible entry in `renesas-cpg-mssr.c` and the `CONFIG_CLK_R8A774A1` build path. Consumers include SDHI, RPC-IF, PCIe, USB, VIN/CSI, DU/HDMI/LVDS, audio SSI/SCU, I2C, CAN, timers, GPIO, and DMA.

## Risks and Test Signals
Risks are wrong PLL mode decoding, missing module gates for board peripherals, parent-rate mistakes for SD/RPC/div6 clocks, and accidentally disabling critical RWDT (`402`) or INTC-AP/GIC (`408`). Test signals are clean boot on RZ/G2M DTs, expected `/sys/kernel/debug/clk/clk_summary` rates, working SDHI/RPC/PCIe/USB/display/audio paths, no prohibited-mode error on valid hardware, and successful suspend/resume with unused-clock pruning enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a774a1-cpg-mssr.c -->
