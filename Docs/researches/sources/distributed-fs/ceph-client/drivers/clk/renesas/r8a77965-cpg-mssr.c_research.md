<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a77965-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a77965-cpg-mssr.c

## Purpose
`r8a77965-cpg-mssr.c` is the R-Car M3-N Gen3 CPG/MSSR clock description. It is close to the M3-W family but has its own DT clock IDs and module coverage, including SDHI, RPC, CANFD, CSI, HDMI, display/capture/video, audio, SATA, PCIe, USB, Ethernet, GPIO, I2C, and timers.

## Important APIs, Types, and Functions
The central declarations are `r8a77965_core_clks[]`, `r8a77965_mod_clks[]`, `r8a77965_crit_mod_clks[]`, `CPG_PLL_CONFIG_INDEX()`, `cpg_pll_configs[]`, `r8a77965_cpg_mssr_init()`, and `r8a77965_cpg_mssr_info`. It uses Gen3 helper macros for Z clocks, SDH/SD clocks, RPC/RPCD2, fixed factors, div6 clocks, and critical module IDs.

## Control Flow, State, and Persistence
The init path is linear: read mode pins with `rcar_rst_read_mode_pins()`, index the 16-row PLL table from MD14/MD13/MD19/MD17, reject prohibited rows where `extal_div` is zero, and call `rcar_gen3_cpg_init(cpg_pll_config, CLK_EXTALR, cpg_mode)`. Static module definitions cover 12 MSSR banks. No file-local state persists; clock state is in CCF and CPG/MSSR hardware.

## Dependencies and Integration Points
Dependencies are `dt-bindings/clock/r8a77965-cpg-mssr.h`, `renesas-cpg-mssr.h`, `rcar-gen3-cpg.h`, and reset-mode-pin support. It integrates through `CONFIG_CLK_R8A77965` and `"renesas,r8a77965-cpg-mssr"`. The table feeds drivers for serial/MSIOF, DMAC, SDIF, PCIe, USB, thermal, PWM, FCP/VSP/DU/HDMI/LVDS, CSI/VIN, Ethernet AVB, SATA, GPIO, CAN, RPC-IF, I2C, SSI/SCU, RWDT, and GIC.

## Risks and Test Signals
Risks include subtle differences from M3-W/M3-W+, missing M3-N-only gates such as `dab`, and wrong PLL strap rejection. Test on M3-N boards, verify clk summary rates, probe SDHI/SATA/PCIe/USB/RPC/display/video/audio/Ethernet/CAN, check suspend/resume and runtime PM, and confirm RWDT (`402`) and INTC-AP (`408`) are not disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a77965-cpg-mssr.c -->
