# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_ethtool.c

## Purpose
`ipoib_ethtool.c` supplies the driver's ethtool operations: driver/firmware identity, RX coalescing configuration, selected netdev statistics, link state, and link speed reporting derived from the active InfiniBand port attributes.

## Important APIs, Types, And Functions
`struct ipoib_stats` maps ethtool stat names to `struct rtnl_link_stats64` offsets. `ipoib_get_drvinfo()` fills firmware, bus, and driver strings. `ipoib_get_coalesce()` and `ipoib_set_coalesce()` read/write `priv->ethtool` and call `rdma_set_cq_moderation()` for the receive CQ. `ipoib_get_ethtool_stats()`, `ipoib_get_strings()`, and `ipoib_get_sset_count()` expose eight global stats. `ipoib_get_link_ksettings()` maps InfiniBand active speed and width into ethtool speed/duplex fields. `ipoib_set_ethtool_ops()` installs the static ops table.

## Control Flow And State
Coalescing state is persisted only in `priv->ethtool` for the lifetime of the netdev and is reapplied by user request, not stored externally. `set_coalesce` rejects values beyond `u16`, tolerates `-EOPNOTSUPP` from devices that cannot moderate CQs, and otherwise records the requested values. Link settings return unknown speed/duplex if carrier is down; otherwise they query the RDMA port and multiply lane speed by active width.

## Dependencies And Integration Points
The file depends on Linux ethtool/netdevice APIs and RDMA helpers (`ib_get_device_fw_str`, `ib_query_port`, `ib_width_enum_to_int`, `rdma_set_cq_moderation`). It is wired from `ipoib_setup_common()` in `ipoib_main.c`, and uses `ipoib_priv()` plus `priv->ca`, `priv->port`, and `priv->recv_cq` from the shared device state.

## Risks And Test Signals
Notable risks are offset-based stat reads from a legacy `dev->stats` view, hardware that reports unsupported speed/width values, and coalescing devices that partially accept moderation parameters. Test signals include `ethtool -i`, `ethtool -c/-C`, `ethtool -S`, carrier-down reporting, active speed/width changes, and devices returning `-EOPNOTSUPP` from CQ moderation.
