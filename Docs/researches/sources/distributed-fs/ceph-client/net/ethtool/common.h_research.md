# sources/distributed-fs/ceph-client/net/ethtool/common.h

## Purpose
This header exposes shared ethtool constants, string tables, global operation pointers, and helper prototypes to ethtool ioctl and netlink implementation files.

## Important APIs, Types, And Functions
Important definitions include `ETHTOOL_DEV_FEATURE_WORDS`, `ETHTOOL_LINK_MODE()`, timestamp bit-count macros, and declarations for all shared ethtool string tables. It declares helpers for link status, legacy conversion, channel validation, RSS context allocation/busy checks, RSS hash symmetry checks, ring parameter config, RX ring count, timestamp/PHC lookup, hwtstamp qualifier support, module EEPROM calls, MAC Merge support, and RSS notifications. It also declares global pointers `ethtool_phy_ops` and `ethtool_pse_ops`.

## Control Flow
The header has no runtime control flow. It defines compile-time glue used by consumers to reach implementations in `common.c`, ioctl code, netlink code, PHY/PSE code, and module EEPROM code. The `ethtool_rss_notify()` wrapper becomes a no-op when ethtool netlink is disabled.

## State, Persistence, And Dependencies
The header owns no state, but exposes global ops pointers and functions that mutate netdevice ethtool state. It depends on Linux netdevice and ethtool public headers plus forward declarations for generic netlink and hwtstamp provider descriptors.

## Integration Points
Nearly every file in `net/ethtool` includes this header for common names and validation APIs. It keeps shared helpers out of individual feature files and provides conditional compatibility when netlink support is absent.

## Risks
Changing prototypes or macro semantics can break many ethtool feature handlers. Conditional `ethtool_rss_notify()` behavior must match build configuration so code can call it unconditionally without unresolved symbols. Global ops pointer declarations require careful initialization under the right locks.

## Test Signals
Build tests with and without `CONFIG_ETHTOOL_NETLINK`, plus compile coverage of ioctl, netlink, PHY, PSE, and module EEPROM paths, are the main signals. Runtime signals come from common helper users such as channel SET, RSS notifications, timestamp queries, and module EEPROM access.
