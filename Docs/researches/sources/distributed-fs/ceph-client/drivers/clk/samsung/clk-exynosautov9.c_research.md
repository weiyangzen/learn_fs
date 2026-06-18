# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynosautov9.c

## Purpose
`clk-exynosautov9.c` is the Samsung common clock framework provider for the ExynosAuto V9 SoC. It describes the SoC's CMU register blocks as CCF clocks using IDs from `dt-bindings/clock/samsung,exynosautov9.h`. The file covers `CMU_TOP` plus platform-probed `CMU_BUSMC`, `CMU_CORE`, `CMU_DPUM`, `CMU_FSYS0`, `CMU_FSYS1`, `CMU_FSYS2`, `CMU_PERIC0`, `CMU_PERIC1`, and `CMU_PERIS`.

The top CMU provides shared PLLs and derived top-level clocks for automotive SoC domains such as ACC, APM, audio, bus fabric, CPU clusters, DisplayPort/display, FSYS storage and PCIe/USB/UFS, G2D/G3D, ISP, MFC, memory interface, NPU, PERIC, and PERIS. The secondary CMUs publish local muxes, dividers, and gates for DMA, coherency, display, PCIe, MMC, USB, UFS, USI/I2C serial ports, watchdogs, and sysreg access.

## Important APIs, Types, And Functions
The file uses the Samsung clock descriptor types `struct samsung_pll_clock`, `struct samsung_mux_clock`, `struct samsung_div_clock`, `struct samsung_fixed_factor_clock`, `struct samsung_gate_clock`, and `struct samsung_cmu_info`. Macros `PLL()`, `PNAME()`, `MUX()`, `DIV()`, `FFACTOR()`, and `GATE()` encode the register-level topology. Registration is performed by `exynos_arm64_register_cmu()`.

`top_pll_clks[]` defines five shared top PLLs with the `pll_0822x` type. `top_mux_clks[]`, `top_div_clks[]`, `top_fixed_factor_clks[]`, and `top_gate_clks[]` build the main tree and include a fixed 1:4 derivative for FSYS0 PCIe. `fsys1_pll_clks[]` adds an MMC PLL using `pll_0831x` inside the FSYS1 CMU. `busmc_cmu_info`, `core_cmu_info`, `dpum_cmu_info`, `fsys0_cmu_info`, `fsys1_cmu_info`, `fsys2_cmu_info`, `peric0_cmu_info`, `peric1_cmu_info`, and `peris_cmu_info` describe local CMU islands.

`exynosautov9_cmu_top_init()` registers `CMU_TOP` early with `CLK_OF_DECLARE()`. `exynosautov9_cmu_probe()` handles all non-top CMUs by looking up `of_device_get_match_data()` and passing the selected descriptor to `exynos_arm64_register_cmu()`. `exynosautov9_cmu_init()` registers the platform driver from `core_initcall()`.

## Control Flow
`CMU_TOP` is available early through compatible `samsung,exynosautov9-cmu-top`, which is necessary because every local CMU depends on top-level parent clocks such as `dout_clkcmu_*` outputs. The platform driver then binds to each local CMU node listed in `exynosautov9_cmu_of_match[]`. Probe has no branch-specific imperative programming; it only selects the descriptor and lets the Samsung CMU framework create clock providers and register the clocks.

Runtime control flow is table-driven. Consumers request clocks by phandle ID; CCF resolves the clock object registered from these tables. Mux clocks select oscillator, PLL, or top-derived parents. Divider clocks program local divisors for bus, peripheral, MMC, or USI rates. Gate clocks enable or disable IP clock ports through bit 21 of gate registers. PLL handling is delegated to Samsung PLL helpers.

The top-level clock tree fans out broadly. For example, FSYS0 PCIe clocks derive from top PCIe parents and are gated locally per PCIe lane/function; FSYS1 owns MMC and USB roots and includes a local MMC PLL; FSYS2 provides UFS embedded clocks; PERIC0/PERIC1 each expose a regular pattern of USI IPCLK and PCLK gates.

## State And Persistence
There is no persistent state outside hardware registers and in-kernel CCF objects. `*_clk_regs[]` arrays list registers known to the Samsung CMU framework for each block. PLL selections, mux choices, divisors, and gates reflect bootloader state at registration time and later runtime changes made by clock consumers.

Clock lifetime policy is encoded through descriptor flags. `CMU_TOP` keeps APM, CPU cluster switch/cluster clocks, MIF, and PERIS bus clocks from unused-clock disable with `CLK_IGNORE_UNUSED`; BUSC and BUSMC bus gates are `CLK_IS_CRITICAL`; CORE CCI and CMU PCLK gates are `CLK_IS_CRITICAL`; several local PCLKs such as FSYS0/FSYS1 and PERIS sysreg are `CLK_IGNORE_UNUSED`. FSYS1's MMC SDCLK gate uses `CLK_SET_RATE_PARENT`, so rate changes may propagate toward the MMC parent path.

## Dependencies And Integration Points
The file depends on Linux CCF, OF, and platform-device APIs, Samsung ARM64 clock helpers in `clk.h` and `clk-exynos-arm64.h`, and ExynosAuto V9 clock IDs in `dt-bindings/clock/samsung,exynosautov9.h`. Unlike the Exynos990 file, it does not include `clk-pll.h` directly, relying on the shared Samsung clock headers it includes.

Integration points include DMA in BUSMC, CCI and core bus clocks, display/decon/DMA/DPP/SYSMMU clocks in DPUM, multiple PCIe Gen3 lane configurations in FSYS0, MMC and USB DRD clocks in FSYS1, UFS embedded clocks in FSYS2, USI/I2C serial controllers in PERIC0 and PERIC1, watchdog/sysreg clocks in PERIS, and top-level clocks consumed by CPU, bus, graphics, media, NPU, audio, and storage/networking domains. The device tree must expose separate compatible nodes for every local CMU block and must use the matching binding IDs.

## Risks
The file's risk is concentrated in descriptor fidelity and DTS synchronization. A `CLKS_NR_*` value must remain one greater than the highest binding ID for that CMU. Parent names such as `dout_clkcmu_fsys*_bus`, `dout_clkcmu_peric*_ip`, and `dout_cmu_boost` must correspond to actual registered clocks. If a local CMU is probed before its top parent is registered or if a parent name differs from the top descriptor, consumers may see orphaned clocks or rate calculation failures.

Several register definitions deserve extra review against the SoC manual because reused offsets are visible in the source. `CLK_CON_DIV_PLL_SHARED2_DIV4` and `CLK_CON_DIV_PLL_SHARED4_DIV2` share `0x18d4`; `CLK_CON_GAT_GATE_CLKCMU_CPUCL1_SWITCH` and `CLK_CON_GAT_GATE_CLKCMU_DPUM_BUS` both use `0x2060`; and the top MIF mux macro is defined twice with the same value. These may be harmless copy artifacts or genuine shared/aliased registers, but they are high-value checks before changing the file.

FSYS0 has a large PCIe descriptor matrix with separate refclk, DBI, master, slave, pipe, Gen3A, and Gen3B clocks for multiple lane groupings. A single parent or gate offset mistake can break link training on only one lane mode. FSYS1 combines a local MMC PLL, a top-level MMC card parent, a divider, and `CLK_SET_RATE_PARENT`; incorrect modeling can affect eMMC/SD timing. PERIC0/PERIC1 use highly regular USI/IPCLK/PCLK patterns, which are easy to copy incorrectly.

## Test Signals
Basic validation is a boot with successful registration for `samsung,exynosautov9-cmu-top` and all platform CMUs in `exynosautov9_cmu_of_match[]`: busmc, core, dpum, fsys0, fsys1, fsys2, peric0, peric1, and peris. `clk_summary` should show the five shared PLLs, top mux/div/gate clocks, FSYS1 MMC PLL, local bus-user muxes, local dividers, and all expected PCIe/MMC/USB/UFS/USI/PERIS gates without unexpected orphan parents.

Hardware validation should cover DMA through BUSMC, CCI/core fabric stability, display pipeline operation through DPUM and SYSMMU clocks, PCIe Gen3 link training for the populated lane groupings, MMC card/eMMC rate changes and data transfer, USB20/USB30 DRD enumeration, UFS embedded link-up on both instances, serial traffic through all populated PERIC0/PERIC1 USI channels, watchdog operation through PERIS, and suspend/resume or unused-clock cleanup with critical BUSC/BUSMC/CORE clocks still enabled. Descriptor-specific tests should compare clock rates and parent selections against expected TRM values for top shared PLL dividers, FSYS1 MMC, FSYS0 PCIe, and PERIC serial clocks.
