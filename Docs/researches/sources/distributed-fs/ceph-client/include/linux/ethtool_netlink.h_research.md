# sources/distributed-fs/ceph-client/include/linux/ethtool_netlink.h

Purpose: kernel helpers for ethtool generic-netlink integration, especially cable-test event reporting and aggregate stats.

Important APIs/types/functions: link-mode mask word count, pause stat count, multicast group enum, cable test allocation/result/fault/amplitude/pulse/step helpers, aggregate MAC/PHY/control/pause/RMON stat helpers, `ethtool_dev_mm_supported()`, `ethnl_pse_send_ntf()`, and disabled stubs.

Control flow: PHY drivers start a cable test, allocate netlink state, emit result/fault/step events, and signal finish. Etntool netlink code aggregates stats from device callbacks for user replies. Without `CONFIG_ETHTOOL_NETLINK`, helpers return `-EOPNOTSUPP` or no-op.

State/persistence: transient cable-test state and netlink notifications; aggregate stats are snapshots.

Dependencies/integration: generic netlink family, PHY devices, netdev ethtool ops, UAPI ethtool netlink generated constants, PSE notifications.

Risks/test signals: risks are emitting events without allocation, config-off behavior, source-index mismatches in cable pairs, and stats aggregation double-counting. Test cable test lifecycle, netlink multicast listeners, config-off callers, MAC Merge support reporting, and stat aggregation with partial driver callbacks.
