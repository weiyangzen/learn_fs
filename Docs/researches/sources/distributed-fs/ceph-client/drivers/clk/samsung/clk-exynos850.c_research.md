# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos850.c

## Purpose

`clk-exynos850.c` is the Common Clock Framework driver data and registration glue for Samsung Exynos850 clock management units. It describes register offsets, PLLs, muxes, dividers, gates, fixed-rate inputs, and CPU clock rate/divider tables for the SoC, then registers each CMU through the Samsung ARM64 clock helper layer. The file covers CMU_TOP, APM, AUD, CMGP, CPUCL0, CPUCL1, G3D, HSI, IS, MFCMSCL, PERI, CORE, and DPU.

The implementation is mostly declarative. Runtime behavior is driven by arrays of `struct samsung_*_clock` descriptors and `struct samsung_cmu_info` blocks that are consumed by `exynos_arm64_register_cmu()`.

## Important APIs, Types, And Data

- `CLKS_NR_*` constants size each CMU clock provider by using the last dt-binding clock ID plus one. These must stay synchronized with `include/dt-bindings/clock/exynos850.h`.
- Register offset macros such as `PLL_CON0_PLL_SHARED0`, `CLK_CON_MUX_MUX_CLKCMU_*`, `CLK_CON_DIV_*`, and `CLK_CON_GAT_*` encode the CMU register maps.
- `top_clk_regs`, `apm_clk_regs`, and equivalent arrays list registers saved/restored or initialized by the Samsung CMU core.
- `struct samsung_pll_clock` arrays describe PLL blocks. TOP has shared0/shared1/MMC PLLs without rate tables, AUD has its PLL without a rate table, CPU clusters provide `cpu_pll_rates`, and G3D has a PLL without a rate table.
- `PNAME(...)` arrays describe parent clock name lists for muxes. These form the main dependency graph between TOP outputs and downstream CMU user muxes.
- `struct samsung_mux_clock`, `struct samsung_div_clock`, `struct samsung_gate_clock`, `struct samsung_fixed_rate_clock`, and `struct samsung_cpu_clock` arrays describe CCF clocks registered by the Samsung helpers.
- `struct samsung_cmu_info` instances are the integration contract for each CMU. Fields include descriptor arrays, register save lists, number of clock IDs, optional `.clk_name` parent dependency, optional `.cpu_clks`, and `.manual_plls`.
- `E850_CPU_DIV0()` and `exynos850_cluster_clk_d` define CPU child divider programming data for the CPU clock framework.
- `CPU_CLK()` entries create `cluster0_clk` and `cluster1_clk`, selecting the cluster PLL and switch-user muxes with Exynos850-specific CPU clock layouts.

## Control Flow

Early boot registration happens through `CLK_OF_DECLARE()`:

- `exynos850_cmu_top_init()` registers CMU_TOP early because other CMUs depend on its exported `dout_*` and `gout_*` roots.
- `exynos850_cmu_cpucl0_init()` and `exynos850_cmu_cpucl1_init()` register CPU cluster CMUs early so CPU frequency clocks exist as soon as possible.
- `exynos850_cmu_peri_init()` registers CMU_PERI early because the MCT timer depends on it.

The rest of the CMUs are registered by a platform driver:

- `exynos850_cmu_init()` is a `core_initcall()` that registers `exynos850_cmu_driver`.
- `exynos850_cmu_of_match` maps compatible strings to CMU info blocks for APM, AUD, CMGP, G3D, HSI, IS, MFCMSCL, CORE, and DPU.
- `exynos850_cmu_probe()` retrieves the matched `struct samsung_cmu_info` with `of_device_get_match_data()` and calls `exynos_arm64_register_cmu(dev, dev->of_node, info)`.

Within each CMU, the Samsung CCF helpers register fixed-rate clocks first as needed, then PLLs, muxes, dividers, gates, and CPU clocks based on the descriptor arrays. The clock topology is encoded by clock names, so parent names must exactly match clocks registered earlier or in the same CMU.

## CMU Coverage And Integration Points

- CMU_TOP defines the SoC-wide shared PLLs, MMC PLL, derived shared dividers, and top-level mux/div/gate outputs feeding APM, AUD, CORE, CPU clusters, DPU, G3D, HSI, IS, MFCMSCL, and PERI. Several IS and MFCMSCL top gates are marked `CLK_IS_CRITICAL` because downstream CMU register access depends on them.
- CMU_APM defines always-on and low-power clocks for RTC, PMU alive, I3C PMIC, SPEEDY, GPIO alive, mailbox, and CHUB/CMGP bus paths. It provides local fixed-rate RCO/DLL clocks and marks PMU alive critical.
- CMU_AUD defines an audio PLL, audio CPU/bus/audio-interface dividers, UAIF parent muxes, fixed external audio clock inputs, ABOX gates, codec MCLK, SYSMMU, GPIO, watchdog, and USB tick derived FM/SPDY clocks.
- CMU_CMGP defines a 49.152 MHz RCO source, ADC and two USI clocks, and gates for ADC, GPIO, SYSREG, and CMGP USI IP/PCLK paths. USI mux/div/gates use `CLK_SET_RATE_PARENT` where rate propagation is expected.
- CMU_CPUCL0 and CMU_CPUCL1 each define a cluster PLL, switch-user/debug-user muxes, read-only CPU/CMUREF/PCLK and embedded cluster dividers, cluster gates, and CPU clock descriptors. `.manual_plls = true` allows managed CPU PLL rate control using the provided PLL table.
- CMU_G3D defines GPU PLL/user switch muxing, a bus divider, and GPU/bus/sysreg/tzpc gates. Its PLL intentionally has no rate table, preventing normal `set_rate`.
- CMU_HSI defines user muxes for HSI bus, SD card, USB20 DRD, and RTC selection, plus gates for USB reference clocks, MMC card clocks, PPMU, GPIO, and SYSREG.
- CMU_IS defines image subsystem user muxes for bus, GDC, ITP, and VRA, a bus peripheral divider, and gates for CSIS, DMA, IPP, ITP, MCSC, VRA, PPMU, SYSMMU, and SYSREG.
- CMU_MFCMSCL defines user muxes for MFC, M2M, MCSC, and JPEG, a bus peripheral divider, and gates for codec/image processing, PPMU, SYSMMU, TZPC, and SYSREG.
- CMU_PERI defines peripheral bus/UART/HSI2C/SPI user muxes, HSI2C and SPI dividers, and gates for HSI2C, I2C, MCT, PWM, SPI, UART, watchdogs, TMU, GPIO, and SYSREG.
- CMU_CORE defines core bus/CCI/MMC/SSS user muxes, a bus peripheral divider, and gates for CCI, GIC, embedded MMC, DMA, security subsystem, GPIO, and SYSREG. CCI and GIC are critical.
- CMU_DPU defines display user mux/divider and gates for DECON, DMA, DPP, PPMU, SMMU, SYSREG, and CMU PCLK. The CMU PCLK is ignored-unused pending the display driver.

## State And Persistence Behavior

The driver does not maintain heap state or persistent storage itself. Persistent hardware state is in memory-mapped CMU registers. The `*_clk_regs` arrays tell the Samsung clock framework which registers are important for save/restore and initialization. CCF state such as enable counts, rates, and parents is owned by the common clock core and Samsung helper code after registration.

CPU cluster dividers are read-only in descriptor flags (`CLK_DIVIDER_READ_ONLY`) and often `CLK_GET_RATE_NOCACHE`, so runtime rate reporting reads hardware rather than trusting cached values. Critical and ignore-unused flags affect boot-time clock disable behavior: critical clocks cannot be disabled, while ignore-unused protects clocks that currently lack consumers.

## Dependencies

- Linux CCF headers and platform/of infrastructure: `<linux/clk-provider.h>`, `<linux/of.h>`, `<linux/platform_device.h>`, `<linux/mod_devicetable.h>`.
- Exynos850 dt-binding IDs from `<dt-bindings/clock/exynos850.h>`.
- Samsung clock helper internals from `clk.h`, CPU clock support from `clk-cpu.h`, and ARM64 CMU registration from `clk-exynos-arm64.h`.
- Device tree compatible strings for each CMU must match the DT nodes and must provide mapped register regions and parent clocks such as `oscclk`, `rtcclk`, and the named TOP outputs.
- Consumer drivers depend on these clock names/IDs through DT `clocks` references: CPUfreq, timer/MCT, UART/I2C/SPI/HSI2C, MMC, USB, audio/ABOX, GPU, display, camera/image, MFC/JPEG, DMA, SYSMMU, and security engines.

## Risks And Edge Cases

- `CLKS_NR_*` values are fragile: if dt-binding IDs change without updating these sizes, providers can reject valid IDs or allocate sparse arrays incorrectly.
- Clock parent names are string-coupled. A typo in names such as `dout_*`, `gout_*`, or `mout_*` silently breaks parent resolution and can produce wrong rates or deferred registration.
- Several PLLs intentionally omit rate tables because manual PLL control is not enabled by default. Adding rate changes for those clocks without hardware sequencing support can fail or destabilize the SoC.
- Early registration order is important. TOP must be present before dependent CMUs, CPU clocks must exist early for CPUfreq/boot CPU setup, and PERI must be available for MCT.
- `CLK_IGNORE_UNUSED` appears on GPIO, CMU PCLK, ABOX, and XIU-like clocks where consumers are incomplete. Removing these flags before consumers are ready can hang boot or break register access.
- `CLK_IS_CRITICAL` protects CCI, GIC, PMU alive, IS/MFCMSCL access paths, and other essential buses. Incorrectly relaxing these can cause hard hangs; overusing them can hide missing consumers and increase power draw.
- CPU clock rate tables and `E850_CPU_DIV0()` values must match silicon OPP expectations. Wrong dividers can break debug/peripheral clocks while CPU frequency scaling appears superficially correct.
- Some gate parent choices use functional clocks instead of bus clocks. Changes need hardware manual validation because rate propagation and enable sequencing can affect peripheral programming.

## Test Signals

- Build coverage: compile with `CONFIG_COMMON_CLK_SAMSUNG`, `CONFIG_ARCH_EXYNOS`, and dt-binding header consistency checks.
- Boot log signals: CMU registration succeeds for TOP, CPUCL0, CPUCL1, PERI, and platform CMUs; no missing parent warnings from CCF; no failed `of_clk_add_provider` or duplicate clock names.
- Device-tree validation: each compatible in `exynos850_cmu_of_match` and each `CLK_OF_DECLARE` string appears in Exynos850 DT nodes with correct register ranges.
- Runtime CCF inspection: `/sys/kernel/debug/clk/clk_summary` shows expected parentage, rates, critical flags, and enabled consumers.
- Functional smoke tests: MCT timer boot, CPUfreq transitions on both clusters, UART console, I2C/SPI/HSI2C, eMMC/SD, USB, audio, GPU, display, camera/image, MFC/JPEG, and suspend/resume.
- Negative test indicators: boot hangs after unused-clock disable, missing parent messages, impossible CPU rates, peripheral timeouts, or inability to access downstream CMU registers.
