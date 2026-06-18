# subset-b-001123 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-ipq4019.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-ipq4019.c

## Purpose

`gcc-ipq4019.c` is the Qualcomm Global Clock Controller driver for IPQ4019-class SoCs. It registers the GCC clock tree and reset lines used by APSS, PCNOC, BLSP, SDCC, PCIe, USB, ESS, crypto, audio, QPIC, IMEM, and 2.4/5 GHz WCSS blocks. The file is older than the alpha-PLL based IPQ5018/IPQ5210 drivers and carries custom FEPLL/divider logic for the APSS CPU PLL and fixed FEPLL outputs.

The exported ABI is the device-tree clock and reset provider described by `dt-bindings/clock/qcom,gcc-ipq4019.h`. Consumers request IDs from `gcc_ipq4019_clocks[]` and `gcc_ipq4019_resets[]`; no public C functions are exported.

## Important APIs, Types, And Functions

The driver depends on the common qcom clock framework: `qcom_cc_probe()`, `struct qcom_cc_desc`, `struct clk_regmap`, `struct clk_rcg2`, `struct clk_branch`, `struct qcom_reset_map`, `clk_rcg2_ops`, `clk_rcg2_floor_ops` where applicable, `clk_branch2_ops`, and `clk_regmap_div` helpers.

Two local data types model the FEPLL hardware:

- `struct clk_fepll_vco` describes feedback-divider and reference-divider bitfields in a PLL_DIV register.
- `struct clk_fepll` wraps a `clk_regmap_div` with optional fixed divider, divider table, frequency table, and VCO descriptor.

The custom operations are central:

- `clk_fepll_vco_calc_rate()` reads the PLL divider register through regmap and calculates `parent / refclkdiv * 2 * fdbkdiv`.
- `clk_cpu_div_determine_rate()` maps requested APSS CPU rates through `ftbl_apss_ddr_pll[]` and selects the parent.
- `clk_cpu_div_set_rate()` writes the APSS CPU divider field and waits with `udelay(1)` because the hardware has no completion bit.
- `clk_cpu_div_recalc_rate()` handles the APSS nonlinear divider encoding, including half-step values encoded above 10.
- `clk_regmap_clk_div_recalc_rate()` provides fixed or table-driven FEPLL-derived rates.
- `gcc_ipq4019_cpu_clk_notifier_fn()` moves `apps_clk_src` to a safe FEPLL500 parent before APSS rate changes.

## Clock And Reset Model

The root parent set is small: XO, FEPLL200, FEPLL500, DDRPLL-derived SDCC/APSS outputs, WCSS FEPLL divided outputs, and FEPLL125DLY. The file defines fixed FEPLL outputs such as `fepll125`, `fepll200`, `fepll500`, APSS DDR PLL dividers for CPU and SDCC, and table-backed WCSS 2G/5G dividers.

RCG sources cover PCNOC AHB, audio PWM, BLSP I2C/SPI/UART, GP1-GP3, SDCC1 apps, APSS apps and APSS AHB, FEPHY delay, USB mock UTMI, and WCSS 2G/5G. Branch clocks gate the corresponding peripherals and bus paths. Several branches use `BRANCH_HALT_VOTED`, meaning enable state is controlled through shared vote registers such as `0x6000`; others use direct branch registers and normal halt polling.

`pcnoc_clk_src` is marked `CLK_IS_CRITICAL`, reflecting that the peripheral NoC clock must stay alive for system access. Many consumer-visible clocks use `CLK_SET_RATE_PARENT`, allowing device drivers to propagate rate requests up to their source clock.

The reset map includes WiFi0/WiFi1 cold/warm/radio resets, USB2/USB3 PHY resets, PCIe reset groups, ESS/MAC resets, subsystem BCRs, NoC timeout BCRs, BLSP, crypto, SDCC, QPIC, TLMM, SPDM, MPM, and related hardware reset lines. Reset entries are simple register/bit mappings; the common reset controller implements assertion and deassertion.

## Control Flow

At boot, `core_initcall(gcc_ipq4019_init)` registers a platform driver named `qcom,gcc-ipq4019`. Device-tree matching uses compatible `qcom,gcc-ipq4019`.

`gcc_ipq4019_probe()` calls `qcom_cc_probe(pdev, &gcc_ipq4019_desc)`. The common qcom code maps the MMIO region using `gcc_ipq4019_regmap_config`, initializes the listed `clk_regmap` entries, and registers reset controls. After successful clock-controller registration, the probe registers `gcc_ipq4019_cpu_clk_notifier` against `apps_clk_src.clkr.hw.clk`.

Normal runtime operations are driven by Linux CCF consumers. Rate changes call through `clk_rcg2_ops` or the custom FEPLL CPU divider ops. Branch enables update hardware enable bits and wait according to each branch halt policy. APSS rate changes are special: before the rate change, the notifier forces the APSS source parent to safe parent index 2, which the file documents as FEPLL500 in `gcc_xo_ddr_500_200`.

## State And Persistence

All meaningful state is hardware register state accessed through regmap. There is no file-backed persistence, heap-owned persistent state, or runtime cache beyond static clock descriptor objects and common CCF registration structures. Divider values, parent selections, branch enables, and reset assertions persist only as long as the GCC hardware and power domain retain registers.

The custom FEPLL code reads live VCO fields instead of caching them. The APSS divider set path writes a divider field and uses a fixed microsecond delay because the hardware exposes no completion status. That makes bootloader-programmed PLL values and current hardware state important inputs to recalc behavior.

## Dependencies And Integration Points

The driver relies on Linux platform-device probing, device tree, CCF, regmap, qcom common clock/reset helpers, and dt-binding ID stability. It includes `linux/clk.h` for notifier registration and parent switching. Integration consumers include APSS CPU frequency code, BLSP serial/I2C/SPI controllers, SDHCI, USB, PCIe, crypto, ESS Ethernet switch, WiFi/WCSS blocks, and reset-controller clients.

## Risks

The main risk is register-description accuracy. Parent maps, source-selection values, M/N/D values, divider encodings, and reset bits must match the IPQ4019 GCC hardware manual and dt bindings. A one-entry error can silently produce bad peripheral rates or gate the wrong domain.

The FEPLL VCO calculation divides by `refclkdiv` read from hardware. If hardware or boot firmware leaves a zero divider, the code has no explicit guard. This is usually prevented by valid silicon initialization, but it is still a hardware-state dependency. APSS rate changes also depend on the safe parent index staying aligned with `gcc_xo_ddr_500_200`; a parent-list reorder without updating `gcc_ipq4019_cpu_safe_parent` would be dangerous.

The custom APSS divider path lacks status polling and depends on `udelay(1)`. If a future SoC revision needs longer settling or exposes a real status bit, this code would need adjustment. Critical/voted clocks should be treated carefully because incorrect halt policy can cause false timeout warnings or shut down shared infrastructure.

## Test Signals

Build-level signals are successful compilation with the IPQ4019 dt-binding header and no sparse/Coccinelle issues around static initializers. Boot-level signals are a clean probe for `qcom,gcc-ipq4019`, no CCF duplicate-name warnings, no branch halt timeout messages, and a populated `/sys/kernel/debug/clk/clk_summary` containing APSS, PCNOC, BLSP, USB, PCIe, WCSS, ESS, and SDCC clocks.

Functional signals include serial console stability through BLSP UART rates, SDCC1 frequency changes including 400 kHz and high-speed modes, USB2/USB3 enumeration, PCIe link bring-up, ESS/WCSS resets working for network devices, and cpufreq/APSS rate changes completing without lockups. Reset testing should assert/deassert representative USB, PCIe, WiFi, and ESS reset IDs and verify the target hardware recovers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-ipq4019.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-ipq5018.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-ipq5018.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-ipq5210.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-ipq5210.c -->
