# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-eliza.c

## Purpose

`gcc-eliza.c` is the GCC driver for the Qualcomm Eliza platform, matched by `qcom,eliza-gcc`. It exports global clocks, resets, and GDSC power domains for PCIe, UFS, USB3, QUPv3 serial engines, SDCC, PDM, GPU, camera, display, video, and NoC/QMIP fabrics. Compared with `gcc-apq8084.c`, it uses newer Qualcomm clock-controller patterns: Lucid OLE alpha PLLs, hardware-controlled shared RCGs, PHY mux clocks, read-only dividers, critical CBCR handling, DFS RCG metadata, and driver data callbacks.

## Important APIs, Types, And Data

The main types are `struct clk_alpha_pll`, `struct clk_alpha_pll_postdiv`, `struct clk_regmap_phy_mux`, `struct clk_regmap_mux`, `struct clk_rcg2`, `struct clk_regmap_div`, `struct clk_branch`, `struct gdsc`, `struct qcom_reset_map`, `struct clk_rcg_dfs_data`, `struct qcom_cc_driver_data`, and `struct qcom_cc_desc`.

PLL and parent infrastructure includes fixed Lucid OLE PLLs `gcc_gpll0`, `gcc_gpll4`, `gcc_gpll7`, `gcc_gpll8`, and `gcc_gpll9`; `gcc_gpll0_out_even`, a post-divider with divide-by-2 output; and parent maps for TCXO, sleep clock, GPLL main/even outputs, PCIe pipe inputs, UFS symbol inputs, and USB3 PHY pipe input.

Notable clock classes include PCIe PHY muxes, UFS symbol PHY muxes, the USB3 pipe mux, shared RCGs for GP/PCIe/PDM/QUPv3/SDCC/UFS/USB3 clocks, read-only dividers for pipe and UTMI derived paths, and branch gates with multiple halt policies, hardware clock-gating fields, and vote-register bits. Public registration tables are `gcc_eliza_clocks[]`, `gcc_eliza_gdscs[]`, and `gcc_eliza_resets[]`, all indexed by `dt-bindings/clock/qcom,eliza-gcc.h`. `gcc_eliza_driver_data` declares critical CBCRs, dynamic frequency scaling RCGs, and a post-map register configuration callback.

## Control Flow

`subsys_initcall(gcc_eliza_init)` registers the platform driver. The OF match table binds `qcom,eliza-gcc`. `gcc_eliza_probe()` calls `qcom_cc_probe(pdev, &gcc_eliza_desc)`. The common Qualcomm probe path maps registers, applies `gcc_eliza_driver_data`, registers all clocks/resets/GDSCs, marks critical CBCRs, wires DFS data, and invokes `clk_eliza_regs_configure()`. That callback calls `qcom_branch_set_force_mem_core()` for `gcc_ufs_phy_ice_core_clk` and `gcc_ufs_phy_axi_clk`, forcing memory core behavior needed by those UFS PHY clock branches.

After probe, consumers use standard CCF, reset, and genpd APIs. Many RCGs use `clk_rcg2_shared_ops`, `clk_rcg2_shared_no_init_park_ops`, or `clk_rcg2_shared_floor_ops`, which is important for shared hardware and safe parking behavior.

## State And Persistence

Software state is static metadata only. Hardware registers persist the active clock-controller state: PLL enable bits, postdiv selection, mux selection, RCG command state, M/N/D values, branch enables, halt state, HWCG state, reset state, and GDSC state. The driver data affects initial hardware policy by marking critical CBCRs and forcing memory core on for two UFS clocks.

The GDSCs include PCIe controller/PHY domains, UFS memory/PHY domains, USB30 primary, and USB3 PHY. Several use `POLL_CFG_GDSCR`, `RETAIN_FF_ENABLE`, and some PCIe domains are `VOTABLE`, with collapse control bits in `0x5214c`. These flags determine persistence and retention behavior across power transitions.

## Dependencies And Integration Points

The driver depends on Qualcomm clock helpers from the same directory: alpha PLLs, RCGs, branches, regmap dividers/muxes/PHY muxes, GDSC, reset, and common probe code. It also depends on the Eliza dt-binding header for all public clock, reset, and GDSC IDs.

Devicetree integration supplies parent indexes for `bi_tcxo`, `sleep_clk`, PCIe pipe clocks, UFS PHY symbol clocks, and USB3 PHY pipe clock. Downstream consumers include PCIe host/PHY drivers, UFS PHY/storage, USB3 controller/PHY, QUPv3 UART/I2C/SPI/QSPI blocks, SDCC/eMMC/SD, PDM audio, GPU SMMU/GEMNOC, camera/display/video fabric, and reset consumers for those subsystems. Critical CBCR entries protect essential camera, display, GPU, PCIe RSCC, and video AHB/XO clocks from being treated as ordinary unused gates. DFS metadata integrates QUPv3 RCGs with Qualcomm dynamic frequency switching infrastructure.

## Risks And Test Signals

The public arrays are ABI-sensitive. `gcc_eliza_clocks[]`, `gcc_eliza_gdscs[]`, and `gcc_eliza_resets[]` must stay aligned with `qcom,eliza-gcc.h`. The source uses many large register offsets and shared vote registers; incorrect bits can disturb unrelated global clocks. QUPv3 RCGs use `clk_rcg2_shared_no_init_park_ops`, so replacing these ops with generic RCG ops could introduce boot-time or runtime glitches. PHY-derived pipe and symbol clocks use muxes around external PHY outputs and commonly have delayed or skipped halt checks. The UFS force-memory-core configuration is platform-specific and should be preserved.

Static checks should verify that the binding constants cover every array entry and that `gcc_eliza_driver_data` points to live clock objects. Probe should log successful registration for `qcom,eliza-gcc` with no regmap or registration errors. Runtime tests should inspect `clk_summary` for parent selection and rates on QUPv3, SDCC, PCIe, UFS, and USB3 clocks; confirm critical CBCRs remain enabled when required; and validate DFS transitions for QUPv3 serial clocks. GDSC tests should power-cycle PCIe, UFS, USB30, and USB3 PHY domains.
