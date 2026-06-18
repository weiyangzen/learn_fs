# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sar2130p.c

## Purpose
Implements the Qualcomm/QTI Global Clock Controller driver for SAR2130P. It exposes a narrower GCC clock set than SA8775P, centered on Lucid OLE GPLLs, PCIe0/PCIe1, USB3 primary, SDCC1, two QUPv3 wrappers, PDM, display/video/GPU/IRIS interconnect clocks, DDRSS SPAD/PCIe support clocks, reset lines, and GDSC power domains for PCIe, USB3, and votable MMU/Turing blocks.

## Important APIs, Types, And Functions
- `struct clk_alpha_pll` describes Lucid OLE GPLL0, GPLL1, GPLL4, GPLL5, GPLL7, and GPLL9; `struct clk_alpha_pll_postdiv` provides GPLL0 even and GPLL9 even postdiv outputs.
- Parent maps connect `bi_tcxo`, sleep clock, GPLL outputs, PCIe pipe clocks, and USB3 pipe clock inputs to RCGs and muxes. The DT clock enum must match `qcom,sar2130p-gcc.h` binding order.
- `struct clk_regmap_phy_mux` handles PCIe pipe clock parents, while `struct clk_regmap_mux` handles the USB3 primary pipe source.
- `struct clk_rcg2` plus frequency tables program DDRSS SPAD, GP1-3, PCIe auxiliary/rchng, PDM2, QUPv3 wrap0/wrap1 serial engines, SDCC1 apps/ICE, USB30 master/mock UTMI, and USB3 PHY auxiliary rates.
- `struct clk_branch` entries gate aggregate/config NoC clocks, GPU/display/video/IRIS clocks, PCIe clock sets, QUPv3 wrapper clocks, SDCC1, PDM, and USB3 branches.
- `struct gdsc` entries cover four votable HLOS MMU/Turing domains plus PCIe0/1 controller and PHY domains and USB30/USB3 PHY domains.
- `gcc_sar2130p_probe()` maps registers, registers DFS data for twelve QUPv3 RCGs, enables always-on display/video/GPU AHB/XO branches, clears the GDSC sleep vote auto-removal register, and registers the descriptor.

## Control Flow
The driver binds to `qcom,sar2130p-gcc` and is registered from `subsys_initcall(gcc_sar2130p_init)`. Probe uses `qcom_cc_map()` with a regmap max register of `0x1f1030`, registers DFS metadata for QUPv3 wrap0 and wrap1 serial clocks, then performs SoC-specific initialization before the common registration step. The initialization keeps `GCC_DISP_AHB_CLK`, `GCC_VIDEO_AHB_CLK`, `GCC_VIDEO_XO_CLK`, and `GCC_GPU_CFG_AHB_CLK` enabled through direct `qcom_branch_set_clk_en()` writes. It also writes `0` to register `0x62204` to clear `GDSC_SLEEP_ENA_VOTE`, preventing GDSC votes from being removed automatically during sleep. `qcom_cc_really_probe()` then exposes the clocks, resets, and GDSCs to kernel consumers.

After registration, normal operations flow through the common clock, reset, and genpd frameworks. Device drivers request binding IDs, then the qcom ops program RCGs, select pipe-clock muxes, propagate rates to parent PLLs where flagged, gate/un-gate branches, poll or skip halt status based on each branch definition, and manage GDSC votes.

## State And Persistence
The driver has no heap-owned runtime state beyond framework registration; all meaningful mutable state is hardware register state. PLLs share enable register `0x62018`, with per-PLL bit masks. RCG, mux, branch, reset, and GDSC offsets are hard-coded static data. The always-on branch enables and the `0x62204` sleep-vote override remain in hardware until the controller is reset or reprogrammed. DFS metadata persists through the qcom clock framework for QUPv3 serial rate changes. GDSCs are persistent hardware power-domain controls coordinated by genpd and qcom GDSC helpers.

## Dependencies And Integration Points
Depends on the Linux common clock framework, OF/platform driver matching, regmap, qcom alpha PLL, branch, RCG, regmap divider/mux/PHY mux, reset, and GDSC helper code, plus `dt-bindings/clock/qcom,sar2130p-gcc.h`. Integration points include PCIe root-complex drivers, USB3/PHY drivers, SDHCI, QUPv3 serial clients, PDM, GPU/display/video/IRIS blocks, DDRSS-related consumers, and power-domain users of the MMU/Turing/PCIe/USB GDSCs.

## Risks And Edge Cases
The sleep-vote register write is a high-impact platform quirk: if removed or moved after consumers start using GDSCs, power votes can disappear in sleep. Branch halt policies include several `BRANCH_HALT_SKIP` entries for aggregate, DDRSS, display, PCIe master, pipe, video, and IRIS clocks; changing these to polled halt checks risks false timeouts on hardware that lacks reliable halt status. Binding-table index drift is risky because the clock array is addressed by generated DT IDs. PCIe pipe sources are external PHY clocks, so device tree and PHY driver ordering must provide those parents before consumers try to use PCIe. The `subsys_initcall` timing differs from the other two files and may be required for dependent subsystems.

## Test Signals
Validation signals include successful probe and descriptor registration, QUPv3 serial ports changing rates through DFS, USB3 and PCIe links training with pipe clocks supplied by PHY parents, SDCC1 operating at expected app/ICE rates, video/GPU/display clients not losing AHB/XO access during runtime PM or suspend, and GDSC votes surviving sleep. Static checks should compare clock/reset/GDSC IDs against `qcom,sar2130p-gcc.h`, verify no NULL holes for required public IDs, and build the driver with qcom clock helpers enabled.
