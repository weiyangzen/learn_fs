# sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-dp.c

## Purpose
This driver provides the RK3288 DisplayPort/eDP PHY as a generic PHY. It controls a 24 MHz PHY clock and GRF bits for reference-clock selection and SIDDQ power state.

## Important APIs, Types, And Functions
`struct rockchip_dp_phy` stores the device, parent GRF regmap, and `phy_24m` clock. `rockchip_set_phy_state()` is the central helper used by `.power_on` and `.power_off`; it writes GRF high-word update masks and enables/disables the 24 MHz clock. `rockchip_dp_phy_probe()` obtains the clock, forces it to 24 MHz, locates the parent syscon GRF, selects the internal eDP reference clock, creates the PHY, and registers a simple OF provider.

## Control Flow
Probe requires both the PHY node and a parent OF node because the parent supplies the GRF syscon. After clock and GRF setup, it creates one PHY. Power-on clears SIDDQ through GRF and prepares/enables `phy_24m`. Power-off disables the clock first and writes SIDDQ off. Consumers reach the driver through `of_phy_simple_xlate()`.

## State And Persistence
There is no complex software state beyond handles. Hardware power state lives in GRF SIDDQ and ref-clock selection bits; clock framework state tracks `phy_24m` prepare/enable count.

## Dependencies And Integration Points
The driver depends on generic PHY, common clock, Rockchip GRF syscon as parent, regmap, and compatible string `rockchip,rk3288-dp-phy`. It is consumed by the Rockchip display pipeline through a PHY phandle.

## Risks And Test Signals
The main risk is sequencing: power-on writes SIDDQ before clock enable, and error handling returns clock failures after the PHY is already unsuspended in GRF. Test signals include GRF ref-clock selection during probe, 24 MHz clock rate enforcement, successful display link training after PHY power-on, and SIDDQ assertion when the display stack powers down.
