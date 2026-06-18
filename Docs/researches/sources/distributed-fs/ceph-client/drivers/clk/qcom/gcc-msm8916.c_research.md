# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8916.c

## Purpose
This file is the Qualcomm Global Clock Controller driver for MSM8916. It describes the SoC-wide GCC clock, reset, and power-domain register layout for the common clock framework, including GPLL/BIMC PLL sources, root clock generators, voteable branch gates, multimedia and bus clocks, reset lines, and GDSC power domains for camera, display, video, and GPU blocks.

## Important APIs, Types, And Functions
The driver is almost entirely table-driven. It uses Qualcomm clock-provider types from the local qcom clock framework: `struct clk_pll`, `struct clk_regmap`, `struct clk_rcg2`, `struct clk_branch`, `struct gdsc`, `struct qcom_reset_map`, `struct regmap_config`, and `struct qcom_cc_desc`. `gcc_msm8916_probe()` registers fixed board inputs with `qcom_cc_register_board_clk()` and `qcom_cc_register_sleep_clk()`, then delegates mapping, registration, reset controller setup, and GDSC registration to `qcom_cc_probe()`. `gcc_msm8916_init()` registers the platform driver at `core_initcall()` time and `gcc_msm8916_exit()` unregisters it for module unload.

The clock data covers `gpll0`, `gpll1`, `gpll2`, and `bimc_pll` plus vote wrappers, parent maps for XO/GPLL/BIMC/sleep/DSI/external audio sources, many `freq_tbl` tables, RCGs for APSS AHB, PCNOC/SNOC, camera CSI/VFE/JPEG/CCI/MCLK/PHY timers, BLSP I2C/SPI/UART, crypto, GP, MDSS, PDM, SDCC, USB, audio, Venus, and BIMC/GPU paths, and branch gates for leaf clocks. `gcc_msm8916_clocks[]` binds these objects to the numeric IDs from `dt-bindings/clock/qcom,gcc-msm8916.h`. `gcc_msm8916_resets[]` binds reset IDs from `dt-bindings/reset/qcom,gcc-msm8916.h` to BCR offsets.

## Control Flow
At boot or module load, the platform driver matches `qcom,gcc-msm8916`. Probe first creates an `xo_board` clock from the firmware `xo` input at 19.2 MHz, then registers the sleep clock. If either input registration fails, probe aborts before touching the GCC register block. On success, `qcom_cc_probe()` maps the GCC MMIO resource using `gcc_msm8916_regmap_config`, registers every `clk_regmap` entry in `gcc_msm8916_clocks[]`, exposes the reset map, and registers the five GDSCs listed in `gcc_msm8916_gdscs[]`.

The runtime clock operations are handled by generic qcom clock ops selected in each table entry. PLLs use `clk_pll_ops` and vote clocks use `clk_pll_vote_ops`; RCGs use `clk_rcg2_ops` with the declared parent maps and rate tables; branch gates use `clk_branch2_ops` or simple branch behavior with halt checks such as `BRANCH_HALT` and `BRANCH_HALT_VOTED`. Rate changes flow from CCF consumers into the RCG frequency tables and, where `CLK_SET_RATE_PARENT` is present, may propagate to the selected parent.

## State And Persistence
The file has no private runtime allocation beyond the qcom common clock core's registration state. Persistent hardware state is the GCC register block itself: PLL mode/config/status registers, RCG command/config/M/N/D registers, branch enable bits, BCR reset registers, and GDSC control registers. The static clock descriptors live for the module lifetime and are indexed directly by DT binding IDs, so table ordering and sparse indexes are part of the ABI.

Several branch gates are voteable and use halt-voted semantics, so their state can be shared with other masters or firmware. GDSCs for Venus, MDSS, JPEG, VFE, and Oxili use `PWRSTS_OFF_ON` and persist power-domain state through the generic GDSC framework. There is no explicit suspend/resume save/restore in this driver; system sleep relies on hardware retention, firmware, and the common qcom clock/power-domain infrastructure.

## Dependencies And Integration Points
The driver depends on the MSM8916 clock and reset dt-bindings, the `qcom,gcc-msm8916` device-tree node, GCC MMIO resources, firmware-provided `xo` and `sleep_clk` inputs, and optional external parent clocks such as DSI PHY PLL and audio MCLK/I2S inputs. Consumers include BLSP serial/I2C/SPI, SDCC/eMMC/SD, USB HS, crypto, PRNG, camera, MDSS, Venus, GPU/Oxili, modem/TBU/SMMU, PDM, and low-power audio blocks.

Integration with the kernel happens through `qcom_cc_desc`: it publishes clocks to OF consumers by numeric clock IDs, reset controls by reset IDs, and GDSC power domains by power-domain IDs. The regmap config uses 32-bit registers, 4-byte stride, a `0x80000` maximum register, and fast I/O, so all clock/reset offsets must stay inside that declared map.

## Risks And Test Signals
The main risks are table drift and binding mismatch. A wrong array index can expose a clock under the wrong DT ID; a wrong parent map or frequency table entry can silently program an invalid mux/divider; a bad halt check can hang enable/disable paths; and a missing vote-aware branch can disable a resource still needed by firmware or another processor. GPLL and BIMC parent choices are especially sensitive because many derived bus, GPU, display, camera, and storage clocks depend on them. GDSC offset or power-state mistakes can leave multimedia blocks inaccessible or powered unexpectedly.

Useful test signals include successful probe on an MSM8916 device with no missing parent warnings, populated `/sys/kernel/debug/clk/clk_summary` entries matching the dt-binding IDs, working UART console and BLSP buses, SDCC1/2 rate changes, USB HS enumeration, camera/display/video/GPU probe with matching GDSC power transitions, reset-controller users successfully asserting/deasserting BCR lines, and suspend/resume or runtime-PM smoke tests showing no stuck branch halt checks.
