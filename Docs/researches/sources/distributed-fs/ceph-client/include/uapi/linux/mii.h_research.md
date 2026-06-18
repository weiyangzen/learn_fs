# sources/distributed-fs/ceph-client/include/uapi/linux/mii.h

## Purpose
Defines MII/PHY register numbers, bitfields, advertised link modes, link partner ability bits, flow-control bits, MMD access flags, and ioctl payload for PHY register access.

## Important APIs, Types, And Functions
Exports `MII_*` register constants, `BMCR_*`, `BMSR_*`, `ADVERTISE_*`, `LPA_*`, `EXPANSION_*`, `ESTATUS_*`, SGMII encodings, 1000BASE-T control/status bits, `FLOW_CTRL_*`, `MII_MMD_CTRL_*`, and `struct mii_ioctl_data`.

## Control Flow
Networking tools issue SIOCxMII ioctls using `mii_ioctl_data` with PHY id/register number and input/output values. Drivers interpret register bitfields to reset PHYs, start autonegotiation, advertise modes, and report link capabilities.

## State, Persistence, And Dependencies
State lives in PHY hardware registers and driver-managed link state. Dependencies are `linux/types.h` and `linux/ethtool.h`.

## Integration Points
Used by legacy `mii-tool`, ethtool paths, PHY drivers, and network device ioctl handlers.

## Risks
Some bit values are overloaded between twisted-pair and 1000BASE-X contexts. Register accesses can be hardware-specific, and ioctl callers must handle endianness and unsupported registers correctly.

## Test Signals
Validate ioctl read/write round trips on simulated PHYs, reset/autoneg bits, advertisement masks, SGMII speed decode, MMD access modes, and compatibility of `struct mii_ioctl_data`.
