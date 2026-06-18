# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_ethtool.h

Purpose: Declares the single helper that attaches Ionic ethtool operations to a netdev.

Important APIs/types/functions: `ionic_ethtool_set_ops(struct net_device *netdev)` assigns the static `ionic_ethtool_ops` table in `ionic_ethtool.c`.

Control flow: LIF/netdev allocation calls this during netdev setup, before registration.

State and dependencies: No persistent state beyond the netdev's `ethtool_ops` pointer. Depends on netdev definitions through including files.

Risks and test signals: Build coverage should ensure the LIF code includes and calls this helper. Runtime `ethtool -i`, stats, rings, channels, RSS, and timestamp queries validate that the ops pointer was installed before netdev registration.
