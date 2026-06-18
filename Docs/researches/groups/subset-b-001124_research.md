# Research: subset-b-001124

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-ipq5332.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-ipq5332.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-ipq5424.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-ipq5424.c -->
