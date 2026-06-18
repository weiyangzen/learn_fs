<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio.h -->
# sources/distributed-fs/ceph-client/include/linux/mdio.h

## Purpose
This header is the central Linux MDIO interface for generic MDIO devices, MDIO drivers, Clause 22/45 bus operations, and ethtool/linkmode translation helpers.

## Important APIs, types, and functions
It defines `enum mdio_mutex_lock_class`, `struct mdio_device`, `struct mdio_driver_common`, `struct mdio_driver`, and `struct mdio_if_info`. Device APIs include create/register/remove/reset, get/put, and driver register/unregister. Bus APIs include locked and unlocked Clause 22 helpers, Clause 45 helpers, modify/modify_changed variants, and `mdiodev_*` wrappers. Link helpers translate EEE, 10GBASE-T, BASE-T1, 10BASE-T1, and Clause 73 advertisement/status bits between MDIO registers and ethtool link modes.

## Control flow
MDIO bus providers register `mii_bus` instances; devices are created at addresses 0-31 and matched to `mdio_driver` instances. Callers use `mdiobus_*` functions when they need bus-level locking and `__mdiobus_*` under existing locks. Clause 45 helpers include device address selection. Ethtool helpers map raw MMD and AN register bits to userspace-visible link capabilities.

## State and persistence
`struct mdio_device` stores bus address, reset GPIO/control, delays, flags, and callbacks. PHY/MDIO register state persists in hardware; driver data persists through the device model until remove.

## Dependencies and integration points
It depends on UAPI MDIO constants, bitfield helpers, module device tables, netdevice and ethtool types, GPIO descriptors, reset controls, and phylib. It integrates MAC drivers, PHY drivers, PCS devices, and ethtool.

## Risks and test signals
Risks include using unlocked helpers without holding the bus lock, Clause 45 ID encoding mistakes, reset timing bugs, linkmode translation omissions, nested MDIO lock-class misuse, and read-modify-write races. Test C22/C45 reads and writes, nested and muxed buses, reset GPIO/control sequencing, EEE and BASE-T1 ethtool conversion, device removal, and modify_changed return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio.h -->
