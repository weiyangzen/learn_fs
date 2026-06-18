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
