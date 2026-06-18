# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rv1126.c

## Purpose

`clk-rv1126.c` is the Rockchip clock driver for RV1126. It registers both the main CRU and the PMUCRU using a platform-driver probe that dispatches to compatible-specific init functions. The driver describes PLLs, CPU clocking, PMU clocks, main-domain branches, critical-clock protection, soft resets, restart handling, MMC phase clocks, GMAC mode muxing, and GRF/SGRF-backed gates and muxes.

The hardware coverage is broad for a vision SoC: PMU always-on clocks, CPU/core, bus, SCR/JTAG, UART/I2C/SPI/PWM/GPIO/ADC/timer/watchdog/CAN/decompress/OTP, audio I2S/PDM/AUDPWM/codec, VI/ISP/CSI, JPEG/VDEC/IVE, VO/RGA/VOP/DSI/IEP, PHP/storage/USB/GMAC, DDR, top/PHY clocks, and low-power reference clocks.

## Important APIs, Types, And Data

- `enum rv1126_pmu_plls` declares the PMU GPLL. `enum rv1126_plls` declares main APLL, DPLL, CPLL, and HPLL.
- `rv1126_pll_rates[]` provides a shared RK3036-style PLL table from 1.608 GHz to 96 MHz. DPLL is registered without a rate table, indicating DDR-sensitive or externally controlled use.
- CPU clock data uses `rv1126_cpuclk_rates[]` and `rv1126_cpuclk_data` to map ARM parent rates to ACLK core and PCLK debug dividers for a single-core ARM clock.
- Parent arrays define PMU 32 kHz and WiFi sources, USB/MIPI PHY references, ARM PLL parents, bus roots, UART fractional parents, I2S/audio fractional and IO parents, VOP pixel fractional parents, GMAC RGMII/RMII/mode parents, and DDR clock parents.
- `rgmii_mux_idx[]` supplies a non-linear mux table for `MUXTBL(RGMII_MODE_CLK, ...)`, mapping logical RGMII mode selections to hardware encodings.
- `rv1126_pmu_pll_clks[]` and `rv1126_pll_clks[]` register PMU and main PLLs separately against their own register spaces.
- PMU fractional mux helpers cover RTC 32 kHz and UART1. Main fractional mux helpers cover UART0/2/3/4/5, I2S0 TX/RX, I2S1, I2S2, AUDPWM, and VOP DCLK.
- `rv1126_clk_pmu_branches[]` describes PMUCRU clocks: PMU bus, RTC/div32k, WiFi, UART1, I2C0/2, PWM0/1, SPI0, GPIO0 debounce, PMUPVTM, USB/MIPI PHY refs, PMU/PMUGRF/PMUSGRF/PMUCRU, chip version OTP, and scrkeygen.
- `rv1126_clk_branches[]` describes the main CRU. It includes USB480M selection, CPU/debug, bus and SGRF gates, UART0/2-5, I2C1/3-5, SPI1, PWM2, GPIO1-4, ADC/timer/spinlock/decompress/CAN/OTP, CPU/NPU TSADC, audio, VO/display, PHP/storage, USB, GMAC, top PHY gates, DDR, and internal NIU fabric gates.
- `rv1126_cru_critical_clocks[]` protects PLLs and important fabric, DDR, USB, JPEG, and VDEC interconnect clocks.
- `struct clk_rv1126_inits` stores a function pointer used as `of_match` data to select `rv1126_clk_init()` or `rv1126_pmu_clk_init()`.

## Control Flow

`builtin_platform_driver_probe(clk_rv1126_driver, clk_rv1126_probe)` registers a built-in platform probe. The match table contains `rockchip,rv1126-cru` and `rockchip,rv1126-pmucru`, each with a pointer to the appropriate init wrapper. `clk_rv1126_probe()` obtains match data with `of_device_get_match_data()`, returns `-EINVAL` if absent, and invokes the selected init function.

`rv1126_pmu_clk_init()` maps the PMUCRU register region, initializes a provider sized to `CLKPMU_NR_CLKS`, registers the PMU GPLL, registers PMU branches, registers two banks of PMU soft resets, and adds the OF provider.

`rv1126_clk_init()` maps the main CRU region, creates a provider sized to `CLK_NR_CLKS`, registers APLL/DPLL/CPLL/HPLL, registers the ARM clock, registers main branches, registers 15 soft reset banks, registers restart at `RV1126_GLB_SRST_FST`, protects critical clocks, and adds the OF provider.

Runtime behavior is framework-driven: CCF consumers request rates or enables, Rockchip ops program mux/divider/fractional/gate/GRF fields, MMC phase ops program sample/drive registers, reset consumers assert/deassert registered soft resets, and restart uses the Rockchip restart notifier.

## State And Persistence Behavior

The driver keeps no heap or file-static runtime state. The platform device match data selects an init path, and after init the CCF and reset frameworks own software state. Mutable hardware state is held in PMUCRU and CRU PLL, mux, divider, gate, fractional divider, GRF mux, SGRF gate, MMC phase, soft reset, and global reset registers.

Important behavior:

- PMUCRU and CRU are independent providers with separate register mappings and clock ID spaces.
- Critical clocks include PLLs and bus roots that must survive unused-clock cleanup.
- GRF-backed muxes and SGRF-backed gates mean not all clock control bits live in the CRU register block; syscon/GRF access through Rockchip helpers must be available.
- DPLL has no rate table, matching its DDR clock role.
- GMAC clocking has multiple mode-dependent paths: internal divider, external RGMII inputs, RGMII/RMII dividers, non-linear RGMII mux encoding, and no-reparent constraints on the final GMAC source/tx-rx muxes.

## Dependencies And Integration Points

The file depends on platform devices, OF matching, OF address mapping, Linux CCF, Rockchip clock/reset helpers, GRF/SGRF helper support in `clk.h`, and `dt-bindings/clock/rockchip,rv1126-cru.h`. Device tree must provide both main `rockchip,rv1126-cru` and PMU `rockchip,rv1126-pmucru` nodes where needed, plus external parent clocks such as oscillator inputs, USB480M PHY, WiFi oscillator, I2S MCLK inputs, JTAG IO clock, GMAC RGMII input clocks, and MIPI/USB PHY reference inputs.

Consumers include CPUfreq, PMU firmware, UART/I2C/SPI/PWM/GPIO/timer/watchdog/CAN/ADC, audio I2S/PDM/AUDPWM/codec, SDMMC/SDIO/eMMC/NAND/SFC, USB host/OTG/PHY, GMAC, display VOP/DSI/IEP/RGA, camera and ISP/CSI, JPEG/VDEC/IVE media engines, DDR controller/monitor, OTP/scrkeygen, reset consumers, and restart.

## Risks And Edge Cases

- Main CRU and PMUCRU must both bind when consumers reference clocks across domains. Missing PMUCRU can break UART1, PMU GPIO, WiFi, PHY refs, and 32 kHz clocks.
- `rv1126_pmu_clk_init()` returns after failed `rockchip_clk_init()` without `iounmap(reg_base)`, unlike the main CRU path. That is an init-time leak on failure.
- GRF and SGRF-backed controls (`MUXGRF`, `SGRF_GATE`) rely on correct syscon integration and register offsets such as `RV1126_GRF_IOFUNC_CON1`; bad GRF access can break GMAC or security-owned gates.
- GMAC mode selection is complex. Wrong mux table indices, external clock parents, or no-reparent constraints can break RGMII/RMII timing.
- DPLL/DDR clocks are exposed but not normally rate-programmable. Treating them like ordinary PLLs risks memory instability.
- Critical-clock names must match registered clock names. A typo silently weakens protection against unused-clock cleanup.
- Fractional audio/UART/VOP clocks are sensitive to parent rates and reparenting rules. Incorrect parent choice can cause serial baud drift, audio sample-rate error, or display pixel-clock failure.

## Test Signals

Validation should show both `rockchip,rv1126-cru` and `rockchip,rv1126-pmucru` probing successfully, populated clock summaries for both providers, protected critical clocks, and registered main/PMU reset controllers. Rate tests should cover ARM clock changes, UART0-5 and UART1 PMU fractional rates, I2S/PDM/AUDPWM audio rates, VOP DCLK fractional rates, SDMMC/SDIO/eMMC phases, GMAC RGMII/RMII modes, USB480M selection, 32 kHz/RTC sources, and DDR clock readout. Functional tests should exercise storage, USB, GMAC, camera/ISP/CSI, JPEG/VDEC/IVE, display, audio, serial, PMU wake clocks, GPIO debounce, ADCs, timers/watchdogs, OTP/security gates, soft resets, suspend/resume, and restart.
