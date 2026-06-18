# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-glymur.c

## Purpose
`gcc-glymur.c` is the Qualcomm Global Clock Controller driver for the Glymur SoC compatible string `qcom,glymur-gcc`. It declares the GCC clock tree, reset lines, GDSC power domains, dynamic frequency scaling hooks, critical keepalive CBCRs, and the platform-driver binding needed for the common Qualcomm clock-controller core to expose these resources to Linux consumers.

The file is almost entirely declarative hardware description: register offsets, parent selections, frequency tables, halt checks, enable bits, and descriptor arrays. Runtime behavior is delegated to shared Qualcomm clock framework helpers such as alpha PLL, RCG2, branch, regmap mux/divider, reset, and GDSC code.

## Important APIs, Types, And Functions
The primary public entry points are `gcc_glymur_probe()`, `gcc_glymur_init()`, and `gcc_glymur_exit()`. Probe simply calls `qcom_cc_probe(pdev, &gcc_glymur_desc)`, while init and exit register and unregister the `platform_driver` at `subsys_initcall` time.

Important data structures include:

- `struct clk_alpha_pll` and `struct clk_alpha_pll_postdiv` for GPLL0, GPLL1, GPLL4, GPLL5, GPLL7, GPLL8, GPLL9, GPLL14, and the even post-dividers for GPLL0/GPLL14.
- `struct parent_map` and `struct clk_parent_data` arrays for translating logical parent IDs to hardware mux values and common clock framework parent references.
- `struct clk_regmap_phy_mux`, `struct clk_regmap_mux`, and `struct clk_regmap_div` for external PHY pipe clocks, symbol clocks, pipe muxes, and read-only divider sources.
- `struct clk_rcg2` plus `struct freq_tbl` tables for programmable roots, including GP clocks, PCIe auxiliary and rate-change clocks, PDM, QUPv3 serial/QSPI roots, SDCC apps clocks, UFS core clocks, USB2/USB3 roots, and USB4 master/PHY/TMU/SB roots.
- `struct clk_branch` for the actual gateable or voted branch clocks exposed to consumers.
- `struct gdsc` entries for PCIe, UFS, USB2/3/4, and USB PHY power domains.
- `struct qcom_reset_map` for block-control reset lines and a few asserted-reset bits.
- `struct clk_rcg_dfs_data` for DFS-enabled QUPv3 RCGs.
- `struct qcom_cc_desc` and `struct qcom_cc_driver_data`, which collect all clocks, resets, power domains, DFS data, critical CBCRs, and the register-configuration callback for `qcom_cc_probe()`.

`clk_glymur_regs_configure()` is the one local hardware-configuration callback. It calls `qcom_branch_set_force_mem_core(regmap, gcc_ufs_phy_ice_core_clk, true)` to force memory core retention behavior for the UFS PHY ICE core branch.

## Control Flow
At boot or module load, `gcc_glymur_init()` registers the `gcc-glymur` platform driver. Device-tree matching uses `qcom,glymur-gcc`; when a matching platform device appears, `gcc_glymur_probe()` passes `gcc_glymur_desc` to the shared Qualcomm CC probe path.

The shared probe path maps the GCC register range using `gcc_glymur_regmap_config`, registers every non-null entry in `gcc_glymur_clocks`, registers resets from `gcc_glymur_resets`, registers GDSC power domains from `gcc_glymur_gdscs`, applies the driver-data hooks, and wires all resources to the device-tree clock, reset, and power-domain providers. After registration, ordinary kernel clock consumers drive enable, disable, parent-select, and set-rate operations through the ops pointers embedded in each static clock object.

Clock control is table-driven. A rate request on an RCG consults its `freq_tbl`, chooses the requested or supported floor/closest/shared rate according to the assigned ops, programs the command RCGR and M/N/D or divider fields, and may propagate parent rate requests because most programmable roots use `CLK_SET_RATE_PARENT`. Branch enable/disable operations write the configured `enable_reg`/`enable_mask` and then apply the selected halt policy, such as `BRANCH_HALT`, `BRANCH_HALT_VOTED`, `BRANCH_HALT_SKIP`, or `BRANCH_HALT_DELAY`.

## State, Persistence, And Hardware Behavior
There is no filesystem or userspace-persistent state. State lives in static kernel data and in MMIO registers behind the regmap. The static declarations are immutable after registration except for normal common-clock framework bookkeeping.

Persistent hardware-visible effects include enabled PLLs, programmed RCG rates and parents, branch enable bits, reset assertions/deassertions, GDSC power states, DFS metadata used for runtime rate switching, and the UFS ICE force-memory-core setting made by `clk_glymur_regs_configure()`. Those values persist until changed by another clock/reset/power-domain operation or by hardware reset.

Some clocks are intentionally protected. `gcc_glymur_critical_cbcrs` lists camera AHB/XO, display AHB, GPU CFG AHB, and video AHB/XO CBCR registers for keepalive handling by the common Qualcomm code. `gcc_disp_hf_axi_clk` is also marked `CLK_IS_CRITICAL`, preventing normal late unused-clock cleanup from disabling it.

## Dependencies
This file depends on Linux platform-device, module, regmap, common clock framework, and device-tree matching APIs. It also depends heavily on Qualcomm clock-controller internals from nearby headers:

- `clk-alpha-pll.h` for Taycan EKO T PLL operations and register layouts.
- `clk-rcg.h` for RCG2 roots, frequency tables, DFS declarations, and shared/no-init/park/floor ops.
- `clk-branch.h`, `clk-regmap.h`, `clk-regmap-divider.h`, `clk-regmap-mux.h`, and `clk-regmap-phy-mux.h` for clock gate, mux, divider, and PHY mux implementations.
- `common.h` for `qcom_cc_probe()` and driver descriptor plumbing.
- `gdsc.h` for power-domain registration and GDSC flags such as `POLL_CFG_GDSCR`, `RETAIN_FF_ENABLE`, and `VOTABLE`.
- `reset.h` for reset-map registration.
- `dt-bindings/clock/qcom,glymur-gcc.h` for all exported clock, reset, and GDSC numeric IDs used as array indices.

External parent clocks are supplied by device tree using the local `DT_*` indices, including TCXO, TCXO_AO, sleep clock, PCIe pipe clocks, UFS symbol clocks, USB3 pipe clocks, USB4 PHY pipe/RX/DP/sys mux clocks, and QUSB4 PHY RX clocks.

## Integration Points
The device-tree node with compatible `qcom,glymur-gcc` is the integration anchor. Consumers reference this provider through clock, reset, and power-domain phandles whose IDs come from `qcom,glymur-gcc.h`.

Major consumer blocks represented here include PCIe controllers and PHYs for lanes 0 through 6 plus tunnel GDSCs, QUPv3 wrappers 0/1/2 and out-of-band serial/QSPI roots, SDCC2 and SDCC4, UFS PHY and ICE, USB2 primary, USB3 MP/primary/secondary/tertiary, USB4 controllers 0/1/2, camera/display/video/GPU/AV1E/EVA NoC and AHB branches, PDM, and assorted NoC/QMIP/RSCC support clocks.

The USB and PCIe portions are tightly coupled to external PHY-provided clocks through `clk_parent_data.index` entries and `clk_regmap_phy_mux` sources. Correct device-tree parent ordering is therefore part of the driver contract. The QUPv3 roots are additionally integrated with the GCC DFS mechanism via `gcc_dfs_clocks`.

## Risks
The main risk is hardware-description accuracy. A wrong register offset, bit mask, parent-map value, halt policy, frequency table entry, exported ID index, or GDSC wait value can break boot, hang a peripheral during enable/disable, select the wrong PLL, or corrupt another clock domain.

Array-index correctness is critical because `gcc_glymur_clocks`, `gcc_glymur_gdscs`, and `gcc_glymur_resets` are keyed directly by device-tree binding constants. Binding drift between this C file and `qcom,glymur-gcc.h` would expose the wrong resource to consumers.

External parent dependencies are another risk. Many USB4, USB3, PCIe, QUSB4, and UFS muxes select clocks provided outside this GCC driver. Missing, reordered, or incorrectly named device-tree parent inputs can make registration fail or leave consumers with unusable parent selections.

Several branches use `BRANCH_HALT_SKIP` or `BRANCH_HALT_DELAY`, which avoids strict halt polling for clocks whose status may not behave like ordinary GCC branches. These settings need hardware validation; using strict halt checks where hardware cannot report cleanly can deadlock enable paths, while skipping checks can hide a failed clock transition.

The local `clk_glymur_regs_configure()` callback writes UFS ICE branch configuration during probe. If the target register or branch identity is wrong, the failure mode may appear later as UFS ICE or storage instability rather than a probe-time error.

## Test Signals
Build coverage should include the GCC driver and its binding header with warnings enabled, ensuring all static initializers, enum IDs, and array indices compile cleanly.

Boot-time signals include successful probe for `qcom,glymur-gcc`, absence of `qcom_cc_probe()` registration errors, no missing parent-clock messages, and registered clock/reset/power-domain providers under debugfs or kernel logs.

Runtime validation should exercise representative consumers: PCIe links on all described controllers, USB2/USB3/USB4 ports including PHY pipe-clock switching, UFS including ICE paths, SDCC2/SDCC4 rate changes, QUPv3 serial/QSPI transfers across DFS-capable roots, and camera/display/video/GPU/AV1E/EVA clients that depend on voted or critical branches.

Power-management tests should suspend/resume with active and idle PCIe, USB, UFS, and QUPv3 devices; toggle each GDSC through consumer drivers; and verify that critical CBCRs and `CLK_IS_CRITICAL` clocks are not disabled by unused-clock cleanup. Reset tests should assert/deassert representative BCRs through the reset controller and confirm affected hardware recovers.
