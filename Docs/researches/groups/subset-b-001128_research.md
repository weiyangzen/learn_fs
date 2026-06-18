# Research: subset-b-001128

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-milos.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-milos.c

## Purpose
This file is the Qualcomm Global Clock Controller provider for the Milos platform. It describes the GCC register block as common-clock framework objects, reset-controller entries, and GDSC power domains, then publishes them for the `qcom,milos-gcc` device-tree compatible. The covered hardware includes Lucid-OLE GPLLs, PCIe, UFS, USB3, SDCC, QUPv3, PDM, GPU/display/video interconnect clocks, hardware-controlled UFS clocks, QUPv3 DFS-capable RCGs, and GCC-owned resets and power domains.

## Important APIs, Types, And Functions
The driver is built almost entirely from Qualcomm clock-controller data types: `struct clk_alpha_pll`, `struct clk_alpha_pll_postdiv`, `struct clk_rcg2`, `struct clk_regmap_mux`, `struct clk_regmap_div`, `struct clk_branch`, `struct gdsc`, `struct qcom_reset_map`, `struct clk_rcg_dfs_data`, `struct qcom_cc_driver_data`, and `struct qcom_cc_desc`. The only runtime callback is `gcc_milos_probe()`, which delegates registration to `qcom_cc_probe(pdev, &gcc_milos_desc)`. Module lifetime is handled by `platform_driver_register()` from `gcc_milos_init()` via `subsys_initcall()` and `platform_driver_unregister()` in `gcc_milos_exit()`.

Key data structures include the DT-parent enum matching `dt-bindings/clock/qcom,milos-gcc.h`, internal parent IDs for GPLLs and external PHY clocks, 16 `parent_map`/`clk_parent_data` groups, RCG2 frequency tables, `gcc_milos_clocks[]`, `gcc_milos_resets[]`, `gcc_milos_gdscs[]`, `gcc_milos_dfs_clocks[]`, and `gcc_milos_critical_cbcrs[]`. `gcc_milos_desc` sets `.use_rpm = true` and attaches `gcc_milos_driver_data`, so the common QCOM CC core can handle RPM-aware registration, critical CBCR retention, and DFS RCG setup.

## Control Flow
Probe matching starts from `gcc_milos_match_table` with compatible `qcom,milos-gcc`. When the platform device probes, `qcom_cc_probe()` maps the GCC register resource using `gcc_milos_regmap_config`, registers every clock in `gcc_milos_clocks[]`, registers reset lines from `gcc_milos_resets[]`, creates GDSC power domains from `gcc_milos_gdscs[]`, and applies Milos-specific driver data for critical CBCRs and DFS-capable RCGs.

The static clock graph is layered from roots to leaves. GPLL0/2/4/6/7/9 are fixed Lucid-OLE alpha PLLs sourced from `bi_tcxo`; GPLL0 also exposes an even postdivider. Parent maps combine `bi_tcxo`, `sleep_clk`, GPLL outputs, and externally supplied PCIe/UFS/USB PHY pipe or symbol clocks. RCGs generate GP, PCIe aux/phy_rchng, PDM, QUPv3 serial/QSPI, SDCC, UFS, and USB master/mock/aux rates. Register muxes select external pipe/symbol parents with XO fallbacks, read-only dividers model pipe-div2/QUP S2/mock-UTMI postdiv paths, and branches gate the final consumer clocks with the appropriate halt policy and rate-parent flags.

## State And Persistence
The driver has no private mutable state beyond static descriptors. Persistent state is hardware state in the GCC MMIO register block: PLL vote bits, RCG command registers, branch enable/halt registers, hardware clock-gating bits, reset bits, and GDSC control registers. Linux framework state is maintained by the common clock, reset, and genpd/GDSC frameworks after `qcom_cc_probe()`. Several branches use `BRANCH_HALT_SKIP`, `BRANCH_HALT_VOTED`, or `BRANCH_HALT_DELAY`, reflecting hardware paths where halt status is absent, voted by another owner, or delayed. UFS exposes paired software and `_HW_CTL` branches that share CBCR addresses with different enable bits, so hardware-controlled retention depends on the exact bit assignments. Critical CBCRs for camera, display, GPU, and video AHB/XO clocks are listed separately to avoid unsafe disable during registration or late init.

## Dependencies And Integration Points
The driver depends on `dt-bindings/clock/qcom,milos-gcc.h` for clock, reset, and GDSC IDs; the device tree must provide the GCC MMIO resource and external parent clocks in the binding order (`bi_tcxo`, `sleep_clk`, PCIe pipe clocks, UFS RX/TX symbol clocks, and USB3 pipe clock). It integrates with the Qualcomm common clock code in `common.c`, alpha PLL support, RCG2 support, regmap mux/div helpers, branch clock helpers, reset support, and GDSC power-domain support. Consumers are PCIe, UFS, USB3, SDCC/eMMC, QUPv3 serial/SPI/I2C/QSPI, PDM, GPU, display, camera, video, and interconnect fabric drivers that request the exported DT clock/reset/power-domain IDs.

## Risks And Test Signals
The main risks are register offset or bit mismatches in a very large static table, binding-index drift between `gcc_milos_clocks[]` and `qcom,milos-gcc.h`, incorrect external pipe/symbol parent ordering, and bad halt policy selection causing enable/disable timeouts or false success. GDSC collapse masks for PCIe domains share `0x5214c`; incorrect masks can collapse the wrong PCIe block. DFS entries only cover QUPv3 RCGs, so missing or extra entries would affect serial/QSPI dynamic frequency switching. Critical CBCR omissions can break display/camera/GPU/video paths during boot.

Useful validation signals are a Milos boot with `gcc-milos` probing successfully, no `qcom_cc_really_probe()` or clock registration errors, correct entries in `/sys/kernel/debug/clk/clk_summary`, working PCIe0/1 link training, UFS gear changes, USB3 operation, SDCC/eMMC rate changes, QUPv3 UART/SPI/I2C/QSPI transfers across advertised rates, GDSC on/off transitions for PCIe/UFS/USB, reset assertions for listed BCRs, and suspend/resume tests showing retained critical clocks and hardware-controlled UFS clocks behave correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-milos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8660.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8660.c

## Purpose
This file is the Qualcomm GCC provider for MSM8660. It exposes an older GCC register layout through the common clock and reset frameworks, covering PLL8, a voteable PLL8 clock, GSBI UART/QUP clocks for twelve GSBI blocks, GP clocks, PRNG, SDC1-5, TSIF, USB FS/HS clocks, AHB/H bus gates, EBI2, ADM, modem, PMIC arbitration, SSBI, RPM message RAM, and a large SoC reset map.

## Important APIs, Types, And Functions
The implementation uses legacy Qualcomm clock structures: `struct clk_pll`, `struct clk_regmap` for `pll8_vote`, pre-RCG2 `struct clk_rcg`, `struct clk_branch`, `struct qcom_reset_map`, `struct regmap_config`, and `struct qcom_cc_desc`. Parent data maps firmware names `pxo`/`pxo_board` and `cxo`/`cxo_board` plus the internal voted PLL8 output. Frequency tables are plain `struct freq_tbl` arrays for GSBI UART, GSBI QUP, GP, SDC, TSIF, and USB rates.

`gcc_msm8660_probe()` is the sole probe callback and simply calls `qcom_cc_probe(pdev, &gcc_msm8660_desc)`. `gcc_msm8660_init()` registers the platform driver with `core_initcall()`, making this provider available early enough for core platform devices. `gcc_msm8660_exit()` unregisters the platform driver for module unload paths.

## Control Flow
The platform driver matches `qcom,gcc-msm8660`. During probe, the common QCOM CC helper maps registers using `gcc_msm8660_regmap_config`, registers every entry in `gcc_msm8660_clks[]`, and registers the reset controller from `gcc_msm8660_resets[]`. There is no custom probe-time programming in this file; all behavior is expressed by static descriptors.

The static clock flow starts at PLL8, sourced from PXO and controlled through PLL mode/status registers. `pll8_vote` gates PLL8 through a vote register bit and is used as the PLL parent for most generated clocks. GSBI UART sources 1-12 share one UART frequency table with 16-bit M/N fields; matching branch clocks gate the UART outputs. GSBI QUP sources 1-12 share a QUP table with 8-bit M/N fields and similar branch gates. GP0-2 add a CXO-capable parent map. SDC1-5, TSIF, USB HS1, and USB FS1/FS2 each define RCG sources plus final branches. The tail of the file registers many simple branch gates for bus or peripheral H clocks, ADM clocks, PMIC clocks, modem AHB clocks, and RPM message RAM.

## State And Persistence
Driver-owned state is static table data only. Hardware state persists in the GCC MMIO block: PLL8 programming, vote bits, RCG NS/MD registers, branch enable bits, halt status bits, hardware clock-gating bits, and reset bits. No GDSCs are modeled in this file. Several branches use `BRANCH_HALT_VOTED` where the hardware gate is vote-controlled or shared with another entity. The provider has no suspend/resume save area; clock framework operations directly read and update registers through regmap.

## Dependencies And Integration Points
The driver depends on `dt-bindings/clock/qcom,gcc-msm8660.h` and `dt-bindings/reset/qcom,gcc-msm8660.h` for stable array indexes, device-tree compatible `qcom,gcc-msm8660`, external `pxo` and `cxo` clock names, and Qualcomm common clock helpers for legacy PLLs, legacy RCGs, branches, regmap, and resets. Consumers include serial, SPI/I2C GSBI QUP, SD card, USB, TSIF, PRNG, PMIC/SSBI, ADM DMA, EBI2, RPM, modem, and fabric-related platform drivers.

## Risks And Test Signals
The largest risk is repetitive-table drift: GSBI blocks use regular register spacing but different halt bits, so copy/paste mistakes can expose a clock that enables one block while polling another. Parent-name compatibility is also important because the old binding expects `pxo` and `cxo` firmware clock names with board-name fallbacks. Reset map risk is high because many entries share nearby registers with different bit positions; a bad reset entry can reset an unrelated fabric, modem, or peripheral block. Missing `CLK_SET_RATE_PARENT`, `CLK_SET_RATE_GATE`, or `CLK_SET_PARENT_GATE` flags could permit unsafe parent/rate changes while a legacy RCG is active.

Validation signals include successful early probe, no missing PXO/CXO parent warnings, UART console on a GSBI UART, working GSBI QUP I2C/SPI, SDC card detection and rate changes, USB FS/HS operation at 60 MHz transceiver rates, PRNG availability, PMIC/SSBI and RPM message RAM access, reset-controller use by USB/SDC/GSBI clients, and clk-summary output showing PLL8, PLL8 vote, source clocks, and H clocks with expected enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8660.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8909.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-msm8909.c -->
