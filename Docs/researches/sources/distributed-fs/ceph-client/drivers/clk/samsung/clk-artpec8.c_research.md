# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-artpec8.c

## Purpose

`clk-artpec8.c` is the ARTPEC-8 SoC clock controller description for the Linux common clock framework using Samsung's shared clock registration helpers. It defines register offsets, parent name arrays, PLLs, muxes, dividers, gates, and `samsung_cmu_info` descriptors for ARTPEC-8 CMU domains, then binds those descriptors to device-tree compatible strings.

The covered domains are `CMU_CMU`, `CMU_BUS`, `CMU_CORE`, `CMU_CPUCL`, `CMU_FSYS`, `CMU_IMEM`, and `CMU_PERI`. `CMU_CMU` is the root-like shared clock domain with audio/shared PLLs and exported `dout_clkcmu_*` clocks. Domain CMUs then select those exported clocks through user muxes and expose peripheral-facing gates.

## Important APIs, types, and functions

- Samsung CCF arrays use `PLL()`, `FFACTOR()`, `FRATE()`, `MUX()`, `nMUX()`, `MUX_F()`, `DIV()`, `DIV_F()`, and `GATE()`.
- `struct samsung_cmu_info` instances (`cmu_cmu_info`, `cmu_bus_info`, `cmu_core_info`, `cmu_cpucl_info`, `cmu_fsys_info`, `cmu_imem_info`, `cmu_peri_info`) bundle each domain's clocks, clock ID count, and register list.
- `artpec8_pll_audio_rates` supplies the audio PLL rate table for `pll_1031x`; shared PLLs and CPUCL/FSYS PLLs are registered without file-local rate tables.
- `artpec8_clk_cmu_imem_init()` registers IMEM directly through `samsung_cmu_register_one()` and is wired by `CLK_OF_DECLARE()`.
- `artpec8_cmu_probe()` resolves OF match data and calls `exynos_arm64_register_cmu(dev, dev->of_node, info)`.
- `artpec8_cmu_init()` registers the platform driver at `core_initcall()`.

## Control flow and integration

Boot-time registration has two paths. IMEM is registered early for `"axis,artpec8-cmu-imem"` through `CLK_OF_DECLARE`, which avoids depending on the platform driver for early infrastructure clocks. The other CMUs bind through the `artpec8-cmu` platform driver; probe selects a static `samsung_cmu_info` from `artpec8_cmu_of_match` and delegates bus-clock enablement, CMU initialization, and clock provider registration to `exynos_arm64_register_cmu()`.

`CMU_CMU` registers `fout_pll_shared0`, `fout_pll_shared1`, and `fout_pll_audio`, divides shared PLL outputs, and creates exported clocks for bus, core, CPU cluster, FSYS, IMEM, MIF, PERI, GPU, video, and accelerator domains. `CMU_CPUCL` defines a CPU cluster PLL path, switch-user path, CPU/debug dividers, and critical gates for CPU, shortstop, and CoreSight debug clocks. `CMU_FSYS` covers PCIe, EQOS, QSPI, MMC, UART, NAND, I2C, PWM, USB, and XHB clocks. `CMU_PERI` covers DSIM, I2S, SPI, UART, I2C, and audio-out clocks, including a fixed 100 MHz `clk_peri_audio`.

## State and persistence behavior

The file owns no mutable runtime state beyond static `__initconst` clock descriptors. Register state is represented by each `*_clk_regs` list and then persists in hardware after registration. This file uses the simple `exynos_arm64_register_cmu()` path, not the PM-specific helper, so it does not install suspend/resume save-restore handling. Critical, ignore-unused, and rate-parent flags influence later common clock framework behavior.

## Dependencies

Dependencies include `dt-bindings/clock/axis,artpec8-clk.h`, Samsung's `clk.h` macros and helpers, `clk-exynos-arm64.h`, Linux CCF provider APIs, platform-device probing, and device-tree CMU nodes with correct `reg` and optional parent clock properties. Cross-domain parent names must match the registered names produced by other CMUs.

## Risks and edge cases

- `CMU_*_NR_CLK` values must track the binding header exactly.
- Parent names are string contracts; typos create orphaned clocks or broken rate propagation.
- IMEM early registration bypasses the platform-driver path and assumes registers are accessible early.
- Missing `CLK_IS_CRITICAL` flags can break boot or console/storage access after unused-clock cleanup; excessive use can hide missing consumers.
- Raw register offsets and divider widths compile even when wrong, so failures are usually hardware-only.
- Internal-only clocks use ID `0`; consumer-visible clocks must not accidentally use it.

## Test signals

Useful validation includes kernel build and binding checks, ARTPEC-8 boot without clock registration errors, `clk_summary` showing all CMU domains and expected parents, working UART/storage/network/peripheral clocks after unused-clock cleanup, and rate-change tests for clocks using `CLK_SET_RATE_PARENT`. Low-power testing should still verify clock state even though this file has no local PM path.
