# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_net.c

## Purpose
Main Linux glue for standalone Ocelot ports. It connects netdev, switchdev, tc, devlink, phylink, FDMA, PTP, stats, VLAN/FDB/MDB/MRP, bridge, and LAG events to the common Ocelot switch library.

## Important APIs/types/functions
Provides `ocelot_devlink_ops`, notifier blocks, `ocelot_port_devlink_init/teardown`, `ocelot_setup_tc_cls_flower`, `ocelot_port_to_netdev`, `ocelot_netdev_to_port`, `ocelot_probe_port`, and `ocelot_release_port`. Netdev ops include open/stop/xmit/MTU/RX mode/MAC/FDB/VLAN/features/tc/ioctl/hwtstamp; ethtool ops provide stats/link/timestamp views.

## Control flow, state, persistence
Probe allocates a netdev with private port state, assigns ops/features, learns the port MAC, initializes hardware, creates phylink, optionally hooks FDMA NAPI, links devlink port, and registers the netdev. Xmit chooses FDMA through static key or the injection-group path and integrates PTP rewrite/timestamping. TC block callbacks offload matchall police/mirror and flower. Switchdev/notifier flows offload bridge/LAG membership, sync STP/ageing/VLAN/flags, manage bridge numbers, and update LAG active state. State lives in `priv->tc`, `ocelot_port`, bridge bitmap, phylink, workqueue MAC actions, and hardware tables.

## Dependencies and integration
Integrates all neighboring Ocelot files: devlink, FDMA, flower, policing, PTP, stats, MRP, plus Linux bridge/switchdev/tc/phylink/PHY APIs.

## Risks and test signals
Risks include bridge/LAG notifier ordering, offload counter mismatches, multicast workqueue vs teardown, and ignored FDMA TX busy. Test probe/remove unwind, bridge/LAG join/leave, VLAN/FDB/MDB, tc police/mirror/flower, PTP hwtstamp, FDMA/non-FDMA TX, and ethtool stats.
