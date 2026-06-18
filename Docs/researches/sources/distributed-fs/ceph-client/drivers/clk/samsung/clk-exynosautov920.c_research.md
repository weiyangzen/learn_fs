# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynosautov920.c

## Purpose
`clk-exynosautov920.c` is the Samsung common clock framework provider for the ExynosAuto v920 SoC. It describes the SoC clock-management units as static Samsung CCF descriptors, then registers those descriptors either very early through `CLK_OF_DECLARE()` or through a `core_initcall()` platform driver. The file covers the top-level CMU, three CPU cluster CMUs, PERIC0/PERIC1 serial-peripheral CMUs, MISC, HSI0/HSI1/HSI2, M2M, MFC, MFD, and G3D.

The top CMU is the parent source for most other domains. It exposes shared PLLs, the MMC PLL, fixed-factor post-dividers, and a large set of `dout_clkcmu_*` exported clocks for accelerator, audio, CPU, display, DSP/GPU/NPU, high-speed I/O, image/media, NoC, SDMA/SNW/SSP, and TAA users. Leaf CMUs then create user muxes and local dividers for their block-level consumers.

## Important APIs, Types, And Functions
The driver uses Samsung clock helper data types from `clk.h` and `clk-exynos-arm64.h`: `struct samsung_pll_clock`, `struct samsung_mux_clock`, `struct samsung_div_clock`, `struct samsung_fixed_factor_clock`, and `struct samsung_cmu_info`. Descriptors are built with the Samsung macros `PLL()`, `MUX()`, `DIV()`, `FFACTOR()`, and `PNAME()`. Public numeric IDs come from `dt-bindings/clock/samsung,exynosautov920.h`, and each domain defines a `CLKS_NR_*` value as the final clock ID plus one.

The active code paths are intentionally small. `exynosautov920_cmu_top_init()`, `exynosautov920_cmu_cpucl0_init()`, `exynosautov920_cmu_cpucl1_init()`, and `exynosautov920_cmu_cpucl2_init()` call `exynos_arm64_register_cmu(NULL, np, info)` from early OF declarations. `exynosautov920_cmu_probe()` retrieves a matched `struct samsung_cmu_info` with `of_device_get_match_data()` and calls `exynos_arm64_register_cmu(dev, dev->of_node, info)` for the platform-driver managed CMUs. `exynosautov920_cmu_init()` registers the platform driver at `core_initcall()` time.

The most important descriptors are `top_cmu_info`, `cpucl0_cmu_info`, `cpucl1_cmu_info`, `cpucl2_cmu_info`, `peric0_cmu_info`, `peric1_cmu_info`, `misc_cmu_info`, `hsi0_cmu_info`, `hsi1_cmu_info`, `hsi2_cmu_info`, `m2m_cmu_info`, `mfc_cmu_info`, `mfd_cmu_info`, and `g3d_cmu_info`. Their `clk_regs` arrays list the registers that the Samsung framework can save/restore or otherwise account for.

## Control Flow
At boot, the OF clock provider for `samsung,exynosautov920-cmu-top` registers first because downstream domains depend on its shared PLL-derived `dout_clkcmu_*` outputs. The CPU cluster providers also register early so CPU clock topology is available before later platform devices need CPU frequency or cluster clocks. Each early init path is a direct pass-through into `exynos_arm64_register_cmu()`.

Later, the platform driver named `exynosautov920-cmu` matches power-domain style CMUs: PERIC0, PERIC1, MISC, HSI0, HSI1, HSI2, M2M, MFC, MFD, and G3D. The probe function does not branch by compatible string itself; it relies on `.data` in `exynosautov920_cmu_of_match[]` to select the corresponding `samsung_cmu_info`.

After registration, runtime behavior is table-driven by the common clock framework. Clock consumers request rates or parent changes by ID or clock name. Generic Samsung clock operations program the MMIO mux select fields, divider fields, PLL controls, and fixed-factor relationships described by the arrays. This file contains no interrupt handler, no deferred work, and no custom rate-selection code beyond the CPU PLL rate table.

## State And Persistence
There is no filesystem persistence and no private dynamic state in this driver. State lives in SoC CMU registers and in the common clock framework structures allocated by the Samsung registration helpers. The `__initconst` tables are boot-time descriptor data and can be discarded after init.

The top CMU defines seven PLL outputs: shared0 through shared5 and MMC. Their post-dividers are represented as fixed-factor clocks such as `dout_shared*_div1` through `dout_shared*_div4`, plus `dout_tcxo_div2`. CPUCL0, CPUCL1, and CPUCL2 each define a local `pll_531x` CPU PLL using a common `cpu_pll_rates` table spanning 2.4 GHz down to 288 MHz for a 38.4 MHz oscillator. HSI2 defines an Ethernet PLL, and G3D defines a GPU PLL. PERIC, MISC, HSI0/1, M2M, MFC, and MFD mostly add local user muxes/dividers around clocks sourced from TOP.

Register restore coverage depends on each `*_clk_regs` array. Any omitted offset will not be tracked by the Samsung CMU helper for that domain, so these arrays are part of the suspend/resume state contract.

## Dependencies And Integration Points
The driver depends on Linux CCF and OF platform infrastructure plus the Samsung Exynos ARM64 clock registration helpers. Device tree must provide the compatible strings used by `CLK_OF_DECLARE()` and `exynosautov920_cmu_of_match[]`, and clock consumers must use IDs from `samsung,exynosautov920.h`.

Major integration points are CPU frequency/cluster clocking, high-speed storage and I/O, media and display engines, GPU, NoC fabrics, and peripheral serial controllers. PERIC0 exposes muxes/dividers for USI00 through USI08, USI I2C, and I3C; PERIC1 does the same for USI09 through USI17. HSI0 provides PCIe APB division. HSI1 selects MMC-card, NoC, and USB DRD clocks. HSI2 integrates Ethernet, UFS-related user clocks, and Ethernet PTP division. M2M, MFC, and MFD expose media block NoC or function clocks, while G3D publishes GPU NoC/switch sources.

## Risks
The primary risk is descriptor accuracy. Parent arrays must match hardware selector encodings and parent order, especially in the top CMU where many domains choose among eight shared-PLL divider options. A wrong parent list or selector width can silently route an entire domain to the wrong rate.

Clock ID bounds are also sensitive. Each `CLKS_NR_*` definition must remain one greater than the highest binding ID used by that CMU, or consumers can receive missing or misindexed clocks. Register-offset mistakes are high impact because most arrays are dense hardware tables with no runtime validation beyond probe success and later consumer behavior.

Early registration order is intentional. Moving TOP or CPUCL registration into the platform-driver-only path can leave dependent domains without parents during early boot. CPU PLL rate-table changes can break CPU frequency scaling, voltage assumptions, or boot firmware handoff. HSI2 and G3D local PLLs have no explicit rate table in this file, so their firmware/default programming and generic PLL handling need hardware validation if touched.

There are a few maintenance smells worth preserving as explicit review points: `PLL_LOCKTIME_PLL_SHARED4` and `PLL_LOCKTIME_PLL_SHARED5` both map to `0x0018`, and formatting is inconsistent in several later CMU sections. These may be intentional SoC definitions or copy/paste mistakes, but they should be checked against the hardware manual before changing.

## Test Signals
Build validation should include compiling this driver with the matching `samsung,exynosautov920.h` binding header and checking for duplicate or missing clock IDs. Boot validation should show successful registration for the early TOP and CPU cluster providers and successful platform probes for all matched CMUs, with no missing-parent warnings.

Runtime signals include a populated debugfs clock tree containing `fout_shared*_pll`, `fout_mmc_pll`, `dout_clkcmu_*`, `fout_cpucl*_pll`, PERIC USI/I2C/I3C clocks, HSI Ethernet/UFS/USB/MMC clocks, M2M/MFC/MFD clocks, and G3D clocks. Hardware-oriented tests should cover CPU frequency transitions, serial/I2C/SPI/I3C operation across PERIC0/PERIC1, MMC, USB DRD, UFS, Ethernet including PTP clocking, PCIe APB access, media encode/decode/display paths, GPU probe and clocks, and suspend/resume if CMU register save/restore is enabled.
