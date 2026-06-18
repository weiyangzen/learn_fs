# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_phy_8960.c

## Purpose
Defines the simple MSM8960 HDMI PHY power sequencing and resource names.

## Important APIs, types, and functions
- `hdmi_phy_8960_powerup()` writes fixed PHY register values for analog setup and power-up.
- `hdmi_phy_8960_powerdown()` writes `0x7f` to power down the PHY.
- `msm_hdmi_phy_8960_cfg` advertises type, callbacks, one regulator, and one clock.

## Control flow
Power-up logs the pixel clock but does not vary programming by it. It writes REG2 low, fixed analog values to REG0/REG1, zeros several config registers, and writes REG3 `0x20`. Power-down writes the all-powerdown value to REG2.

## State and persistence
No software state is stored. Hardware register values persist while the PHY remains powered. Resource names are consumed by common `hdmi_phy.c`.

## Dependencies and integration points
Depends on `hdmi_phy_write()` and MSM8960 register definitions from `hdmi.h`. The config is referenced by the DT match table in `hdmi_phy.c`.

## Risks
The programming sequence is fixed and opaque, so changes require hardware validation. The ignored pixel clock means all modes rely on a single PHY tuning set while the PLL handles frequency.

## Test signals
Signals include successful modes on MSM8960 hardware, powerdown leakage/HPD behavior, and absence of PHY bring-up errors.
