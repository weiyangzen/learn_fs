# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rv1103b.c

## Purpose

`clk-rv1103b.c` is the CRU driver for Rockchip RV1103B. It registers the SoC's PLLs, CPU clock, clock branches, restart notifier, and OF clock provider using the Rockchip clock framework. The file is table-driven and tuned for a small camera/AI-oriented SoC with PMU, VI/ISP, VEPU, NPU, peripheral, DDR, storage, audio, UART, and always-on low-speed clock domains.

The driver exposes clock IDs from `dt-bindings/clock/rockchip,rv1103b-cru.h` to device-tree consumers. It also performs a small post-registration hardware initialization step that selects PVTPLL sources for CPU, NPU, VI, and VEPU paths.

## Important APIs, Types, And Data

- `enum rv1103b_plls` declares `dpll` and `gpll`; both are registered from `rv1103b_pll_clks[]` using `pll_rk3328` descriptors and `rv1103b_pll_rates[]`.
- `rv1103b_pll_rates[]` contains a compact RK3036-style rate table for 1.2 GHz, 1.188 GHz, and 1.0 GHz. PLL lock status is read through `RV1103B_GRF_SOC_STATUS0`.
- CPU-rate macros encode ACLK core and PCLK debug divisors in `RV1103B_CORECLKSEL_CON(2)`. `rv1103b_cpuclk_rates[]` lists supported CPU parent rates from 1.608 GHz down to 396 MHz with associated bus/debug dividers.
- Parent arrays define derived GPLL divider parents, low-speed PMU roots, UART fractional muxes, SAI/audio muxes, NPU/VEPU/ISP PVTPLL alternatives, storage/peripheral parents, 32 kHz sources, and IO output muxes.
- `rv1103b_clk_uart0_fracmux`, `rv1103b_clk_uart1_fracmux`, and `rv1103b_clk_uart2_fracmux` are final mux stages for UART integer, fractional, and 24 MHz parents.
- `rv1103b_rcdiv_pmu_fracmux` finalizes the `clk_32k` selection from RC-divided, RTC, or IO 32 kHz sources.
- `rv1103b_clk_branches[]` is the main descriptor array. It contains GPLL fixed divisors, UART/SPI/I2C/PWM/timer/watchdog/GPIO/ADC/storage gates, SAI and audio codec clocks, VI/ISP/CSI/VICAP clocks, VEPU/NPU roots, DDR monitor clocks, PMU and PMU1 low-power clocks, crypto/RNG/OTP/RGA/GMAC/USB/decompress clocks, and IO-output clocks.
- `rv1103b_armclk` is a mux between `armclk_gpll` and `clk_core_pvtpll`, registered with `rockchip_clk_register_armclk_multi_pll()` so CPU clocking can switch between multiple PLL sources.

## Control Flow

`CLK_OF_DECLARE(rv1103b_cru, "rockchip,rv1103b-cru", rv1103b_clk_init)` installs an early OF init hook. `rv1103b_clk_init()` computes the number of clock slots from the maximum ID in `rv1103b_clk_branches[]`, maps the CRU register range with `of_iomap()`, creates a Rockchip clock provider with `rockchip_clk_init()`, and returns early with an error message on mapping or provider setup failure.

On success, it registers PLLs with `rockchip_clk_register_plls()`, registers the main branch table, registers the multi-PLL CPU clock, registers a restart notifier at `RV1103B_GLB_SRST_FST`, and publishes the provider with `rockchip_clk_of_add_provider()`. Finally it writes `PVTPLL_SRC_SEL_PVTPLL` to the CPU, NPU, VI, and VEPU clock-select registers so those domains use PVTPLL sources where their muxes expose them.

At runtime, CCF consumers use the registered clocks. Rockchip helper ops update mux, divider, fractional, gate, and PLL registers with hiword masks; restart is handled by the common Rockchip restart notifier path.

## State And Persistence Behavior

The file keeps no dynamic private state after init. Provider and clock state is owned by the Rockchip clock framework. Mutable state is in CRU and PMU CRU registers: PLL configuration and mode bits, divider/mux fields, fractional divider registers, gate registers, CPU clock dividers, restart register, and the PVTPLL source-selection fields explicitly written at the end of init.

Several descriptors affect state behavior:

- `CLK_IS_CRITICAL` protects PLLs and key bus/root clocks such as `armclk_gpll`, LSCLK roots, VI source roots, PERI roots, PMU root, DDR root, and SRAM-related clocks.
- `CLK_SET_RATE_PARENT` on UART, SAI, NPU/VEPU/ISP PVTPLL root muxes, MIPI output, and 32 kHz mux paths allows leaf requests to propagate into source clocks.
- `CLK_SET_RATE_NO_REPARENT` on `clk_32k` avoids unexpected source switching after the selected 32 kHz parent is established.
- The PVTPLL writes are persistent only until reset or later firmware/driver writes; there is no suspend-time save/restore in this file.

## Dependencies And Integration Points

The driver depends on OF address mapping, Linux CCF, Rockchip clock helpers, and the RV1103B clock binding header. Device tree must provide the `rockchip,rv1103b-cru` node and external parent names used in the graph, including `xin24m`, `clk_rc_osc_io`, `clk_32k_rtc`, `clk_32k_io`, SAI IO clocks, MIPI reference outputs, USB UTMI IO clocks, SPI2AHB IO clock, and PVTPLL clocks (`clk_core_pvtpll`, `clk_npu_pvtpll`, `clk_vepu_pvtpll`, `clk_isp_pvtpll_src`).

Consumer integration includes CPUfreq, low-power MCU and PMU firmware, UART0-2, I2C0-4, SPI, PWM, timers, watchdogs, GPIO debounce, SARADC/TSADC, SAI/audio codec, NPU/RKNN, VEPU, ISP/VICAP/CSI, eMMC/SDMMC/SFC, DDR monitor, USB OTG/PHY, crypto/RNG/OTP, RGA, GMAC, decompressor, spinlock, mailboxes, and restart.

## Risks And Edge Cases

- The PVTPLL source writes after provider registration are direct `writel_relaxed()` calls. If a PVTPLL parent is absent, unprepared, or not rate-compatible, CPU/NPU/VI/VEPU consumers can see unexpected clocks.
- The computed clock count depends on branch IDs only; if a future CPU or PLL clock ID exceeds the branch maximum, the provider allocation could be too small.
- The file uses both `RV1103B_*` and some `RK3568_PMU_CLKSEL_CON` register macros for PMU 32 kHz and GPIO debounce paths. Those aliases must match the RV1103B register layout.
- Fractional UART and SAI clocks are parent-rate sensitive, especially because `RV1103B_FRAC_MAX_PRATE` indicates fractional parent-rate constraints even though the constant is not directly referenced in this file.
- Critical clock flags are required for low-speed roots, DDR, VI, and peripheral fabric; dropping them can make late unused-clock cleanup break boot or firmware paths.
- As with all Rockchip clock tables, incorrect binding ID, gate bit, mux width, or divider field can silently affect unrelated hardware.

## Test Signals

Validation should show successful early init for `rockchip,rv1103b-cru`, registered PLLs, a populated clock summary, and no missing-parent messages. Rate tests should exercise CPU frequency changes, UART baud-rate generation through fractional muxes, SAI/audio rates, 32 kHz source selection, storage clocks, ISP/VEPU/NPU roots, and MIPI output clocks. Functional tests should cover serial console, storage boot, camera capture, video encode, RKNN/NPU workloads, audio, USB OTG, GMAC, crypto/RNG/OTP access, timers/watchdogs, GPIO debounce wake paths, and restart behavior.
