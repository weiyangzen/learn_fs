# subset-b-001137 Research

Grouped research for the listed Qualcomm GCC clock-controller driver files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sc7280.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sc7280.c

## Purpose
Implements the Qualcomm Global Clock Controller driver for SC7280. It describes the SoC-wide GCC clock tree, reset lines, and GDSC power domains consumed by platform devices for PCIe, UFS, USB, SDCC, QUPv3 serial engines, QSPI, PDM, camera/display/video throttle paths, GPU/WPSS/MSS support clocks, and always-on fabric/control clocks. The driver binds to `qcom,gcc-sc7280` and registers its clocks, resets, and power domains with the Linux common clock, reset-controller, and genpd frameworks through the Qualcomm clock-controller helpers.

## Important APIs, Types, And Data
The file is almost entirely static hardware description using Qualcomm clock types. `struct clk_alpha_pll` and `struct clk_alpha_pll_postdiv` define GPLL0/1/4/9/10 and GPLL0 even/odd postdiv outputs using Lucid PLL ops. `struct parent_map` and `struct clk_parent_data` arrays translate hardware mux values into parents such as `bi_tcxo`, `sleep_clk`, GPLL outputs, UFS symbol clocks, PCIe pipe clocks, and USB3 wrapper pipe clocks.

Clock sources are represented mainly by `struct clk_rcg2` plus `struct freq_tbl` tables. Important families include general-purpose clocks, PCIe aux and PHY ref/change clocks, PDM, QSPI, QUPv3 wrap0/wrap1 serial engine RCGs, SDCC1/2/4 app clocks, UFS PHY AXI/ICE/aux/unipro clocks, USB3 primary/secondary master/mock-UTMI/PHY clocks, and security-controller clocks. Branch gates use `struct clk_branch` with `clk_branch2_ops`, halt registers, enable registers, and halt policies such as `BRANCH_HALT`, `BRANCH_HALT_VOTED`, `BRANCH_HALT_SKIP`, and `BRANCH_HALT_DELAY`. Pipe and symbol clock front ends use `clk_regmap_phy_mux`, `clk_regmap_mux`, and read-only `clk_regmap_div` objects.

The published lookup surface is `gcc_sc7280_clocks[]`, which maps 162 dt-binding clock IDs from `dt-bindings/clock/qcom,gcc-sc7280.h` to `struct clk_regmap` instances. `gcc_sc7280_resets[]` maps 16 reset IDs to BCR registers for PCIe, QUSB2 PHY, SDCC, UFS, USB3, and AHB2PHY blocks. `gcc_sc7280_gdscs[]` maps 10 GDSCs, including PCIe, UFS PHY, USB30 primary/secondary, MMNOC MMU TBU votes, and Turing MMU TBU votes. `gcc_sc7280_desc` aggregates the regmap config, clock table, reset table, and GDSC table for registration.

## Control Flow
Kernel initialization is via `subsys_initcall(gcc_sc7280_init)`, which registers `gcc_sc7280_driver`. Device-tree matching on `qcom,gcc-sc7280` calls `gcc_sc7280_probe()`. Probe first maps the MMIO resource with `qcom_cc_map(pdev, &gcc_sc7280_desc)` and returns the mapping error directly if it fails.

After regmap creation, probe performs SC7280-specific register setup before exposing the provider. It forces several branch clocks on with `qcom_branch_set_clk_en()` for camera, display, video, and GPU configuration/XO/AHB paths, then sets bit 13 in register `0x7100c`. It also calls `qcom_branch_set_force_mem_core()` for `gcc_ufs_phy_ice_core_clk`, keeping the UFS PHY ICE core memory island forced while that clock is managed. Probe then registers DFS-capable QUPv3 RCGs through `qcom_cc_register_rcg_dfs()`; only if this succeeds does it call `qcom_cc_really_probe()` to register clocks, resets, and GDSCs with the kernel frameworks. Module exit unregisters the platform driver.

## State And Persistence
Runtime state is hardware register state in the GCC MMIO region and framework-owned clock/reset/power-domain registrations. The driver itself has no dynamic allocations or persistent files beyond resources allocated by the Qualcomm common clock helpers. Clock rates are constrained by the static frequency tables and encoded into RCG registers at runtime by common clock operations. Branch enables and halt status are held in CBCR/vote registers; reset state is controlled through BCR register writes; GDSC state is held in GDSCR registers and exposed to genpd.

The probe-time always-on writes intentionally persist for the lifetime of the boot and protect interconnect/control paths that should not be disabled by ordinary clock consumers. DFS registration adds serial-engine RCGs to Qualcomm's dynamic frequency switching path for QUPv3 wrap0 and wrap1 ports, so rate changes can be coordinated with the hardware DFS mechanism rather than treated as simple one-off RCG writes.

## Dependencies And Integration Points
The driver depends on Linux platform-driver and OF matching, `regmap`, common clock provider APIs, Qualcomm clock helpers in `drivers/clk/qcom`, reset support, GDSC support, and the SC7280 dt-binding IDs. External parent clocks are resolved by firmware names such as `bi_tcxo`, `sleep_clk`, `pcie_0_pipe_clk`, `pcie_1_pipe_clk`, UFS symbol clocks, and USB3 wrapper pipe clocks; missing or mismatched DT clock names will break parts of the tree.

Integration points are broad: PCIe controllers consume aux, cfg, AXI, pipe, refgen/refchange clocks plus PCIe GDSCs and resets; UFS consumes AXI, ICE, PHY aux, symbol, unipro clocks plus UFS GDSC/reset; USB controllers and PHYs consume master, mock UTMI, sleep, com aux, pipe clocks and USB GDSCs/resets; SDHCI consumes SDCC app/AHB/ICE clocks; QUPv3 serial ports rely on DFS-enabled RCGs and voted AHB/core branches. Device tree must use IDs from `qcom,gcc-sc7280.h`, and the binding document must stay aligned with the clocks, resets, power domains, and parent names implemented here.

## Risks
Register offsets, mux values, and dt-binding indices are the primary risk: a one-entry shift in `gcc_sc7280_clocks[]`, reset IDs, or GDSC IDs can route consumers to the wrong hardware. Parent-map mistakes can select an invalid GPLL, XO, sleep, pipe, or symbol parent and produce silent rate or enable failures. The probe-time always-on list is sensitive because removing one of those writes may cause later subsystem hangs, while adding unnecessary always-on clocks increases idle power.

Halt-check policy is also risky. `BRANCH_HALT_SKIP` and `BRANCH_HALT_DELAY` are used for clocks whose hardware status may not behave like ordinary CBCRs; changing them to strict halt checks can introduce enable/disable timeouts. Conversely, using skipped checks too broadly can hide clocks that never actually turn on. UFS ICE force-memory handling is a specific integration hazard because storage stability depends on both rate programming and the memory-core retention behavior.

## Test Signals
Build-level signals are successful compilation of `drivers/clk/qcom/gcc-sc7280.c` and dt-binding consistency with `qcom,gcc-sc7280.h` and `qcom,gcc-sc7280.yaml`. Boot signals include a successful `gcc-sc7280` probe, no unresolved parent-clock warnings, no `qcom_cc_really_probe()` failures, and populated `/sys/kernel/debug/clk/clk_summary` entries with expected parentage and rates.

Functional signals should cover PCIe link training on both controllers, UFS enumeration and high-speed operation, USB primary/secondary host/device behavior, SDCC1/2/4 card or eMMC traffic, QUPv3 UART/I2C/SPI rate changes, QSPI access, and suspend/resume. Negative signals include clock enable timeouts, GDSC transition failures, reset-controller failures, serial baud drift, UFS ICE errors, PCIe pipe-clock problems, and unexpected power regressions from always-on or voted branch changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sc7280.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sc8180x.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sc8180x.c

## Purpose
Implements the Qualcomm Global Clock Controller driver for SC8180x. It publishes the main GCC clock, reset, and GDSC topology for a larger SC8180x platform, covering Ethernet, NPU, GPU, four PCIe controllers, PCIe PHY refgen, multiple USB3 controllers including multiport USB, UFS memory/card/card2 paths, QUPv3 serial wrappers, SDCC, TSIF, QSPI, PDM, camera/display/video fabric clocks, and critical CPU/NPU/GPU/control fabric clocks. The driver binds to `qcom,gcc-sc8180x` and delegates most registration to the modern Qualcomm `qcom_cc_probe()` path.

## Important APIs, Types, And Data
The file statically declares the GCC topology using Qualcomm clock types. GPLL0/1/4/7/9 are `struct clk_alpha_pll` instances using TRION PLL registers and fixed TRION ops; GPLL0 also exposes an even post-divider through `struct clk_alpha_pll_postdiv`. `trion_vco[]` constrains supported VCO range, and parent maps select `bi_tcxo`, `sleep_clk`, `aud_ref_clk`, GPLL outputs, and named GPLL2/GPLL5 parents.

Clock-rate generation is handled by many `struct clk_rcg2` instances with `struct freq_tbl` tables. Key RCG families include EMAC PTP/RGMII, GP1-GP5, NPU AXI, PCIe aux/refgen, PDM, QSPI and QSPI_1, QUPv3 wrap0/wrap1/wrap2 serial engines, SDCC2/4, TSIF, UFS card/card2/phy AXI/ICE/PHY/unipro, USB30 MP/primary/secondary master and mock-UTMI, and USB3 PHY aux clocks. Branch gates use `struct clk_branch` and `clk_branch2_ops` with a mix of strict, voted, skipped, and delayed halt checks. Several UFS paths have both normal and hardware-controlled branch variants for AXI, ICE, PHY aux, and unipro clocks.

The exported clock table, `gcc_sc8180x_clocks[]`, maps 239 dt-binding IDs to clock providers, including the GPLLs themselves. `gcc_sc8180x_resets[]` maps 49 reset IDs, including EMAC, GPU, MMSS, NPU, PCIe controllers and PHYs, QUP wrappers, QUSB2 PHY instances, USB3 PHY/DP/UniPHY blocks, SDCC, TSIF, UFS, USB30, AHB2PHY, and delayed video AXI clock BCRs. `gcc_sc8180x_gdscs[]` maps 16 GDSCs for EMAC, four PCIe controllers, UFS card/card2/phy, USB MP/primary/secondary, and MMNOC/Turing vote domains. `gcc_sc8180x_driver_data` supplies critical CBCRs, DFS RCGs, and a register-configuration callback to `qcom_cc_probe()`.

## Control Flow
Initialization uses `core_initcall(gcc_sc8180x_init)`, registering `gcc_sc8180x_driver` early in boot. Matching on `qcom,gcc-sc8180x` calls `gcc_sc8180x_probe()`, which simply returns `qcom_cc_probe(pdev, &gcc_sc8180x_desc)`. Unlike the SC7280 driver, this file does not manually call `qcom_cc_map()`, set critical branches, register DFS, then call `qcom_cc_really_probe()`; those steps are described through `qcom_cc_desc.driver_data`.

During the shared probe path, the regmap is created from `gcc_sc8180x_regmap_config`, critical CBCR registers in `gcc_sc8180x_critical_cbcrs[]` are kept enabled, DFS-capable QUPv3 RCGs from `gcc_sc8180x_dfs_clocks[]` are registered, and `clk_sc8180x_regs_configure()` runs. That callback updates registers `0x4d110` and `0x71028` to disable the GPLL0 active input to NPU and GPU through MISC registers. Registration then exposes the clocks, resets, and GDSCs described by `gcc_sc8180x_desc`. Module exit unregisters the platform driver.

## State And Persistence
Persistent runtime state is MMIO state in the SC8180x GCC register block plus framework registrations. The maximum modeled register is `0xc0004`; accesses are 32-bit, stride-4, fast-IO regmap operations. Static frequency tables define legal rates and parent selections, while active clock rate, mux, divider, branch-enable, vote, and halt state reside in hardware registers.

The descriptor sets `.use_rpm = true`, so integration with Qualcomm RPM-aware clock handling is part of this driver's runtime behavior. Critical CBCRs keep video, camera, display, CPUSS GNOC/DVM, NPU config AHB, and GPU config AHB clocks from being disabled. GDSC state is exposed through genpd and held in GDSCR registers; most local peripheral domains use `POLL_CFG_GDSCR`, while shared MMNOC/Turing vote domains use `VOTABLE`. Reset state is controlled through BCR entries, with video AXI reset mappings using bit-specific delayed reset descriptions.

## Dependencies And Integration Points
The driver depends on Linux platform/OF probing, `regmap`, common clock APIs, reset-controller support, Qualcomm GCC helper code, GDSC support, and `dt-bindings/clock/qcom,gcc-sc8180x.h`. Parent clocks must be available under names such as `bi_tcxo`, `sleep_clk`, `aud_ref_clk`, and named GPLL2/GPLL5 providers. The driver also relies on the common Qualcomm probe implementation understanding `struct qcom_cc_driver_data` for critical CBCRs, DFS RCGs, and register callbacks.

Consumers include EMAC for PTP/RGMII/AXI/AHB clocks and EMAC GDSC/reset; NPU for high-rate AXI and voted trigger/AT clocks; PCIe 0-3 controllers for aux, cfg, AXI, pipe, clkref, PHY refgen, GDSC, and resets; UFS memory/card/card2 controllers for AXI/ICE/PHY/unipro/symbol/clkref clocks and GDSCs; USB30 MP/primary/secondary controllers and PHYs for master, mock-UTMI, sleep, aux, com-aux, pipe, clkref, GDSC, and resets; QUPv3 wrappers for serial bus clocks and DFS; SDCC2/4, TSIF, PDM, QSPI, GPU, display, camera, and video blocks for their clock/reset needs. Binding and dt-binding ID drift would directly affect those consumers.

## Risks
The largest risks are table alignment and hardware-description accuracy. With 239 clocks and 49 resets, ID mismatches against `qcom,gcc-sc8180x.h` can miswire consumers in ways that compile cleanly but fail at runtime. The four PCIe instances and three USB30 groups have many similar offsets, making copy/paste register errors plausible. UFS card, UFS card2, and UFS phy clocks share similar AXI/ICE/PHY/unipro patterns with both normal and hardware-control branches, so incorrect halt policy or source selection can break storage power sequencing.

The shared `qcom_cc_probe()` driver-data path reduces custom probe code but makes correctness depend on the common helper honoring critical CBCRs, DFS RCGs, and register configuration in the intended order. The `clk_sc8180x_regs_configure()` writes are opaque SoC-specific policy; removing or changing them can affect NPU/GPU GPLL0 active input behavior. `.use_rpm = true` introduces integration risk with RPM-managed clock state and vote semantics. Critical clocks protect stability but can also hide missing consumers or raise idle power.

## Test Signals
Build signals are successful compilation, no dt-binding enum mismatches, and schema consistency with `qcom,gcc-sc8180x.yaml`. Probe signals are successful `gcc-sc8180x` registration, no parent-resolution warnings, and populated debugfs clock summaries showing GPLL, RCG, branch, and critical-clock state. Common helper behavior should be validated by confirming critical CBCRs remain enabled and DFS RCGs for QUPv3 wrap0/wrap1/wrap2 are registered.

Functional signals should cover EMAC link and PTP clocking, NPU/GPU initialization, PCIe link training across all enabled controllers, UFS memory/card/card2 enumeration and high-speed transfers, USB MP/primary/secondary operation, SDCC2/4 traffic, TSIF reference behavior, QUPv3 serial rates, QSPI access, and suspend/resume across GDSC-backed domains. Failure signals include branch halt timeouts, GDSC polling failures, RPM vote mismatches, reset timeout regressions on delayed video AXI resets, storage symbol-clock failures, PCIe pipe/clkref failures, and unexpected idle-power changes around critical CBCR handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sc8180x.c -->
