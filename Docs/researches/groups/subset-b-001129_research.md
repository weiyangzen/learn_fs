# Research: subset-b-001129

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8916.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8916.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8917.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8917.c

## Purpose
This file implements the Qualcomm GCC provider for MSM8917-family SoCs, with compatible data for `qcom,gcc-msm8917`, `qcom,gcc-qm215`, `qcom,gcc-msm8937`, `qcom,gcc-msm8940`, and `qcom,gcc-sdm439`. It publishes the family clock tree, resets, and GDSC power domains for APSS/bus, BLSP, camera, display, GPU, video, storage, crypto, USB, and related blocks, while applying per-SoC differences in available clock IDs, GPU parent choices, PLL ranges, and multimedia frequency tables.

## Important APIs, Types, And Functions
The driver uses qcom CCF building blocks: `struct clk_alpha_pll`, `struct clk_alpha_pll_postdiv`, `struct clk_pll`, `struct clk_regmap`, `struct clk_rcg2`, `struct clk_branch`, `struct gdsc`, `struct qcom_reset_map`, `struct qcom_cc_desc`, and parent/frequency map helpers. `gpll0_sleep_clk_src`, `gpll0_early`, `gpll0`, `gpll3_early`, `gpll3`, `gpll4_early`, `gpll4`, `gpll6_early`, and `gpll6` define the main PLL sources. `gpll3_early_config` is programmed explicitly at probe time with `clk_alpha_pll_configure()`.

Most RCGs and branches mirror hardware domains: APSS AHB, BLSP1/2 I2C/SPI/UART, byte/esc/pixel/display clocks, camera GP/CCI/CPP/CSI/CSIPHY/CSIPHY timer/MCLK/VFE/JPEG clocks, crypto, GPU `gfx3d`, GP clocks, PDM, SDCC apps and SDCC1 ICE, USB HS system/PHY/AHB, Venus/Vcodec, and SMMU/TBU/DCC/QDSS support. `gcc_msm8917_clocks[]`, `gcc_msm8937_clocks[]`, and `gcc_msm8940_clocks[]` expose different sparse clock-ID sets from `dt-bindings/clock/qcom,gcc-msm8917.h`. `gcc_msm8917_resets[]` exposes a small reset set for CAMSS micro, MSS, USB/PHY, and MDSS.

`msm8937_clock_override()` and `sdm439_clock_override()` mutate selected static descriptors before registration to match SoC-specific GPLL3, VFE, CPP, Vcodec, CSI PHY timer, USB, and GPU behavior. `gcc_msm8917_probe()` chooses the descriptor from OF match data, applies those overrides when needed, maps the register block with `qcom_cc_map()`, configures GPLL3, and finishes with `qcom_cc_really_probe()`.

## Control Flow
The platform driver registers at `core_initcall()` and matches one of five compatibles. Probe obtains `struct qcom_cc_desc` from `of_device_get_match_data()`. For QM215 it changes the GFX3D parent map to the QM215-specific map. For MSM8937 and MSM8940 it applies `msm8937_clock_override()` and then selects the correct GFX3D frequency table. For SDM439 it applies `sdm439_clock_override()`, including the SDM439 GFX3D table. MSM8917 uses the base descriptors without mutation.

After compatibility adjustment, probe maps the GCC MMIO region through `qcom_cc_map()`. A mapping error returns immediately. The driver then configures `gpll3_early` from `gpll3_early_config`; the base configuration is a 1 GHz-class alpha PLL setup, while MSM8937/MSM8940 adjust GPLL3 to a 750 MHz configuration and narrower VCO table. Finally `qcom_cc_really_probe()` registers the clocks, resets, and GDSCs from the chosen descriptor. Runtime operations are generic CCF/qcom ops: alpha PLL ops handle dynamic PLL updates and postdividers, RCG2 ops select parents/dividers from rate tables, branch ops gate leaves and check halt bits, and GDSC ops manage power domains.

## State And Persistence
State is held in static descriptor objects until registration and then in GCC hardware registers. Probe-time overrides mutate global static tables, so the driver assumes one SoC-compatible instance per kernel boot; registering multiple different compatibles in one kernel instance would be unsafe because the mutations are not per-device copies. Hardware state includes PLL configuration and vote bits, RCG config/cmd registers, branch enable and halt bits, BCR reset lines, and GDSC power-domain registers.

`gpll3_early` supports dynamic update and `gpll3` has `CLK_SET_RATE_PARENT`, making it a rate source for several multimedia clocks. Display byte/pixel sources and GFX3D also propagate rates to parents in selected paths. There is no explicit suspend/resume path; clock and power-domain persistence is delegated to the common clock framework, qcom PLL/branch/RCG helpers, GDSC support, firmware, and hardware retention.

## Dependencies And Integration Points
The driver depends on `dt-bindings/clock/qcom,gcc-msm8917.h`, device-tree compatibles for the five supported SoCs, indexed parent clocks for XO, sleep clock, and DSI PLL byte/output inputs, and the qcom common clock, alpha PLL, branch, RCG, reset, and GDSC helpers. Unlike the MSM8916 driver, the parent data uses DT parent indexes for external inputs rather than registering fixed board clock names locally.

Consumers are the platform's APSS/bus fabric, BLSP1/2 controllers, CAMSS, MDSS, Adreno/Oxili, Venus, SDCC/eMMC/SD plus inline crypto, USB HS/QUSB2 PHY, crypto/prng, MSS, SMMU/TBU, QDSS/DCC, PDM, and miscellaneous GP clocks. Descriptor selection controls both what clock IDs exist and which GDSCs are exported: MSM8917/QM215 use the base GDSC set, while MSM8937/MSM8940/SDM439 add the Oxili CX domain and use the MSM8937-flavored Oxili GX domain.

## Risks And Test Signals
The highest-risk behavior is probe-time mutation of shared static descriptors. A missed override can use an invalid rate table or parent map for a derivative SoC; an unintended override can affect later registration if the driver were ever instantiated for more than one compatible. Sparse clock tables are also risky because MSM8937/MSM8940-only IDs, dual DSI clocks, CSI2/VFE1 clocks, Oxili AON/timer clocks, IPA TBU, and extra BLSP2 QUP4 entries must match the binding exactly. PLL risk centers on GPLL3 configuration and VCO limits; wrong values can destabilize camera, display, video, or GPU rates.

Useful test signals include clean probe for each compatible, GPLL3 rate matching the selected SoC configuration, `clk_summary` showing only the expected ID set for the matched descriptor, BLSP1/2 UART/I2C/SPI operation, SDCC1/2 and SDCC1 ICE operation, USB HS enumeration, MDSS byte/pixel/esc clocks with DSI parents, CAMSS with CSI0/1/2 and VFE0/1 where supported, Venus and GPU power-domain transitions, reset controls for MSS/USB/MDSS/CAMSS micro, and rate-change tests for GFX3D/VFE/CPP/Vcodec confirming the compatible-specific tables are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8917.c -->
