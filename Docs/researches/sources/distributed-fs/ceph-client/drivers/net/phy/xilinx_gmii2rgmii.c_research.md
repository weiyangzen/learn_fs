# sources/distributed-fs/ceph-client/drivers/net/phy/xilinx_gmii2rgmii.c

## Purpose
`xilinx_gmii2rgmii.c` is an MDIO driver for the Xilinx GMII-to-RGMII converter. It finds the real downstream PHY referenced by `phy-handle`, wraps that PHY driver's status and loopback callbacks, and programs the converter speed bits whenever the PHY speed changes.

## Important APIs, Types, And Functions
`struct gmii2rgmii` stores the attached `phy_device`, original `phy_driver`, copied wrapper `phy_driver`, and converter `mdio_device`. Main functions are `xgmiitorgmii_configure()`, `xgmiitorgmii_read_status()`, `xgmiitorgmii_set_loopback()`, and `xgmiitorgmii_probe()`.

## Control Flow
Probe allocates private data, enables an optional clock, parses `phy-handle`, finds the PHY device, defers if the PHY or its driver is not ready, copies the original driver structure, overrides `read_status` and `set_loopback`, stores private data on the real PHY's MDIO device, and replaces `phy_dev->drv` with the wrapper. Status and loopback callbacks call the original driver implementation or generic fallback first, then write `XILINX_GMII2RGMII_REG` speed bits for 10/100/1000 according to `phydev->speed`.

## State And Persistence
Persistent state is the wrapper object and the converter register value. The driver mutates the attached PHY's driver pointer at runtime; the original pointer is retained in private data for delegation.

## Dependencies And Integration Points
It depends on MDIO driver registration, phylib, OF MDIO lookup, optional clocks, and standard BMCR speed bits. It integrates between a converter MDIO device and an already registered external PHY.

## Risks And Edge Cases
The wrapper approach is invasive: it replaces `phy_dev->drv` and there is no remove callback restoring the original driver pointer. Probe deferral handles absent/not-ready PHYs, but lifetime coupling between converter and PHY must remain valid. `xgmiitorgmii_configure()` does not check MDIO read/write errors, so converter programming failures are silent. Unknown speeds fall through to 10 Mbps.

## Test Signals
Test probe ordering with PHY unavailable and later ready, optional clock failures, status changes at 10/100/1000, loopback configuration, MDIO write verification, removal/unbind behavior, and downstream PHY drivers with and without custom `read_status` or `set_loopback`.
