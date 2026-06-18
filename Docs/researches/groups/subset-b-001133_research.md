# subset-b-001133 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8996.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8996.c

### Purpose
`gcc-msm8996.c` is the Qualcomm Global Clock Controller driver for MSM8996-family device trees matching `qcom,gcc-msm8996`. It describes the GCC register block to the common Qualcomm clock-controller core, exposing GPLL roots, RCG sources, branch gates, reset lines, fixed-factor helper clocks, and GDSC power domains used by USB, UFS, PCIe, SDCC, BLSP, QSPI, modem, graphics, LPASS, and interconnect consumers.

### Important APIs, Types, And Functions
The file is built around `struct clk_alpha_pll`, `struct clk_alpha_pll_postdiv`, `struct clk_fixed_factor`, `struct clk_rcg2`, `struct clk_branch`, `struct gdsc`, `struct qcom_reset_map`, `struct regmap_config`, and `struct qcom_cc_desc`. Static parent maps and `struct clk_parent_data` arrays encode mux values for XO, sleep clock, audio reference clock, GPLL0, GPLL0 early divide, and GPLL4. Frequency tables (`struct freq_tbl`) define rates for USB, SD/eMMC, BLSP SPI/I2C/UART, PDM, TSIF, GP, PCIe, UFS, and QSPI sources. `gcc_msm8996_probe()` maps the GCC registers with `qcom_cc_map()`, sets a low-power HMSS AHB control bit with `regmap_update_bits()`, then registers the descriptor with `qcom_cc_really_probe()`.

### Control Flow
Module/core initialization registers `gcc_msm8996_driver` through `core_initcall()`. On a matching platform device, probe maps the register window using `gcc_msm8996_regmap_config`, performs the one-off `HMSS_AHB_CLK_SLEEP_ENA` write at register `0x52008`, and hands all declarative resources to the Qualcomm common clock code. From that point, the common clock framework resolves clock IDs from `dt-bindings/clock/qcom,gcc-msm8996.h` into entries in `gcc_msm8996_clocks`, registers additional fixed-factor hardware clocks from `gcc_msm8996_hws`, registers reset controls from `gcc_msm8996_resets`, and exposes GDSC power domains from `gcc_msm8996_gdscs`. Runtime enable, disable, rate selection, parent selection, halt polling, and reset assertions are delegated to the generic qcom clock, reset, regmap, and GDSC operations referenced by the static structs.

### State, Persistence, And Dependencies
Persistent kernel state is mostly framework-owned after registration: clock hardware objects, clock-provider lookup entries, reset-controller lines, and genpd-backed GDSC power domains. Hardware state persists in the GCC MMIO registers described by `enable_reg`, `halt_reg`, `cmd_rcgr`, PLL offsets, reset offsets, and GDSC control offsets. The driver depends on the platform device created from device tree, external parents named `cxo`, `sleep_clk`, and `aud_ref_clk`, the MSM8996 clock/reset binding IDs, and local Qualcomm helpers in `common.h`, `clk-alpha-pll.h`, `clk-rcg.h`, `clk-branch.h`, `reset.h`, and `gdsc.h`.

### Dependencies And Integration Points
The output clocks are consumed by subsystem drivers through the common clock framework and by device-tree clock specifiers. USB and UFS consumers depend on master, sleep, mock UTMI, PHY AUX, pipe, AXI, UniPro, ICE, symbol, and reference clocks. PCIe consumers use three controller instances plus common PHY and AUX clocks. SDCC, BLSP, TSIF, PDM, QSPI, GP, HMSS, modem, MMSS/GPU, SMMU, NOC, and LPASS consumers receive their corresponding branch or RCG clocks. Reset integration is via `qcom_reset_map`, while power-domain integration is via GDSCs such as aggregate NOC, USB30, PCIe0-2, UFS, and HLOS vote LPASS domains.

### Risks
Most risk is data accuracy risk: wrong register offsets, mux values, parent arrays, binding indexes, or halt modes can silently break boot-critical peripheral clocks. The `gcc_msm8996_hws` side list is important because fixed-factor clocks like `gpll0_early_div` and UFS post-dividers are not normal `clk_regmap` entries; omitting them would break parent resolution. GDSC flags are power-sensitive: `aggre0_noc_gdsc` is `VOTABLE | ALWAYS_ON`, and USB30 intentionally uses retention-on power state until USB suspend support is adequate. The probe-time HMSS AHB sleep-enable bit affects low-power behavior and should not be moved after registration without understanding downstream clock usage.

### Test Signals
Useful validation includes booting an MSM8996 device with this GCC node present, confirming `/sys/kernel/debug/clk/clk_summary` exposes the expected GCC clock names and parent trees, exercising USB2/USB3, UFS including ICE, all SDCC instances, BLSP UART/I2C/SPI buses, QSPI, PCIe0-2, audio/TSIF/PDM, and modem/MMSS consumers. Suspend/resume and runtime PM should be checked for GDSC behavior, especially USB retention and the HMSS AHB sleep path. Reset-controller users should assert/deassert representative USB, PCIe, UFS, BLSP, bus-timeout, and MSS reset lines and verify no register access beyond `max_register = 0x8f010`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8996.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8998.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8998.c

### Purpose
`gcc-msm8998.c` is the Qualcomm GCC clock-controller driver for MSM8998 device trees matching `qcom,gcc-msm8998`. It provides the SoC-wide clock/reset/power-domain description for a large set of peripheral and interconnect consumers, including BLSP, USB3, UFS, PCIe, SDCC, TSIF, PDM, HMSS, GPU, MMSS, MSS, SSC, LPASS votes, and reference-clock outputs.

### Important APIs, Types, And Functions
The driver uses Fabia alpha PLL support through `struct clk_alpha_pll`, `struct clk_alpha_pll_postdiv`, `clk_alpha_pll_fixed_fabia_ops`, and `clk_alpha_pll_postdiv_fabia_ops`. It defines GPLL0 through GPLL4 and their even/main/odd/test post-dividers, parent maps for XO, sleep clock, audio reference clock, GPLL0 main, GPLL4 main, and early-div mux positions, and a large collection of `struct clk_rcg2` and `struct clk_branch` objects. `gcc_msm8998_probe()` is the only custom function: it calls `qcom_cc_map()`, sets the HMSS AHB sleep-enable bit, writes `GCC_MMSS_MISC` and `GCC_GPU_MISC`, then calls `qcom_cc_really_probe()`.

### Control Flow
`core_initcall(gcc_msm8998_init)` registers a platform driver. Probe maps the regmap using a 32-bit, 4-byte-stride, fast-IO config covering registers through `0x8f000`. Before exposing clocks to consumers, it enables hardware low-power control for `hmss_ahb_clk` at `0x52008` bit 21 and disables the GPLL0 active input to MMSS and GPU by writing `0x10003` to `GCC_MMSS_MISC` and `GCC_GPU_MISC`. Registration then flows through `qcom_cc_really_probe()`, which publishes the `gcc_msm8998_clocks` array, `gcc_msm8998_resets`, and `gcc_msm8998_gdscs` to common clock, reset, and genpd users.

### State, Persistence, And Dependencies
The persistent software objects are all static clock/regmap/GDSC/reset descriptors. Hardware state is retained in PLL control registers, RCG command registers, branch enable and halt registers, reset control offsets, and GDSC control registers. The driver depends on device-tree bindings from `qcom,gcc-msm8998.h`, external parents named `xo`, `sleep_clk`, and `aud_ref_clk`, and the common Qualcomm GCC infrastructure. Unlike MSM8996, this file does not define a separate `clk_hws` list; all exposed clocks in its descriptor are `clk_regmap` backed.

### Dependencies And Integration Points
Clock IDs in the MSM8998 binding map directly into `gcc_msm8998_clocks`. BLSP QUP and UART clocks share reusable SPI, I2C, and UART rate tables. SDCC2/SDCC4 use floor-rate RCG operations. UFS gets AXI, AHB, ICE, PHY AUX, UniPro, RX/TX symbol, and reference clocks. USB3 gets master, mock UTMI, sleep, PHY AUX, pipe, and AHB2PHY clocks. PCIe exposes controller, PHY, AUX, AXI, and pipe clocks, while GPU/MMSS clocks receive GPLL0 and BIMC/SNOC feeds. GDSCs cover PCIe, UFS, USB30, and LPASS ADSP/core voting domains. Reset lines cover peripheral blocks, PHYs, bus timeouts, voltage-sensor resets, MSS restart, GPU, and interconnect blocks.

### Risks
The probe writes are ordering-sensitive because they happen before clock registration and affect MMSS/GPU GPLL0 input selection and HMSS low-power operation. Parent-data correctness is subtle: some mux values labeled as early-div sources are represented by GPLL0 main hardware in the parent data, matching the hardware table expected by this downstream driver. PLL type and postdivider selection must match Fabia register layout; using default alpha PLL ops would corrupt rate programming. GDSC flags differ by domain: USB30 remains retention-on for suspend limitations, LPASS core is `ALWAYS_ON`, and other domains are votable. Binding-array holes or mismatched enum values would expose wrong clocks to device-tree consumers.

### Test Signals
Validation should include MSM8998 boot with early console surviving GCC registration, `clk_summary` inspection for GPLL0-4 and postdivider outputs, functional tests for BLSP buses, USB3, UFS, SDCC2/4, PCIe, GPU/MMSS consumers, TSIF/PDM, and SSC clocks. Runtime PM and system suspend should cover USB retention, UFS and PCIe GDSCs, LPASS votes, and HMSS AHB low-power entry. Reset tests should include USB PHY resets, PCIe link/PHY resets, UFS, BLSP, TSIF, voltage-sensor resets, GPU/MSS resets, and bus-timeout reset lines while checking for regmap errors from the probe-time update/write calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8998.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-nord.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-nord.c

### Purpose
`gcc-nord.c` is the Qualcomm Technologies GCC driver for device trees compatible with `qcom,nord-gcc`. It is a modern, PCIe-focused clock-controller description that exposes GPLL0, GP test clocks, PCIe A/B/C/D controller and PHY clocks, PCIe NOC clocks, QUPv3 wrapper/QSPI clocks, PDM clocks, SMMU vote clocks, resets, GDSC power domains, RPM-aware registration, and dynamic frequency-scaling metadata.

### Important APIs, Types, And Functions
Important static types include `struct clk_alpha_pll`, `struct clk_alpha_pll_postdiv`, `struct clk_regmap_phy_mux`, `struct clk_rcg2`, `struct clk_regmap_div`, `struct clk_branch`, `struct gdsc`, `struct qcom_reset_map`, `struct clk_rcg_dfs_data`, `struct qcom_cc_driver_data`, and `struct qcom_cc_desc`. GPLL0 uses Lucid OLE alpha PLL operations and an even post-divider table. Four PCIe pipe clock sources use `clk_regmap_phy_mux_ops` and device-tree parent indexes for external pipe clocks. Several RCGs set `hw_clk_ctrl = true` and use shared RCG ops. `gcc_nord_probe()` is intentionally thin and delegates directly to `qcom_cc_probe()`.

### Control Flow
`subsys_initcall(gcc_nord_init)` registers `gcc_nord_driver`, so this driver appears with other subsystem-level clock providers. Matching probe invokes `qcom_cc_probe(pdev, &gcc_nord_desc)`, which maps registers according to `gcc_nord_regmap_config`, registers all clocks in `gcc_nord_clocks`, exposes reset controls in `gcc_nord_resets`, registers GDSCs in `gcc_nord_gdscs`, honors `use_rpm = true`, and attaches driver data for DFS-capable RCGs. Runtime behavior is then framework-driven: consumers prepare/enable branch clocks, choose RCG rates from the tables, use muxed pipe parents from PHY-provided clocks, assert reset lines, and vote GDSC power domains.

### State, Persistence, And Dependencies
State persists in the GCC hardware registers up to `max_register = 0x1f41f0`, including Lucid OLE PLL controls, postdivider bits, RCG command registers, branch enable/halt registers, PHY mux registers, reset registers, and GDSC/collapse-control registers. Software state is static and registered once through qcom common clock code. Device-tree parents are index-based rather than mostly name-based: `DT_BI_TCXO`, `DT_SLEEP_CLK`, and four PCIe pipe clocks must be provided in the expected order from the binding. Dependencies include `clk-regmap-divider.h`, `clk-regmap-mux.h`, and `clk-regmap-phy-mux.h` in addition to the standard qcom PLL, RCG, branch, reset, and GDSC helpers.

### Dependencies And Integration Points
The clock table is centered on PCIe. Each of PCIe A-D has AUX, CFG AHB, DTI/QTC, master AXI, PHY AUX, PHY rate-change, PIPE, slave AXI, and slave Q2A AXI clocks, backed by a matching pipe mux and controller/PHY GDSCs. The PCIe NOC has async bridge, CNOC, master/slave AXI, PDB, power-control, QoS external reference, refgen, safety, timestamp counter, XO, and GDSC resources. QUPv3 wrapper 3 exposes core, 2x, M, S AHB, S0 divider, and QSPI reference clocks; the QSPI reference RCG is registered in the DFS list with `DEFINE_RCG_DFS()`. PDM and SMMU/TCU vote clocks integrate with audio and IOMMU users. Reset mappings cover each PCIe controller/PHY/link-down block, PCIe NOC, PDM, QUPv3 wrapper, and TCSR PCIe reset.

### Risks
PCIe lane bring-up is sensitive to parent ordering and pipe mux behavior; if the device tree supplies pipe clocks out of order or a mux register is wrong, the controller can fail only at link training time. The GDSCs use collapse-control masks in register `0x8d02c` with `POLL_CFG_GDSCR`, `RETAIN_FF_ENABLE`, and `VOTABLE`; incorrect masks can collapse the wrong PCIe domain or leave retention state inconsistent. Shared RCGs with `hw_clk_ctrl = true` rely on hardware-managed control and can race if treated like ordinary software-only clocks. The descriptor uses `use_rpm = true`, so RPM integration must be available for expected vote semantics. The very large regmap range makes offset mistakes less likely to be caught by max-register bounds.

### Test Signals
Validation should include boot with a `qcom,nord-gcc` node and all indexed parent clocks present, `clk_summary` checks for GPLL0, GP clocks, PCIe A-D source/branch clocks, PCIe NOC clocks, QUPv3/QSPI clocks, PDM, and vote clocks. PCIe testing should cover each A-D port independently, link down/up reset paths, PHY GDSC transitions, pipe parent switching, rate-change clocks, and system suspend/resume with retention. QUPv3/QSPI tests should exercise DFS changes on `gcc_qupv3_wrap3_qspi_ref_clk_src`. Reset-controller tests should assert controller, PHY, link-down, NOC, PDM, QUPv3, and TCSR resets while verifying qcom common-clock registration succeeds with RPM enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-nord.c -->
