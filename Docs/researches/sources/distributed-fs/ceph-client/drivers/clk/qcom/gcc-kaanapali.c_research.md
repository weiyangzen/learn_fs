# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-kaanapali.c

## Purpose
This file is the Qualcomm Global Clock Controller driver for the Kaanapali SoC compatible string `qcom,kaanapali-gcc`. It declares the SoC's GCC clock tree, reset lines, GDSC power domains, DFS-capable RCGs, and critical CBCRs, then exposes them through the common Qualcomm clock-controller probe path. The driver is mostly static hardware description: each `clk_alpha_pll`, `clk_rcg2`, `clk_branch`, mux, divider, reset, and GDSC entry maps a device-tree clock/reset ID to MMIO offsets and common clk operations.

## Important APIs, Types, And Functions
- `struct clk_alpha_pll` and `struct clk_alpha_pll_postdiv` define fixed Taycan EKO T GPLLs: `gcc_gpll0`, `gcc_gpll0_out_even`, `gcc_gpll1`, `gcc_gpll4`, `gcc_gpll7`, and `gcc_gpll9`.
- `struct parent_map` and `struct clk_parent_data` arrays encode RCG parent selector values and the corresponding Linux clock parents. Some parents are external DT clocks such as `DT_BI_TCXO`, `DT_SLEEP_CLK`, PCIe pipe, UFS symbols, and USB pipe.
- `struct clk_regmap_phy_mux`, `struct clk_regmap_mux`, and `struct clk_regmap_div` cover PHY-sourced pipe/symbol clocks and read-only post-dividers, notably PCIe pipe, UFS RX/TX symbol clocks, USB3 pipe selection, QUPV3 wrap1 S2, and USB mock UTMI postdivider.
- `struct clk_rcg2` instances provide programmable roots for GP clocks, PCIe aux/rchng, PDM, QUPV3/I2C/QSPI serial engines, SDCC2/SDCC4, UFS PHY AXI/ICE/Unipro/AUX, and USB3 master/mock/aux clocks. Frequency tables use `F()` entries with parent IDs, dividers, and M/N values.
- `struct clk_branch` instances gate leaf and bus clocks. They use `clk_branch2_ops` or `clk_branch2_aon_ops`, `BRANCH_HALT`, `BRANCH_HALT_VOTED`, `BRANCH_HALT_SKIP`, or `BRANCH_HALT_DELAY`, and optional hardware clock-gating fields.
- `struct gdsc` entries describe power domains for PCIe, PCIe PHY, UFS memory PHY, UFS PHY, USB30 primary, and USB3 PHY.
- `gcc_kaanapali_clocks[]`, `gcc_kaanapali_gdscs[]`, and `gcc_kaanapali_resets[]` are the binding-facing registration tables indexed by `dt-bindings/clock/qcom,kaanapali-gcc.h`.
- `gcc_dfs_clocks[]` declares dynamic frequency scaling support for selected QUPV3 RCGs.
- `gcc_kaanapali_critical_cbcrs[]` lists boot-critical CBCR offsets the common driver data preserves.
- `clk_kaanapali_regs_configure()` calls `qcom_branch_set_force_mem_core()` for `gcc_ufs_phy_ice_core_clk`.
- `gcc_kaanapali_probe()` delegates to `qcom_cc_probe(pdev, &gcc_kaanapali_desc)`.

## Control Flow
At module/subsys initialization, `gcc_kaanapali_init()` registers a platform driver named `gcc-kaanapali`. Device-tree matching on `qcom,kaanapali-gcc` invokes `gcc_kaanapali_probe()`, which passes the descriptor to `qcom_cc_probe()`. The Qualcomm common clock-controller layer maps the MMIO range according to `gcc_kaanapali_regmap_config`, registers the clock providers, reset controller, and GDSC domains, applies `gcc_kaanapali_driver_data`, and makes the exported IDs available to consumers. Runtime clock operations thereafter are handled by the common clk framework and Qualcomm helper ops referenced by each static object.

There is no custom runtime state machine in this file. The only local side-effect outside registration is `clk_kaanapali_regs_configure()`, which forces memory core retention behavior for the UFS ICE core branch during controller setup.

## State And Persistence
State is hardware state in GCC MMIO registers. The driver does not allocate persistent private state or store software configuration across boots. PLL enable state, branch enables, mux selects, divider values, GDSC status, resets, hardware clock gating, DFS changes, and critical CBCR handling all persist only as register contents until hardware reset or power loss. The `qcom_cc_desc` and static clock descriptors are immutable registration data.

## Dependencies And Integration Points
- Linux common clk framework via `clk-provider.h`.
- Qualcomm clock helper implementations: `clk-alpha-pll`, `clk-branch`, `clk-rcg`, `clk-regmap`, `clk-regmap-divider`, `clk-regmap-mux`, `clk-regmap-phy-mux`, `common`, `gdsc`, and `reset`.
- Device-tree clock/reset bindings in `dt-bindings/clock/qcom,kaanapali-gcc.h`; array indices must match the binding constants exactly.
- External parent clocks are supplied by device tree indices: XO, always-on XO, sleep clock, PCIe pipe, UFS symbol clocks, and USB3 pipe wrapper clock.
- Consumer drivers for PCIe, UFS, USB3, SDCC, QUPV3 serial engines, PDM, camera/display/video/GPU/EVA, and interconnect/NOC paths request these clocks, resets, and power domains by DT ID.
- GDSCs integrate with Linux generic power domains through the Qualcomm GDSC layer.

## Risks And Edge Cases
- Binding/table index drift is the largest correctness risk: a misplaced entry in `gcc_kaanapali_clocks[]`, `gcc_kaanapali_gdscs[]`, or `gcc_kaanapali_resets[]` silently exposes the wrong hardware control to consumers.
- The driver relies on many hard-coded register offsets and bit numbers. A wrong `halt_reg`, `enable_reg`, `hwcg_reg`, collapse register, or reset offset can cause hangs, incorrect power collapse, or clocks that appear enabled but do not reach hardware.
- `BRANCH_HALT_SKIP`, `BRANCH_HALT_DELAY`, and `BRANCH_HALT_VOTED` choices encode hardware behavior. Overly strict halt checking can time out; overly loose checking can hide failures.
- External PHY mux parents for PCIe/UFS/USB require correct DT parent ordering and PHY provider readiness. Bad parent wiring can break high-speed link bring-up even when GCC registration succeeds.
- `qcom_branch_set_force_mem_core()` on the UFS ICE core is a targeted workaround. Removing or misapplying it may regress UFS inline crypto or low-power behavior.
- DFS metadata is limited to QUPV3 RCGs. Missing a DFS-capable RCG or listing the wrong RCG can cause firmware/clock handoff issues.
- Critical CBCR offsets keep infrastructure clocks alive. Omissions can break boot or runtime PM; stale offsets can keep unnecessary clocks on.

## Test Signals
- Build coverage: compile the driver with the matching Qualcomm clock framework and Kaanapali bindings enabled.
- Probe coverage: boot a Kaanapali DT with `qcom,kaanapali-gcc` and confirm `qcom_cc_probe()` succeeds without regmap, clock registration, reset, or GDSC errors.
- Clock summary: inspect `/sys/kernel/debug/clk/clk_summary` for expected GPLLs, QUPV3, SDCC, UFS, USB, PCIe, and media clocks, including sensible parentage and rates after consumers probe.
- Functional consumers: exercise PCIe link training, UFS enumeration and inline crypto path, USB3 link modes, SDCC2/SDCC4 storage, QUPV3 I2C/SPI/UART/QSPI, PDM, and display/camera/video/GPU/EVA clocks as applicable to the board.
- Power-management signals: suspend/resume and runtime PM tests should verify GDSC transitions, retained critical CBCRs, and no unexpected clock-off hangs.
- Reset signals: consumer reset assertions/deassertions should target expected blocks, especially PCIe, QUPV3 wrappers, UFS, USB PHYs, and media resets.
