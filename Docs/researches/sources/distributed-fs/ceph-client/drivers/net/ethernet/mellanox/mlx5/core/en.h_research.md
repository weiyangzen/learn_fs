# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en.h

## Purpose

`en.h` is the central mlx5e Ethernet driver contract. It defines datapath/control structures for channels, RQs, SQs, CQs, XDP/AF_XDP, PTP, flow steering, DCB, health reporters, profile callbacks, feature flags, sizing constants, and public function prototypes used across the mlx5e Ethernet implementation.

## Important APIs, Types, and Functions

Major definitions include:

- Sizing/feature constants for MTU conversion, MPWQE/UMR limits, queue sizes, CQ moderation defaults, channel counts, and TX recovery intervals.
- `struct mlx5e_params` for active channel/netdev configuration: queue sizes, RQ type, channel count, mqprio/DCB, moderation, packet merge, inline mode, VLAN/FCS, DIM, XDP, XSK, MTU, PTP RX, and terminate lkey.
- Datapath structures: `mlx5e_cq`, `mlx5e_txqsq`, `mlx5e_xdpsq`, `mlx5e_icosq`, `mlx5e_rq`, `mlx5e_channel`, and `mlx5e_channels`.
- State enums for RQ, SQ, channel, private interface, profile features, packet merge mode, and devcom events.
- `struct mlx5e_priv`, the primary netdev private state with channel maps, RX resources, flow steering, work items, stats, reporters, feature modules, DCB/XSK/QoS state, debugfs root, and devcom.
- `struct mlx5e_profile`, the callback table for NIC/profile-specific init, cleanup, enable/disable, stats, carrier, TIS, and feature behavior.
- Prototypes for open/close, channel switching, queue creation/destruction, moderation, stats, ethtool, VLAN, XDP, mkey/TIS, flow steering, health, and netdev profile management.

## Control Flow

This header defines the common lifecycle shape but implements little behavior. Typical mlx5e flows allocate `mlx5e_priv`, build `mlx5e_params`, create device resources, open channels, activate queues, attach netdev, and later safe-switch or reopen channels under `state_lock`. Channel structures aggregate one RQ, per-TC SQs, internal control SQs, XDP SQs, optional AF_XDP RQ/SQ, NAPI, and queue metadata.

Datapath handlers are function pointers selected from params and feature state. Health/reporting paths use the same structure fields for diagnostics and recovery. Profile callbacks allow NIC, representor, and other profiles to share core open/close/channel machinery while customizing resources and features.

## State and Persistence Behavior

`struct mlx5e_priv` persists for the netdev lifetime and owns long-lived resources such as flow steering, RX resources, workqueue, stats, health reporters, XSK pools, DCB state, QoS state, feature modules, and channel arrays. `struct mlx5e_channels` and individual channel/queue objects persist while the netdev is open or channels are allocated. Queue producer/consumer indexes, DIM state, page pools, XDP program pointers, CQ state, and hardware object IDs are mutable datapath state.

Concurrency is split between datapath cacheline-aligned fields, `state_lock`, netdev/RTNL locking in callers, RCU for selected queue mappings, spinlocks for ICOSQ synchronization, and workqueue recovery paths.

## Dependencies and Integration Points

The header connects nearly every mlx5e module: flow steering, RX resources, DCB, QoS, PTP, TLS/IPsec/PSP/MACsec optional accelerators, XDP/AF_XDP, devlink health reporters, ethtool, netdev ops, mlx5 core objects, work queues, page pools, DIM, switchdev, and Hyper-V VHCA stats.

## Risks and Edge Cases

- Many enum comments require keeping reporter string arrays in other files synchronized.
- Several size constants are tied to hardware field widths and static array sizing; changing them can silently break WQE layout assumptions.
- `mlx5e_get_max_num_channels()` restricts kdump kernels to one channel; tests must account for crash-kernel behavior.
- `mlx5e_get_max_sq_aligned_wqebbs()` prevents DS field overflow by reducing the maximum; changes to WQE sizing must preserve this.
- Large shared structures are sensitive to cacheline layout and lock ownership. Adding fields in datapath areas can affect performance.
- Many prototypes assume callers hold `state_lock`, RTNL, netdev lock, or channel inactive state; misuse can race with queue teardown/reopen.

## Test Signals

Full mlx5e build matrix with XDP, AF_XDP, DCB, PTP, TLS, IPsec, PSP, MACsec, ARFS/RXNFC, QoS, and Hyper-V options. Runtime coverage for netdev open/close, channel count changes, MTU changes, coalesce changes, XDP attach/detach, XSK bind/unbind, health recovery, and safe channel reopen. Static checks for enum/string synchronization and WQE size assumptions.
