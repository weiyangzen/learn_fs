# subset-b-001136 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sa8775p.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sa8775p.c

## Purpose
Implements the Qualcomm Global Clock Controller driver for SA8775P. It publishes the SoC's GCC clock tree, resets, and GDSC power domains to the common clock framework and genpd through the qcom clock-controller helpers. The driver covers general-purpose PLLs, QUPv3 serial engines, SDCC, UFS PHY and UFS card controllers, USB2/USB3 primary and secondary blocks, PCIe0/PCIe1, EMAC0/EMAC1, GPU/display/camera/video interconnect clocks, throttle clocks, and assorted clock reference enables.

## Important APIs, Types, And Functions
- `struct clk_alpha_pll` and `struct clk_alpha_pll_postdiv` define Lucid EVO GPLL0, GPLL1, GPLL4, GPLL5, GPLL7, GPLL9, and GPLL0 even post-divider outputs, all ultimately parented by the DT `bi_tcxo` clock.
- `struct parent_map` plus `struct clk_parent_data` arrays encode mux values for RCGs and pipe/symbol muxes. The first enum must match the DT binding order, while the second enum names internal parent IDs.
- `struct clk_rcg2` entries and `struct freq_tbl` tables implement programmable rate sources for EMAC, GP clocks, PCIe auxiliary/rchng clocks, PDM, QUPv3 serial ports, SDCC1, TSCSS, UFS card/PHY, USB, and QSPI-style QUPv3 wrap3 clocks.
- `struct clk_regmap_mux`, `struct clk_regmap_phy_mux`, and `struct clk_regmap_div` represent hardware muxes/dividers for PCIe pipe/aux clocks, UFS symbol clocks, USB PHY pipe clocks, QUPv3 wrap3 divider, and UTMI post-dividers.
- `struct clk_branch` gates the leaf clocks and carries halt policy (`BRANCH_HALT`, `BRANCH_HALT_VOTED`, `BRANCH_HALT_SKIP`, `BRANCH_HALT_DELAY`) plus rate propagation flags such as `CLK_SET_RATE_PARENT`.
- `struct gdsc` entries model PCIe, UFS card/PHY, USB, and EMAC power domains; PCIe domains use votable/retain/poll flags.
- `gcc_sa8775p_clocks`, `gcc_sa8775p_resets`, `gcc_sa8775p_gdscs`, and `gcc_sa8775p_desc` are the exported descriptor tables consumed by `qcom_cc_really_probe()`.
- `gcc_sa8775p_probe()` maps MMIO with `qcom_cc_map()`, registers DFS-capable RCGs, forces required always-on clocks, enables FORCE_MEM_CORE_ON for the UFS PHY ICE core clock, then registers the clock controller.

## Control Flow
Module loading is via `core_initcall(gcc_sa8775p_init)`, which registers the platform driver for compatible `qcom,sa8775p-gcc`. Probe maps the GCC register space using the descriptor's regmap config (`32-bit` registers, stride `4`, max register `0xc7018`, `fast_io`). If the map succeeds, the driver registers dynamic frequency scaling metadata for the QUPv3 serial clock sources, sets a fixed group of camera, display, GPU, and video AHB/XO clocks on with direct branch enable writes, marks the UFS PHY ICE core branch for forced memory-core retention, and finally calls `qcom_cc_really_probe()` to publish clocks, resets, and power domains.

Runtime clock control after probe is delegated to the common qcom clock ops. Consumers request IDs from `dt-bindings/clock/qcom,sa8775p-gcc.h`; the framework then uses the registered regmap-backed clock objects to set parent muxes, program RCG M/N/D values from frequency tables, toggle branch enable bits, observe halt bits, assert resets, or vote GDSCs.

## State And Persistence
The driver is statically described; persistent state lives in GCC hardware registers and in framework objects registered at probe. PLL enable state is controlled through a shared enable register at `0x4b028`, while individual RCGs, branches, muxes, and dividers use their declared offsets. The explicit always-on branch enables persist until reset or firmware/kernel reprogramming. DFS registration persists in the qcom clock framework for QUPv3 clocks. GDSC state is backed by GDSCR registers and is reference-counted by genpd users; reset state is driven by the reset-controller API and hardware reset registers.

## Dependencies And Integration Points
Depends on Linux common clock framework headers, platform-driver/OF matching, regmap, qcom clock primitives (`clk-alpha-pll`, `clk-branch`, `clk-rcg`, `clk-regmap*`, `clk-regmap-phy-mux`), qcom reset/GDSC helpers, and the SA8775P GCC DT binding. It integrates with device-tree consumers for UART/SPI/I2C via QUPv3, SDHCI, UFS, USB, PCIe, Ethernet, GPU, camera/display/video, and power-domain users. The source includes `common.h`, so probe relies on qcom CC mapping/registration helpers rather than open-coding platform resource handling.

## Risks And Edge Cases
The DT input-clock enum is explicitly required to match the binding order; any mismatch silently corrupts parent lookup for external clocks such as TCXO, sleep, UFS symbols, USB/PCIe pipes, and RXC references. Large descriptor tables are index-sensitive against the binding IDs; omitted or shifted entries break consumers by ID. Many branches use voted or skipped halt checks, so a wrong halt policy can hang enable/disable paths or mask a dead clock. Always-on direct register writes are not represented as normal consumers and must remain consistent with hardware requirements for MM/GPU/video access. The UFS ICE forced memory-core setting is a SoC quirk; dropping it can create data-path failures during low-power transitions.

## Test Signals
Useful validation signals are successful probe on `qcom,sa8775p-gcc`, all expected clock/debugfs IDs present, QUPv3 serial rates selectable through DFS, SDCC/UFS/USB/PCIe/EMAC drivers able to enable their clocks and deassert resets, GDSC power domains transitioning without timeout, and suspend/resume retaining the explicitly protected MM/GPU/video/UFS paths. Static test signals include binding index consistency, no duplicate clock/reset IDs, and build coverage for `CONFIG_SA_GCC_8775P` or the relevant qcom GCC Kconfig option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sa8775p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sar2130p.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sar2130p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sc7180.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sc7180.c

## Purpose
Implements the Qualcomm/QTI Global Clock Controller driver for SC7180. It registers Fabia GPLLs, RCG rate sources, fixed factor hardware, branch gates, resets, and GDSCs for core SoC peripherals including QUPv3, SDCC1/2, UFS PHY, USB3, QSPI, PDM, crypto, CPU/system NoC, camera/display/video, GPU, NPU, modem, and LPASS-related clocks.

## Important APIs, Types, And Functions
- `struct clk_alpha_pll` defines Fabia GPLL0, GPLL1, GPLL4, GPLL6, and GPLL7, with `gpll0_out_even` as a Fabia post-divider.
- `struct clk_fixed_factor gcc_pll0_main_div_cdiv` provides a CCF-visible divide-by-two hardware clock, exported through `gcc_sc7180_hws` as `GCC_GPLL0_MAIN_DIV_CDIV`.
- Parent maps and parent-data arrays use firmware clock names such as `bi_tcxo`, `bi_tcxo_ao`, and `sleep_clk`, plus internal PLL hardware pointers, to construct RCG parent selections.
- `struct clk_rcg2` and frequency tables cover CPUSS AHB, GP1-3, PDM2, QSPI, QUPv3 wrap0/wrap1 serial ports, SDCC1/2, UFS PHY, USB30, USB3 PHY auxiliary, and secure controller rates.
- `struct clk_branch` gates leaf and vote clocks across UFS, USB, boot ROM, camera/display/video, crypto, CPUSS, GPU, NPU, QSPI, QUPv3, SDCC, MSS, and LPASS. Some CPU/system NoC branches are marked `CLK_IS_CRITICAL`.
- `struct gdsc` exposes UFS PHY, USB30 primary, and two votable MMNOC MMU TBU domains.
- `gcc_sc7180_probe()` maps the controller, disables GPLL0 active input to MM/NPU/GPU blocks through three MISC register updates, enables required always-on clocks, registers DFS data, and calls `qcom_cc_really_probe()`.

## Control Flow
The platform driver binds to `qcom,gcc-sc7180` and is registered via `core_initcall(gcc_sc7180_init)`. Probe maps GCC registers using the descriptor's regmap config (`max_register = 0x18208c`). Before common registration, it writes MISC bits at `0x09ffc`, `0x4d110`, and `0x71028` with mask/value `0x3` to disable the GPLL0 active input path for multimedia blocks, NPU, and GPU. It then forces several branches on: CPUSS GNOC, video/camera/display AHB and XO clocks, and GPU CFG AHB. The QUPv3 wrap0/wrap1 serial RCGs are registered for DFS, and the shared qcom CC registration publishes the descriptor's clocks, hardware-only clock, resets, and GDSCs.

Normal consumer operations are handled by the common clock framework. Rate requests select frequency-table entries, parent muxes choose PLL or XO/sleep parents, branches gate hardware and poll or skip halt status according to their definitions, reset IDs assert/deassert BCR registers, and GDSC users vote power domains through genpd.

## State And Persistence
The driver is declarative except for probe-time register programming. Hardware register state stores PLL enables at `0x52010`, RCG configuration, branch enables, reset assertions, and GDSC power votes. Probe-time MISC writes and always-on branch enables persist until hardware reset or later firmware/kernel changes. Critical flags on CPUSS/system NoC clocks prevent the common clock framework from disabling paths needed for CPU/interconnect operation. The `gcc_sc7180_hws` table separately persists the fixed-factor GPLL0 main divider registration in addition to the regmap clocks.

## Dependencies And Integration Points
Depends on Linux CCF, error/kernel/module/platform/OF/regmap support, qcom alpha PLL, branch, RCG, common CC, reset, and GDSC helpers, plus `dt-bindings/clock/qcom,gcc-sc7180.h`. It integrates with SC7180 device-tree clock consumers for serial engines, storage, USB, QSPI, crypto, CPU/interconnect, GPU/NPU, camera/display/video, modem, and LPASS. Unlike the newer SA8775P/SAR2130P drivers, this source uses firmware-name parent lookup rather than numeric DT parent indexes for external TCXO/sleep clocks.

## Risks And Edge Cases
The probe-time GPLL0 active-input disable writes are undocumented-looking SoC quirks; removing or altering them can destabilize MM/NPU/GPU clocking. `CLK_IS_CRITICAL` on CPUSS and system NoC clocks is essential to avoid disabling CPU/interconnect paths. Parent lookup relies on firmware clock names, so DT clock-names mismatches break parent resolution. Several UFS/USB symbol or pipe branches use skipped halt checks where hardware status may not reflect external PHY-driven clocks. Binding-array index consistency remains critical because public consumers address clocks, resets, and GDSCs by generated IDs. The separate `clk_hws` table for the fixed factor divider must remain in sync with the binding ID.

## Test Signals
Useful runtime signals are successful probe, presence of `GCC_GPLL0_MAIN_DIV_CDIV` and all public regmap clocks, stable boot without CPUSS/GNOC clock disable warnings, working QUPv3 DFS serial rates, SDCC1/2 and UFS storage operation, USB3 enumeration, QSPI/PDM/crypto availability, GPU/NPU/display/video clients enabling clocks without halt timeouts, and suspend/resume with GDSC votes intact. Static signals include binding ID alignment, build coverage for the SC7180 GCC driver, and review of probe writes against downstream or hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sc7180.c -->
