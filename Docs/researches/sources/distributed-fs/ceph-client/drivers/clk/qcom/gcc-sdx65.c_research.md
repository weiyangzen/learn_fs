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
