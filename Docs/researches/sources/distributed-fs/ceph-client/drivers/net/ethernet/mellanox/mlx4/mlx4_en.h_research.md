# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/mlx4_en.h

## Purpose

`mlx4_en.h` is the private Ethernet driver header for mlx4. It defines mlx4 Ethernet constants, descriptor and ring structures, CQ/RX/TX state, per-port profiles, device-level Ethernet state, multicast and MAC bookkeeping, DCB/XDP/PTP/statistics integration, and function prototypes shared by the mlx4 Ethernet implementation files. It connects the mlx4 core device API to Linux `net_device`, NAPI, ethtool, XDP, page-pool, PTP, hardware timestamping, RSS, and DCB features.

## Important APIs, Types, And Functions

The header defines ring sizing, allocation, interrupt moderation, bounce-buffer, checksum, loopback, pause, queue, and MTU constants such as `MAX_RX_RINGS`, `MAX_TX_RINGS`, `TXBB_SIZE`, `MLX4_EN_ALLOC_SIZE`, `MLX4_EN_MAX_RX_FRAGS`, `MLX4_EN_DEF_RX_RING_SIZE`, coalescing thresholds, `MLX4_EN_EFF_MTU()`, and self-test loopback limits. It defines descriptor state in `mlx4_en_tx_info`, `mlx4_en_tx_desc`, `mlx4_en_rx_desc`, `mlx4_en_tx_ring`, `mlx4_en_rx_ring`, and `mlx4_en_cq`.

Configuration and lifetime state is captured by `mlx4_en_port_profile`, `mlx4_en_profile`, `mlx4_en_dev`, `mlx4_en_rss_map`, `mlx4_en_port_state`, `mlx4_en_mc_list`, `mlx4_en_frag_info`, `mlx4_en_stats_bitmap`, `mlx4_en_priv`, `mlx4_mac_entry`, and optional DCB/RFS structures. `mlx4_en_get_cqe()` is an inline CQE accessor parameterized by CQE size.

The prototypes cover netdev creation/destruction, port start/stop, CQ/TX/RX ring creation and activation, NAPI poll handlers, TX submission and completion, XDP TX/recycle paths, RSS steering, drop QP handling, multicast/VLAN filter commands, stats dumping and folding, traffic-class setup, self-test, PTP timestamp conversion, hardware timestamp reset, XDP metadata helpers, and netdev notifier handling.

## Control Flow Role

This header does not implement control flow, but it defines the data contracts used by `en_main.c`, `en_netdev.c`, `en_rx.c`, `en_tx.c`, `en_cq.c`, `en_port.c`, `en_ethtool.c`, and related files. A typical Ethernet bring-up allocates `mlx4_en_dev`, creates one `net_device`/`mlx4_en_priv` per active Ethernet port, configures the profile, creates CQs and TX/RX rings, activates QPs, configures RSS steering and multicast filters, starts NAPI and service/stat delayed work, and later tears those resources down through the paired prototypes. Fast-path TX/RX code reads ring fields laid out here, while slow-path ethtool, DCB, timestamp, and stats code reads `mlx4_en_priv` aggregates.

## State And Persistence Behavior

All state is runtime kernel memory. `mlx4_en_dev` is device-wide and tracks core device pointer, port netdevs, workqueue, UAR/MR/PD resources, PTP clock/timecounter state, notifier blocks, and profile. `mlx4_en_priv` is per netdev/port and owns active VLAN bitmap, link state, ring arrays, CQ arrays, RSS map, work items, counters/stats, multicast lists, MAC hash, tunnel registration, VXLAN port, DCB state, RFS filters, RSS key/hash function, XDP programs on RX rings, and flags. The header deliberately separates device-wide resources from per-port resources, which matters during port restart, netdev close/open, and reload.

Concurrency assumptions are embedded in the layout: TX completion and TX submission fields are separated by cacheline alignment; RX XDP programs are RCU pointers; stats use `stats_lock` and a stats bitmap mutex; UAR access has `uar_lock`; work items handle RX mode changes, restarts, link state, stats, and service tasks. Many counters are `unsigned long` software aggregates folded from per-ring or firmware stats.

## Dependencies And Integration Points

The file depends on Linux networking, VLAN, timestamping, CPU rmap, PTP clock, IRQ, XDP, page-pool-adjacent data structures, optional DCB and RFS configs, and public mlx4 QP/CQ/SRQ/doorbell/cmd headers. It includes `en_port.h` for firmware Ethernet stats mailbox layouts and `mlx4_stats.h` for software stat structs and count constants. Its prototypes are the integration surface between mlx4 core exported APIs and Linux netdev/ethtool/XDP/PTP subsystems.

## Risks

Fast-path struct layout is performance-sensitive; moving fields can increase cacheline sharing or break assumptions in TX/RX code. Ring size constants must remain compatible with hardware descriptor sizes, page allocation, BQL, XDP, and firmware limits. Stats count macros from `mlx4_stats.h` must stay aligned with ethtool string/data iteration. RCU and workqueue fields require correct teardown ordering to avoid use-after-free during close, unregister, or reset. XDP and timestamp fields interact with RX buffer layout and CQE size selected by core caps, so core `main.c` changes to CQE stride/size can affect this header's users.

## Test Signals

Relevant tests include Ethernet netdev open/close, MTU changes, ring resize via ethtool, interrupt moderation updates, RSS indirection changes, multicast/promisc changes, VLAN filtering, XDP attach/drop/redirect/TX, PTP timestamping, hardware timestamp config reset, DCB/PFC where enabled, suspend/resume or devlink reload with netdevs present, and ethtool stats string/count consistency against `NUM_ALL_STATS`.
