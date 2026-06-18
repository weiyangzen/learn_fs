# subset-b-001140 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sdx65.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sdx65.c

## Purpose

`gcc-sdx65.c` is the Qualcomm Global Clock Controller driver for the SDX65 platform. It describes the SDX65 GCC MMIO block to the common Qualcomm clock framework, reset framework, and generic power-domain support. Device-tree consumers use IDs from `dt-bindings/clock/qcom,gcc-sdx65.h`; this file maps those IDs onto GPLL outputs, RCGs, muxes, dividers, branch gates, GDSCs, and reset registers.

The file is primarily declarative. It does not implement new clock algorithms; it instantiates shared Qualcomm clock types with SDX65-specific register offsets, parent selector values, rate tables, halt checks, and probe-time keepalive writes.

## Important APIs, Types, And Functions

- `struct clk_alpha_pll gpll0` and `struct clk_alpha_pll_postdiv gpll0_out_even` expose the main Lucid EVO GPLL and its divide-by-2 output. GPLL0 is enabled through vote register `0x6d000` bit 0 and uses `clk_alpha_pll_fixed_lucid_evo_ops`.
- `struct parent_map` plus `struct clk_parent_data` translate RCG selector values into parent clocks. SDX65 uses older `.fw_name` parent lookup for external parents such as `bi_tcxo`, `bi_tcxo_ao`, `sleep_clk`, `pcie_pipe_clk`, and `usb3_phy_wrapper_gcc_usb30_pipe_clk`.
- `struct clk_regmap_mux` describes PCIe aux, PCIe pipe, and USB3 PHY pipe source muxes. The pipe muxes choose between PHY-provided pipe clocks and TCXO fallback-like parents.
- `struct freq_tbl` tables define legal rates for BLSP I2C/SPI/UART, CPUSS AHB, GP clocks, PCIe aux/rchng, PDM, SDCC1, USB30 master/mock UTMI, and USB3 PHY aux clocks.
- `struct clk_rcg2` entries implement programmable root clock generators through `clk_rcg2_ops`.
- `struct clk_regmap_div` entries expose read-only postdividers for CPUSS AHB and USB30 mock UTMI.
- `struct clk_branch` entries are leaf or vote gates. Their `halt_check` choices distinguish normal gates, voted gates, delayed status checks for pipe/GDSC-related clocks, and hardware clock gating metadata through `hwcg_reg`/`hwcg_bit`.
- `struct gdsc` models the `usb30_gdsc` and `pcie_gdsc` power domains.
- `struct qcom_reset_map gcc_sdx65_resets[]` maps reset IDs for BLSP QUP/UART, PCIe, PDM, QUSB2PHY, SDCC1, USB30, USB3 PHY, and USB PHY CFG blocks.
- `gcc_sdx65_probe()` performs the only imperative hardware setup: it maps the GCC regmap, forces a few infrastructure clocks on, then calls `qcom_cc_really_probe()`.

## Control Flow

Initialization registers a platform driver from `subsys_initcall(gcc_sdx65_init)`. The driver matches `compatible = "qcom,gcc-sdx65"`. Probe does the following:

1. Calls `qcom_cc_map(pdev, &gcc_sdx65_desc)` to map the GCC register space using `gcc_sdx65_regmap_config`.
2. Keeps infrastructure clocks enabled with `qcom_branch_set_clk_en(regmap, 0x6d008)` and direct `regmap_update_bits()` writes for bits 21 and 22 in the same vote register. Comments identify these as `GCC_SYS_NOC_CPUSS_AHB_CLK`, `GCC_CPUSS_AHB_CLK`, and `GCC_CPUSS_GNOC_CLK`.
3. Registers clocks, resets, and GDSCs by passing the descriptor and mapped regmap to `qcom_cc_really_probe()`.

After probe, consumers interact through standard CCF, reset-controller, and power-domain APIs. Rate changes select rows from each `freq_tbl`; branch enable/disable operations write the configured enable registers and poll according to `halt_check`.

## State And Persistence Behavior

The driver's persistent state is hardware register state in the GCC block. There is no private runtime data structure, no suspend/resume callback, no workqueue, and no software persistence. Clock enable bits, parent selectors, dividers, reset assertions, and GDSC state persist in registers until reset, firmware intervention, or later framework operations.

Probe intentionally changes hardware state by enabling several CPUSS/NOC clocks. Those writes are not represented as exported branches in the clock array and should be treated as platform bring-up requirements. GDSC state is managed through the genpd integration after registration. The reset map exposes reset controls but does not assert anything at probe time.

## Dependencies And Integration Points

- Linux CCF and Qualcomm helpers: `clk-alpha-pll.h`, `clk-rcg.h`, `clk-branch.h`, `clk-regmap-mux.h`, `clk-regmap-divider.h`, and `clk-regmap.h`.
- Regmap: 32-bit registers and values, 4-byte stride, `max_register = 0x1f101c`, `fast_io = true`.
- Device tree: binding IDs from `qcom,gcc-sdx65.h` and external parent names referenced by `.fw_name`.
- Platform bus/module lifecycle: platform driver register/unregister through `subsys_initcall()` and `module_exit()`.
- Power domains: `gdsc.h` integrates USB30 and PCIe GDSCs into genpd.
- Reset framework: `reset.h` consumes the `qcom_reset_map` array.

## Subsystems Covered

The clock inventory covers BLSP1 QUP1-4 I2C/SPI application clocks, four BLSP UART application clocks, BLSP AHB/sleep votes, CPUSS AHB source/postdivider, GP1-3, PCIe aux/pipe/rchng/sleep/AXI/AHB/link reference clocks, PDM, SDCC1, USB30 master/mock UTMI/AXI/AHB/sleep clocks, USB3 PHY aux/pipe/reference clocks, USB PHY CFG AHB2PHY, boot ROM AHB, and XO-derived PCIe/link clocks.

## Risks And Edge Cases

- Parent names are binding-sensitive. A missing or renamed `bi_tcxo`, `bi_tcxo_ao`, `sleep_clk`, PCIe pipe, or USB pipe parent can cause probe deferral or incorrect parent selection.
- Pipe-clock muxes and delayed halt checks depend on PHY behavior. Replacing `BRANCH_HALT_DELAY` with strict halt polling can create false failures around PCIe/USB GDSC or PHY-controlled clocks.
- The keepalive writes in probe are critical for CPUSS and NOC reachability. Removing them can break later register access or dependent subsystem bring-up.
- Rate tables are hardware-facing. Incorrect fractional UART rows, SDCC1 rows, or USB mock UTMI settings can cause silent peripheral instability.
- Reset offsets overlap dense GCC register regions. A wrong reset-map entry can reset live PCIe/USB/BLSP hardware.
- The file uses `.fw_name` parent lookup rather than indexed DT parent data used in newer GCC drivers, so binding conversion requires care.

## Test Signals

- Build with the SDX65 GCC option enabled and verify no missing binding IDs or incompatible clock init-data warnings.
- Boot an SDX65 device tree containing `qcom,gcc-sdx65` and check that dependent BLSP, SDCC1, PCIe, USB, and PDM devices no longer defer on GCC resources.
- Inspect `/sys/kernel/debug/clk/clk_summary` for exported names such as `gpll0`, `gpll0_out_even`, `gcc_blsp1_uart1_apps_clk`, `gcc_sdcc1_apps_clk`, `gcc_pcie_pipe_clk`, and `gcc_usb3_phy_pipe_clk`.
- Exercise UART/SPI/I2C, SDCC1 storage, PCIe link training, and USB3 operation.
- Verify reset consumers can assert/deassert BLSP, PCIe, USB PHY, SDCC1, and PDM resets without corrupting unrelated GCC state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sdx65.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sdx75.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sdx75.c

## Purpose

`gcc-sdx75.c` is the Qualcomm Global Clock Controller driver for the SDX75 modem platform. It exports SDX75 GCC clocks, resets, and GDSC power domains to Linux using IDs from `dt-bindings/clock/qcom,sdx75-gcc.h`. Compared with SDX65, this driver describes a larger clock topology: multiple GPLLs, dual EMAC/SGMII domains, three PCIe domains, QUPv3 serial engines with DFS support, SDCC1/SDCC2, USB3, PDM, and related reference clocks.

The implementation remains mostly data-driven. Shared Qualcomm clock operations perform PLL, RCG, mux, divider, branch, reset, and power-domain mechanics from the register metadata encoded here.

## Important APIs, Types, And Functions

- The local `DT_*` enum defines external parent indices in the GCC node's `clocks` list, including TCXO, sleep clock, EMAC SGMII clocks, PCIe pipe clocks, PCIe20 PHY aux, and USB3 PHY pipe.
- The local `P_*` enum defines hardware parent selector names used in `parent_map` arrays.
- `gpll0`, `gpll4`, `gpll5`, `gpll6`, and `gpll8` are Lucid OLE alpha PLLs enabled through `0x7d000` vote bits. `gpll0_out_even` provides the divide-by-2 GPLL0 output.
- Numerous `parent_map`/`clk_parent_data` pairs map RCG selector values to either indexed DT parents or internal GPLL hardware clocks.
- `struct clk_regmap_mux` and `struct clk_regmap_phy_mux` model EMAC SGMII RX/TX muxes and PCIe/USB pipe sources. PCIe pipe clocks use `clk_regmap_phy_mux_ops`, while SGMII and USB pipe paths use regmap mux operations.
- `struct clk_rcg2` entries define EMAC EEE/PTP/RGMII/PHY aux clocks, GP clocks, PCIe aux/rchng clocks, PDM2, QUPv3 serial sources S0-S8, SDCC1/SDCC2, USB30 master/mock UTMI, and USB3 PHY aux. Most use `clk_rcg2_shared_ops`; SDCC sources use shared floor ops to avoid overclocking storage buses.
- `struct clk_regmap_div` exposes read-only pipe div2 and USB mock UTMI postdividers.
- `struct clk_branch` entries are the exported gates and votes. SDX75 heavily uses `BRANCH_HALT_VOTED` for shared infrastructure, `BRANCH_HALT_DELAY` for PHY/pipe and SGMII paths, and `BRANCH_HALT_ENABLE` for reference-clock enable bits.
- Ten `struct gdsc` instances cover EMAC0/1, PCIe root/PHY domains for three PCIe blocks, USB30, and USB3 PHY. They include wait values and `RETAIN_FF_ENABLE`.
- `gcc_dfs_clocks[]` registers QUPv3 RCGs for dynamic frequency switching via `qcom_cc_register_rcg_dfs()`.
- `gcc_sdx75_probe()` maps registers, registers DFS data, enables two always-on PCIe link clocks, then registers the GCC descriptor.

## Control Flow

`subsys_initcall(gcc_sdx75_init)` registers the platform driver. OF matching uses `compatible = "qcom,sdx75-gcc"`. Probe proceeds in a short sequence:

1. `qcom_cc_map()` maps the regmap using a 32-bit, 4-byte-stride config with `max_register = 0x1f41f0`.
2. `qcom_cc_register_rcg_dfs()` registers QUPv3 S0-S8 RCGs for DFS. Probe aborts if this fails.
3. `qcom_branch_set_clk_en()` enables `0x3e004` and `0x3e008`, identified as `GCC_AHB_PCIE_LINK_CLK` and `GCC_XO_PCIE_LINK_CLK`.
4. `qcom_cc_really_probe()` registers the clock, reset, and GDSC arrays with the frameworks.

Runtime control is delegated to the common clock framework. Consumers request clock handles by binding ID, set rates through the RCG tables, vote or gate branches, assert resets through `qcom_reset_map`, and control GDSCs through genpd.

## State And Persistence Behavior

The file has no private mutable driver state beyond framework-registered objects. Hardware register values hold persistent state for PLL votes, RCG parent/rate programming, branch enables, GDSC power state, and resets.

Probe performs persistent writes for DFS registration and two always-on PCIe link clocks. It does not configure GPLL rates in probe; the fixed PLL definitions rely on firmware or shared PLL operations. QUPv3 DFS metadata persists as framework state, while actual frequency choices remain in hardware registers and are changed by consumers through CCF.

## Dependencies And Integration Points

- Linux CCF and Qualcomm clock helpers, including alpha PLL, branch, RCG, regmap divider, regmap mux, and regmap PHY mux support.
- `clk-regmap-phy-mux.h` is important for PCIe pipe clock switching because pipe clocks are PHY-provided and synchronized with PHY state.
- Device-tree binding order is critical because parents use `.index = DT_*`.
- Reset framework receives `gcc_sdx75_resets[]`, including EMAC, eMMC, PCIe root/PHY/link-down/NOCSR, QUSB2PHY, TCSR PCIe, USB30, USB3 PHY, and USB PHY CFG resets.
- GDSC/genpd integration exposes EMAC, PCIe, and USB power domains.
- Platform lifecycle uses `subsys_initcall()` and `module_exit()`.

## Subsystems Covered

SDX75 covers dual EMAC blocks with AXI/AHB, EEE, PTP, RGMII, SGMII MAC/RPCS/XGXS RX/TX clocks and reference enables; three PCIe clock domains with aux, config AHB, master/slave AXI, Q2A, pipe, pipe-div2, rchng, sleep, and clkref clocks; QUPv3 wrapper 0 core and nine serial source/gate pairs; SDCC1/eMMC and SDCC2; USB30 and USB3 PHY clocks; GP1-3; PDM; boot ROM AHB; USB2/USB3 reference enables; and the corresponding GDSCs and resets.

## Risks And Edge Cases

- Indexed external parents must match the binding and DTS clock order. EMAC SGMII RX/TX and PCIe pipe parents are easy to misorder because many names are similar.
- Shared RCG ops and DFS registration for QUPv3 are coupled. Adding or removing QUP sources without updating `gcc_dfs_clocks[]` can break serial-engine DFS behavior.
- SDCC clocks use floor rounding. Converting them to non-floor ops can overclock eMMC/SD paths.
- PHY pipe and SGMII clocks use delayed halt checks. Strict halt polling can fail when PHYs or MACs own status timing.
- GDSC wait values and `RETAIN_FF_ENABLE` are part of power sequencing. Incorrect changes may cause PCIe, EMAC, or USB retention/power-collapse failures.
- Probe-time always-on PCIe link clocks are not normal consumer-managed branches; removing them can affect early PCIe/link infrastructure.
- Reset coverage is dense and spans multiple PCIe instances. Instance-number mixups are a realistic maintenance risk.

## Test Signals

- Build with the SDX75 GCC config enabled and confirm all binding IDs resolve.
- Boot with `qcom,sdx75-gcc` and verify GCC probes before EMAC, PCIe, QUPv3, SDCC, and USB consumers finish probing.
- Check `clk_summary` for GPLLs, `gcc_emac0_*`, `gcc_emac1_*`, `gcc_pcie_*`, `gcc_pcie_1_*`, `gcc_pcie_2_*`, QUPv3 S0-S8 clocks, SDCC clocks, and USB3 pipe/aux clocks.
- Exercise EMAC0/1 link modes, PCIe link training on all described instances, QUP UART/SPI/I2C transfers, eMMC/SD, and USB3.
- Validate GDSC on/off sequencing through runtime PM for EMAC, PCIe, and USB.
- Test reset controls for EMAC, PCIe root/PHY/link-down paths, QUSB2PHY, USB30, USB3 PHY, and eMMC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sdx75.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm4450.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm4450.c

## Purpose

`gcc-sm4450.c` is the Qualcomm Global Clock Controller driver for the SM4450 SoC. It exposes the SoC's GCC clock tree, resets, and power domains using IDs from `dt-bindings/clock/qcom,sm4450-gcc.h`. The topology spans mobile application-processor subsystems: GP clocks, QUPv3 serial wrappers, SDCC/eMMC, UFS, PCIe, USB3/eUSB references, PDM, camera/display/video/GPU/NOC vote clocks, Venus/video clocks, GDSCs, and reset lines.

Like other Qualcomm GCC drivers, it is mostly a board/SoC register description. Shared CCF and Qualcomm helpers implement the behavior; this file supplies register offsets, parent maps, rate tables, halt policies, reset maps, and a small amount of probe-time configuration.

## Important APIs, Types, And Functions

- The `DT_*` enum defines indexed external parents: TCXO, sleep clock, PCIe pipe, UFS RX/TX symbol clocks, and USB3 PHY pipe.
- The `P_*` enum names hardware parent selectors, including GPLL0 main/even/odd and GPLL1/3/4/9/10 outputs.
- `lucid_evo_vco` and `gcc_gpll3_config` define a configurable Lucid EVO PLL used for video/Venus rates. Probe calls `clk_lucid_evo_pll_configure(&gcc_gpll3, regmap, &gcc_gpll3_config)`.
- `gcc_gpll0`, `gcc_gpll1`, `gcc_gpll4`, `gcc_gpll9`, and `gcc_gpll10` are fixed Lucid EVO PLLs; `gcc_gpll0_out_even` and `gcc_gpll0_out_odd` expose divide-by-2 and divide-by-3 postdividers.
- `parent_map`/`clk_parent_data` arrays map selector values to indexed DT parents and internal PLL hardware.
- `struct clk_regmap_phy_mux` models the PCIe pipe source. `struct clk_regmap_mux` models UFS RX/TX symbol and USB3 primary PHY pipe muxes.
- `struct clk_rcg2` entries define GP, PCIe aux/rchng, PDM2, QUPv3 wrapper 0/1 serial sources, SDCC1/SDCC1 ICE/SDCC2, UFS AXI/ICE/PHY aux/UniPro, USB30 primary master/mock UTMI/PHY aux, and video Venus sources. QUP and many subsystem clocks use `clk_rcg2_shared_ops`; SDCC clocks use shared floor ops.
- `struct clk_branch` entries export gateable clocks and votes. SM4450 includes many NOC/MMU/GPU/video vote clocks where `BRANCH_HALT_SKIP`, `BRANCH_HALT_VOTED`, or AON branch ops are intentional.
- GDSCs include PCIe0, UFS PHY, USB30 primary, VCODEC0, and Venus. Some use `POLL_CFG_GDSCR`, `RETAIN_FF_ENABLE`, `VOTABLE`, or `HW_CTRL`.
- `gcc_dfs_clocks[]` registers QUPv3 wrapper 0 and wrapper 1 serial RCGs for DFS.
- `gcc_sm4450_probe()` configures GPLL3, registers DFS, forces UFS ICE memory core behavior, enables several always-on camera/display/GPU/video clocks, sets a video AXI bit, and then registers the descriptor.

## Control Flow

The platform driver is registered at `subsys_initcall(gcc_sm4450_init)` and matches `compatible = "qcom,sm4450-gcc"`. Probe performs these ordered steps:

1. Map the GCC register block through `qcom_cc_map()` using `max_register = 0x1f41f0`.
2. Configure `gcc_gpll3` with `clk_lucid_evo_pll_configure()`, making its video/Venus rate plan available.
3. Register QUPv3 DFS RCGs with `qcom_cc_register_rcg_dfs()`. Probe returns an error on failure.
4. Call `qcom_branch_set_force_mem_core(regmap, gcc_ufs_phy_ice_core_clk, true)` for the UFS ICE core clock.
5. Enable always-on camera, display, GPU config AHB, and video AHB/XO clocks with `qcom_branch_set_clk_en()`.
6. Set bit 21 at `0x4201c`, associated with `gcc_venus_ctl_axi_clk` state/control.
7. Register clocks, resets, and GDSCs with `qcom_cc_really_probe()`.

Runtime behavior is then framework-driven: CCF consumers set rates and enable branches, reset consumers assert mapped resets, and genpd manages the GDSCs.

## State And Persistence Behavior

The main persistent state is in GCC hardware registers. Unlike the two SDX drivers in this work item, SM4450 actively configures a PLL at probe. The GPLL3 configuration writes PLL L/alpha/config/user fields, and those settings persist until reset or reconfiguration. Probe also makes persistent enable writes for camera/display/GPU/video infrastructure, sets UFS ICE force-mem-core behavior, registers DFS metadata, and sets a video AXI control bit.

The driver itself stores no private state and has no suspend/resume path. GDSC, reset, and clock object state is owned by common frameworks after registration.

## Dependencies And Integration Points

- Qualcomm CCF helpers for alpha PLL, branch, RCG, regmap mux/divider, PHY mux, reset, and GDSC handling.
- Device-tree parent order is binding-sensitive because `.index = DT_*` is used throughout.
- UFS integration depends on external UFS symbol clocks and on UFS ICE/core/UniPro/AXI branches.
- PCIe and USB depend on PHY-provided pipe clocks and reference-clock gates.
- Camera, display, GPU, MMU/TBU, DDRSS, and video clocks are exposed as GCC-managed vote or infrastructure clocks for other subsystem drivers.
- Reset framework covers camera, display, GPU, PCIe, PDM, QUPv3 wrappers, QUSB2PHY, SDCC, UFS, USB3/DP PHYs, Venus, VCODEC0, and video resets, including two ARES entries with 400 us delays.

## Subsystems Covered

The driver covers GP1-3, two QUPv3 wrappers with five serial engines each, SDCC1 with ICE and SDCC2, UFS PHY clocks including AHB/AXI/ICE/UniPro/symbol/aux paths, PCIe0 aux/pipe/rchng/AXI/AHB/reference clocks, USB30 primary and USB3 PHY clocks, eUSB/USB/UFS reference enables, PDM, GPU GPLL votes and NOC clocks, camera/display AHB and AXI vote clocks, MMU/TBU vote clocks, QMIP AHB clocks, and video/Venus clocks with VCODEC0 and Venus GDSCs.

## Risks And Edge Cases

- Probe-time GPLL3 configuration is a real hardware programming step. Incorrect PLL config values can break video/Venus rates rather than merely hiding an exported clock.
- UFS has several coupled clocks and special hardware-control branches. Mistakes around ICE, UniPro, symbol clocks, or force-mem-core behavior can cause storage failures.
- Many branches intentionally skip or delay halt checks because status is unreliable or controlled by another block. Tightening halt checks can introduce enable/disable failures.
- GDSC flags differ by domain. For example PCIe0 is votable, VCODEC0 uses hardware control, and several domains poll CFG_GDSCR; changing flags can break runtime PM sequencing.
- Indexed external parents must match DTS order, especially UFS RX/TX symbol and USB/PCIe pipe parents.
- Always-on camera/display/GPU/video votes in probe are platform assumptions. Removing them can break dependent subsystem register access.
- Reset entries include both full block resets and ARES bit resets with delays. Using the wrong reset ID can disrupt active video or PHY hardware.

## Test Signals

- Build with the SM4450 GCC option enabled and check for binding, initializer, and unused-symbol issues.
- Boot an SM4450 device tree with `qcom,sm4450-gcc`; verify GCC probes before UFS, PCIe, USB, QUPv3, camera, display, GPU, and video consumers finish probing.
- Inspect `clk_summary` for `gcc_gpll3`, QUPv3 wrapper 0/1 clocks, `gcc_sdcc1_ice_core_clk`, UFS clocks, PCIe0 pipe/div2 clocks, USB3 primary clocks, GPU/NOC vote clocks, and video/Venus clocks.
- Exercise UFS storage including ICE paths, SDCC1/2, QUP UART/SPI/I2C, PCIe link training, USB3 operation, camera/display/video driver probe, and Venus encode/decode if available.
- Validate GDSC transitions for PCIe0, UFS PHY, USB30 primary, VCODEC0, and Venus under runtime PM.
- Test reset consumers for QUP wrappers, storage, PCIe, USB/DP PHYs, video/Venus, camera/display/GPU, and ARES delayed resets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm4450.c -->
