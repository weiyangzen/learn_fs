# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3128.c

## Purpose
`clk-rk3128.c` implements the CRU driver for the RK3126/RK3128 family. It shares a large common clock topology and then appends small SoC-specific branch tables for RK3126 and RK3128. The covered domains include PLLs, ARM clock dividers, DDR PHY, CPU/peripheral buses, crypto, video encode/decode, VIO/display, timers, PVTM, MIPI, MMC, CIF, I2S, SPDIF, UART, GMAC, TSP, NAND, PMU preclock, SFC, GPS, HDMI, and secure/peripheral gates.

## Important APIs, Types, And Functions
The driver uses `rk3128_pll_rates`, `rk3128_cpuclk_rates`, `rk3128_cpuclk_data`, `rk3128_pll_clks`, `common_clk_branches`, `rk3126_clk_branches`, and `rk3128_clk_branches`. It uses RK3036 PLL macros for APLL/DPLL/CPLL/GPLL, plus factor clocks `gpll_div2` and `gpll_div3` that feed many child muxes. Fractional mux descriptors cover I2S0, I2S1, SPDIF, and UART0-2. `rk3128_common_clk_init()` performs shared provider setup and registration, while `rk3126_clk_init()` and `rk3128_clk_init()` add the variant-specific branches and publish the provider. The two compatibles are `rockchip,rk3126-cru` and `rockchip,rk3128-cru`.

## Control Flow
For either compatible, the variant init function first computes the maximum clock ID required by its small SoC table, then calls `rk3128_common_clk_init()`. The common function maps the CRU, computes the common table max ID, initializes a provider sized to `max(common_nr_clks, soc_nr_clks)`, registers PLLs at `RK3128_GRF_SOC_STATUS0`, registers common branches, registers the ARM clock, registers 9 soft reset registers, and installs the restart notifier. The variant init then registers either RK3126-only secure timer/efuse/SGRF gates or RK3128-only SFC/GPS/HDMI gates, protects critical clocks, and adds the OF provider.

## State And Persistence Behavior
There is no explicit runtime state structure beyond the clock provider and no local suspend/resume save path. Clock state persists in CRU registers. Critical clocks protect CPU, HCLK/PCLK CPU, peri buses, VIO bridge, PMU preclock, and timer5. GPLL-derived factor clocks and DDR-related gates are marked to avoid unsafe disable in core paths. Since the same provider is used for both variants, the allocated clock array must include IDs from both the common and selected variant branches; the `max()` sizing in `rk3128_common_clk_init()` is the key state-safety detail.

## Dependencies And Integration Points
The file integrates with `dt-bindings/clock/rk3128-cru.h`, Rockchip clock helpers, OF mapping, common clock APIs, reset controller setup, and restart handling. It provides clock IDs for CPUfreq, DRM/VOP and display components, VPU/HEVC, crypto, MMC/SDIO/eMMC phase and source clocks, audio controllers, UARTs, GMAC, SPI/SFC/NAND storage, timers, GPIO/I2C/PWM/WDT/SARADC, and PMU/secure peripherals. Device tree compatibility selects the variant-specific surface.

## Risks
Variant split is the main risk: using the wrong compatible can omit SFC/GPS/HDMI clocks on RK3128 or secure timer/efuse/SGRF gates on RK3126. The clock provider sizing must remain synchronized with any new branch table IDs. Shared parent arrays containing GPLL dividers and USB480M require exact parent order because mux values are hardware encodings. Fractional audio/UART clocks can affect parent rates due to `CLK_SET_RATE_PARENT`. Critical clock omissions around `hclk_vio_h2p`, PMU, or timers can appear only during late unused-clock cleanup or suspend/resume.

## Test Signals
Check boot logs for one provider under the selected compatible, inspect `clk_summary` for `gpll_div2` and `gpll_div3` fanout, exercise CPUfreq over all listed ARM rates, verify RK3128 SFC/GPS/HDMI clocks only on RK3128 device trees, verify RK3126 secure gates only on RK3126, run MMC tuning and storage IO, audio playback/capture through I2S/SPDIF fractional paths, UART baud-rate changes, GMAC link and external clock parent selection, display mode set, reset users, and reboot through the RK2928 restart path.
