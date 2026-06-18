# sources/distributed-fs/ceph-client/drivers/clk/qcom/Kconfig

## Purpose
This Kconfig file defines the selectable Qualcomm common clock controller matrix. It enables the shared `COMMON_CLK_QCOM` framework and per-SoC controllers for global, camera, display, GPU, video, TCSR, RPM/RPMh, LPASS, APSS CPU, NSS, PMIC, HFPLL, Krait, and related clock blocks.

## Important APIs, Types, And Functions
The important symbols for this subset are `COMMON_CLK_QCOM`, `QCOM_GDSC`, `QCOM_A53PLL`, `QCOM_A7PLL`, `QCOM_CLK_APCS_MSM8916`, `QCOM_CLK_APCC_MSM8996`, `QCOM_CLK_APCS_SDX55`, `IPQ_APSS_PLL`, `IPQ_APSS_5424`, `IPQ_APSS_6018`, `CLK_KAANAPALI_CAMCC`, and `SM_CAMCC_8750`. Most controller symbols are tristates, allowing built-in or module builds. Selections wire dependencies such as `REGMAP_MMIO`, `RESET_CONTROLLER`, `INTERCONNECT`, `QCOM_GDSC`, SoC GCC providers, SMEM, APCS IPC, and architecture limits.

## Control Flow, State, And Persistence
There is no runtime control flow, but the Kconfig graph determines which C files compile and which provider drivers can satisfy DT compatibles. `COMMON_CLK_QCOM` gates the menu and selects shared infrastructure. Multimedia controllers usually select their SoC GCC to ensure upstream parent clocks are present. CPU/APSS options select or depend on PLL, IPC, SMEM, interconnect, and architecture symbols so CPU clock scaling pieces build together.

## Dependencies, Integration Points, Risks, And Test Signals
This file integrates the clock drivers with kernel configuration, devicetree-described platforms, reset and generic power-domain support, RPM/RPMh firmware interfaces, and interconnect clocks. Risks are missing `select` statements causing parent clocks, GDSCs, or reset support to be absent; overly narrow architecture dependencies hiding COMPILE_TEST coverage; and Makefile/Kconfig drift. Test signals include `allmodconfig`/`allyesconfig`/SoC defconfig builds, module link checks for every selected symbol, DT boot logs finding the expected clock providers, and camera/APSS symbols pulling their paired files from the Makefile.
