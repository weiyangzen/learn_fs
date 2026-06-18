<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/marvell_phy.h -->
# sources/distributed-fs/ceph-client/include/linux/marvell_phy.h

## Purpose
This header centralizes Marvell Ethernet PHY and embedded switch-family IDs plus per-device flag bits used by PHY drivers.

## Important APIs, types, and functions
It defines `MARVELL_PHY_ID_MASK`, many `MARVELL_PHY_ID_*` constants for 88E/88X/88Q PHY families, `MARVELL_PHY_FAMILY_ID(id)`, and `dev_flags` bits such as `MARVELL_PHY_M1145_FLAGS_RESISTANCE`, `MARVELL_PHY_M1118_DNS323_LEDS`, and `MARVELL_PHY_LED0_LINK_LED1_ACTIVE`.

## Control flow
There are no functions. PHY drivers and MDIO matching tables use the constants to match IDs and select quirks or LED/resistance configuration paths.

## State and persistence
No state is stored here. `dev_flags` values become runtime state inside `struct phy_device` consumers.

## Dependencies and integration points
It integrates with phylib drivers, MDIO device ID matching, and Marvell DSA switch families that expose embedded PHY IDs through trapped reads.

## Risks and test signals
Risks include mask collisions across closely related PHYs, switch-family IDs masquerading as PHY model IDs, and incompatible `dev_flags` combinations. Test all declared IDs against expected driver entries, quirk selection, and family extraction for embedded PHYs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/marvell_phy.h -->
