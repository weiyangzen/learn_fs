# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib.h

## Purpose
`ipoib.h` is the shared contract for the IP-over-InfiniBand driver. It defines the packet header layout, device-private state, path/multicast/neighbour caches, connected-mode state, constants for queue sizing and MTU calculations, and cross-file function prototypes used by the netdev, RDMA verbs, multicast, CM, VLAN, netlink, ethtool, and debugfs implementations.

## Important APIs, Types, And Functions
Core constants include `IPOIB_HARD_LEN`, `IPOIB_UD_HEAD_SIZE`, UD/CM MTU and ring sizes, queue limits, work-completion batch sizes, multicast queue limits, and flag bit indices. `IPOIB_OP_RECV` and `IPOIB_OP_CM` tag work-request IDs so CQ polling can dispatch to UD or connected-mode handlers. `IPOIB_QPN()` extracts the 24-bit queue-pair number from an InfiniBand link-layer address.

Important types are `struct ipoib_dev_priv`, `struct ipoib_path`, `struct ipoib_mcast`, `struct ipoib_neigh`, `struct ipoib_ah`, `struct ipoib_rx_buf`, `struct ipoib_tx_buf`, and the connected-mode `struct ipoib_cm_rx`, `struct ipoib_cm_tx`, and `struct ipoib_cm_dev_priv`. `ipoib_priv()` unwraps the RDMA netdev private pointer. `skb_add_pseudo_hdr()` adjusts received packets so the Linux networking stack sees the expected pseudo-header shape.

## Control Flow And State
The header encodes the driver state model. `ipoib_dev_priv` owns runtime device state: InfiniBand device/port/P_Key/GID, QP/CQ/PD resources, NAPI instances, TX/RX rings, path and multicast rbtrees, neighbour RCU hash table, child interfaces, and multiple ordered/delayed work items. Flags such as `IPOIB_FLAG_ADMIN_UP`, `IPOIB_FLAG_OPER_UP`, `IPOIB_PKEY_ASSIGNED`, `IPOIB_FLAG_ADMIN_CM`, and `IPOIB_FLAG_DEV_ADDR_SET` gate open/close, multicast joins, path use, connected mode, and address control.

Connected mode is conditionally compiled under `CONFIG_INFINIBAND_IPOIB_CM`; otherwise the header provides no-op stubs so the rest of the driver builds in datagram-only mode. Multicast state uses flags for found/send-only/busy/attached, with comments documenting the join-state interpretation.

## Dependencies And Integration Points
The file depends on Linux netdevice/skbuff/workqueue/kref/mutex/RCU facilities, neighbour and qdisc infrastructure, and RDMA core headers (`ib_verbs`, `ib_pack`, `ib_sa`). It declares integration points exported among implementation files: NAPI poll handlers, RDMA event handling, multicast join/flush/restart APIs, path lookup/flush APIs, verbs setup, VLAN creation/deletion, netlink registration, sysfs mode and umcast setters, and ethtool setup.

## Risks And Test Signals
Risk concentrates in lifetime and locking contracts: `priv->lock` nests inside TX locking, RCU protects the neighbour hash, AHs are kref-managed and reaped after sends pass `last_send`, and workqueue ordering assumptions are critical. Tests or review signals should cover builds with and without `CONFIG_INFINIBAND_IPOIB_CM` and `CONFIG_INFINIBAND_IPOIB_DEBUG`, queue-size clamping, RX/TX completion dispatch by WR ID flags, P_Key/GID changes, child interface operations, multicast joins/leaves, and CM mode switching.
