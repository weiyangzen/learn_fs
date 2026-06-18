# sources/distributed-fs/ceph-client/include/linux/ethtool.h

Purpose: in-kernel ethtool driver API for link settings, RSS, rings, coalescing, statistics, module EEPROM/power, timestamping, FEC/RMON, MAC Merge, PHY operations, and generic helpers.

Important APIs/types/functions: `struct ethtool_ops`, `struct ethtool_phy_ops`, RSS context/parameter structures, `ethtool_link_ksettings`, link mode bitmap macros, coalesce capability masks, many standardized stats structures, MAC Merge state/config/stats and software verification helpers, `kernel_ethtool_ts_info`, `ethtool_check_ops()`, RX flow rule helpers, virtual-device helpers, per-netdev ethtool state, `ethtool_op_get_link()`, `ethtool_op_get_ts_info()`, string helpers, and forced-speed maps.

Control flow: ethtool ioctl/netlink core validates requests, takes RTNL, calls optional driver callbacks, aggregates or initializes standardized stats, manages RSS contexts in per-netdev state, and handles MAC Merge verification through timer/event helpers.

State/persistence: driver/device settings include link modes, RSS tables/keys/contexts, WOL, coalescing, rings, module power, timestamping, and MAC Merge state. Most is hardware/runtime state; some devices persist firmware/module settings.

Dependencies/integration: UAPI ethtool/netlink, netdev, PHY library, netlink extack, timers, xarray, PTP/hwtstamp, flow rules, module EEPROM, IEEE stats.

Risks/test signals: risks are optional callback NULL handling, incorrect supported_* masks, RSS context lifetime/resizing, stats fields not initialized to `ETHTOOL_STAT_NOT_SET`, RTNL/locking violations, and MAC Merge timer races. Test ioctl and netlink paths, driver callback validation, RSS create/modify/delete, stats omission, module EEPROM page access, PHC timestamping, FEC/RMON, and MAC Merge state transitions.
