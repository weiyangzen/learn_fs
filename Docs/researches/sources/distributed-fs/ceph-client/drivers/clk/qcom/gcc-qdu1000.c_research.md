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
