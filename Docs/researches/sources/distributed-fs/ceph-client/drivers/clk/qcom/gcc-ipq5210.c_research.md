# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-ipq5210.c

## Purpose

`gcc-ipq5210.c` is the Qualcomm GCC driver for IPQ5210. It registers the IPQ5210 clock/reset provider for ADSS PWM, NSS/NSSNOC, PCIe0/PCIe1, QUPv3 serial engines, SDCC1 including ICE, USB0, QPIC, QDSS, PON timing, LPASS, GEPHY/UNIPHY, CMN 12G PLL support clocks, PCNOC/system NoC paths, and QRNG.

The driver is a newer table-driven qcom GCC implementation. It uses dt-binding IDs from `dt-bindings/clock/qcom,ipq5210-gcc.h` and `dt-bindings/reset/qcom,ipq5210-gcc.h`; those IDs index `gcc_ipq5210_clocks[]` and `gcc_ipq5210_resets[]`.

## Important APIs, Types, And Functions

The file uses standard qcom clock primitives: `struct clk_alpha_pll`, `struct clk_alpha_pll_postdiv`, `struct clk_fixed_factor`, `struct clk_rcg2`, `struct clk_regmap_div`, `struct clk_regmap_phy_mux`, `struct clk_branch`, `struct qcom_reset_map`, `struct qcom_cc_desc`, and `struct regmap_config`.

PLL roots are `gpll0_main`, `gpll2_main`, and `gpll4_main`, using `CLK_ALPHA_PLL_TYPE_DEFAULT_EVO` register layouts. `gpll0_div2` and `gcc_xo_div4_clk_src` are fixed-factor derived clocks. `gpll2` has a post-div table with value `0x1` mapping to divide-by-2. `gpll4_main` is marked `CLK_IS_CRITICAL` because the file documents that some bootloader-initialized clocks still use it before kernel consumers exist.

Parent maps `gcc_parent_map_0` through `gcc_parent_map_13` translate local parent enum values to GCC source-select fields. They combine XO, sleep clock, NSS common clock, USB/PCIe pipe clocks, GPLL main/aux outputs, and internal dividers. RCG tables synthesize ADSS PWM, NSS timestamp, system NoC, NSSNOC/MEMNOC, PCIe AXI/AUX/rate-change, QUPv3 serial rates, SDCC1/ICE, USB0, QDSS, PCNOC, QPIC, PON, and LPASS rates.

`gcc_ipq5210_probe()` is intentionally simple and delegates to `qcom_cc_probe(pdev, &gcc_ipq5210_desc)`.

## Clock And Reset Model

The registered clocks include PLLs, postdivs, RCG sources, read-only dividers, phy muxes, fixed factors, and branch gates. `gcc_pcnoc_bfdcd_clk_src` is marked critical because bootloader-initialized users may depend on it even when there are not yet kernel consumers.

PCIe0 and PCIe1 each have AXI master/slave RCGs, AUX RCG, rate-change RCG, AHB/AUX/AXI/bridge branches, and pipe clocks sourced through `clk_regmap_phy_mux` from the corresponding external PCIe30 PHY pipe clock. USB0 similarly has aux, master, mock UTMI, mock UTMI divider, sleep, PHY config, and pipe clocks. QUPv3 exposes six serial engine source clocks and branches. SDCC1 exposes apps and ICE core sources/branches.

Network and fabric coverage is heavy: NSS timestamp, NSSCC/NSSCFG, NSSNOC ATB/MEMNOC/PCNOC/SNOC/QoS/timeout/XO DCD clocks, GEPHY sys, MDIO and MDIO-GEPHY AHB, UNIPHY0/1/2 AHB and SYS clocks, CMN 12GPLL AHB/SYS, and system NoC source clocks. Debug and peripheral clocks include QDSS AT/DAP/TS counter, QRNG AHB, QPIC AHB/functional/IO macro, PON APB/TM/TM2X, LPASS AXIM/SWAY/CNOC/SNOC, and ADSS PWM.

The reset table mirrors these domains. It contains BCR and ARES entries for ADSS, APSS buses, boot ROM, GEPHY, MDIO, NSS/NSSNOC, PCIe0/1 detailed reset groups, QRNG, QUPv3 and its six SE blocks, QUSB2 and USB3 PHY, SDCC/ICE, TLMM, UNIPHY0/1/2, USB0, and QDSS.

## Control Flow

`core_initcall(gcc_ipq5210_init)` registers a platform driver with name `qcom,gcc-ipq5210`. Device-tree matching uses compatible `qcom,ipq5210-gcc`, which differs from the driver name but is normal for OF matching.

When the platform device probes, `qcom_cc_probe()` maps MMIO according to `gcc_ipq5210_regmap_config`, registers all entries in `gcc_ipq5210_clocks[]`, registers the standalone `clk_hw` objects from `gcc_ipq5210_hws[]`, and exposes reset controls from `gcc_ipq5210_resets[]`. Runtime behavior is then handled by common CCF callbacks: rate selection through RCG tables, parent selection through source maps or phy muxes, branch enable/disable with halt checks, and reset controller operations.

## State And Persistence

The driver has no file-backed persistence and no custom runtime state machine. Static C objects describe the hardware. Actual mutable state lives in GCC registers: PLL enable/configuration, RCG command and M/N/D registers, divider fields, branch enable bits, phy mux selections, and reset bits.

Unlike IPQ5018, this file does not explicitly configure a PLL in probe. It relies on the common qcom registration flow and existing hardware state for PLL roots, with critical flags preventing key roots from being disabled as unused. The `__maybe_unused` qualifier on `gcc_ipq5210_clocks[]` is only a compile-time annotation and does not change runtime state when the descriptor references the array.

## Dependencies And Integration Points

The driver depends on Linux platform probing, OF matching, CCF, regmap, qcom alpha PLL, qcom RCG/branch/divider/phy-mux helpers, and qcom reset support. External clocks must be provided in the DT order represented by `DT_XO`, `DT_SLEEP_CLK`, `DT_PCIE30_PHY0_PIPE_CLK`, `DT_PCIE30_PHY1_PIPE_CLK`, `DT_USB3_PHY0_CC_PIPE_CLK`, and `DT_NSS_CMN_CLK`.

Integration consumers include QUPv3 serial controllers, SDHCI with ICE, PCIe controllers and PHYs, USB controller and PHYs, NSS/NSSNOC networking blocks, MDIO/GEPHY/UNIPHY hardware, QPIC, QRNG, QDSS debug, LPASS, PON timing, and reset-controller clients. The binding IDs are the stable interface; clock names are mostly diagnostic.

## Risks

This file is dense with hardware constants. Parent-map source-select values, register offsets, branch halt types, and reset bits are the main correctness risks. Several maps distinguish GPLL main and aux paths while both may point at related `clk_hw` objects; incorrect selection can cause subtle frequency errors.

Critical-clock flags deserve review. `gpll4_main` and `gcc_pcnoc_bfdcd_clk_src` are kept on to protect bootloader-programmed dependencies. Removing those flags before all consumers exist can break early boot or fabric access; leaving them forever can hide missing consumers and increase power.

Phy mux handling differs from simple register muxes: PCIe and USB pipe clock sources use `clk_regmap_phy_mux_ops` and single external pipe parents. Device tree must supply those pipe clocks correctly, or link bring-up and USB SuperSpeed behavior can fail. Reset table entries include many ARES bits at bit 2 plus detailed PCIe sticky/core resets; wrong sequencing by consumers could leave links wedged.

## Test Signals

Build signals are successful compilation with IPQ5210 GCC clock/reset bindings and no initializer warnings. Probe signals are a successful `qcom,ipq5210-gcc` match, no regmap or qcom_cc probe errors, no duplicate clock registration failures, and a `clk_summary` tree showing PLLs, PCNOC/system NoC, QUPv3, PCIe, USB, SDCC, NSS, QPIC, QDSS, LPASS, PON, and GEPHY/UNIPHY clocks.

Functional validation should cover UART/SPI/I2C through all relevant QUPv3 SEs, SDCC1 rate switching and ICE core clocking, PCIe0/1 link training and reset recovery, USB0 enumeration including pipe clock behavior, NSS/UNIPHY/GEPHY networking paths, QPIC access, QRNG availability, QDSS/debug clocks, LPASS clocks if audio is enabled, and PON timing consumers. Reset tests should exercise PCIe detailed resets, USB/PHY resets, QUPv3 SE resets, NSS/NSSNOC resets, and SDCC resets while watching for branch halt timeout logs.
