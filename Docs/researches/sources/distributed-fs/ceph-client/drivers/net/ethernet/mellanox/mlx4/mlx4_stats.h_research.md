# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/mlx4_stats.h

## Purpose

`mlx4_stats.h` defines the software statistics schema used by the mlx4 Ethernet driver. It groups packet, PF counter, port software, XDP, PHY, and flow-control pause statistics and defines the count/index macros used to expose those values through ethtool and related netdev statistic paths.

## Important APIs, Types, And Functions

The header defines `NUM_PRIORITIES` as nine packet-priority buckets, including an extra no-VLAN bucket, and `MLX4_NUM_PRIORITIES` as the eight hardware traffic priorities used by flow-control stats. `mlx4_en_pkt_stats` stores multicast/broadcast/jabber/range-error counters plus RX/TX per-priority frame/byte pairs. `mlx4_en_counter_stats` stores PF-level packets and bytes. `mlx4_en_port_stats` stores software-maintained TSO, queue, timeout, allocation, checksum, and transmit helper counters. `mlx4_en_xdp_stats` stores XDP drop/redirect/redirect-fail/TX/TX-full counters. `mlx4_en_phy_stats` stores physical packets and bytes.

`mlx4_en_flow_stats_rx`, `mlx4_en_flow_stats_tx`, and `mlx4_en_stat_out_flow_control_mbox` describe pause-frame, pause-duration, and pause-transition counters. `MLX4_DUMP_ETH_STATS_FLOW_CONTROL` is the command modifier bit used to request flow-control stats from firmware. Count macros such as `NUM_PKT_STATS`, `NUM_PF_STATS`, `NUM_PORT_STATS`, `NUM_XDP_STATS`, `NUM_PHY_STATS`, `NUM_FLOW_STATS`, and `NUM_ALL_STATS` provide ethtool iteration bounds. `FLOW_PRIORITY_STATS_IDX_RX_FRAMES` and `FLOW_PRIORITY_STATS_IDX_TX_FRAMES` identify offsets in the flattened stat vector, and `MLX4_FIND_NETDEV_STAT()` maps a `struct net_device_stats` member to its index.

## Control Flow Role

The file has no executable logic. Its structs are embedded in `struct mlx4_en_priv`, filled by paths such as `mlx4_en_DUMP_ETH_STATS()` and software stat folding, selected by `mlx4_en_set_stats_bitmap()`, and flattened by ethtool getters. Firmware flow-control mailbox data is read in big-endian form and copied into the software RX/TX flow stat structs.

## State And Persistence Behavior

These counters are runtime statistics. They are reset on netdev reset/port restart paths, refreshed from firmware dump commands, or accumulated from ring software counters. Widths are mixed: many software-facing counters use `unsigned long`, while flow-control counters use `u64` and firmware mailbox fields use `__be64`. The schema relies on strict ordering because ethtool string and data paths cast these structs to linear arrays.

## Dependencies And Integration Points

The header is included by `mlx4_en.h` and consumed by Ethernet netdev, port, and ethtool code. It depends on kernel definitions for `__be64`, `offsetof`, and `struct net_device_stats` through includers. Firmware integration occurs through `MLX4_CMD_DUMP_ETH_STATS` users that fill `mlx4_en_stat_out_flow_control_mbox`.

## Risks

The main risk is count/order drift. Adding, removing, or reordering fields without updating the associated `NUM_*` macros, ethtool strings, bitmap offsets, and extraction loops will mislabel or truncate statistics. The two priority counts are intentionally different (`NUM_PRIORITIES` 9 versus `MLX4_NUM_PRIORITIES` 8); confusing them can overrun arrays or omit no-VLAN packet stats. Mixed `unsigned long`, `u64`, and big-endian mailbox fields require care on 32-bit builds and firmware conversion paths.

## Test Signals

Check ethtool stats count and names against `NUM_ALL_STATS`, run firmware stats dump with and without flow-control stats, verify PFC priority stats when pause priority flags are enabled, exercise XDP drop/redirect/TX paths, trigger queue stop/wake and TX timeout counters, and validate 32-bit builds or sparse/endian checking for mailbox conversion.
