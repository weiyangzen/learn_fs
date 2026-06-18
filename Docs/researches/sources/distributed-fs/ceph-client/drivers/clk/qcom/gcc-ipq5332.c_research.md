# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-ipq5332.c

## Purpose

`gcc-ipq5332.c` is the Qualcomm Global Clock Controller driver for the IPQ5332 SoC. It describes the SoC's GCC register block to the common Qualcomm clock controller framework, exporting clocks, resets, and interconnect hardware clock handles to device-tree consumers using the IDs from `dt-bindings/clock/qcom,ipq5332-gcc.h` and `dt-bindings/interconnect/qcom,ipq5332.h`.

The file is almost entirely declarative. It builds the clock tree from external device-tree parents (`xo`, sleep clock, PCIe/USB pipe clocks), internal GPLLs, RCGs, fixed factors, read-only dividers, PHY muxes, branch gates, and reset maps. Runtime behavior is delegated to shared Qualcomm clock, reset, regmap, and interconnect helpers.

## Important APIs, Types, And Data

- `struct clk_alpha_pll` and `struct clk_alpha_pll_postdiv`: describe GPLL0, GPLL2, and GPLL4 at offsets `0x20000`, `0x21000`, and `0x22000`. The driver uses `CLK_ALPHA_PLL_TYPE_STROMER_PLUS` register layouts and `clk_alpha_pll_stromer_ops` for the main PLLs, with read-only post-dividers for exported GPLL outputs.
- `struct clk_fixed_factor`: exposes derived clocks such as `gpll0_div2`, `gcc_xo_div4_clk_src`, `gcc_system_noc_bfdcd_div2_clk_src`, QDSS timestamp divisions, and `gcc_eud_at_div_clk_src`.
- `struct parent_map` plus `struct clk_parent_data`: map Qualcomm RCG parent selector values to CCF parents. External parents are referenced by index in the GCC node's `clocks` property: `DT_XO`, `DT_SLEEP_CLK`, `DT_PCIE_2LANE_PHY_PIPE_CLK`, `DT_PCIE_2LANE_PHY_PIPE_CLK_X1`, and `DT_USB_PCIE_WRAPPER_PIPE_CLK`.
- `struct freq_tbl`: encodes selectable rates and parent/divider/M/N tuples for RCGs. Important tables cover BLSP SPI/UART, GP clocks, LPASS sway, NSS timestamp, PCIe AXI/aux/rchg, PCNOC/System NOC, QDSS, QPIC, SDCC1, USB, and sleep/XO sources.
- `struct clk_rcg2`: implements root clock generators. Most use `clk_rcg2_ops`; SDCC uses `clk_rcg2_floor_ops`, which is important for MMC rate selection where rounding down avoids overclocking.
- `struct clk_regmap_phy_mux`: models pipe-clock muxes for PCIe and USB using PHY-provided pipe clocks as external parents. These are `gcc_pcie3x2_pipe_clk_src`, `gcc_pcie3x1_0_pipe_clk_src`, `gcc_pcie3x1_1_pipe_clk_src`, and `gcc_usb0_pipe_clk_src`.
- `struct clk_regmap_div`: models read-only dividers for QDSS DAP, USB mock UTMI, and SNOC QoS external reference.
- `struct clk_branch`: exports gateable clocks. Branches carry `halt_reg`, `enable_reg`, `enable_mask`, `halt_check`, a parent, and usually `CLK_SET_RATE_PARENT`.
- `struct qcom_reset_map gcc_ipq5332_resets[]`: maps reset IDs and assert bits to GCC registers for BLSP, PCIe, USB, NSS, WCSS, QDSS, QPIC, SDCC, LPASS, APSS, CMN, UNIPHY, and related blocks.
- `struct qcom_icc_hws_data icc_ipq5332_hws[]`: maps interconnect master/slave pairs to GCC clocks. This lets the interconnect provider vote the correct hardware clock for paths such as PCIe, USB, and NSSNOC.
- `struct qcom_cc_desc gcc_ipq5332_desc`: the integration descriptor passed to `qcom_cc_probe()`. It binds the regmap config, clock array, resets, standalone hardware clocks, and interconnect hardware-clock mappings.

## Clock Topology And Control Flow

Initialization starts at `core_initcall(gcc_ipq5332_init)`, which registers `gcc_ipq5332_driver`. Device-tree matching uses compatible string `qcom,ipq5332-gcc`. Probe is minimal:

1. The platform bus matches the GCC MMIO node.
2. `gcc_ipq5332_probe()` calls `qcom_cc_probe(pdev, &gcc_ipq5332_desc)`.
3. The common Qualcomm CC code maps the register region using `gcc_ipq5332_regmap_config`, registers all `gcc_ipq5332_clocks[]` entries with the common clock framework, registers `gcc_ipq5332_resets[]` with the reset framework, registers `gcc_ipq5332_hws[]` fixed/hardware-only clocks, and wires `icc_ipq5332_hws[]` through the interconnect integration.
4. Consumers call normal CCF, reset-controller, or ICC APIs using device-tree phandles and binding IDs. The per-clock operations then perform regmap reads/writes against the offsets described here.

PLL setup is not imperative in this file. GPLL structures describe where the PLLs live and how to enable them. Consumers of GPLL-derived RCGs request rates through CCF; `clk_rcg2_ops` selects rows from each `freq_tbl`, sets parent selectors, and programs dividers/M/N fields through shared code.

Branch gates form the final enable points. Most branch clocks set `CLK_SET_RATE_PARENT`, so rate changes requested on leaf clocks can propagate to RCG parents. Many infrastructure clocks use `BRANCH_HALT_VOTED`, reflecting shared/votable GCC gates. Pipe clocks use `BRANCH_HALT_DELAY`, reflecting delayed or externally synchronized PHY pipe-clock behavior.

## Subsystems Covered

- BLSP1/QUP: three SPI/I2C application clock pairs and three UART application clocks, plus AHB and sleep gates. I2C branches reuse the SPI application source for each QUP instance.
- PCIe: one 2-lane controller and two 1-lane controllers, with AXI master/slave sources, aux clocks, pipe muxes, pipe branches, rchg clocks, PHY AHB clocks, link-down and sticky reset entries.
- USB0: aux, master, LFPS, mock UTMI, pipe, sleep, PHY CFG AHB, and EUD AT clocks plus PHY and controller resets.
- NSS/NSSNOC/WCSS: NSS timestamp, NSSCC/NSSCFG, NSSNOC ATB/SNOC/PCNOC/QoS/timeout/XO clocks, WCSS/Q6 reset coverage, and interconnect hardware clock mappings.
- NOC and debug: PCNOC, SNOC, system NOC, QDSS AT/DAP/ETR/EUD/timestamp clocks and reset lines.
- Storage and flash: SDCC1 apps/AHB clocks and QPIC/QPIC IO/sleep clocks.
- LPASS/ADSS/CMN/UNIPHY/MDIO/PRNG/CE/general-purpose clocks.

## State And Persistence Behavior

Persistent hardware state is GCC register state in the MMIO block. The driver itself has no mutable private state, no allocations, no workqueues, and no suspend/resume callbacks. CCF and reset state live in framework-managed objects registered by `qcom_cc_probe()`.

Clock enable/disable and rate changes persist in hardware registers until reset or firmware changes them. The driver assumes boot firmware may have initialized some PLLs and branches before Linux probes. It does not explicitly reprogram all frequencies at probe time; it exposes legal rate tables and lets consumers request rates.

Reset state is controlled through `qcom_reset_map` entries. Entries with only an offset represent block reset controls; entries with an offset and bit represent bit-level resets, commonly bit 2 for ARES lines and individual bits for sticky PCIe/WCSS resets.

## Dependencies And Integration Points

- Linux CCF: `<linux/clk-provider.h>`, `clk_alpha_pll_*`, `clk_rcg2_*`, `clk_branch2_ops`, `clk_fixed_factor_ops`, `clk_regmap_div_ro_ops`, and `clk_regmap_phy_mux_ops`.
- Regmap: `gcc_ipq5332_regmap_config` uses 32-bit registers, 4-byte stride, 32-bit values, `max_register = 0x3f024`, and `fast_io = true`.
- Reset framework: `reset.h` and `gcc_ipq5332_resets[]`.
- Interconnect framework: `<linux/interconnect-provider.h>`, `qcom_icc_hws_data`, and platform-driver `.sync_state = icc_sync_state`.
- Device-tree bindings: clock IDs from `qcom,ipq5332-gcc.h`, interconnect IDs from `qcom,ipq5332.h`, and external parent ordering expected by the local `DT_*` enum.
- Platform bus/module lifecycle: `platform_driver_register()` at core init and `platform_driver_unregister()` on module exit. `MODULE_DEVICE_TABLE()` exports OF modaliases.

## Risks And Edge Cases

- Binding/order sensitivity: the local `DT_*` enum must match the GCC node's external clock-parent ordering. Misordered pipe or XO parents can produce silent misclocking.
- Sparse clock ID space: the binding header includes IDs not populated in `gcc_ipq5332_clocks[]` such as some memory NOC/APSS-related clocks. Consumers must only request clocks that this driver actually provides, or tolerate `-ENOENT`/probe deferral from CCF.
- Parent map naming can be confusing: several `P_*_AUX` and `P_*_MAIN` selections map to the same exported post-divider or PLL hardware pointer in C. This mirrors hardware selectors, but reviewers should verify selector values against the downstream clock plan when changing tables.
- PCIe and USB pipe clocks depend on PHY drivers and external parent phandles. If the PHY pipe clock is absent or late, endpoint controller probe may defer or pipe branches may fail halt checks.
- Rate-table mistakes are hardware-facing. Incorrect F() rows can overclock buses or peripherals, especially SDCC1, UART fractional rates, USB mock UTMI/LFPS, and PCIe AXI/aux/rchg clocks.
- Halt-check choice matters. Votable clocks and delayed pipe clocks use special halt checks; converting them to plain `BRANCH_HALT` can create false failures or races during enable/disable.
- Interconnect mappings are part of clock voting. A wrong `qcom_icc_hws_data` clock ID can make bandwidth votes ineffective for PCIe/USB/NSSNOC paths.
- Reset map density is high and register offsets overlap clock branches. Off-by-one reset bits can assert active hardware unexpectedly.

## Test Signals

- Build coverage: compile with `CONFIG_IPQ_GCC_5332` or the relevant Qualcomm GCC option enabled; warnings often catch missing binding IDs, bad array entries, or incompatible init-data types.
- Probe signal: boot on an IPQ5332 device tree containing `compatible = "qcom,ipq5332-gcc"` and verify the platform driver probes before dependent BLSP, PCIe, USB, SDCC, NSS, and QPIC devices leave probe deferral.
- Clock visibility: inspect `/sys/kernel/debug/clk/clk_summary` for exported names such as `gcc_blsp1_uart1_apps_clk`, `gcc_pcie3x2_pipe_clk`, `gcc_usb0_master_clk`, `gcc_sdcc1_apps_clk`, and GPLLs.
- Functional peripherals: exercise UART/SPI/I2C, eMMC/SD via SDCC1, PCIe link training on 2-lane and 1-lane ports, USB0 host/device operation, MDIO/UNIPHY Ethernet paths, QPIC/NAND if present, and NSS/WCSS bring-up.
- Reset checks: use consumers' reset controls or targeted driver probes to assert/deassert BLSP, PCIe, USB PHY, QPIC, SDCC, NSS/WCSS, and UNIPHY resets without wedging shared clocks.
- Interconnect checks: confirm ICC paths for PCIe, USB, and NSSNOC create clock activity or votes in debugfs and that `.sync_state = icc_sync_state` does not leave consumers unsynchronized.
