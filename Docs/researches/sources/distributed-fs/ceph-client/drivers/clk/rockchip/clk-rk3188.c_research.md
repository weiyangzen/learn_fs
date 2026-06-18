# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3188.c

## Purpose
`clk-rk3188.c` supports multiple related Rockchip CRUs: RK3066A, RK3188A, and RK3188. It provides common clocks plus SoC-specific branch and PLL/CPU-clock definitions. The driver covers ARM/CPU buses, DDR, video encode/decode, LCDC/CIF/IPP/RGA, peripheral buses, USB PHYs, MAC, HSADC, SARADC, SPDIF, UARTs, SMC/SPI/MMC, timers, JTAG, GPIO/I2C/PWM, HDMI, GPU, HSIC, GPS, and variant-specific I2S/display arrangements. It also contains compatibility behavior for RK3188 PLL rate programming.

## Important APIs, Types, And Functions
The file defines `rk3188_pll_rates`, RK3066 and RK3188 CPU clock rate/data tables, two PLL arrays (`rk3066_pll_clks`, `rk3188_pll_clks`), common and variant branch arrays, divider tables (`div_core_peri_t`, `div_aclk_cpu_t`, `div_rk3188_aclk_core_t`), and fractional mux descriptors for HSADC, SPDIF, UART0-3, and I2S. `rk3188_common_clk_init()` handles shared provider setup. `rk3066a_clk_init()`, `rk3188a_clk_init()`, and `rk3188_clk_init()` are registered for `rockchip,rk3066a-cru`, `rockchip,rk3188a-cru`, and `rockchip,rk3188-cru`.

## Control Flow
Variant init starts by computing the selected branch table max ID and calling `rk3188_common_clk_init()`, which maps the CRU, initializes a provider sized for common plus variant clocks, registers common branches, soft resets, and restart notifier. RK3066A then registers RK3066 PLLs, RK3066A branches, the RK3066 CPU clock table, critical clocks, and the OF provider. RK3188A registers RK3188 PLLs and branches, registers the RK3188 ARM clock, then looks up `aclk_cpu_pre` and `gpll`, reparents `aclk_cpu_pre` from APLL to GPLL while preserving its current rate, protects critical clocks, and adds the provider. The `rk3188_clk_init()` wrapper first iterates every RK3188 PLL rate and sets `rate->nb = 1`, then delegates to the RK3188A path.

## State And Persistence Behavior
There is no syscore suspend/resume persistence block. The main local state changes are CRU registration, RK3188 rate-table mutation (`nb = 1` for each PLL rate), and the RK3188A reparenting of `aclk_cpu_pre`. That reparenting deliberately keeps `aclk_cpu_pre` off APLL to reduce CPU-clock coupling complexity while restoring the prior rate after parent change. Critical clocks protect CPU/peripheral/VIO buses and `sclk_mac_lbtest`. Common clock state is otherwise persisted in CRU registers and exposed through the common clock framework.

## Dependencies And Integration Points
The driver depends on `dt-bindings/clock/rk3188-cru.h`, Rockchip clock macros, CCF APIs including `__clk_lookup()`, `clk_get_rate()`, `clk_set_parent()`, and `clk_set_rate()`, OF register mapping, reset registration, and restart notifier registration. Consumers include CPUfreq, display/LCDC and image pipeline blocks, VPU, GPU, USB/HSIC, EMAC, HSADC/SARADC, audio, UARTs, MMC/SDIO/eMMC, SPI/SMC, timers, GPIO/I2C/PWM, HDMI, and GPS depending on the selected SoC.

## Risks
This file has several variant-specific hazards. The RK3188 wrapper mutates a shared static PLL rate table at boot; future reuse must account for that side effect. The `__clk_lookup()` reparenting is name-based and can warn or fail if earlier registration changes clock names. Reparenting `aclk_cpu_pre` while preserving rate depends on valid rate propagation through the selected parents. RK3066A and RK3188 use different CPU divider layouts, so mixing compatibles can break CPU/bus timing. Many branches use RK2928 register macros; offset reuse increases copy/paste risk.

## Test Signals
Boot each compatible separately and check for missing reparent warnings. Inspect `clk_summary` to confirm RK3188 `aclk_cpu_pre` parent is GPLL and rate is preserved. Exercise CPUfreq for both RK3066 and RK3188 tables, display paths for dual LCDC/CIF variants, I2S0/1/2 and SPDIF fractional rates, UART0-3 baud changes, MMC/SDIO/eMMC storage, USB OTG/host and HSIC, EMAC link, HSADC/SARADC, GPU/VPU clocks, reset users, and reboot through RK2928 global reset. For RK3188 specifically, validate PLL rates that require the modified `nb` field.
