# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8909.c

## Purpose
This file is the Qualcomm GCC provider for MSM8909. It publishes PLLs, RCG2 sources, branch gates, resets, and GDSC power domains for application, BLSP, camera, crypto, display, GPU/Oxili, PDM, SDCC, USB HS, Venus/video, VFE, SMMU/TCU, MSS, and interconnect-related clocks. It is adapted from MSM8916-style GCC data and Qualcomm downstream MSM8909 clock data.

## Important APIs, Types, And Functions
The file combines modern and legacy Qualcomm clock types: `struct clk_alpha_pll` and `struct clk_alpha_pll_postdiv` for GPLL0/GPLL2/BIMC read-only shared PLLs, `struct clk_pll` plus `struct clk_regmap` vote clock for GPLL1, `struct clk_rcg2` for generated sources, `struct clk_branch` for CBCR gates, `struct gdsc` for MDSS/Oxili/Venus/VFE power domains, and `struct qcom_reset_map` for block resets and MSS restart. `gcc_msm8909_desc` passes these arrays to the common QCOM CC core. `gcc_msm8909_probe()` only calls `qcom_cc_probe(pdev, &gcc_msm8909_desc)`, and `gcc_msm8909_init()` registers the platform driver at `core_initcall()` time.

Important clock-source tables include APSS AHB, BLSP I2C/SPI/UART, camera GP/top AHB/CSI/PHY timer/VFE/MCLK, crypto, GFX3D, GP, MDP, PDM2, SDCC1/2, USB HS system, VCODEC0, and VSYNC. Display-specific RCGs use external DSI PLL parent indexes for byte and pixel clocks. GDSCs use CXC lists to identify dependent branch registers, and `venus_core0_gdsc` is flagged `HW_CTRL`.

## Control Flow
The platform driver binds to `qcom,gcc-msm8909`. Probe delegates to the QCOM common CC layer, which maps the register range up to `0x80000`, registers the `gcc_msm8909_clocks[]` entries, exposes resets from `gcc_msm8909_resets[]`, and registers power domains from `gcc_msm8909_gdscs[]`.

The static graph starts with XO and sleep-clock DT parents plus optional DSI PLL/DSI byte parents. GPLL0/GPLL2/BIMC are alpha PLL early roots with fixed ops and read-only postdivs to avoid changing shared PLL rates. GPLL1 is a legacy PLL with a separate vote clock. RCG2 sources derive APSS/bus, BLSP, display, camera, crypto, GPU, PDM, SDCC, USB, video, and VFE rates from XO, GPLLs, BIMC, or DSI PLL parents. Branches then gate final consumer clocks, usually with `CLK_SET_RATE_PARENT` where the branch should propagate rate requests to its RCG. The clock array maps all source and branch objects to binding IDs, then GDSC and reset arrays complete the provider contract.

## State And Persistence
The driver maintains no dynamic private state. Register state persists in GCC MMIO: alpha PLL vote/config state, GPLL1 PLL and vote bits, RCG command registers, branch enable/halt bits, reset bits, and GDSC power registers. Bus RCGs such as BIMC DDR/GPU and system/PCNOC BFDCD use no explicit frequency tables and can report hardware-selected rates; BIMC-related RCGs use `CLK_GET_RATE_NOCACHE` to avoid stale cached rates. GDSCs persist power-domain state and CXC dependencies in the genpd/GDSC framework after registration. Display pixel/byte clocks depend on external DSI PLL parents that are not owned by this GCC driver.

## Dependencies And Integration Points
The driver depends on `dt-bindings/clock/qcom,gcc-msm8909.h`, compatible `qcom,gcc-msm8909`, external DT parent order (`xo`, `sleep_clk`, `dsi0pll`, `dsi0pll_byte`), and Qualcomm alpha PLL, legacy PLL, RCG2, branch, regmap, reset, and GDSC helpers. Downstream consumers include CPU/APSS bus users, BLSP I2C/SPI/UART, CAMSS, crypto, MDSS/DSI, Oxili GPU, PDM, SDCC1/2, USB HS, Venus video, VFE, SMMU/TCU, MSS, and reset-controller clients.

## Risks And Test Signals
Important risks include binding-index drift in `gcc_msm8909_clocks[]`, wrong DSI PLL parent indexes breaking MDSS byte/pixel clocks, incorrect PLL fixed/read-only ops allowing Linux to disturb shared GPLL/BIMC rates, and GDSC CXC lists that omit a dependent clock or point at the wrong CBCR. The code has many similar BLSP and CAMSS branches, so register or halt-register copy errors are plausible. Reset entries include one delayed USB PHY reset and an MSS restart entry; wrong reset timing or register addresses can break USB PHY bring-up or subsystem restart.

Test signals include successful `gcc-msm8909` core-init probe, visible GPLL/GDSC/reset registration, working BLSP UART/I2C/SPI, SDCC1/2 rate changes, USB HS enumeration, camera CSI/VFE clocks and VFE GDSC transitions, MDSS DSI pixel/byte clocking from external DSI PLLs, Oxili GPU and Venus video power-domain on/off tests, crypto engine operation, MSS restart reset behavior, and clk-summary rates matching expected XO/GPLL-derived tables.
