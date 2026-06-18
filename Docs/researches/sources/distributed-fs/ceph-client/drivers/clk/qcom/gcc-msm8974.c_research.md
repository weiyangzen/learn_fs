# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8974.c

## Purpose
`gcc-msm8974.c` implements the Qualcomm Global Clock Controller for MSM8974-family SoCs and includes MSM8226 compatibility handling plus MSM8974 Pro/Pro-AC clock extensions. It exposes GPLLs, RCG2 roots, branch clocks, resets, and one USB HS/HSIC GDSC for NoC, BLSP/QUP/UART, crypto, SDCC, USB, TSIF, PDM, MSS/LPASS/MMSS support, and assorted system infrastructure.

## Important APIs, Types, And Functions
The PLL layer uses `struct clk_pll` and `clk_pll_ops` for `gpll0`, `gpll1`, and optional `gpll4`, with vote wrappers `gpll0_vote`, `gpll1_vote`, and optional `gpll4_vote` using `clk_pll_vote_ops`. Parent maps describe XO, GPLL0, GPLL1, and GPLL4 hardware selector values. Programmable roots are `struct clk_rcg2` objects using `clk_rcg2_ops` or `clk_rcg2_floor_ops`, with `freq_tbl` tables for USB3, BLSP I2C/SPI/UART, CE1/CE2, GP clocks, PDM2, SDCC, TSIF, USB HS, and HSIC paths.

Consumer gates are `struct clk_branch` objects using `clk_branch2_ops`, with many `CLK_SET_RATE_PARENT` flags on peripheral app clocks. Some AHB/AXI/system branches use `BRANCH_HALT_VOTED` because their enable bits are vote-controlled through shared registers at `0x1484`. `gcc_mmss_gpll0_clk_src` is a simple regmap branch-style vote exported as `mmss_gpll0_vote`. `usb_hs_hsic_gdsc` is a `struct gdsc` power domain at GDSCR offset `0x404` with `PWRSTS_OFF_ON`.

There are three descriptor/resource sets in the file: `gcc_msm8226_clocks`/`gcc_msm8226_resets`/`gcc_msm8226_gdscs`/`gcc_msm8226_desc`, and `gcc_msm8974_clocks`/`gcc_msm8974_resets`/`gcc_msm8974_gdscs`/`gcc_msm8974_desc`. Variant mutators `msm8226_clock_override()` and `msm8974_pro_clock_override()` modify static frequency tables, SDCC1 parent data, and optional GPLL4/CDCCAL clock array entries before registration. `gcc_msm8974_probe()` registers XO and sleep clocks, applies variant overrides, then calls the common probe path.

## Control Flow
The driver is registered at `core_initcall()` and matches `qcom,gcc-msm8226`, `qcom,gcc-msm8974`, `qcom,gcc-msm8974pro`, and `qcom,gcc-msm8974pro-ac`. Probe reads `device_get_match_data()`, and for any compatible other than the base `qcom,gcc-msm8974` it applies a variant override: MSM8226 swaps CE1 and GP clock frequency tables to reduced MSM8226 tables; Pro/Pro-AC enables SDCC1 GPLL4 parent/rates and fills previously NULL GPLL4 and SDCC1 CDCCAL entries in `gcc_msm8974_clocks`.

After override, probe registers a fixed `xo_board` provider at 19.2 MHz and registers the shared sleep clock provider via `qcom_cc_register_sleep_clk()`. It then calls `qcom_cc_probe(pdev, &gcc_msm8974_desc)`, which maps registers, registers clocks, resets, and the USB HS/HSIC GDSC from the descriptor, and exposes clock/reset/power-domain providers to device-tree consumers.

Runtime control is data-driven through common clock ops. RCG2 roots select XO/GPLL parents and program HID/MND fields from frequency tables; branch clocks set enable bits and poll halt status; reset consumers use `gcc_msm8974_resets`; genpd consumers control the USB HS/HSIC domain through the GDSC helper.

## State And Persistence Behavior
There is no persistent storage. Hardware-visible state lives in GCC registers: PLL mode/config/status, PLL vote bits, command RCGR settings, branch enable bits, reset bits, sleep-clock branches, and GDSC power state. Static C state is mostly descriptor data, but the variant override functions mutate global descriptors before registration: CE1/GP frequency table pointers for MSM8226, SDCC1 init parent metadata and frequency table for Pro variants, and optional entries in `gcc_msm8974_clocks`.

Because the static objects are global, the selected variant should be treated as boot-time one-shot state. The file assumes one compatible instance and does not restore mutated descriptor data on remove. Sleep-clock parent references are resolved through the provider registered in probe, and GDSC state persists until changed by genpd or reset.

## Dependencies
Dependencies include Linux platform-driver, OF match, module, regmap, reset-controller, common clock framework, QCOM common CC helpers, PLL/RCG/branch helpers, reset support, and GDSC support. Binding IDs come from `dt-bindings/clock/qcom,gcc-msm8974.h` and `dt-bindings/reset/qcom,gcc-msm8974.h`.

The driver integrates with board/root clocks through `qcom_cc_register_board_clk(dev, "xo_board", "xo", 19200000)` and `qcom_cc_register_sleep_clk(dev)`. It relies on QCOM common CC code to wire the `qcom_cc_desc` arrays into the kernel clock, reset, and genpd frameworks.

## Integration Points
Clock consumers include BLSP1/BLSP2 QUP I2C/SPI and UART ports, CE1/CE2 crypto, GP clocks, SDCC1-4, USB2 PHY sleep clocks, USB3 master/mock/sleep clocks, USB HS and HSIC clocks, TSIF, PDM, PRNG, BAM DMA, boot ROM, NoC/system fabric, MMSS/OCMEM/MSS/LPASS support clocks, and MMSS GPLL0 vote users. Reset consumers include NoC, USB, SDCC, BLSP, PDM, BAM, TSIF, TCSR, boot ROM, message RAM, TLMM, MPM, security, SPMI, SPDM, CE, BIMC, bus timeout, DEHR/RBCPR, and subsystem restart lines.

The `USB_HS_HSIC_GDSC` power domain is exported for USB HS/HSIC consumers. Pro variants add GPLL4 and SDCC1 calibration/sleep clocks to support higher SDCC1 rates. MSM8226 has a narrower hardware description in the file, but the current probe path still calls `qcom_cc_probe()` with `gcc_msm8974_desc` rather than the match-provided descriptor.

## Risks
The highest-risk area is variant handling. The match table includes `gcc_msm8226_desc`, but `gcc_msm8974_probe()` ignores `data` for the final common probe call and always passes `&gcc_msm8974_desc`. As written, MSM8226 gets reduced CE1/GP frequency tables but not the MSM8226 clock/reset/regmap descriptor during registration; that can expose unsupported MSM8974 resources or access beyond MSM8226's declared register range. This should be treated as a strong review/test signal before relying on MSM8226 behavior.

The Pro override mutates global SDCC1 init data and the shared `gcc_msm8974_clocks` array. That is appropriate for a single GCC instance, but it is not reversible and can affect any later probe in the same kernel if multiple compatibles were ever instantiated. Parent-map correctness is also critical for GPLL4 SDCC1 rates because the normal SDCC tables do not include GPLL4.

Other risks are the usual hand-authored GCC table hazards: wrong register offsets, selector values, halt policies, reset offsets, or frequency entries can break one peripheral while the provider still probes. Branches using voted enable registers and the simple MMSS GPLL0 vote require hardware-specific halt behavior to be correct. GDSC offset and power-state assumptions need USB runtime PM validation.

## Test Signals
Build tests should compile all four compatibles' binding IDs and array indexes cleanly. Boot tests should verify successful probe for base MSM8974, MSM8974 Pro/Pro-AC, and MSM8226, with `xo_board` and `sleep_clk` providers registered before GCC clocks resolve.

Runtime signals include clk-summary visibility for expected IDs, BLSP I2C/SPI/UART transfers at listed rates, CE crypto operation at each available rate, SDCC1-4 card/eMMC rate changes, USB2/USB3/HSIC enumeration and suspend/resume, TSIF/PDM/PRNG consumers, reset assertion/deassertion for representative BCRs, MMSS GPLL0 vote behavior, and GDSC on/off transitions for `usb_hs_hsic`. MSM8226 validation should specifically check that only valid MSM8226 resources are exposed and that no register access reaches resources absent from that SoC.
