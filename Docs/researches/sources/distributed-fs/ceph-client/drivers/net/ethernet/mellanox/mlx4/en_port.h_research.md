# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_port.h

## Purpose
Defines Ethernet-port firmware ABI structures and constants used by mlx4_en port commands. It describes VLAN filter mailboxes, multicast command modes, hardware link-mode ids, speed encodings, query-port response layout, and the large Ethernet statistics mailbox returned by firmware.

## Important APIs, Types, and Functions
Important constants include promiscuous command shifts, `MLX4_EN_NUM_TC`, `VLAN_FLTR_SIZE`, multicast modes, `MLX4_PROT_MASK`, `MLX4_EN_*_SPEED` encodings, query masks such as `MLX4_EN_LINK_UP_MASK`, and link mode enum values like `MLX4_10GBASE_KR`, `MLX4_40GBASE_CR4`, and `MLX4_56GBASE_SR4`. Main types are `struct mlx4_set_vlan_fltr_mbox`, `enum mlx4_link_mode`, `struct mlx4_en_query_port_context`, and `struct mlx4_en_stat_out_mbox`.

## Control Flow
The header has no executable control flow. Its field layout directly controls how `en_port.c` packs command mailboxes and decodes firmware responses, while `en_ethtool.c` maps `enum mlx4_link_mode` values into ethtool link-mode masks and speeds.

## State and Persistence Behavior
All structures are transient host representations of firmware command mailboxes, but their layout is persistent ABI for driver/firmware communication. The statistics mailbox contains hundreds of big-endian counters grouped by receive/transmit frame size, priority, VLAN/non-VLAN, bytes, totals, drops, FCS/length errors, broadcast/multicast/unicast, and loopback categories.

## Dependencies and Integration Points
Depends on kernel fixed-width and big-endian types provided by including files. It is included by `en_port.c`, `en_netdev.c`, and `en_ethtool.c`. Its link-mode ids must match mlx4 firmware PTYS/query-port definitions, and its stats fields must match the conversion logic in `mlx4_en_DUMP_ETH_STATS` and string definitions in ethtool.

## Risks
This header is ABI-sensitive: changing field order, width, endian type, or enum values can silently corrupt command interpretation. The statistics struct is large and sparsely consumed; adding or reordering fields requires coordinated updates to stats extraction and ethtool string counts. Speed encodings differ from ethtool speed constants, so translation must remain centralized in users.

## Test Signals
Compile coverage for all include users, firmware query-port decoding, PTYS link-mode mapping, VLAN filter mailbox size checks, stats dump parsing, big-endian conversion checks, and static/layout validation against firmware documentation or known hardware counter output are the main signals.
