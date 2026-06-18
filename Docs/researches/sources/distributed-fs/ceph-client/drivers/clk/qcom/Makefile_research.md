# sources/distributed-fs/ceph-client/drivers/clk/qcom/Makefile

## Purpose
The Qualcomm clock Makefile maps Kconfig symbols to shared framework objects and per-controller object files. It is the build contract connecting the symbols in `Kconfig` to regmap, PLL, RCG, branch, reset, GDSC, RPM, APSS, camera, display, GPU, video, and SoC-specific drivers.

## Important APIs, Types, And Functions
The composite `clk-qcom.o` is built from common infrastructure: `common.o`, `clk-regmap.o`, alpha and legacy PLL helpers, RCG/RCG2, branch clocks, regmap dividers/muxes/mux-divs, PHY muxes, HFPLL, reset, optional Krait support, and optional GDSC support. Subset-relevant mappings include `QCOM_A53PLL -> a53-pll.o`, `QCOM_A7PLL -> a7-pll.o`, `QCOM_CLK_APCS_MSM8916 -> apcs-msm8916.o`, `QCOM_CLK_APCC_MSM8996 -> apcs-msm8996.o clk-cpu-8996.o clk-cbf-8996.o`, `QCOM_CLK_APCS_SDX55 -> apcs-sdx55.o`, `IPQ_APSS_PLL -> apss-ipq-pll.o`, `IPQ_APSS_5424 -> apss-ipq5424.o`, `IPQ_APSS_6018 -> apss-ipq6018.o`, `CLK_KAANAPALI_CAMCC -> cambistmclkcc-kaanapali.o camcc-kaanapali.o`, and `SM_CAMCC_8750 -> cambistmclkcc-sm8750.o camcc-sm8750.o`.

## Control Flow, State, And Persistence
There is no runtime state. Build-time state is the ordered set of `obj-$(CONFIG_...)` and `clk-qcom-$(CONFIG_...)` assignments. The file asks maintainers to keep per-controller entries alphabetically sorted by config, which reduces merge conflicts in a high-churn driver directory.

## Dependencies, Integration Points, Risks, And Test Signals
It integrates Kbuild with Kconfig, generated DT binding constants, module autoloading through each driver, and shared `clk-qcom.o` support. Risks include missing objects for new Kconfig entries, duplicated objects under multiple configs, accidental module link failures when a controller uses helpers not included in `clk-qcom.o`, and sort drift hiding conflicts. Test signals are kernel builds for each selected symbol, `modpost` without unresolved symbols, camera configs building both CAMBISTMCLKCC and CAMCC objects, and MSM8996 APCC building the auxiliary CPU/CBF clock objects.
