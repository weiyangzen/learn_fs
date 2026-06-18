# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8998.c

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
