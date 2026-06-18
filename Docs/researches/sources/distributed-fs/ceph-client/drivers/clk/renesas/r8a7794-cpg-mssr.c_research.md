<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7794-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7794-cpg-mssr.c

## Purpose
`r8a7794-cpg-mssr.c` describes the R-Car E2 Gen2 CPG/MSSR clock controller. It exposes a moderate Gen2 core clock set with `extal`, `usb_extal`, PLL0/1/3, ADSP, SD/QSPI/RCAN, fixed CPU/bus/media outputs, SD2/SD3/MMC0 dividers, and module gates for the E2 peripheral mix.

## Important APIs, Types, and Functions
Important data includes `r8a7794_core_clks[]`, `r8a7794_mod_clks[]`, `r8a7794_crit_mod_clks[]`, `CPG_PLL_CONFIG_INDEX()`, `cpg_pll_configs[]`, `r8a7794_cpg_mssr_init()`, and `r8a7794_cpg_mssr_info`. It uses Gen2 clock types and `DEF_DIV6P1` for SD/MMC clocks. The final info struct selects `rcar_gen2_cpg_clk_register`.

## Control Flow, State, and Persistence
The common driver calls `r8a7794_cpg_mssr_init()`, which reads mode pins, indexes a four-entry Gen2 PLL config table from MD14/MD13, and initializes Gen2 CPG support with the PLL VCO divider argument set to `2`. Static module data covers 12 hardware module banks. The file does not own persistent state; hardware register contents and CCF registrations are the effective runtime state.

## Dependencies and Integration Points
Dependencies are `dt-bindings/clock/r8a7794-cpg-mssr.h`, `renesas-cpg-mssr.h`, `rcar-gen2-cpg.h`, and reset support. It is tied to `CONFIG_CLK_R8A7794` and `"renesas,r8a7794-cpg-mssr"`. Consumers include JPU, VSP, DU, VIN, SDHI/MMCIF, USB, Ethernet/EtherAVB, QSPI, CAN, I2C, GPIO, audio SSI/SCU, serial/MSIOF, timers, watchdog, and interrupt controller.

## Risks and Test Signals
Risks include SD/MMC divider offsets, `usb_extal`-derived RCAN rate selection, and E2-specific missing gates compared with M2/H2. Critical RWDT and INTC-SYS gates must remain enabled. Test by booting E2 hardware, validating PLL/fixed rates, probing SDHI/MMC/QSPI/USB/Ethernet/display/video/audio/serial paths, and exercising runtime PM and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7794-cpg-mssr.c -->
