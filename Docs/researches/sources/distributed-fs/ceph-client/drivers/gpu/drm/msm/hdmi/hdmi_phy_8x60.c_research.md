# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_phy_8x60.c

## Purpose
Programs power-up and power-down sequences for the older 8x60 HDMI PHY.

## Important APIs, types, and functions
- `hdmi_phy_8x60_powerup()` sequences deserializer delay, swing level, power generator, PLL, drivers, lock detect, retiming, and receive sense.
- `hdmi_phy_8x60_powerdown()` resets the PHY, powers down drivers/PLL/power generator, and leaves receive sense enabled.
- `msm_hdmi_phy_8x60_cfg` exposes callbacks plus `core-vdda` regulator and `slave_iface` clock.

## Control flow
Power-up selects output swing based on 27 MHz pixel clock versus other modes, starts from full powerdown, incrementally enables power generator, PLL, ASIC power, lock detect, retiming, drivers, and receive sense, clears several registers, then forces lock detection. Power-down asserts/deasserts controller reset, disables drivers, disables PLL, and powers down most blocks.

## State and persistence
There is no software state. Register programming persists while the PHY is powered and is reset by powerdown or platform reset.

## Dependencies and integration points
Depends on `hdmi_phy_write()`, register bit macros, and the common HDMI PHY platform driver.

## Risks
Timing delays are short and hardware-specific. The special 27 MHz swing setting can affect only SD modes. Leaving receive sense enabled is intentional for cable detection and should not be removed without HPD validation.

## Test signals
Validate 27 MHz and non-27 MHz modes, hotplug after powerdown, PHY lock/stability, and current draw in powerdown with RX sense.
