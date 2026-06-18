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
