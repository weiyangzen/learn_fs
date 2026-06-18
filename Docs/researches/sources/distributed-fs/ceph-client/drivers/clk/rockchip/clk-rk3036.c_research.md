# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3036.c

## Purpose
`clk-rk3036.c` provides the RK3036 CRU clock driver. It declares PLL rates, CPU clock divider programming, and branch clocks for a compact Rockchip SoC with CPU, DDR, peri, video/display, MMC, audio, UART, SPI, NAND/SFC, GPU, MAC, HDMI, USB PHY, timers, GPIO, I2C, PWM, and watchdog clocks. The file is primarily declarative, but it has one important initialization write that forces the shared UART PLL source to GPLL because the other selectable sources are treated as unstable or unsuitable.

## Important APIs, Types, And Functions
The main tables are `rk3036_pll_rates`, `rk3036_cpuclk_rates`, `rk3036_cpuclk_data`, `rk3036_pll_clks`, and `rk3036_clk_branches`. PLLs are described as RK3036 PLL instances for APLL, DPLL, and GPLL, with GPLL flagged `ROCKCHIP_PLL_SYNC_RATE`. CPU clock data maps the ARM clock mux and divider registers through `RK2928_CLKSEL_CON()` offsets. Parent-name arrays describe ARM selection from APLL/GPLL, bus and DDR source selections, USB480M selection, MMC source selection, audio fractional muxes, UART fractional muxes, MAC external clock selection, and LCDC/HDMI display routing.

The branch table uses Rockchip helper macros to register muxes, composites, gates, dividers, factors, fractional muxes, and MMC phase clocks. `rk3036_uart0_fracmux`, `rk3036_uart1_fracmux`, `rk3036_uart2_fracmux`, `rk3036_i2s_fracmux`, and `rk3036_spdif_fracmux` are standalone `rockchip_clk_branch` descriptors referenced by `COMPOSITE_FRACMUX()` entries. `rk3036_clk_init()` is the sole init function and is registered for `rockchip,rk3036-cru` with `CLK_OF_DECLARE()`.

## Control Flow
The OF init hook maps the CRU registers with `of_iomap()`. Before registering clocks, it writes `RK2928_CLKSEL_CON(13)` with `HIWORD_UPDATE(0x2, 0x3, 10)` so `uart_pll_clk` is sourced from GPLL. It then computes the provider size from `rk3036_clk_branches`, initializes the provider, registers PLLs with GRF status offset `RK3036_GRF_SOC_STATUS0`, registers branches, protects critical clocks, registers the ARM clock, registers 9 soft reset registers, registers the restart notifier, and adds the OF clock provider. Error handling logs mapping or provider-init failures and unmaps the CRU base if provider creation fails.

## State And Persistence Behavior
The only imperative state change outside framework registration is the UART parent selection write during init. After that, state is held in CRU registers managed by common clock operations. The critical list protects `aclk_cpu`, `aclk_peri`, `hclk_peri`, `pclk_peri`, `pclk_ddrupctl`, and `ddrphy`, reflecting the minimum fabric and DDR clocks that must not be disabled. There is no syscore suspend/resume state save in this driver, so suspend correctness depends on the platform preserving CRU state or on firmware/kernel code outside this file.

## Dependencies And Integration Points
The driver depends on `dt-bindings/clock/rk3036-cru.h` for numeric IDs, the Rockchip clock helper layer, common clock framework, OF mapping, and reset/restart helper APIs. Consumer integration includes CPUfreq via `ARMCLK`, reset controller clients via `rockchip_register_softrst()`, serial drivers through `SCLK_UART0..2` and `PCLK_UART0..2`, MMC/SDIO/eMMC through source and phase clocks, display through LCDC/HDMI clocks, Ethernet through MAC reference muxing, and audio through I2S/SPDIF fractional clocks.

## Risks
The UART pre-registration write is a notable boot-order risk: if the register offset or mux encoding is wrong, all UART source clocks can inherit a bad parent before the serial driver probes. MMC phase clock register definitions must match the SoC IO timing controls or storage tuning fails. Because many clocks share the RK2928 register macro family, a copy/paste error in offset or bit position can affect unrelated clock domains. Critical-clock coverage is intentionally narrow; removing ignore-unused from fabric or DDR-related gates can cause late boot hangs when unused-clock cleanup runs.

## Test Signals
Validate by booting with `clk_ignore_unused` both enabled and disabled for comparison, checking `clk_summary` for UART parent `uart_pll_clk -> gpll`, running serial console stress on all UARTs, CPUfreq transitions through the supported RK3036 rates, MMC/SDIO/eMMC enumeration and tuning, I2S/SPDIF rate changes using fractional parents, Ethernet link with internal and external RMII clocking where applicable, display scanout through LCDC/HDMI, reset controller users, and reboot through the RK2928 global soft reset path.
