# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos3250.c

## Purpose

This file implements Samsung Common Clock Framework support for the Exynos3250 SoC. It registers the main CMU, the DMC CMU, and the ISP CMU using Samsung clock provider descriptors. Compared with the Exynos2200 arm64 driver, this older Exynos3 driver includes explicit PLL rate tables, CPU clock rate-divider tables, and a small hardware power-control routine that programs core clock-down behavior during idle.

The file covers:

- Main CMU clocks for left/right bus, top, CPU, camera, MFC, G3D, LCD, ISP top, FSYS, PERIL, and PERIR.
- DMC CMU clocks for memory/DDR-related PLLs, muxes, and dividers.
- ISP CMU dividers and gates registered through a platform driver after the main CMU provides parent clocks.

## Important APIs, Types, And Data

Important Samsung and CCF APIs include:

- `struct samsung_cmu_info`, used for each CMU descriptor.
- `struct samsung_pll_rate_table`, used to define supported PLL output rates for `pll_35xx` and `pll_36xx`.
- `struct samsung_pll_clock`, `samsung_mux_clock`, `samsung_div_clock`, `samsung_gate_clock`, and `samsung_fixed_factor_clock` descriptor arrays.
- `struct samsung_cpu_clock` and `struct exynos_cpuclk_cfg_data`, used to define the `armclk` CPU clock and divider programming for CPU frequency changes.
- `samsung_cmu_register_one()`, the main registration helper for a CMU described by `samsung_cmu_info`.
- `CLK_OF_DECLARE()` for early main and DMC CMU registration.
- `platform_driver_probe()` for one-time ISP CMU registration.

The key clock count macros are `CLKS_NR_MAIN`, `CLKS_NR_DMC`, and `CLKS_NR_ISP`, each set to the last binding ID plus one. These depend on `dt-bindings/clock/exynos3250.h`.

Register-offset macros define MMIO fields for source muxes, divider registers, gates, PLL controls, and CPU power controls such as `PWR_CTRL1` and `PWR_CTRL2`.

## Control Flow

Main CMU registration happens early:

1. OF clock init matches `samsung,exynos3250-cmu`.
2. `exynos3250_cmu_init()` calls `samsung_cmu_register_one(np, &cmu_info)`.
3. If registration returns a provider context, `exynos3_core_down_clock(ctx->reg_base)` writes idle clock-down policy into `PWR_CTRL1` and disables the clock-up feature by writing zero to `PWR_CTRL2`.

DMC registration also happens early:

1. OF clock init matches `samsung,exynos3250-cmu-dmc`.
2. `exynos3250_cmu_dmc_init()` calls `samsung_cmu_register_one(np, &dmc_cmu_info)`.

ISP registration is later and platform-driver based:

1. `exynos3250_cmu_platform_init()` runs as a `subsys_initcall()`.
2. It invokes `platform_driver_probe()` with `exynos3250_cmu_isp_driver` and `exynos3250_cmu_isp_probe()`.
3. The probe obtains `pdev->dev.of_node` and registers `isp_cmu_info`.

After registration, CCF and Samsung helper code handle parent lookup, rate changes, divider/mux programming, and gate enable/disable.

## Clock Domain Details

The main CMU defines parent muxes around `fin_pll`, APLL/MPLL/VPLL/UPLL outputs, MPLL user paths, EPLL/VPLL groups, camera/LCD/FSYS/PERIL source groups, and CPU parent selectors. Fixed-factor clocks derive `sclk_mpll_1600`, `sclk_mpll_mif`, `sclk_bpll`, camera/LCD block helper clocks, and a hardcoded `fin_pll` from `xusbxti`.

Main CMU divider clocks produce bus and functional clock rates for GPL/GDL/GPR/GDR, ACLK 400/266/200/160/100, camera, MFC, G3D, LCD/MIPI/FIMD, ISP top serial clocks, TSADC, MMC, UART, SPI, PCM/I2S, and CPU dividers. Some dividers use `CLK_SET_RATE_PARENT` through `_F` variants so consumer rate requests can propagate up the parent chain.

Main CMU gates cover left/right bus helper blocks, PERIR security/system blocks, camera, MFC, G3D, LCD, ISP top, FSYS, and PERIL devices. Many infrastructure gates use `CLK_IGNORE_UNUSED` to prevent the common clock cleanup path from disabling clocks that are needed implicitly by always-on or boot-critical hardware.

PLL rate tables describe supported output rates:

- `exynos3250_pll_rates` for APLL/MPLL/BPLL/UPLL-style `pll_35xx` instances from 100 MHz to 1.2 GHz.
- `exynos3250_epll_rates` for audio-oriented EPLL rates including common 49.152/45.1584/73.728 MHz families.
- `exynos3250_vpll_rates` for video/display-oriented VPLL rates including 74.25/148.5 MHz families and fractional variants.

The CPU clock descriptor registers `armclk` with `CLK_MOUT_APLL` as primary parent, `CLK_MOUT_MPLL_USER_C` as alternate parent, `CLK_CPU_HAS_DIV1`, register base offset `0x14000`, layout `CPUCLK_LAYOUT_E4210`, and the `e3250_armclk_d` divider table for 100 MHz through 1 GHz.

The DMC CMU registers BPLL and EPLL, DMC/D PHY muxes, and DMC dividers. It depends on `fin_pll` and the main-CMU-derived `sclk_mpll_mif` path.

The ISP CMU only registers local dividers and gates. Its dividers derive from main-CMU parents `mout_aclk_266_sub` and `mout_aclk_400_mcuisp_sub`; its gates cover ISP UART/WDT/PWM/I2C/MPWM/MCUCTL/PPMU/QE/SMMU/CSIS/LITE/FD/DRC/ISP blocks plus scaler/SPI and `sclk_mpwm_isp`.

## State And Persistence Behavior

Persistent hardware state is MMIO state in the CMU registers listed by `exynos3250_cmu_clk_regs[]` and `exynos3250_cmu_dmc_clk_regs[]`, plus the ISP gate/divider registers registered in `isp_cmu_info`. The Samsung clock framework uses those lists to retain/restore clock controller state where supported.

The file has one direct state mutation outside generic CCF registration: `exynos3_core_down_clock()` writes:

- `PWR_CTRL1` with core-down ratio settings, divider-down enables, and WFI/WFE usage bits for cores 0 and 1.
- `PWR_CTRL2` with zero to disable bootloader-enabled clock-up behavior.

There is no private dynamic state. Registration allocates CCF state in the Samsung provider context and publishes DT clock providers. All descriptor arrays are `__initconst` and are freed after init.

## Dependencies And Integration Points

The file depends on:

- Linux CCF and platform/OF headers.
- Raw MMIO access from `linux/io.h` for idle power-control register writes.
- Samsung clock helpers in `clk.h`, CPU clock support in `clk-cpu.h`, and PLL support in `clk-pll.h`.
- DT binding IDs in `dt-bindings/clock/exynos3250.h`.

Device-tree compatible strings are:

- `samsung,exynos3250-cmu`
- `samsung,exynos3250-cmu-dmc`
- `samsung,exynos3250-cmu-isp`

Clock consumers integrate by referencing binding IDs and the names registered by these descriptors, including bus clocks, serial clocks, display/media clocks, MMC/USB/FSYS clocks, CPU `armclk`, DMC clocks, and ISP local clocks.

## Risks And Maintenance Notes

- The file hardcodes `fin_pll` as a fixed-factor alias of `xusbxti` with a comment noting this is a hack until detection is implemented. Boards using a different oscillator source can report or program incorrect rates.
- Clock ID count macros must remain synchronized with `exynos3250.h`; otherwise CCF provider arrays can be undersized.
- Parent-name strings are cross-table contracts. ISP and DMC depend on clocks registered by the main CMU, so registration order and naming must remain stable.
- `exynos3_core_down_clock()` performs raw writes based on Exynos3/Exynos4x12-style power control semantics. Wrong reuse on a variant with different `PWR_CTRL` layout would affect CPU idle behavior.
- The ISP gate table labels a `GATE_IP_ISP1` section but many entries use `GATE_IP_ISP0` as the register argument. This may be intentional if the manual mapping aliases those bits, but it is a high-value audit target because wrong gate registers can break scaler/SPI/ISP subdevices.
- Extensive `CLK_IGNORE_UNUSED` use protects implicit dependencies but can hide missing consumer references and increase idle power.
- PLL rate tables are constrained to 24 MHz input (`24 * MHZ`). Other oscillator assumptions require corresponding table updates.
- `exynos3250_cmu_isp_probe()` does not validate `pdev->dev.of_node`; the platform match path should provide it, but defensive checks would improve robustness.

## Test Signals

Useful validation signals include:

- Kernel build coverage with `CONFIG_COMMON_CLK_SAMSUNG`, `CONFIG_ARCH_EXYNOS`, and `dt-bindings/clock/exynos3250.h`.
- Boot logs showing registration of main, DMC, and ISP CMUs without unresolved parent messages.
- `/sys/kernel/debug/clk/clk_summary` confirming expected parentage and rates for `armclk`, APLL/MPLL/VPLL/UPLL, BPLL/EPLL, DMC clocks, MMC/UART/SPI/I2S/PCM, display/media, and ISP clocks.
- CPU frequency changes through cpufreq, verifying `armclk` parent switching and divider values follow `e3250_armclk_d`.
- Idle/resume tests confirming `PWR_CTRL1`/`PWR_CTRL2` programming does not destabilize WFI/WFE entry and that retained CMU registers restore functional clocks.
- Peripheral smoke tests for UART, I2C, SPI, MMC, USB, display, camera/media, DMC, and ISP blocks.
- DT binding validation for all three compatible strings and for consumers using the exported clock IDs.
