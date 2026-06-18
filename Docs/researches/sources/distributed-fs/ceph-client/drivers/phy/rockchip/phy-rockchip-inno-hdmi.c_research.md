# sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-inno-hdmi.c

## Purpose
This driver controls RK3228/RK3328 Innosilicon HDMI PHYs and also registers the PHY pre-PLL as a clock provider for the HDMI pixel clock. It owns PLL rate tables, TMDS configuration tables, post-PLL programming, optional RK3328 ESD interrupt handling, and generic PHY power callbacks.

## Important APIs, Types, And Functions
`struct inno_hdmi_phy` stores MMIO regmap, clocks, PHY, registered `clk_hw`, current pixel/TMDS clocks, chip version, IRQ, and platform ops. `pre_pll_config`, `post_pll_config`, and `phy_config` tables encode supported rates and analog settings. Clock ops for RK3228/RK3328 implement prepare/unprepare, recalc, determine_rate, and set_rate. Generic PHY callbacks use `inno_hdmi_phy_power_on()` and `power_off()`. Variant ops initialize bypass/internal control and program post-PLL/driver settings. RK3328 IRQ handlers detect ESD/AGND events and repower the PHY.

## Control Flow
Probe maps MMIO through regmap, gets and enables `sysclk` and `refpclk`, gets `refoclk`, requests an optional IRQ, creates the PHY, sets bus width 8, runs variant init, registers `pin_hd20_pclk` or `clock-output-names` as a clock provider, and registers the PHY provider. HDMI clock consumers set the pixel clock through the registered clk; the driver selects exact pre-PLL table entries and waits for lock. PHY power-on derives TMDS clock from bus width, looks up post-PLL and analog config, ensures pre-PLL rate is set/enabled, enables `phyclk`, calls variant power-on, and waits for post-PLL lock. Power-off calls variant power-off and disables the PHY clock.

## State And Persistence
The driver caches `pixclock`, `tmdsclock`, and `chip_version`. Hardware state includes pre/post PLL registers, TMDS drive settings, interrupt masks, and clock provider state. `of_clk_del_provider()` runs on remove; sysclk/refpclk are disabled by a devm action.

## Dependencies And Integration Points
It depends on generic PHY, common clock provider APIs, regmap MMIO, optional nvmem cell `cpu-version`, platform IRQs, and clocks `sysclk`, `refpclk`, and `refoclk`. It integrates with DRM HDMI components as both a PHY and a pixel clock provider. Compatible strings are `rockchip,rk3228-hdmi-phy` and `rockchip,rk3328-hdmi-phy`.

## Risks And Test Signals
Supported rates are table-driven; unsupported pixel clocks fail `determine_rate` or pre/post-PLL lookup. RK3228 rejects fractional pre-PLL entries in determine_rate while RK3328 accepts them. IRQ repower assumes cached clocks/config are valid. Test signals include clock rate negotiation for CEA/VESA modes, pre/post PLL lock polling, RK3328 nvmem version handling including defer, ESD IRQ recovery, 10-bit bus-width TMDS scaling, and provider cleanup on remove.
