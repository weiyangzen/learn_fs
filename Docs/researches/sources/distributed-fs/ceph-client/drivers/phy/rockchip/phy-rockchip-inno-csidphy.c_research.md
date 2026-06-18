# sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-inno-csidphy.c

## Purpose
This driver controls Rockchip Innosilicon MIPI CSI D-PHY receiver blocks across multiple SoCs. It configures lane enables, THS settle timing, optional calibration, reset controls, pclk/runtime PM, and SoC-specific GRF bits.

## Important APIs, Types, And Functions
`struct rockchip_inno_csidphy` stores MMIO, pclk, GRF regmap, reset bulk, match data, current MIPI D-PHY config, and selected HS frequency code. `struct dphy_drv_data` supplies offsets, HS frequency table, GRF register table, and reset names per SoC. `rockchip_inno_csidphy_configure()` validates MIPI options and chooses HS range. `rockchip_inno_csidphy_power_on()` enables pclk/runtime PM, resets analog/digital logic, enables lanes and optional high-rate calibration, programs THS settle for clock/data lanes, and enables GRF lanes. Power-off disables lanes, powers down PLL/LDO where applicable, and releases PM/clock.

## Control Flow
Probe reads match data, gets `rockchip,grf`, maps PHY registers, gets `pclk`, obtains the variant reset bulk, creates the PHY, registers a provider, and enables runtime PM. Consumers configure MIPI lane/rate values first; power-on then uses that state to program lane masks and timing. Variants cover PX30/RK3326/RK1808/RK3368/RK3568/RK3588 with different pwrctl/calib offsets and reset lists.

## State And Persistence
Software retains the last MIPI config and `hsfreq` code. Runtime PM state is managed per power-on/off, while clocks are prepared in `.init` and enabled in `.power_on`. Hardware state is volatile register programming and GRF lane control.

## Dependencies And Integration Points
The driver uses generic PHY, MIPI D-PHY validation helpers, syscon/regmap via `rockchip,grf`, reset bulk APIs, runtime PM, and platform MMIO. It integrates with CSI receiver/camera pipelines through PHY configure and power callbacks.

## Risks And Test Signals
The range lookup uses zero as the "not found" sentinel, so tables with cfg `0x00` make the lowest range invalid. Lane count must be configured before power-on because masks use `config.lanes`. Optional pwrctl/calib offsets differ by SoC, so missing data can silently skip calibration or power control. Test signals include probe on each compatible, reset count bounds, high-rate calibration above 1500 Mbps, lane masks for 1-4 lanes, runtime PM balance, and camera capture at boundary rates from the HS tables.
