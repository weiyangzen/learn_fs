<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/fixed_phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/fixed_phy.c

## Purpose
`fixed_phy.c` implements the fixed MDIO bus: a software-emulated MDIO bus that exposes fixed-link PHY devices to PHYLIB. It lets MAC and DSA drivers use normal `phy_device` flows even when the link is not backed by a real MDIO PHY.

## Important APIs, Types, And Functions
`struct fixed_phy` binds a `phy_device`, `fixed_phy_status`, and optional `link_update` callback. Exported APIs are `fixed_phy_register()`, `fixed_phy_register_100fd()`, `fixed_phy_unregister()`, `fixed_phy_change_carrier()`, and `fixed_phy_set_link_update()`. Internal helpers include `fixed_mdio_read()`, `fixed_mdio_write()`, `fixed_phy_find()`, `fixed_phy_get_free_addr()`, and module init/exit for the fixed MDIO bus.

## Control Flow
Module init allocates and registers an MDIO bus named `fixed-0` with read/write callbacks. `fixed_phy_register()` validates the requested fixed state with `swphy_validate_state()`, defers if the bus is not registered, allocates one of eight bitmap-backed pseudo addresses, stores status with link forced true, creates a PHY device through `get_phy_device()`, attaches an OF node if provided, marks it `is_pseudo_fixed_link`, and registers it with PHYLIB.

`fixed_mdio_read()` finds the pseudo PHY, invokes its optional `link_update()` against the attached netdev, and returns a synthetic register value from `swphy_read_reg()`. Writes are ignored. Carrier changes mutate the stored fixed link state directly.

## State And Persistence
State is global to the module: `fixed_phy_ids`, `fmb_fixed_phys[]`, and `fmb_mii_bus`. A registered fixed PHY owns a bitmap slot until `fixed_phy_unregister()` removes the PHY device, releases the OF node, clears the slot, and frees the device. No persistent storage exists outside memory.

## Dependencies And Integration Points
The file depends on PHYLIB, MDIO bus registration, `linux/phy_fixed.h`, OF node refcounting, and `swphy` synthetic register helpers. It integrates with MAC drivers that use fixed-link devicetree nodes and with DSA loop or switch setups that need pseudo PHYs.

## Risks
Only eight fixed PHY slots are available. The global static storage requires correct unregister ordering to avoid stale slots. `fixed_phy_change_carrier()` and link update callbacks mutate shared state without explicit locking in this file, relying on higher-level PHY/RTNL context. Reads for missing pseudo PHYs return `0xffff`, mimicking absent MDIO devices.

## Test Signals
Test fixed-link registration and unregister, slot exhaustion, OF node lifetime, `fixed_phy_register_100fd()`, synthetic BMCR/BMSR/LPA reads through `swphy_read_reg()`, carrier changes reflected in MAC link state, DSA loop allocation, and deferred registration before the fixed bus is initialized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/fixed_phy.c -->
