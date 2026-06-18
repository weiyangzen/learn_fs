# subset-b-001155 Renesas CPG/MSSR clock driver research

This grouped report covers the requested Renesas R-Car/RZ-G CPG/MSSR clock-provider source files. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7790-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7790-cpg-mssr.c

## Purpose
`r8a7790-cpg-mssr.c` is the R-Car H2 Gen2 CPG/MSSR clock description. It exposes legacy Gen2 external inputs (`extal`, `usb_extal`), PLL0/PLL1/PLL3 roots, fixed CPU/bus/media clocks, SD/MMC/SSP/QSPI/RCAN clocks, and module gates for the large H2 multimedia and peripheral surface.

## Important APIs, Types, and Functions
Important symbols include `r8a7790_core_clks[]`, `r8a7790_mod_clks[]`, `r8a7790_crit_mod_clks[]`, `CPG_PLL_CONFIG_INDEX()`, `cpg_pll_configs[]`, `r8a7790_cpg_mssr_init()`, and `r8a7790_cpg_mssr_info`. The file uses Gen2 helpers and types such as `CLK_TYPE_GEN2_MAIN`, `CLK_TYPE_GEN2_PLL0`, `CLK_TYPE_GEN2_ADSP`, `CLK_TYPE_GEN2_SD*`, `CLK_TYPE_GEN2_QSPI`, `CLK_TYPE_GEN2_RCAN`, and `rcar_gen2_cpg_clk_register`.

## Control Flow, State, and Persistence
The init function reads mode pins, computes a three-bit PLL table index from MD14/MD13/MD19, selects one of eight `rcar_gen2_cpg_pll_config` entries, and calls `rcar_gen2_cpg_init(cpg_pll_config, 2, cpg_mode)`. The `2` argument reflects the Gen2 PLL0/PLL1 VCO division model used by this SoC. Module gates are declared for 12 banks. Runtime state is limited to CCF registration and hardware gate/rate registers.

## Dependencies and Integration Points
The file depends on `dt-bindings/clock/r8a7790-cpg-mssr.h`, `renesas-cpg-mssr.h`, `rcar-gen2-cpg.h`, and `rcar-rst.h`. It is matched through `"renesas,r8a7790-cpg-mssr"` in `renesas-cpg-mssr.c` and built by `CONFIG_CLK_R8A7790`. Consumers include VIN/VSP/FDP/DU, USB, Ethernet, QSPI, SDHI/MMCIF, serial/MSIOF, audio SSI/SCU, CAN, I2C, GPIO, timers, DMAC, and interrupt/watchdog infrastructure.

## Risks and Test Signals
Risks include legacy Gen2 rate-table mistakes, the PLL VCO/2 distinction, `usb_extal`/RCAN parent mismatches, and missing gates for H2-only multimedia units. RWDT (`402`) and INTC-SYS/GIC (`408`) are critical. Test signals are H2 DT boot, expected PLL and fixed-clock rates, working SDHI/MMC/QSPI/USB/Ethernet/display/video/audio, and no regressions with runtime PM or unused-clock disabling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7790-cpg-mssr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7791-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7791-cpg-mssr.c

## Purpose
`r8a7791-cpg-mssr.c` defines the R-Car M2-W/M2-N Gen2 CPG/MSSR clock provider. It supplies Gen2 PLL/fixed-factor core clocks, SD/QSPI/RCAN clocks, and a module gate map for serial, display/video, audio, USB, Ethernet, CAN, I2C, GPIO, timers, and DMA blocks.

## Important APIs, Types, and Functions
Core definitions are in `r8a7791_core_clks[]`; module gates are in `r8a7791_mod_clks[]`; critical gates are in `r8a7791_crit_mod_clks[]`. Init data is selected by `CPG_PLL_CONFIG_INDEX()` and `cpg_pll_configs[]`, while `r8a7791_cpg_mssr_info` exports the tables and `rcar_gen2_cpg_clk_register`. This file also includes `<linux/of.h>` and uses `of_device_is_compatible()` for M2-N compatibility handling.

## Control Flow, State, and Persistence
Probe runs `r8a7791_cpg_mssr_init()`, reads mode pins, selects one of eight PLL configurations, and calls `rcar_gen2_cpg_init()`. The control flow includes device-tree compatible checks so the same data can serve the closely related `r8a7793` path registered by `renesas-cpg-mssr.c`. State is not persisted by the driver; it publishes CCF clocks and lets the common CPG/MSSR code operate hardware gates.

## Dependencies and Integration Points
Dependencies include the R-Car M2 binding header, `rcar-gen2-cpg.h`, `renesas-cpg-mssr.h`, OF matching, and reset-mode-pin reads. Build/match integration includes both `"renesas,r8a7791-cpg-mssr"` and `"renesas,r8a7793-cpg-mssr"` data references. Consumers include VCP/VPC/JPU/FDP/VSP/DU/VIN, SDHI/MMCIF, QSPI, USB, audio, I2C/IIC, CAN, Ethernet AVB, timers, serial, and GPIO.

## Risks and Test Signals
Risks are M2-W versus M2-N/R-Car M2 variant drift, Gen2 PLL table mistakes, and gate IDs that differ from H2/E2. Critical RWDT and INTC-SYS clocks must not be disabled. Test on both compatible variants where possible, compare clk summary rates with expected strap modes, probe SDHI/MMC/QSPI/display/video/audio/USB/Ethernet, and run unused-clock disable plus suspend/resume tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7791-cpg-mssr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7792-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7792-cpg-mssr.c

## Purpose
`r8a7792-cpg-mssr.c` is the R-Car V2H Gen2 CPG/MSSR data file. It defines a smaller Gen2 clock tree focused on imaging/video use cases, with PLL roots, QSPI, `z/zg/zx/zs`, bus clocks, SD/RCAN/R/OSC clocks, and a module table for video, display, capture, serial, storage, GPIO, I2C, CAN, audio, timers, and DMA.

## Important APIs, Types, and Functions
The key objects are `r8a7792_core_clks[]`, `r8a7792_mod_clks[]`, `r8a7792_crit_mod_clks[]`, `CPG_PLL_CONFIG_INDEX()`, `cpg_pll_configs[]`, `r8a7792_cpg_mssr_init()`, and `r8a7792_cpg_mssr_info`. It uses the Gen2 helper stack via `rcar-gen2-cpg.h` and `rcar_gen2_cpg_clk_register`, with `DEF_BASE` entries for Gen2 PLLs/QSPI/RCAN and fixed-factor definitions for bus/media clocks.

## Control Flow, State, and Persistence
The init path reads CPG mode pins, derives the PLL config from MD14/MD13, selects one of four `rcar_gen2_cpg_pll_config` rows, and calls `rcar_gen2_cpg_init(cpg_pll_config, 2, cpg_mode)`. The shared CPG/MSSR code consumes `num_hw_mod_clks = 12 * 32` and the module list to operate stop/reset bits. There is no persistent state beyond registered clocks and programmed hardware registers.

## Dependencies and Integration Points
Dependencies are the `r8a7792` clock binding, the common CPG/MSSR framework, Gen2 CPG helper code, and reset-mode-pin access. Integration is through `CONFIG_CLK_R8A7792` and the `"renesas,r8a7792-cpg-mssr"` compatible. Notable consumers include JPU, VSP, DU, VIN, PCIe, USB, SDHI, QSPI, I2C, GPIO, CAN, SSI/SCU, serial/MSIOF, timers, watchdog, and interrupt controller clocks.

## Risks and Test Signals
Risks include overgeneralizing from other Gen2 SoCs, because V2H has fewer SD/audio/display modules and different PLL mode indexing. Wrong gate IDs can leave camera/display blocks unclocked. Tests should cover V2H boot, clk summary rate validation, video capture/display pipelines, SDHI/QSPI/USB/PCIe, CAN/I2C/GPIO, audio if present, and preservation of RWDT/INTC-SYS critical gates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7792-cpg-mssr.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7796-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7796-cpg-mssr.c

## Purpose
`r8a7796-cpg-mssr.c` provides the R-Car M3-W/M3-W+ Gen3 CPG/MSSR clock data. It supplies the standard Gen3 PLL/S/SD/RPC/div6 core clocks and a module gate table for M3-W peripherals, with a small revision-compatible fixup for M3-W+.

## Important APIs, Types, and Functions
Important symbols are `r8a7796_core_clks[]`, mutable `r8a7796_mod_clks[]`, `r8a7796_crit_mod_clks[]`, `r8a77961_mod_nullify[]`, `cpg_pll_configs[]`, `r8a7796_cpg_mssr_init()`, and `r8a7796_cpg_mssr_info`. The file uses `<linux/of.h>`, `of_device_is_compatible()`, and `mssr_mod_nullify()` to remove module `617` (`FCPCI0`) for `"renesas,r8a77961-cpg-mssr"`.

## Control Flow, State, and Persistence
Init reads CPG mode pins, decodes the four Gen3 PLL mode bits, validates nonzero `extal_div`, applies the M3-W+ nullification fixup when the compatible is `r8a77961`, and then calls `rcar_gen3_cpg_init()`. The module clock table is `__initdata` instead of `const` because the nullify step mutates it during init. After boot, state exists in the common clock framework and hardware registers.

## Dependencies and Integration Points
The file depends on `dt-bindings/clock/r8a7796-cpg-mssr.h`, OF matching, Gen3 CPG code, common CPG/MSSR support, and reset-mode-pin access. It is used by both `CONFIG_CLK_R8A77960` and `CONFIG_CLK_R8A77961` match entries in `renesas-cpg-mssr.c`. Consumers include SDHI, PCIe, USB, display/video/capture, audio, Ethernet AVB, CAN, RPC, I2C, timers, GPIO, DMA, watchdog, and GIC blocks.

## Risks and Test Signals
Risks include forgetting that the module table is mutated for M3-W+, mismatching the M3-W/M3-W+ DT compatible, or changing PLL/SD/RPC parents copied from H3. Test both compatibles, confirm FCPCI0 is absent/null on M3-W+, validate clk summary rates, exercise SDHI/RPC/PCIe/USB/display/video/audio/Ethernet, and check RWDT/GIC critical clocks under unused-clock pruning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7796-cpg-mssr.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a77970-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a77970-cpg-mssr.c

## Purpose
`r8a77970-cpg-mssr.c` describes the R-Car V3M Gen3 CPG/MSSR clock tree. It is a smaller Gen3 provider with PLL0/PLL1/PLL3 roots, Z2/ZTR/ZT/ZX and S1/S2 clocks, one SDHI channel, RPC/RPCD2, CANFD/MSO/CSI dividers, and a V3M-oriented module gate map.

## Important APIs, Types, and Functions
Important objects include `r8a77970_core_clks[]`, `r8a77970_mod_clks[]`, `r8a77970_crit_mod_clks[]`, `cpg_pll_configs[]`, `r8a77970_cpg_mssr_init()`, custom `r8a77970_cpg_clk_register()`, and `r8a77970_cpg_mssr_info`. This file defines V3M-specific SD clock types handled by a custom registrar before delegating other clocks to `rcar_gen3_cpg_clk_register`.

## Control Flow, State, and Persistence
Init reads mode pins, indexes a four-entry PLL config table from MD14/MD13, and calls `rcar_gen3_cpg_init()`. During clock registration, `r8a77970_cpg_clk_register()` intercepts `CLK_TYPE_R8A77970_SD0H` and `CLK_TYPE_R8A77970_SD0`, picks divider tables and shifts, and registers divider-table clocks at `CPG_SD0CKCR`; all other core clocks use the generic Gen3 registrar. State is framework registration and hardware register values only.

## Dependencies and Integration Points
The file depends on `dt-bindings/clock/r8a77970-cpg-mssr.h`, Gen3 CPG helpers, the common CPG/MSSR framework, reset-mode-pin support, and common clock divider APIs. It integrates through `CONFIG_CLK_R8A77970` and `"renesas,r8a77970-cpg-mssr"`. Consumers include timers, serial/MSIOF, SYS-DMAC, SDHI0, USB, FDP/VSP/VIN, Ethernet AVB, GPIO, CANFD, RPC-IF, I2C, RWDT, and INTC-AP.

## Risks and Test Signals
The custom SD divider path is the main risk: wrong shift/table/parent handling can break SDHI0 rates. The smaller module set also makes copy-paste from larger Gen3 SoCs risky. Test V3M boot, SDHI0 frequency changes, RPC/CAN/Ethernet/USB/video capture paths, clk summary parent/rate checks, and critical RWDT/GIC preservation during clock pruning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a77970-cpg-mssr.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a779a0-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a779a0-cpg-mssr.c

## Purpose
`r8a779a0-cpg-mssr.c` is the R-Car V3U Gen4 CPG/MSSR clock provider. It defines Gen4 PLL-derived roots, Z0/Z1/ZG CPU/GPU clocks, S1/S3 divisions, SD0, RPC, CANFD/CSI/DSI/MSO dividers, OCO/R selection, and module gates for high-bandwidth video, ISP, Ethernet AVB, display, CSI, VIN, and peripheral blocks.

## Important APIs, Types, and Functions
Important symbols are `r8a779a0_core_clks[]`, `r8a779a0_mod_clks[]`, `r8a779a0_crit_mod_clks[]`, `CPG_PLL_CONFIG_INDEX()`, `cpg_pll_configs[]`, `r8a779a0_cpg_mssr_init()`, and `r8a779a0_cpg_mssr_info`. It uses Gen4 helpers from `rcar-gen4-cpg.h`, including Gen4 PLL/Z/SD/RPC/OSC/MDSEL support, and marks `.reg_layout = CLK_REG_LAYOUT_RCAR_GEN4`.

## Control Flow, State, and Persistence
Init reads MD14/MD13 mode pins, indexes a four-entry Gen4 PLL table, and calls `rcar_gen4_cpg_init(cpg_pll_config, CLK_EXTALR, cpg_mode)`. The table contains a prohibited row but this init path does not perform the explicit `extal_div` rejection used by later Gen4 files. The module table spans `15 * 32` hardware module clocks. State is common-clock registration plus Gen4 CPG/MSSR hardware registers.

## Dependencies and Integration Points
Dependencies include `dt-bindings/clock/r8a779a0-cpg-mssr.h`, `rcar-gen4-cpg.h`, `renesas-cpg-mssr.h`, reset-mode-pin support, and common clock infrastructure. It matches through `CONFIG_CLK_R8A779A0` and `"renesas,r8a779a0-cpg-mssr"`. Consumers include ISP/ISPCS, AVB0-5, CANFD, CSI4, DU/DSI, FCP/VSP, VIN00-37, SDHI0, HSCIF/SCIF, I2C, MSIOF/MSI, TMU/TPU, RPC-IF, PFC, and watchdog.

## Risks and Test Signals
Risks include Gen4 register-layout mismatches, unvalidated prohibited strap handling, large VIN/ISP module coverage errors, and wrong PLL20/21/30/31/ZG parentage. Test V3U boot, clk summary rates for Z/S/SD/RPC/DSI/CANFD/CSI, ISP/VIN/display/AVB/SDHI/RPC probing, watchdog critical gate behavior (`907`), and suspend/runtime PM with Gen4 layout operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a779a0-cpg-mssr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a779f0-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a779f0-cpg-mssr.c

## Purpose
`r8a779f0-cpg-mssr.c` describes the R-Car S4-8 Gen4 CPG/MSSR clock tree. It provides EXTAL/EXTALR, PLL1/2/3/5/6 roots, S0 and segmented MM/RT/PER/HSC/CC fixed factors, SD0, RPC, MSO, R/OSC, and module gates for serial, I2C, MSIOF, PCIe, SDHI, timers, watchdog, PFC, Ethernet switch/SerDes, and UFS.

## Important APIs, Types, and Functions
Key definitions are `r8a779f0_core_clks[]`, `r8a779f0_mod_clks[]`, `r8a779f0_crit_mod_clks[]`, `CPG_PLL_CONFIG_INDEX()`, `cpg_pll_configs[]`, `r8a779f0_cpg_mssr_init()`, and `r8a779f0_cpg_mssr_info`. It uses Gen4 fixed PLL helper macros such as `DEF_GEN4_PLL_F9_24` and `DEF_GEN4_PLL_V9_24`, Gen4 SD/RPC/OSC/MDSEL helpers, and `CLK_REG_LAYOUT_RCAR_GEN4`.

## Control Flow, State, and Persistence
The init function reads mode pins, indexes the four-entry PLL table from MD14/MD13, rejects the prohibited row where `extal_div` is zero, and calls `rcar_gen4_cpg_init()`. The module table covers `28 * 32` hardware module clocks, reflecting high-numbered S4-8 module IDs. State is declarative CCF registration and hardware gate/divider state.

## Dependencies and Integration Points
Dependencies are `dt-bindings/clock/r8a779f0-cpg-mssr.h`, Gen4 CPG support, the common CPG/MSSR core, and reset-mode-pin reading. It integrates through `CONFIG_CLK_R8A779F0` and `"renesas,r8a779f0-cpg-mssr"`. Consumers include HSCIF/SCIF, I2C, MSIOF, PCIe, SDHI0, system DMAC, TMU/CMT, PFC, TSC, R-Switch2, Ethernet SerDes, UFS, watchdog, and RPC.

## Risks and Test Signals
Risks include wrong domain-specific S0 divisor parentage, high module-bank sizing, prohibited mode handling, and rates for Ethernet/UFS/PCIe clocks. Test S4-8 boot, `clk_summary` for S0* domain clocks and RPC/SD/MSO, probe PCIe/UFS/Ethernet switch/serial/I2C/SDHI, verify RWDT critical module `907`, and exercise suspend/runtime PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a779f0-cpg-mssr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a779g0-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a779g0-cpg-mssr.c

## Purpose
`r8a779g0-cpg-mssr.c` is the R-Car V4H Gen4 CPG/MSSR clock description. It exposes a rich Gen4 clock tree with PLL1-PLL6 roots, S0 domain splits for VIO/VC/HSC/MM/RT/PER/CC, SV VIP/IR clocks, VIO/VC buses, CANFD/CSI/DSI/SD/MSO/RPC clocks, and module gates for ISP, AVB/TSN, CSI, display, VSP/FCP, serial, I2C, VIN, PFC, audio, and timers.

## Important APIs, Types, and Functions
Important objects are `r8a779g0_core_clks[]`, `r8a779g0_mod_clks[]`, `CPG_PLL_CONFIG_INDEX()`, `cpg_pll_configs[]`, `r8a779g0_cpg_mssr_init()`, and `r8a779g0_cpg_mssr_info`. It uses `rcar-gen4-cpg.h`, Gen4 PLL/Z/SD/RPC/OSC/MDSEL helpers, domain-specific fixed factors, and sets `.reg_layout = CLK_REG_LAYOUT_RCAR_GEN4`. No critical module array is defined in this file.

## Control Flow, State, and Persistence
Init reads mode pins, indexes the four-entry Gen4 PLL table, rejects prohibited `extal_div == 0` mode, and calls `rcar_gen4_cpg_init(cpg_pll_config, CLK_EXTALR, cpg_mode)`. The exported info advertises `30 * 32` hardware module clocks. Runtime state is the common clock graph and Gen4 CPG/MSSR hardware state; the file does not store persistent software data.

## Dependencies and Integration Points
Dependencies include `dt-bindings/clock/r8a779g0-cpg-mssr.h`, Gen4 CPG support, common CPG/MSSR infrastructure, and reset-mode-pin reads. It matches via `CONFIG_CLK_R8A779G0` and `"renesas,r8a779g0-cpg-mssr"`. Consumers include ISP, AVB0-2, TSN, CANFD, CSI4, display/DSI, FCP/VSP, VIN00-17, HSCIF/SCIF, I2C, MSIOF, SDHI0, TMU/CMT, PFC, TSC, RPC, SSI/SSIU, and watchdog modules.

## Risks and Test Signals
Risks include the large domain-split clock tree, absent critical-clock annotations, high module IDs such as TSN/SSI, and close similarity to V4M/V4H derivatives. Test V4H boot, clk summary validation for VIO/VC/HSC/PER/MM domains, VIN/CSI/display/ISP/AVB/TSN/SDHI/RPC/audio probing, and suspend/runtime PM with careful watchdog and interrupt monitoring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a779g0-cpg-mssr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a779h0-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a779h0-cpg-mssr.c

## Purpose
`r8a779h0-cpg-mssr.c` describes the R-Car V4M Gen4 CPG/MSSR clock topology. It provides EXTAL/EXTALR, PLL1-PLL6 roots, C0-C3 Z clocks, S0 domain splits, IMP/VIO/VC source and bus clocks, SD0, RPC, CANFD/CSI/DSI/MSO, and module gates for ISP, AVB/RGMII, CSI, display, VSP/FCP, serial, I2C, VIN, timers, PFC, audio, and watchdog-related modules.

## Important APIs, Types, and Functions
Important definitions include `r8a779h0_core_clks[]`, `r8a779h0_mod_clks[]`, `CPG_PLL_CONFIG_INDEX()`, `cpg_pll_configs[]`, `r8a779h0_cpg_mssr_init()`, and `r8a779h0_cpg_mssr_info`. It uses Gen4 PLL helpers, domain fixed-factor definitions, Gen4 SD/RPC/OSC/MDSEL helpers, and `CLK_REG_LAYOUT_RCAR_GEN4`. Like `r8a779g0`, it has no explicit critical module clock array.

## Control Flow, State, and Persistence
Init reads MD14/MD13 mode pins, indexes a four-entry PLL table, rejects the prohibited row, and initializes Gen4 CPG state using `CLK_EXTALR`. The module table declares a `30 * 32` hardware module space and includes high-numbered audio modules. Runtime state is held in common-clock registrations and Gen4 CPG/MSSR hardware registers; nothing is persisted across reboot.

## Dependencies and Integration Points
Dependencies are `dt-bindings/clock/r8a779h0-cpg-mssr.h`, `rcar-gen4-cpg.h`, `renesas-cpg-mssr.h`, and reset-mode-pin support. It integrates through `CONFIG_CLK_R8A779H0` and `"renesas,r8a779h0-cpg-mssr"`. Consumers include ISP, AVB/RGMII, CANFD, CSI4, display/DSI, FCP/VSP, HSCIF/SCIF, I2C, MSIOF, SDHI0, VIN, TMU/CMT, PFC, TSC, RPC, SSI/SSIU, IMP/VIO/VC blocks, and watchdog.

## Risks and Test Signals
Risks include V4M-specific IMP/VIO/VC clock routing, high module IDs, missing critical-clock protections, and close-but-not-identical V4H clock names. Test V4M boot, clk summary for ZC/S0/IMP/VIO/VC domains, SDHI/RPC/CSI/VIN/display/AVB/audio/serial/I2C probing, runtime PM, suspend/resume, and watchdog/interrupt stability during unused-clock pruning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a779h0-cpg-mssr.c -->
