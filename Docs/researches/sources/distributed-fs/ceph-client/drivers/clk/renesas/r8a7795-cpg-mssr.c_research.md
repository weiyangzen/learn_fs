<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7795-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7795-cpg-mssr.c

## Purpose
`r8a7795-cpg-mssr.c` is the R-Car H3 Gen3 CPG/MSSR clock provider. It defines a large clock tree with EXTAL/EXTALR inputs, PLL0-PLL4, Z-family CPU/GPU clocks, S0-S3 fixed divisions, four SDHI channels, RPC/RPCD2, CANFD/CSI/MSO/HDMI dividers, OSC/R clocks, and a broad module gate set for high-end R-Car H3 peripherals.

## Important APIs, Types, and Functions
Key symbols are `r8a7795_core_clks[]`, `r8a7795_mod_clks[]`, `r8a7795_crit_mod_clks[]`, `cpg_pll_configs[]`, `r8a7795_denylist[]`, `r8a7795_cpg_mssr_init()`, and `r8a7795_cpg_mssr_info`. It uses `soc_device_match()` to reject ES1 revisions, Gen3 clock macros for Z/SD/RPC/OSC/div6 clocks, and exports `rcar_gen3_cpg_clk_register`.

## Control Flow, State, and Persistence
Initialization first checks the denylist and panics on unsupported `r8a7795` ES1.* silicon to avoid unsafe clocking. It then reads mode pins, uses MD14/MD13/MD19/MD17 to index a 16-entry PLL table, rejects prohibited strap rows where `extal_div` is zero, and calls `rcar_gen3_cpg_init()`. Runtime state is declarative clock registration plus hardware gate/rate state; the driver stores no persistent data across resets.

## Dependencies and Integration Points
Dependencies include `dt-bindings/clock/r8a7795-cpg-mssr.h`, `renesas-cpg-mssr.h`, `rcar-gen3-cpg.h`, `rcar-rst.h`, and SoC revision matching from `linux/sys_soc.h`. It binds through `CONFIG_CLK_R8A7795` and `"renesas,r8a7795-cpg-mssr"`. Consumers span GPU, FDP/FCP/VSP/DU/HDMI/LVDS, CSI/VIN, PCIe, USB, SATA, Ethernet AVB, SDHI, RPC-IF, CAN, I2C, GPIO, audio, timers, watchdog, and GIC.

## Risks and Test Signals
Risks are high because this file is a template for many derivatives: ES1 handling, PLL strap validation, clock IDs in DT bindings, and multimedia gate coverage must remain synchronized. Test on supported H3 revisions, confirm ES1 rejection if applicable, inspect clk summary rates, exercise SDHI/RPC/PCIe/USB/display/video/audio/Ethernet/SATA, and verify RWDT and INTC-AP critical gates survive clock pruning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7795-cpg-mssr.c -->
