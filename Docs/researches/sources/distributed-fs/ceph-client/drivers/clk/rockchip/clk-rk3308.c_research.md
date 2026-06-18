# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3308.c

## Purpose
`clk-rk3308.c` implements the RK3308 CRU clock driver. RK3308 is audio-heavy, and the file reflects that with extensive PDM, I2S 8-channel TX/RX, I2S 2-channel, SPDIF TX/RX, fractional mux, and external MCLK routing. It also covers CPU, DDR, bus/peripheral fabrics, VOP display, NAND/SFC/MMC, MAC, RTC32K, USBPHY reference, Wi-Fi, UART0-4, timers, ADC/OTP/PWM/CAN/one-wire, and reset/restart support.

## Important APIs, Types, And Functions
The core definitions are `rk3308_pll_rates`, `rk3308_cpuclk_rates`, `rk3308_cpuclk_data`, `rk3308_pll_clks`, and `rk3308_clk_branches`. PLLs include APLL, DPLL, VPLL0, VPLL1, and GPLL. Parent arrays emphasize DPLL/VPLL0/VPLL1 combinations, USB480M/xin24m fallbacks, UART fractional muxes, NAND/MMC divide-by-50 alternatives, MAC external clock selection, DDR standby muxing, RTC32K fractional/divider options, Wi-Fi oscillator/source switching, and the many audio TX/RX muxes. Fractional mux descriptors exist for UART0-4, VOP DCLK, RTC32K, PDM, every I2S TX/RX path, I2S 2-channel paths, and SPDIF TX/RX. `rk3308_clk_init()` is the only init function and is registered for `rockchip,rk3308-cru`.

## Control Flow
The init function maps the CRU, computes the provider clock count from `rk3308_clk_branches`, initializes the provider, registers PLLs with `RK3308_GRF_SOC_STATUS0`, registers all branches, protects critical clocks, registers the ARM clock, registers 10 soft-reset registers, installs the restart notifier for `RK3308_GLB_SRST_FST`, and adds the OF clock provider. The branch table itself declares the clock graph in domain order, with source composites followed by leaf gates and bus gates.

## State And Persistence Behavior
No local suspend/resume save logic is present. Clock state persists through CRU registers and common clock framework state. Critical clocks protect `aclk_bus`, `hclk_bus`, `pclk_bus`, `aclk_peri`, `hclk_peri`, `pclk_peri`, `hclk_audio`, `pclk_audio`, `sclk_ddrc`, and `clk_ddrphy4x`, showing that both the main fabric and audio fabric must survive unused-clock cleanup. Many audio clocks use `CLK_SET_RATE_PARENT`, so rate requests can propagate to VPLL/DPLL parents. Hiword-mask flags are consistently used for mux/divider/gate writes.

## Dependencies And Integration Points
The driver depends on `dt-bindings/clock/rk3308-cru.h`, Rockchip clock helper macros, OF mapping, CCF provider registration, reset controller helpers, and restart notifier support. Consumers include CPUfreq, DDR controller/PHY, ALSA audio controllers for PDM/I2S/SPDIF, display/VOP, NAND/SFC/MMC/SDIO/eMMC including drive/sample phases, MAC, UART0-4, Wi-Fi, USBPHY, RTC, timers, GPIO/I2C/SPI/PWM/ADC/OTP/CAN/one-wire, and reset-controller users.

## Risks
The audio graph is the dominant risk. There are many parallel TX/RX fractional paths and external MCLK parents; a parent-order or mux-width error may affect only one sample-rate direction or one I2S instance. Shared VPLL/DPLL parents mean audio rate changes can interact with other domains if flags are wrong. RTC32K has multiple possible sources, so low-power or wake behavior depends on correct muxing. MAC external/internal clock selection and MMC divide-by-50 alternatives are board- and timing-sensitive. Critical audio bus clocks should not be pruned without full audio validation.

## Test Signals
Check `clk_summary` for VPLL0/VPLL1/DPLL fanout and all audio mux parents. Run playback and capture across PDM, I2S0-3 8-channel TX/RX, I2S0-1 2-channel, SPDIF TX/RX, and external MCLK configurations at common 44.1 kHz and 48 kHz families. Exercise UART0-4 baud changes, VOP display clock changes, MMC/SDIO/eMMC tuning, NAND/SFC, MAC link with external clock, RTC32K source behavior, Wi-Fi and USBPHY reference clocks, CPUfreq, reset users, late unused-clock cleanup, and restart through RK3308 global soft reset.
