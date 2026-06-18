# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_ethtool.h

## Purpose
`wx_ethtool.h` declares the shared ethtool-facing API implemented by `wx_ethtool.c` for PF and VF WangXun drivers. It is the contract other driver modules use to populate `struct ethtool_ops` tables without duplicating common libwx logic.

## Important APIs, types, and functions
The header exports prototypes for stats, driver info, link settings, WOL, pause configuration, ring parameters, coalescing, channels, RSS indirection and key access, RSS hash field controls, message level, timestamp info, PTP timestamp statistics, and VF ethtool-op installation. It uses kernel ethtool types such as `struct ethtool_link_ksettings`, `struct ethtool_rxfh_param`, `struct ethtool_rxfh_fields`, `struct kernel_ethtool_ts_info`, and `struct ethtool_ts_stats`.

## Control flow and behavior
There is no executable control flow in this header. Its declarations show which common operations are expected to be wired into device-specific PF ethtool ops, and which subset is available to VF devices through `wx_set_ethtool_ops_vf()`.

## State and persistence
The header owns no state. All declared operations act on `struct net_device` and reach driver state through `netdev_priv(netdev)` in the implementation.

## Dependencies and integration points
Consumers must include the appropriate Linux netdevice and ethtool definitions before or alongside this header. It integrates with `wx_hw.h` and `wx_lib.h` indirectly because several declared functions reconfigure RSS tables, EITR registers, or hardware stats.

## Risks and edge cases
Prototype drift between this header and `wx_ethtool.c` would break module builds. Because the header does not include all dependent type headers itself, include ordering in consumers matters. API compatibility also tracks kernel ethtool signatures, especially the newer `kernel_ethtool_*` and `netlink_ext_ack` parameters.

## Test signals
Build coverage is the main signal: all PF/VF drivers including this header should compile without incompatible-pointer warnings when assigning ethtool ops. Runtime smoke tests should verify every op pointer wired by consumers maps to a declared and exported implementation.
