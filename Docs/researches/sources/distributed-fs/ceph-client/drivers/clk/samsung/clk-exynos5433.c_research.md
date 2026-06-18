# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos5433.c

## Purpose

`clk-exynos5433.c` describes and registers the Samsung Exynos5433 clock tree for Linux's Common Clock Framework. It is a SoC clock-controller driver, not a Ceph-specific component despite its repository path. The file maps Exynos5433 CMU register layouts into Samsung clock-provider descriptors for PLLs, muxes, dividers, gates, fixed-rate clocks, fixed-factor clocks, and CPU clocks.

The driver covers many independent clock management units: early boot CMUs such as TOP, CPIF, MIF, PERIC, PERIS, BUS0/1/2, APOLLO, and ATLAS, plus runtime-PM managed CMUs such as AUD, CAM0, CAM1, DISP, FSYS, G2D, G3D, GSCL, MFC, HEVC, ISP, MSCL, and IMEM. Each CMU section defines register offsets, save/restore register lists, parent-name arrays, clock descriptors, and one `struct samsung_cmu_info` used by the shared Samsung clock framework.

## Important APIs, Types, and Data

- `struct samsung_cmu_info` is the central descriptor passed to Samsung clock registration code. Each instance points at arrays of `samsung_pll_clock`, `samsung_mux_clock`, `samsung_div_clock`, `samsung_gate_clock`, `samsung_fixed_rate_clock`, `samsung_fixed_factor_clock`, optional `samsung_cpu_clock`, clock ID capacity, register save lists, suspend override lists, and optional parent/runtime clock name.
- `CLK_OF_DECLARE()` registers selected CMUs during early device-tree clock-provider initialization. This file uses it for TOP, CPIF, MIF, PERIC, PERIS, BUS0, BUS1, BUS2, APOLLO, and ATLAS.
- `platform_driver_register()` plus `core_initcall()` registers `exynos5433_cmu_driver` for CMUs that need normal platform probing and PM integration.
- `exynos_arm64_register_cmu_pm(pdev, false)` is the platform driver's probe implementation and delegates mapping, clock registration, and PM state setup to shared Exynos ARM64 clock code.
- Runtime PM callbacks use `exynos_arm64_cmu_suspend()` and `exynos_arm64_cmu_resume()`. System sleep noirq callbacks force runtime suspend/resume via `pm_runtime_force_suspend()` and `pm_runtime_force_resume()`.
- Clock descriptor macros from the Samsung clock framework are the main implementation language: `PLL()`, `MUX()`, `MUX_F()`, `DIV()`, `DIV_F()`, `GATE()`, `FFACTOR()`, `FRATE()`, `CPU_CLK()`, and `PNAME()`.
- `dt-bindings/clock/exynos5433.h` supplies the numeric clock IDs. Local `CLKS_NR_*` constants are intentionally defined as the last valid ID plus one for each CMU.

## Control Flow

Early boot CMUs are initialized when matching device-tree nodes are scanned. Each `exynos5433_cmu_*_init(struct device_node *np)` function is tiny and calls `samsung_cmu_register_one(np, &*_cmu_info)`. This path is used for always-needed roots and interconnect clocks, including TOP PLL outputs, memory/interface clocks, peripheral buses, and CPU cluster clocks.

Runtime-managed CMUs are matched by `exynos5433_cmu_of_match`. When a compatible node such as `samsung,exynos5433-cmu-fsys` or `samsung,exynos5433-cmu-disp` probes, the generic `exynos5433_cmu_probe()` calls `exynos_arm64_register_cmu_pm()`. Those CMU descriptors include `.clk_name` when the CMU requires an upstream parent clock to be enabled while accessing its registers or serving child clocks.

Clock registration is declarative. For a CMU, the shared framework consumes the `samsung_cmu_info` arrays in order: fixed/fixed-factor roots, PLLs, muxes, dividers, gates, and CPU clocks where present. The resulting `clk_hw` providers become available to consumers through device tree clock phandles using the IDs from `exynos5433.h`.

## CMU Coverage

- TOP defines ISP/AUD PLLs, top-level parent selection, bus/media/peripheral dividers, fixed input clocks for audio/SPI, and high-level gates for camera, display, FSYS, PERIC, GSCL, G2D, MFC, HEVC, ISP, MSCL, G3D, IMEM, PERIS, and bus domains.
- CPIF defines the MPHY PLL and UFS MPHY-related clocks.
- MIF defines MEM0/MEM1/BUS/MFC PLLs, DDR and memory-interface clocks, display source clocks, CPIF/bus exports, and many DREX/CCI/secure peripheral gates.
- PERIC and PERIS cover serial, I2C, SPI, audio peripheral, GPIO, PMU, sysreg, timer, thermal, watchdog, secure key, chip ID, RTC, eFuse, and OTP clocks.
- FSYS handles storage and high-speed IO clocks: MMC, UFS, PCIe, USB host/device, DMA, USB/USF PHY fixed-rate inputs, and PHY muxes.
- G2D, GSCL, MSCL, MFC, HEVC, ISP, CAM0, and CAM1 describe media/camera/image-processing local clock domains, including SMMU and BTS support clocks.
- DISP covers display PLL, MIPI/HDMI PHY inputs, DECON/DSIM/HDMI/display gates, and fixed factors for RGB VCLK outputs.
- AUD describes the audio subsystem's local mux/divider/gate tree and fixed external audio inputs.
- APOLLO and ATLAS define CPU cluster PLLs, muxes, read-only/debug dividers, gates, and `samsung_cpu_clock` rate tables for cluster frequency switching.
- BUS0/1/2 and IMEM are smaller bus/security domains with common divider/gate patterns.

## State and Persistence Behavior

The driver itself owns no heap-resident long-lived state beyond what the shared clock framework allocates during registration. Its persistent state is hardware state: clock-controller registers, PLL programming, mux selections, divider values, and gate bits.

Register preservation is declared per CMU through `*_clk_regs` arrays. The shared Samsung CMU code uses these offsets to save and restore CMU register values around suspend/resume or runtime power transitions. Some CMUs also provide `*_suspend_regs` arrays with explicit values to program for suspend. Examples include forcing critical ACLK or UART clocks on, keeping ISP/AUD/MPHY/DISP PLLs enabled during suspend, and selecting safe mux parents before power transitions.

Flags in descriptors encode important persistence policy. `CLK_IS_CRITICAL` prevents framework cleanup from disabling clocks needed for the SoC to remain operational. `CLK_IGNORE_UNUSED` is used extensively for clocks that may be required by firmware, secure world, boot-critical hardware, or blocks not fully modeled by Linux consumers. `CLK_SET_RATE_PARENT`, `CLK_RECALC_NEW_RATES`, `CLK_GET_RATE_NOCACHE`, and `CLK_DIVIDER_READ_ONLY` define how rate changes propagate and how CPU/debug dividers are observed.

## Dependencies and Integration Points

The source depends on Linux CCF headers, platform device matching, runtime PM, and Samsung-specific clock helpers from `clk.h`, `clk-cpu.h`, `clk-exynos-arm64.h`, and `clk-pll.h`. It integrates with device tree through compatible strings such as `samsung,exynos5433-cmu-top`, `samsung,exynos5433-cmu-mif`, `samsung,exynos5433-cmu-aud`, and others in `exynos5433_cmu_of_match`.

Downstream consumers are normal Linux device drivers that request clocks by phandle and ID. Examples include serial/I2C/SPI controllers, MMC/UFS/USB/PCIe, display, audio, camera, GPU, video codec, scaler, SMMU, BTS, PMU/sysreg, and CPU-frequency paths. Parent clock names are string-linked across CMUs, so registration order and stable naming matter: TOP/MIF/CPIF roots feed many runtime-managed leaf domains.

The CPU clock integration is notable. APOLLO and ATLAS use `CPU_CLK()` with Exynos5433-specific divider layout and rate tables, allowing cpufreq or CPU clock users to switch PLL-backed cluster rates through the Samsung CPU clock helper rather than through ordinary mux/divider calls alone.

## Risks and Maintenance Notes

- The file is heavily table-driven, so small ID, parent-name, bit-position, or register-offset mistakes can silently miswire clocks and break unrelated devices.
- Several descriptors intentionally keep clocks enabled with `CLK_IGNORE_UNUSED` or `CLK_IS_CRITICAL`; removing these flags can cause suspend hangs, boot failures, inaccessible secure-world resources, or devices losing clocks after late init cleanup.
- Cross-CMU parent names are fragile. Typos in parent strings create orphaned clocks or fallback behavior that may only appear at runtime when a consumer enables or changes rate.
- Suspend register override values are hardware-specific constants. Changing them requires board-level suspend/resume validation because they force PLLs, muxes, and gate states during low-power entry.
- Some entries appear suspicious or typo-prone, such as duplicated gate bit positions in MIF/MFC/HEVC/CAM1 areas and misspelled clock names like `mout_aclk-cam0_400_user`, `aclk_bts_mdam1`, and `sclk_pixelasycm_*`. These may preserve ABI-visible names or mirror upstream quirks, so they should not be "cleaned up" without checking consumers and binding compatibility.
- The driver mixes early `CLK_OF_DECLARE` registration and platform-driver registration. Moving a CMU between those paths changes boot ordering and PM behavior.

## Test Signals

- Build signal: the file should compile with the ARM64 Samsung clock framework and the Exynos5433 clock binding header. Compiler errors usually indicate broken descriptor initializers, missing IDs, or macro argument mistakes.
- Device-tree signal: all compatible strings for Exynos5433 CMU nodes should bind either through `CLK_OF_DECLARE` or `exynos5433_cmu_of_match`; missing providers show up as deferred probes or `clk_get()` failures in dependent drivers.
- Runtime signal: `/sys/kernel/debug/clk/clk_summary` should show expected parent chains, enabled critical roots, and sane rates for PLL, bus, storage, display, camera, audio, and CPU clocks.
- Functional signal: boot console UART, I2C/SPI peripherals, MMC/UFS storage, USB/PCIe, display, audio, camera/media, GPU, and codec drivers should probe without clock errors.
- Power-management signal: runtime suspend/resume of platform-managed CMUs should restore clock registers; system suspend/resume should not hang in mux-status polling or lose UART/PLL state.
- Rate-change signal: CPU cluster rate transitions for APOLLO and ATLAS and set-rate operations for MMC/SPI/audio/display paths should propagate through the intended mux/divider/PLL parents.
