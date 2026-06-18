# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos2200.c

## Purpose

This file provides Samsung Common Clock Framework support for the Exynos2200 SoC. It describes the clock tree, reset-safe register save ranges, PLLs, muxes, dividers, fixed-rate inputs, and fixed-factor derived clocks for multiple Exynos2200 clock management units (CMUs). The driver is almost entirely declarative: hardware register offsets and clock descriptors are collected into `struct samsung_cmu_info` blocks, then registered either early through `CLK_OF_DECLARE()` or later through a platform driver.

The covered CMUs are:

- `CMU_TOP`, the global root clock provider and PLL/divider source for many downstream domains.
- `CMU_ALIVE`, low-power always-on clocks and internal RCO sources.
- `CMU_PERIS`, system peripheral clocks needed early for GIC/MCT-style infrastructure.
- `CMU_CMGP`, GPIO/I2C/SPI/USI peripheral clocks in the CMGP domain.
- `CMU_HSI0`, high-speed I/O clocks for USB/eUSB/DP-related signals.
- `CMU_PERIC0`, `CMU_PERIC1`, and `CMU_PERIC2`, peripheral serial/I2C/SPI/UART/USI clock domains.
- `CMU_UFS`, UFS/MMC-card/NOC user clocks.
- `CMU_VTS`, voice trigger system/DMIC/serial-lif clocks.

## Important APIs, Types, And Data

The primary APIs and types come from the Samsung clock provider layer and Linux CCF:

- `struct samsung_cmu_info` is the central per-CMU descriptor. Each instance provides arrays for PLL, mux, divider, fixed-rate, and fixed-factor clocks, the clock ID table size, register offsets that must be retained/restored, and an optional `clk_name` used by `exynos_arm64_register_cmu()`.
- `struct samsung_pll_clock`, `struct samsung_mux_clock`, `struct samsung_div_clock`, `struct samsung_fixed_factor_clock`, and `struct samsung_fixed_rate_clock` hold clock descriptions consumed by the common Samsung registration helpers.
- `PLL()`, `MUX()`, `DIV()`, `FFACTOR()`, and `FRATE()` macros instantiate those descriptors.
- `PNAME()` declares parent-name arrays used by mux clocks.
- `CLK_OF_DECLARE()` registers early DT init callbacks for root or boot-critical CMUs.
- `platform_driver_register()` registers the later-probed CMUs through an `of_device_id` match table.
- `exynos_arm64_register_cmu()` performs the actual CCF registration for an Exynos arm64 CMU.

Clock ID count macros such as `CLKS_NR_TOP`, `CLKS_NR_ALIVE`, `CLKS_NR_PERIS`, `CLKS_NR_CMGP`, `CLKS_NR_HSI0`, `CLKS_NR_PERIC0`, `CLKS_NR_PERIC1`, `CLKS_NR_PERIC2`, `CLKS_NR_UFS`, and `CLKS_NR_VTS` intentionally equal the last DT binding clock ID plus one. These must stay synchronized with `dt-bindings/clock/samsung,exynos2200-cmu.h`.

## Control Flow

The control flow is split between early OF init and platform-driver probe:

1. During early boot, the OF clock init path matches `samsung,exynos2200-cmu-top`, calls `exynos2200_cmu_top_init()`, and registers `top_cmu_info`. `CMU_TOP` is deliberately early because its PLLs and divided outputs feed other domains.
2. `samsung,exynos2200-cmu-alive` is also early via `exynos2200_cmu_alive_init()`, because ALIVE-generated NOC/RCO outputs feed low-power and downstream domains.
3. `samsung,exynos2200-cmu-peris` is early via `exynos2200_cmu_peris_init()`, because PERIS clocks support boot-critical system peripherals such as interrupt/timer blocks.
4. `exynos2200_cmu_init()` is called at `core_initcall()` time and registers a platform driver named `exynos2200-cmu`.
5. For non-early domains, `exynos2200_cmu_probe()` receives the matching `struct samsung_cmu_info` from `of_device_get_match_data()`, then calls `exynos_arm64_register_cmu(dev, dev->of_node, info)`.

There is no runtime algorithm beyond CCF registration. Rate calculation, mux selection, divider programming, enable/disable, and save/restore behavior are delegated to the Samsung clock framework using the static descriptors in this file.

## Clock Domain Details

`CMU_TOP` defines the root PLLs `fout_shared0_pll` through `fout_shared4_pll`, `fout_mmc_pll`, and `fout_shared_mif_pll` using `pll_4311`. It then exposes broad mux and divider outputs for CPU clusters, DSU, G3D, DSP, camera, display, multimedia, MIF, HSI, UFS, PERIC, PERIS, VTS, CP, and NOC buses. `top_fixed_factor_clks` derives fixed `/1`, `/2`, and `/4` shared PLL outputs plus `dout_tcxo_div3` and `dout_tcxo_div4`.

`CMU_ALIVE` selects between `oscclk`, ALIVE/TOP-provided outputs, and internal RCOs. It declares fixed-rate clocks `rco_i3c_pmic` and `rco_alive` at 49.152 MHz and `rco_400` at 393.216 MHz. ALIVE mux/divider outputs feed always-on NOC, CMGP, CHUB/VTS, GNSS, SDMA, UFD, PMU, SPMI, timer, CSIS, and DSP clock paths.

`CMU_PERIS` is compact and exposes GIC/NOC user muxes plus fixed-factor `dout_peris_otp` and `dout_peris_ddd_ctrl` clocks. It is intentionally early because system interrupt/timer and secure peripheral infrastructure can depend on it before normal platform drivers are probed.

`CMU_CMGP` describes CMGP I2C, SPI/I2C, SPI multi-slave control, and USI0-USI6 mux/divider clocks. Its parent path depends on ALIVE-generated `dout_alive_cmgp_noc` and `dout_alive_cmgp_peri` outputs.

`CMU_HSI0` exposes user muxes for HSI0 DPGTC, DPOSC, NOC, and USB32DRD, an RTC mux choosing `rtcclk` or `oscclk`, and a small divider for the eUSB clock. The register retention list includes many HSI0 gate registers, but this file only registers mux/divider clocks for the public clock IDs in this domain.

`CMU_PERIC0`, `CMU_PERIC1`, and `CMU_PERIC2` handle serial peripheral clocks. PERIC0 covers a smaller set around I2C and USI04. PERIC1 covers I2C, SPI multi-slave, Bluetooth UART, and USI07-USI10 including SPI/I2C subclocks. PERIC2 covers I2C, SPI multi-slave, debug UART, and USI00/01/02/03/05/06/11 including OIS-oriented USI paths. These domains select from `oscclk` and TOP-provided PERIC IP/NOC outputs, then divide for peripheral bus or serial clock rates.

`CMU_UFS` registers user muxes for UFS/MMC-card, UFS NOC, and embedded UFS clock inputs. It mostly acts as a consumer of TOP UFS outputs and registers no local divider array.

`CMU_VTS` registers VTS NOC/RCO/DMIC muxes, DMIC and serial-lif dividers, and fixed-rate placeholder DMIC pad inputs `dmic_clk0_in`, `dmic_clk1_in`, and `dmic_clk2_in` at 100 MHz. Its `clk_name` is `dmic`, which signals the default input name expected by the registration helper.

## State And Persistence Behavior

The file has no private heap state or persistent data of its own. All persistent hardware-facing state is MMIO clock controller state represented by register offsets in `*_clk_regs[]`. Those arrays tell the Samsung CMU framework which registers are important for clock configuration save/restore across suspend, resume, or power-domain transitions.

Runtime state is owned externally by:

- The CCF `struct clk_hw` objects allocated by the Samsung registration helpers.
- The OF clock provider records published for DT clock consumers.
- The actual hardware registers in each CMU MMIO block.

Because all descriptor arrays are marked `__initconst`, their storage is discarded after init once the Samsung clock core has copied or consumed the definitions it needs. Any mismatch between a retained register list and registered clocks is a hardware state loss risk during low-power transitions.

## Dependencies And Integration Points

The driver depends on:

- Linux CCF headers from `linux/clk-provider.h`.
- Device-tree matching from `linux/of.h`, `linux/mod_devicetable.h`, and `linux/platform_device.h`.
- Samsung common helpers in `drivers/clk/samsung/clk.h`.
- Exynos arm64 registration helpers in `drivers/clk/samsung/clk-exynos-arm64.h`.
- The DT binding IDs in `dt-bindings/clock/samsung,exynos2200-cmu.h`.

The outward integration points are DT compatible strings:

- `samsung,exynos2200-cmu-top`
- `samsung,exynos2200-cmu-alive`
- `samsung,exynos2200-cmu-peris`
- `samsung,exynos2200-cmu-cmgp`
- `samsung,exynos2200-cmu-hsi0`
- `samsung,exynos2200-cmu-peric0`
- `samsung,exynos2200-cmu-peric1`
- `samsung,exynos2200-cmu-peric2`
- `samsung,exynos2200-cmu-ufs`
- `samsung,exynos2200-cmu-vts`

Clock consumers integrate through DT clock IDs and names. Parent names such as `oscclk`, `rtcclk`, `dout_cmu_*`, `dout_alive_*`, `dout_shared*_div*`, `rco_*`, and DMIC pad inputs must match names registered by earlier CMUs or external fixed-clock providers.

## Risks And Maintenance Notes

- Clock ID count macros are fragile. If the DT binding gains an ID and the corresponding `CLKS_NR_*` macro is not updated, clock provider arrays can be too small.
- Parent-name strings are runtime contracts. A typo in a `PNAME()` entry can leave a clock orphaned even if the register offset is correct.
- Early registration order matters. TOP, ALIVE, and PERIS are dependencies for later domains; moving them behind platform-driver probe can break boot-time consumers.
- Register offsets are SoC-specific MMIO contracts. A wrong offset or bit width in `MUX()`/`DIV()` silently manipulates the wrong field and can hang a bus or peripheral.
- Several domains include extensive gate register offsets in `*_clk_regs[]` while only exposing mux/divider clocks. That can be intentional for retention, but it should be checked against the Samsung CMU save/restore model.
- `top_fixed_factor_clks` uses repeated IDs for the `dout_mmc_div*` entries that appear to reuse `CLK_DOUT_SHARED_MIF_DIV4`. If intentional, those outputs are name-only/internal; if accidental, it can collide in the clock ID table.
- Fixed-rate placeholder clocks such as the VTS DMIC inputs encode board assumptions. Real boards may need external fixed-clock providers or more accurate rates.
- `exynos2200_cmu_probe()` does not check `of_device_get_match_data()` for `NULL`. The match table should prevent this, but malformed binding or direct driver binding would pass a null info pointer to the registration helper.

## Test Signals

Useful validation signals include:

- Build coverage with `CONFIG_COMMON_CLK_SAMSUNG` and the Exynos2200 DT binding header enabled.
- Boot logs showing successful registration of each compatible CMU and no unresolved parent-clock warnings.
- `/sys/kernel/debug/clk/clk_summary` confirming that TOP, ALIVE, PERIS, CMGP, HSI0, PERIC0/1/2, UFS, and VTS clocks appear with expected parents and rates.
- Device probe success for serial, I2C/SPI/USI, UFS, USB/eUSB, timer, watchdog, GIC/MCT-adjacent, and DMIC/VTS consumers that request these clocks.
- Suspend/resume tests verifying that clocks in `*_clk_regs[]` retain or restore functional parent/divider settings.
- DT binding checks ensuring compatible strings and clock ID references match `samsung,exynos2200-cmu.h`.
