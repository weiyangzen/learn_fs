# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_port.c

## Purpose
Wraps mlx4 firmware commands for Ethernet port filtering, link query, and statistics extraction. It updates active VLAN filters, decodes port link state/speed/autoneg/transceiver data, folds software ring counters into netdev stats, and translates firmware Ethernet/PFC/PF/PHY counters into Linux-visible stats structures.

## Important APIs, Types, and Functions
The file exports `mlx4_SET_VLAN_FLTR`, `mlx4_en_QUERY_PORT`, `mlx4_en_fold_software_stats`, and `mlx4_en_DUMP_ETH_STATS`. The helper `en_stats_adder` sums priority-specific big-endian counters in `struct mlx4_en_stat_out_mbox`. Firmware mailbox structures come from `en_port.h`; software destination structs are `net_device_stats`, `mlx4_en_port_stats`, `mlx4_en_packet_stats`, `mlx4_en_phy_stats`, `mlx4_en_flow_stats`, and `mlx4_counter`.

## Control Flow
`mlx4_SET_VLAN_FLTR` allocates a command mailbox, packs `priv->active_vlans` into 128 big-endian 32-bit entries in reverse hardware order, sends `MLX4_CMD_SET_VLAN_FLTR`, and frees the mailbox. `mlx4_en_QUERY_PORT` sends `MLX4_CMD_QUERY_PORT`, then decodes link-up, speed, autoneg, ANC/ANE flags, and transceiver into `priv->port_state`. `mlx4_en_DUMP_ETH_STATS` allocates normal and flow-control mailboxes, dumps Ethernet stats, optionally reads default counter stats and flow-control stats, locks `stats_lock`, folds software counters, resets aggregate software fields, sums per-ring stats, updates Linux netdev stats, packet stats, PF stats, per-priority flow stats, non-PFC flow stats, and PHY stats, then frees mailboxes.

## State and Persistence Behavior
The file updates in-memory netdev and private stats snapshots. `reset` in `mlx4_en_DUMP_ETH_STATS` asks firmware to clear hardware counters after dumping. VLAN filters and port query state are firmware-backed; active VLAN membership itself is kept in `priv->active_vlans` by netdev VLAN callbacks. Stats are guarded by `priv->stats_lock`, while comments note that port query is called from already synchronized ethtool context.

## Dependencies and Integration Points
Depends on Linux VLAN helpers, netdevice stats, mlx4 command mailbox APIs, default counter APIs, and capability flags such as `FLOWSTATS_EN`. It integrates with `en_netdev.c` for VLAN add/remove, stats work, open stat clearing, and link updates, and with `en_ethtool.c` for statistics display and link settings.

## Risks
The stats mailbox layout is ABI-sensitive and uses many big-endian fields. Stats string order in ethtool must match the exact struct write order here. Flow-control mailbox memory is initialized to all `0xff` when unsupported, so consumers must tolerate invalid values. Software stats are skipped for master mode and inactive ports; changing that policy can double count PF/port counters. VLAN bit packing order is hardware-specific.

## Test Signals
Validate VLAN filter programming with sparse and dense VLAN sets, link query for all supported speed encodings and link-down state, stats dump/reset, slave/master/non-master stat differences, flow-control counters with and without `FLOWSTATS_EN`, software RX/TX counter folding under traffic, dropped/error counter mapping, and ethtool stats count/order consistency.
