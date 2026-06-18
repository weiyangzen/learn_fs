# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-ipq5424.c

## Purpose

`gcc-ipq5424.c` is the Qualcomm Global Clock Controller driver for the IPQ5424 SoC. It exposes the SoC GCC hardware to Linux as a clock provider, reset controller, and interconnect hardware clock provider. Device-tree consumers use binding IDs from `dt-bindings/clock/qcom,ipq5424-gcc.h`, `dt-bindings/reset/qcom,ipq5424-gcc.h`, and `dt-bindings/interconnect/qcom,ipq5424.h`.

Like other Qualcomm GCC drivers, this file is primarily a hardware description table. It models PLLs, parent muxes, RCGs, fixed factors, read-only dividers, PHY muxes, branch gates, reset lines, and interconnect clock mappings, then hands those descriptors to `qcom_cc_probe()`.

## Important APIs, Types, And Data

- `struct clk_alpha_pll`: describes GPLL0, GPLL2, and GPLL4. GPLL0/GPLL4 use `CLK_ALPHA_PLL_TYPE_DEFAULT_EVO`; GPLL2 uses `CLK_ALPHA_PLL_TYPE_NSS_HUAYRA`. Main PLLs use `clk_alpha_pll_ops`.
- `struct clk_alpha_pll_postdiv`: exposes `gpll0_out_aux` and `gpll2_out_main`. GPLL2 has a fixed post-divider table with value `0x1 -> div 2`.
- `CLK_IGNORE_UNUSED`: set on GPLL4 because boot firmware may leave GPLL4 feeding clocks whose Linux consumers are not all present yet. The comment says the flag should be removable once consumers exist.
- `struct clk_fixed_factor`: provides `gpll0_div2`, `gcc_xo_div4_clk_src`, `gcc_qdss_tsctr_div2_clk_src`, `gcc_qdss_dap_sync_clk_src`, and `gcc_eud_at_div_clk_src`.
- `struct parent_map` and `struct clk_parent_data`: translate hardware source selectors to CCF parents. External parents are indexed as `DT_XO`, `DT_SLEEP_CLK`, four PCIe pipe clocks, and `DT_USB_PCIE_WRAPPER_PIPE_CLK`.
- `struct freq_tbl`: declares rates for ADSS PWM, PCIe AXI/aux/rchg, QUPv3 I2C/SPI/UART, SDCC1 apps and ICE core, USB0/USB1 mock UTMI, WCSS AHB, QDSS, System NOC/PCNOC, LPASS, sleep, QPIC, and related sources.
- `struct clk_rcg2`: root clock generators. Most use `clk_rcg2_ops`; SDCC1 apps uses `clk_rcg2_floor_ops`.
- `struct clk_regmap_div`: read-only dividers for QUPv3 I2C0/I2C1 and USB0/USB1 mock UTMI clocks.
- `struct clk_regmap_phy_mux`: pipe-clock muxes for PCIe0 through PCIe3 and USB0.
- `struct clk_branch`: final gate clocks for PCIe, CNOC/ANOC/SNOC/NSSNOC, QUPv3, SDCC, UNIPHY, USB, CMN, LPASS, QPIC, QDSS, ADSS, MDIO, PRNG, and other blocks.
- `struct qcom_reset_map gcc_ipq5424_resets[]`: a large map of block resets, ARES lines, and multi-bit reset groups for QUPv3, IMEM, TME, DDR/GEMNOC, NSS/WCSS, security blocks, LPASS, PCIe0-3, USB0/USB1, QDSS, SNOC/ANOC/PCNOC, QPIC, SDCC, DCC, SPDM, MPM, RBCPR, CMN, TCSR, TLMM, UNIPHY XPCS, and QUSB PHYs.
- `struct qcom_icc_hws_data icc_ipq5424_hws[]`: maps ANOC/CNOC PCIe, CNOC USB, NSSNOC, and LPASS interconnect nodes to clocks that should be voted for bandwidth paths.
- `struct qcom_cc_desc gcc_ipq5424_desc`: central registration descriptor for clocks, resets, hardware-only clocks, and ICC hardware clocks.

## Clock Topology And Control Flow

The module registers a platform driver at `core_initcall(gcc_ipq5424_init)`. Device-tree matching uses compatible string `qcom,ipq5424-gcc`. `gcc_ipq5424_probe()` calls `qcom_cc_probe(pdev, &gcc_ipq5424_desc)` and does no custom setup.

The common probe path maps the MMIO region with `gcc_ipq5424_regmap_config`, registers the `gcc_ipq5424_clocks[]` indexed clock table, registers standalone fixed-factor hardware clocks from `gcc_ipq5424_hws[]`, registers resets from `gcc_ipq5424_resets[]`, and exposes interconnect hardware clocks from `icc_ipq5424_hws[]`. The driver's platform `.sync_state = icc_sync_state` integrates interconnect synchronization with late/consumer probing.

Clock requests flow through standard CCF APIs. Leaf branch clocks call shared Qualcomm branch ops; branches with `CLK_SET_RATE_PARENT` propagate rate requests to their RCGs or fixed factors. RCG ops choose a row from the `freq_tbl`, program parent select/divider/M/N fields, and then branch ops gate or ungate the final CBCR. Reset requests flow through the reset controller using the reset map offsets/bits.

## Subsystems Covered

- PLL/root sources: XO, sleep, GPLL0, GPLL0/2/4 outputs, GPLL0 div2, and read-only post-dividers.
- PCIe: four controllers named PCIe0-PCIe3. PCIe0/1 are treated as 1-lane ANOC/CNOC paths and PCIe2/3 as 2-lane paths in the interconnect mapping. Each port has AXI M/S sources, AXI branches, AHB, aux, pipe mux/branch, rchng source/branch, and reset/sticky reset coverage.
- QUPv3: AHB master/slave branches plus two I2C, two SPI, and two UART application clocks. I2C has read-only divider clocks between RCG and branch.
- USB: USB0 has aux, master, mock UTMI, pipe, sleep, PHY CFG AHB, EUD AT, and pipe source. USB1 has master, mock UTMI, sleep, and PHY CFG AHB coverage plus QUSB2_1 reset.
- Storage/crypto: SDCC1 apps clock, SDCC1 ICE core clock, and SDCC AHB clock.
- NSS/NSSNOC/WCSS/UNIPHY/MDIO: NSS clocks, NSSNOC bridge/ref clocks, WCSS AHB source, MDIO AHB, and three UNIPHY AHB/SYS clock pairs with XPCS resets.
- NOC/debug/audio/flash: System NOC, PCNOC/CNOC/ANOC/SNOC paths, QDSS AT/DAP/timestamp roots, LPASS sway/AXIM/core/SNOC/CNOC clocks, CMN 12GPLL clocks, QPIC IO and core clocks, ADSS PWM, and PRNG.

## State And Persistence Behavior

The driver maintains no private runtime state beyond static descriptors. CCF, reset, regmap, and interconnect frameworks own registered state after probe. Hardware state persists in the GCC registers described by the offsets and bit masks.

PLL enable bits are shared at `0xb000` for GPLL0, GPLL2, and GPLL4. GPLL4 is marked `CLK_IGNORE_UNUSED`, so the common clock framework should not disable it during unused-clock cleanup even if no Linux consumer currently holds it. That preserves bootloader-provided clocking for downstream blocks.

Many clocks are read-only in the sense that the driver exposes a source or divider but uses read-only ops for postdividers/dividers. This means Linux can observe or use the clock as a parent but should not attempt arbitrary divider programming for those elements.

The reset map includes both conventional block-control resets and packed multi-bit reset registers, especially for WCSS and PCIe sticky/core/AXI/aux/AHB resets. Those bits persist until explicitly deasserted or until the relevant hardware reset domain changes.

## Dependencies And Integration Points

- CCF and Qualcomm clock helpers: `clk-alpha-pll.h`, `clk-branch.h`, `clk-rcg.h`, `clk-regmap.h`, `clk-regmap-divider.h`, `clk-regmap-mux.h`, `clk-regmap-phy-mux.h`, and `common.h`.
- Regmap: 32-bit register width, 4-byte stride, 32-bit values, `max_register = 0x3f024`, and `fast_io = true`.
- Reset framework: reset IDs from `dt-bindings/reset/qcom,ipq5424-gcc.h` map through `gcc_ipq5424_resets[]`.
- Interconnect framework: `qcom_icc_hws_data` entries map interconnect paths to clock IDs; `.sync_state = icc_sync_state` is used by the platform driver.
- Device tree: the GCC node must provide external parent clocks in the order expected by the local `DT_*` enum, including four PCIe pipe-clock parents and the USB/PCIe wrapper pipe clock.
- Platform/module lifecycle: `MODULE_DEVICE_TABLE(of, gcc_ipq5424_match_table)`, `platform_driver_register()`, `core_initcall()`, and `module_exit()`.

## Risks And Edge Cases

- External parent ordering is critical. A mismatch among `DT_PCIE30_PHY0_PIPE_CLK` through `DT_PCIE30_PHY3_PIPE_CLK` or `DT_USB_PCIE_WRAPPER_PIPE_CLK` would connect pipe gates to the wrong PHY parent.
- GPLL4's `CLK_IGNORE_UNUSED` is a deliberate workaround. Removing it before all consumers are represented can break clocks initialized by firmware but not yet claimed by Linux.
- The clock array is sparse relative to binding values. Some binding IDs are not represented in `gcc_ipq5424_clocks[]` in this source. Consumers should be checked against the implemented table.
- The reset map is very large and includes mixed naming styles, block resets, ARES bits, and packed reset groups. Changes are high risk because a wrong offset/bit can reset unrelated fabric, security, memory, or PCIe state.
- PCIe port naming and lane semantics require care. The driver has four numbered ports while ICC names distinguish ANOC/CNOC and 1-lane/2-lane paths. Any device-tree or ICC mismatch can result in bandwidth votes going to the wrong port clock.
- USB1 coverage is partial compared with USB0. USB1 branches use PCNOC-derived master and sleep/mock UTMI/PHY CFG clocks but no USB1 pipe mux in this file; consumers must match actual hardware capabilities.
- RCG rate tables encode hardware clock plans. Mistakes can cause unstable UART baud rates, I2C/SPI rates, SDCC overclocking, USB UTMI/pipe failures, PCIe link issues, or QPIC timing problems.
- Some branches omit explicit `halt_check` while others use `BRANCH_HALT`, `BRANCH_HALT_VOTED`, or `BRANCH_HALT_DELAY`. Halt-check changes can create false enable failures or hide real hardware stalls.

## Test Signals

- Build coverage: compile the IPQ5424 GCC option and ensure all included binding IDs resolve, especially reset bindings from `dt-bindings/reset/qcom,ipq5424-gcc.h`.
- Probe signal: boot with a `qcom,ipq5424-gcc` node and verify the driver name `qcom,gcc-ipq5424` probes early enough for PCIe, USB, QUPv3, SDCC, NSS, UNIPHY, QPIC, and LPASS consumers.
- Clock debugfs: inspect `/sys/kernel/debug/clk/clk_summary` for `gpll4`, `gcc_pcie0_pipe_clk`, `gcc_pcie3_axi_m_clk`, `gcc_qupv3_uart0_clk`, `gcc_sdcc1_ice_core_clk`, `gcc_usb1_mock_utmi_clk`, `gcc_uniphy2_sys_clk`, and `gcc_qdss_at_clk`.
- Peripheral tests: validate PCIe link training on all four ports, USB0 and USB1 operation, QUPv3 UART/SPI/I2C transfers, SDCC1 including ICE if present, MDIO/UNIPHY Ethernet paths, QPIC/NAND, LPASS paths, and NSS/WCSS bring-up.
- Reset tests: exercise block resets for QUPv3, PCIe0-3, USB0/USB1 PHYs, SDCC, QPIC, NSS/WCSS, UNIPHY XPCS, and selected NOC/security resets only where the target board can tolerate it.
- Interconnect tests: create bandwidth votes on PCIe, USB, NSSNOC, and LPASS paths and confirm the mapped clocks enable or vote as expected.
