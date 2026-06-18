# sources/distributed-fs/ceph-client/include/linux/mii.h

## Purpose
Generic MII/GMII helper interface for PHY link management, ethtool integration, advertisement translation, duplex/flow-control resolution, and fixed BMCR encoding.

## Important APIs/Types
`struct mii_if_info` stores PHY IDs/masks, advertising state, duplex/autoneg/GMII flags, netdev pointer, and MDIO callbacks. External APIs cover link checks, autoneg restart, ethtool get/set, GMII support, media checks, and generic MII ioctl. Inline helpers translate ethtool/linkmode/MII advertisement bits, resolve negotiated speed/duplex, handle 1000Base-T/X, advertise and resolve pause, and encode fixed BMCR.

## Control Flow
Drivers initialize `mii_if_info`, route MDIO reads/writes through callbacks, and invoke helpers from ioctl, ethtool, autoneg, and link-monitor paths. Inline helpers perform bit selection, priority selection, and pause-resolution logic.

## State And Persistence
Driver-owned `mii_if_info` and PHY registers hold state. Helpers produce values that drivers write to MII registers or expose through ethtool.

## Dependencies And Integration Points
Depends on net if definitions, linkmode helpers, UAPI MII constants, ethtool structures, and MDIO callbacks. Bridges older MII helpers with modern ethtool link settings.

## Risks
Legacy `ethtool_cmd` limitations, incomplete newer-speed translation, 1000Base-X/T bit meaning confusion, and using fixed BMCR encoding for unsupported speeds.

## Test Signals
Ettool advertisement round trips, ioctl access, autoneg restart, negotiated duplex, pause matrices, GMII detection, fixed BMCR encodings, and PHY drivers using both legacy and modern APIs.
