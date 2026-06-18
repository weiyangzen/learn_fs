# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-ipq5018.c

## Purpose

`gcc-ipq5018.c` is the Qualcomm GCC driver for IPQ5018. It provides the clock and reset provider consumed by device-tree nodes for serial buses, crypto, Ethernet/GMAC/GEPHY/UNIPHY, PCIe0/PCIe1, USB0, SDCC1, QPIC, QDSS, LPASS, WCSS/Q6, NoC paths, UBI32, and miscellaneous system blocks. Compared with IPQ4019, it uses the standard qcom alpha-PLL, RCG2, branch, mux, divider, and fixed-factor primitives rather than local PLL math.

The source is table driven. The binding IDs from `dt-bindings/clock/qcom,gcc-ipq5018.h` and `dt-bindings/reset/qcom,gcc-ipq5018.h` index `gcc_ipq5018_clks[]` and `gcc_ipq5018_resets[]`.

## Important APIs, Types, And Functions

The important framework types are `struct clk_alpha_pll`, `struct clk_alpha_pll_postdiv`, `struct clk_fixed_factor`, `struct clk_rcg2`, `struct clk_regmap_div`, `struct clk_regmap_mux`, `struct clk_branch`, `struct qcom_reset_map`, `struct qcom_cc_desc`, and `struct regmap_config`.

Four PLL roots are modeled: `gpll0_main`, `gpll2_main`, `gpll4_main`, and `ubi32_pll_main`. Read-only postdiv objects expose `gpll0`, `gpll2`, `gpll4`, and `ubi32_pll`, and `gpll0_out_main_div2` provides a fixed half-rate parent. `ubi32_pll_config` is actively programmed in probe with `clk_alpha_pll_configure()`, making UBI32 core clocks depend on this driver rather than only boot firmware.

Parent data and parent maps are extensive and hardware-specific. They combine external DT parents such as XO, sleep clock, PCIe pipe clocks, USB pipe clock, GEPHY RX/TX, and UNIPHY RX/TX with internal GPLL and UBI32 PLL outputs. RCG frequency tables define BLSP, GMAC RX/TX, GP clocks, LPASS, PCIe, PCNOC, QDSS, QPIC, SDCC1, system NoC, UBI0, USB, Q6, and WCSS source rates.

The only procedural function with material logic is `gcc_ipq5018_probe()`. It maps registers with `qcom_cc_map()`, configures `ubi32_pll_main`, and then calls `qcom_cc_really_probe()`.

## Clock And Reset Model

The clock model starts with XO and sleep-clock DT parents, then derives GPLL0/GPLL2/GPLL4 and UBI32 clocks. RCGs synthesize functional rates for BLSP I2C/SPI/UART, crypto, GMAC0/GMAC1 RX/TX, GMAC common clocks, PCIe aux/AXI, PCNOC, QDSS trace/debug, QPIC, SDCC1, system NoC, UBI0, USB0, Q6, and WCSS.

Branch clocks gate the final consumer-visible clocks. There are many network-facing clocks: GEPHY RX/TX, UNIPHY RX/TX/SYS/AHB, GMAC0/GMAC1 cfg/PTP/RX/TX/sys, SNOC GMAC paths, WCSS AHB/AXI/debug, and Q6 clocks. PCIe0 and PCIe1 each have AHB, AUX, AXI master/slave, bridge, and PIPE clocks. USB0 exposes aux, LFPS, master, mock UTMI, PHY config, sleep, EUD AT, and pipe clocks.

Special infrastructure clocks include `gcc_sleep_clk_src` marked critical and `gcc_xo_clk` marked `CLK_SET_RATE_PARENT | CLK_IS_CRITICAL`. `gcc_ipq5018_hws[]` registers fixed-factor or synthetic `clk_hw` objects that are not in the main `clk_regmap` list.

The reset map is broad: voltage droop detector, BLSP, boot ROM, BTSS, common block, crypto, DCC, DDRSS, GEPHY/GMAC, LPASS, MDIO, PCIe0/1, PCNOC timeouts, PRNG, Q6/QDSS/QPIC, USB/PHY, UBI0/UBI32, UNIPHY, WCSS, and grouped GEPHY misc reset using a bitmask.

## Control Flow

`core_initcall(gcc_ipq5018_init)` registers the platform driver. Device-tree matching uses `qcom,gcc-ipq5018`.

Probe copies the static descriptor into a local `ipq5018_desc`, maps the GCC MMIO space using `qcom_cc_map()`, programs the UBI32 PLL through `clk_alpha_pll_configure(&ubi32_pll_main, regmap, &ubi32_pll_config)`, and finally invokes `qcom_cc_really_probe()` to register clocks, hardware-only clock nodes, and reset controllers. After probe, all operations are CCF driven. Consumers request rates, parent changes, and enable/disable operations, which dispatch through the selected qcom ops for each clock primitive.

## State And Persistence

The driver has no durable persistence and no dynamic long-lived state beyond static descriptors registered with the clock framework. Hardware register state is the source of truth for PLL status, RCG configuration, mux selection, branch enables, and reset assertions.

Unlike IPQ4019, one important piece of state is programmed during probe: the UBI32 PLL configuration. That means boot behavior and UBI0/UBI32 clocks depend on this driver reaching probe successfully. Other PLLs are represented with standard alpha-PLL ops and read-only postdivs, so their state is generally inherited from hardware or managed by the common qcom PLL code.

## Dependencies And Integration Points

The driver integrates with platform probing, OF matching, CCF, regmap, qcom alpha PLL code, qcom branch/RCG/divider/mux/phy-mux helpers, and the qcom reset controller. External parent clocks are supplied by device tree using the order in the local `DT_*` enum, so the DTS clock list must match the driver comments and binding.

Consumers include UART/SPI/I2C BLSP devices, crypto engine, PCIe controllers, USB controller/PHY, SDCC1/eMMC or SD card host, Ethernet MAC/PHY and MDIO drivers, WCSS/Q6 remoteproc or wireless paths, QDSS/debug, LPASS, QPIC NAND, and reset clients. The binding ID arrays are the integration contract; reordering entries without changing bindings would break consumers.

## Risks

The highest risk is parent-map and frequency-table correctness. Several maps use hardware source select values that do not match array position, and GMAC/GEPHY/UNIPHY rates depend on external RX/TX parent clocks plus divider blocks. A wrong parent select value can produce a plausible but incorrect clock tree.

There are source-name irregularities worth tracking. The `gcc_mdio0_ahb_clk` C symbol initializes the visible clock name as `gcc_mdioi0_ahb_clk`, and `gcc_wcss_axi_s_clk` uses visible name `gcc_wi_s_clk`. If debug tooling, assigned-clock names, or downstream consumers rely on names rather than binding IDs, these typos can confuse integration. Binding IDs still point to the intended objects.

Probe programs UBI32 PLL unconditionally after register mapping. Bad PLL config values can destabilize UBI0 core rates. Critical clocks (`gcc_sleep_clk_src`, `gcc_xo_clk`) and delayed/voted halt checks need hardware-accurate policy. Many resets share registers; bit or bitmask mistakes can reset adjacent network or WCSS hardware.

## Test Signals

Build tests should cover this file with the IPQ5018 clock and reset binding headers enabled. Probe tests should show `qcom,gcc-ipq5018` matching, no failed `qcom_cc_map()` or `qcom_cc_really_probe()`, no duplicate clock names except known source-name quirks if accepted, and a sensible clock tree in `clk_summary`.

Functional signals include BLSP UART console and SPI/I2C transfers, SDCC1 mode changes through floor-rate ops, PCIe0/1 link training, USB0 enumeration and suspend/resume, GMAC0/GMAC1 link rates including 10/100/1000-style parent choices, MDIO access, QPIC transfers, QDSS clocks when debug is enabled, WCSS/Q6 boot, and UBI0 core operation at configured rates. Reset testing should exercise PCIe, USB, GEPHY, GMAC, UBI0, WCSS, and Q6 reset IDs while watching for unintended neighbor resets.
