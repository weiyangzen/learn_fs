# subset-b-001135 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-qcs8300.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-qcs8300.c

## Purpose
This file is the Qualcomm Global Clock Controller driver for the QCS8300 SoC. It describes the GCC clock tree, reset lines, and GDSC power domains that Linux exposes to consumers through the common clock framework, reset controller framework, and Qualcomm CC/GDSC helpers. The hardware blocks represented here include GPLLs, RCG frequency generators, branch gates, register muxes for PHY-sourced clocks, divider wrappers, QUPv3 serial engines, SDCC1, UFS PHY, USB2/USB3, dual PCIe controllers, EMAC0, GPU/DDR interconnect clocks, camera/display/video infrastructure clocks, and assorted clock references.

## Important APIs, Types, And Functions
- `struct clk_alpha_pll` and `struct clk_alpha_pll_postdiv` define fixed Lucid EVO GPLL providers: `gcc_gpll0`, `gcc_gpll1`, `gcc_gpll4`, `gcc_gpll7`, `gcc_gpll9`, and `gcc_gpll0_out_even`.
- `struct parent_map` plus `struct clk_parent_data` encode the hardware parent selector values for RCGs and muxes, including external DT clock indices such as `DT_BI_TCXO`, `DT_SLEEP_CLK`, PCIe pipe clocks, UFS symbol clocks, USB3 pipe clock, and EMAC `DT_RXC0_REF_CLK`.
- `struct clk_regmap_mux` and `struct clk_regmap_phy_mux` handle PHY-facing muxes for PCIe pipe/aux, UFS symbol, and USB3 pipe sources. The PHY muxes depend on one external pipe clock parent and use `clk_regmap_phy_mux_ops`.
- `struct clk_rcg2` objects plus `struct freq_tbl` arrays define programmable sources for EMAC, GP clocks, PCIe aux/rchng, PDM, QUPv3 serial ports, SDCC1 apps/ICE, UFS AXI/ICE/UniPro/aux, USB2, and USB3.
- `struct clk_regmap_div` supplies read-only dividers for PCIe pipediv2 clocks, QUPv3 wrap3 S0, and USB mock UTMI postdivs.
- `struct clk_branch` objects expose gateable branch clocks with halt checks, optional hardware clock gating bits, parents, and `CLK_SET_RATE_PARENT` propagation where rate changes should reach the RCG or mux.
- `struct gdsc` entries expose power domains for EMAC0, PCIe0, PCIe1, UFS PHY, USB20 primary, and USB30 primary.
- `gcc_qcs8300_clocks`, `gcc_qcs8300_resets`, and `gcc_qcs8300_gdscs` are the exported descriptor tables indexed by `dt-bindings/clock/qcom,qcs8300-gcc.h`.
- `gcc_qcs8300_probe()` maps the register space, registers dynamic frequency scaling data for QUP RCGs, forces several infrastructure clocks on, sets FORCE_MEM_CORE_ON for the UFS ICE clock branch, and then calls `qcom_cc_really_probe()`.
- `gcc_qcs8300_init()` registers the platform driver at `subsys_initcall`, and `gcc_qcs8300_exit()` unregisters it for module unload.

## Control Flow
Driver binding starts when a device tree node matches `qcom,qcs8300-gcc`. `gcc_qcs8300_probe()` calls `qcom_cc_map()` with `gcc_qcs8300_desc`, which maps the GCC MMIO resource through regmap using 32-bit registers, 4-byte stride, and a maximum register of `0x472cffc`. If mapping succeeds, the probe registers DFS support for all QUPv3 RCGs listed in `gcc_dfs_clocks`, including wrap0 S0-S7, wrap1 S0-S7, and wrap3 S0. The probe then directly enables always-on infrastructure branch registers for camera AHB/XO, display AHB/XO, GPU config AHB, and video AHB/XO, applies a force-mem-core setting to `gcc_ufs_phy_ice_core_clk`, and finally registers all clocks, resets, and GDSCs through the Qualcomm common-clock descriptor.

After registration, consumers interact with the driver through common framework operations. RCG clocks select a parent from their parent map and program M/N/D and divider fields according to their frequency table. Branch clocks enable or disable hardware bits and poll halt status according to `BRANCH_HALT`, `BRANCH_HALT_VOTED`, `BRANCH_HALT_SKIP`, or `BRANCH_HALT_DELAY`. Votable PCIe GDSCs use collapse control bits under `0x4b104`; other GDSCs use the local GDSCR. Reset consumers assert and deassert mapped BCR or ARES bits through the reset map.

## State And Persistence
The driver has no filesystem or durable storage state. Persistent hardware state is MMIO register state in the GCC block: PLL enable votes, RCG configuration words, branch enable and halt bits, hardware clock gating bits, reset registers, GDSC power-domain registers, and force-mem-core bits. Static C tables are immutable after module load except for framework-managed clock state stored in common clock structures. Runtime clock enable counts, prepared states, rate selections, and power-domain references are held by kernel frameworks and reflected into GCC registers on demand. The explicit always-on writes in probe persist until reset or later firmware/kernel changes.

## Dependencies And Integration Points
The driver depends on the Linux common clock framework, platform device binding, OF matching, regmap, Qualcomm clock helpers (`clk-alpha-pll`, `clk-rcg`, `clk-branch`, `clk-regmap-*`, `clk-regmap-phy-mux`, `common`, `gdsc`, `reset`), and QCS8300 device-tree binding constants. Integration points include device-tree `clocks` phandles for external TCXO, sleep, PCIe pipe, UFS symbol, USB3 pipe, and EMAC reference sources; clock consumers in PCIe, UFS, USB, SDHCI, serial/QUP, Ethernet, GPU, display/camera/video, and interconnect-adjacent drivers; reset consumers for block resets and PHY resets; and genpd users of GCC GDSCs.

## Risks And Edge Cases
- Register offsets and binding indices are tightly coupled to QCS8300 hardware and the dt-binding header. A wrong index in `gcc_qcs8300_clocks` or reset/GDSC arrays can expose the wrong control to a device-tree consumer.
- The file mixes several halt-check modes. `BRANCH_HALT_SKIP` and `BRANCH_HALT_DELAY` are intentional for PHY/ref clocks that may not report ordinary halt status, but using them on the wrong branch can hide enable failures.
- External PHY-derived parents are only valid if the board DTS supplies the expected clock phandles in the same order as the local DT enum. PCIe, UFS, USB, and EMAC links are sensitive to those parents.
- Probe performs direct always-on writes. These are required infrastructure keeps, but they can obscure missing consumer votes or interact with power-management expectations if the hardware contract changes.
- PCIe GDSCs are votable and use shared collapse-control bits. Incorrect masks would affect the other PCIe domain.
- QUPv3 DFS registration must stay in sync with the RCGs that need dynamic frequency switching; missing entries can affect serial rates during runtime changes.
- The UFS ICE force-mem-core call is a targeted workaround/control requirement; moving or dropping it risks UFS inline crypto clock instability.

## Test Signals
Useful validation signals include successful probe without `qcom_cc_map()` or `qcom_cc_really_probe()` errors, registered clock names under debugfs, device-tree consumers resolving all IDs from `qcom,qcs8300-gcc.h`, successful rate set/round operations for SDCC1, QUPv3, UFS, USB, PCIe, and EMAC RCGs, stable PCIe/UFS/USB link bring-up using PHY pipe/symbol clocks, reset toggling for the mapped BCRs, genpd transitions for EMAC/PCIe/UFS/USB GDSCs, and no branch halt timeout warnings when consumers enable clocks. Build-time coverage should include this file in a kernel configuration with `CONFIG_QCOM_GCC_QCS8300` and binding checks for the matching GCC node and its external clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-qcs8300.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-qdu1000.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-qdu1000.c

## Purpose
This file is the Qualcomm Global Clock Controller driver for the QDU1000 SoC. It registers the SoC's GCC clocks, resets, and GDSC power domains with the Linux kernel. Compared with general application-processor GCC drivers, this one is centered on telecom and networking blocks: eCPRI DMA/GSI and clock-controller paths, 100G Ethernet wrapper/debug clocks, PCIe, USB3, SDCC5, QUPv3 wrappers, TSC clocks, PDM, SM bus clocks, and a broad set of GPLL sources.

## Important APIs, Types, And Functions
- `struct clk_alpha_pll` providers define `gcc_gpll0` through `gcc_gpll8`, all using Lucid EVO fixed PLL ops and a common enable register at `0x62018`.
- `struct clk_alpha_pll_postdiv` exposes even outputs for GPLL0, GPLL1, GPLL2, and GPLL5 using the shared divide-by-two post-divider table.
- Parent maps and parent data arrays describe selector encodings for TCXO, sleep, GPLL main/even outputs, PCIe PHY aux/pipe inputs, and USB3 pipe inputs.
- `struct clk_regmap_mux` and `struct clk_regmap_phy_mux` expose PCIe aux/pipe and USB3 pipe clock sources that bridge GCC control with external PHY clocks from device tree.
- RCGs define frequency plans for eCPRI aggregate NOC DMA/GSI, GP1-GP3, PCIe aux/rchng, PDM2, QUPv3 wrap0/wrap1 serial ports, SDCC5 apps/ICE, SM bus XO, TSC, USB30 master/mock UTMI, and USB3 PHY aux.
- Branch clocks expose functional gates for eCPRI, Ethernet debug/100G APB, DDRSS eCPRI, PCIe, PDM, QUPv3, SDCC5, SM bus, SNOC/GEMNOC PCIe fabric, TSC, USB2 ref, and USB3.
- `pcie_0_gdsc`, `pcie_0_phy_gdsc`, and `usb30_prim_gdsc` expose power domains for PCIe controller, PCIe PHY, and primary USB3.
- `gcc_qdu1000_clocks`, `gcc_qdu1000_resets`, and `gcc_qdu1000_gdscs` are the descriptor arrays indexed by `dt-bindings/clock/qcom,qdu1000-gcc.h`.
- `gcc_qdu1000_probe()` maps GCC MMIO, sets FORCE_MEM_CORE_ON for `gcc_pcie_0_mstr_axi_clk` by updating bit 14 at `0x9d024`, registers DFS data for QUPv3 RCGs, and calls `qcom_cc_really_probe()`, reporting failures with `dev_err_probe()`.
- `gcc_qdu1000_init()` and `gcc_qdu1000_exit()` register and unregister the platform driver around the OF compatible `qcom,qdu1000-gcc`.

## Control Flow
The platform driver is registered during subsystem initialization and binds to a matching GCC device-tree node. Probe first maps the register resource using a 32-bit regmap with 4-byte stride and maximum register `0x1f41f0`. Before the clock tree is exposed, probe sets a PCIe master AXI force-memory-core bit to keep memory logic retained as required by the hardware path. It then registers dynamic frequency scaling data for QUPv3 wrap0 and wrap1 serial RCGs, and finally registers all descriptor tables with the Qualcomm common clock core.

Normal runtime control is table-driven after probe. Clock consumers request clocks by binding ID; RCGs select parent PLLs or external sources and program the command-RCGR fields; branch clocks gate hardware and check halt status; PHY muxes follow external pipe clocks; reset consumers toggle BCR registers; and genpd consumers power PCIe/PCIe PHY/USB3 GDSCs. Several fabric and DDRSS/eCPRI clocks use always-on branch ops or skipped halt checks where the hardware does not provide a normal halt transition.

## State And Persistence
The driver does not persist data outside the kernel and GCC hardware. State lives in memory-mapped GCC registers: PLL vote bits, RCG frequency programming, branch enable/halt/hwcg bits, BCR reset registers, GDSC state registers, and the forced PCIe memory-core bit. Common clock framework state tracks prepare/enable counts and rate selections, while genpd tracks power-domain references. Static descriptor tables are fixed after load and are shared for all consumers of the single GCC device.

## Dependencies And Integration Points
The file depends on Linux platform/OF/regmap support, common clock APIs, Qualcomm PLL/RCG/branch/regmap mux/divider/PHY mux helpers, GDSC and reset helpers, and the QDU1000 dt-binding header. Device-tree integration must supply TCXO, sleep, PCIe pipe/aux, and USB3 pipe parent clocks matching the local DT enum. Downstream consumers include eCPRI and Ethernet subsystems, PCIe host and PHY drivers, USB3/USB PHY drivers, SDHCI for SDCC5, QUPv3 serial clients, PDM, TSC, and interconnect/fabric-related blocks.

## Risks And Edge Cases
- The clock table is dense and binding-indexed. Any mismatch with `qcom,qdu1000-gcc.h` can miswire clock, reset, or GDSC consumers.
- The direct `regmap_update_bits()` in probe is a hardware-specific side effect. If the target register or bit definition changes, PCIe behavior or power retention can regress.
- Several PLLs and even post-dividers are exported and also used as parents for eCPRI clock-controller branches. Parent map errors can produce incorrect high-speed fabric or eCPRI rates.
- External PHY clocks are mandatory for PCIe and USB3 pipe paths. DTS parent ordering mistakes can leave muxes pointing at TCXO or an invalid pipe source.
- Some network/fabric clocks use `BRANCH_HALT_SKIP` or always-on branch ops, so ordinary halt polling will not catch every bad hardware transition.
- QUPv3 DFS coverage includes wrap0/wrap1 only; adding or removing serial RCGs must keep `gcc_dfs_clocks` synchronized.
- The GDSC set is smaller than the number of functional blocks, so many blocks rely only on clock/reset control and external power sequencing.

## Test Signals
Strong signals include successful driver probe for `qcom,qdu1000-gcc`, no `Failed to register GCC clocks` error, all dt-binding IDs resolving for clock/reset/GDSC consumers, visible registered clocks in debugfs, valid rate operations for eCPRI DMA/GSI, QUPv3, SDCC5, TSC, PCIe, and USB3 clocks, PCIe and USB3 PHY links receiving their external pipe parents, reset assertions working for eCPRI, Ethernet, PCIe, PDM, QUP, SDCC5, TSC, USB, and PHY BCRs, and genpd transitions for PCIe0, PCIe0 PHY, and USB30 primary. Kernel build coverage should compile this driver with Qualcomm GCC support and device-tree validation should confirm the GCC node's compatible string and external clock list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-qdu1000.c -->
