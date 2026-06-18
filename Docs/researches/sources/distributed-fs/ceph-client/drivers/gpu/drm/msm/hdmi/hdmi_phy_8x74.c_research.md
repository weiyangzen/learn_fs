# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_phy_8x74.c

## Purpose
Defines minimal 8x74/8084 HDMI PHY register programming and resource names.

## Important APIs, types, and functions
- `hdmi_phy_8x74_powerup()` writes fixed analog, BIST, pattern, and power-control register values.
- `hdmi_phy_8x74_powerdown()` writes `0x7f` to power-control register 0.
- `msm_hdmi_phy_8x74_cfg` supplies callbacks, two regulators, and two clocks.

## Control flow
Power-up writes ANA_CFG0/1, clears BIST and pattern registers, and writes PD_CTRL1 `0x20`. Power-down writes PD_CTRL0 `0x7f`. Pixel clock is accepted by the callback but not used.

## State and persistence
No software state. PHY register state persists while resources remain enabled.

## Dependencies and integration points
Depends on `hdmi_phy_write()` and the DT match table in `hdmi_phy.c`, where both 8974 and 8084 compatibles map to this config.

## Risks
The fixed configuration may not cover all board-level signal integrity needs. Powerdown and powerup touch different power-control registers, so sequencing assumptions are hardware-specific.

## Test signals
Successful HDMI modes on 8974/8084, PHY powerdown recovery, and signal integrity across standard pixel clocks.
