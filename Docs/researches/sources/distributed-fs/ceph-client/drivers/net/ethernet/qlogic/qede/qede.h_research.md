# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede.h

## Purpose
`qede.h` is the central private header for the QEDE network driver. It defines device state, statistics, queue structures, fastpath layout, VLAN/RSS/XDP/RDMA/PTP fields, feature flags, constants, and cross-file function prototypes used by the QEDE main, fastpath, filter, ethtool, DCB, PTP, and RDMA modules.

## Important APIs, Types, And Functions
Key structures are `struct qede_dev`, `struct qede_fastpath`, `struct qede_rx_queue`, `struct qede_tx_queue`, `struct qede_stats`, `struct qede_vlan`, `struct qede_rdma_dev`, `struct qede_coalesce`, and `struct qede_reload_args`. Important macros derive queue counts and queue indexes, including `QEDE_RSS_COUNT()`, `QEDE_TSS_COUNT()`, `QEDE_RX_QUEUE_IDX()`, `QEDE_TXQ_*` mapping helpers, `QEDE_QUEUE_CNT()`, and chip checks `QEDE_IS_BB()`/`QEDE_IS_AH()`. It declares externally implemented operations such as datapath transmit/poll, XDP, VLAN/filter configuration, RSS filling, ethtool setup, reload, MTU change, coalescing, aRFS, flower filters, and DCB hook installation.

## Control Flow
The header does not execute logic directly, but it defines the state transitions and call contracts shared by implementation files. `enum QEDE_STATE` distinguishes closed, open, and recovery states protected by `qede_lock`. `qede_reload_args` carries small mutation callbacks into reload flows so ethtool, MTU, feature, and XDP changes can update state at the correct point. Queue mapping macros convert between netdev TX queue IDs, fastpath IDs, traffic classes, and XDP queue IDs.

## State, Persistence, And Dependencies
`struct qede_dev` is the persistent per-netdev state: QED core device and ops pointers, netdev/pci/devlink objects, debug settings, flags, device info, fastpath arrays, requested and active queue counts, interrupt info, lock-protected state, RX buffer sizing, stats, RSS indirection/key/caps initialization bits, VLAN list and accept-any-VLAN state, delayed slowpath and periodic work, tunnel ports, aRFS state, WoL, RDMA, XDP program pointer, error/recovery flags, dump command state, and stats coalescing controls. Queue state persists DMA rings, producer/consumer indexes, handles passed to QED, NAPI status blocks, XDP metadata, and per-queue counters. Dependencies include Linux networking, workqueue, interrupt, BPF/XDP, TC flower, QED public interfaces, QED chain/HSi definitions, and optional CPU rmap/DCB/RDMA support.

## Integration Points
Every QEDE implementation file includes this header. The QED core driver provides hardware operations through `struct qed_eth_ops` and common ops; Linux netdev, ethtool, DCBNL, XDP, TC flower, VLAN, RFS, and PTP subsystems call into functions declared here. VF-specific behavior is visible through `QEDE_FLAGS_IS_VF` and `IS_VF()`, which ethtool and filter paths use to restrict PF-only stats or operations.

## Risks
The header concentrates ownership of many shared fields, so changes to queue counts, RSS initialization, feature flags, or reload callbacks can affect multiple subsystems. Queue index macros assume consistent `fp_num_rx`, `fp_num_tx`, `num_queues`, and `dev_info.num_tc` values. Statistics arrays in `qede_ethtool.c` use offsets into structs defined here, so struct field removal/renaming must update those arrays. Locking comments matter: `state` is protected by `qede_lock`, stats by `stats_lock`, and aRFS has its own spinlock. XDP and GRO_HW interactions depend on `xdp_prog` and MTU constraints being kept coherent.

## Test Signals
Build all optional configurations, run netdev open/close/reload paths, change queue/channel counts, enable XDP and GRO_HW, add/remove VLANs, exercise RSS indirection updates, collect ethtool stats, run per-queue coalescing, validate TX queue mapping under multiple traffic classes, and test VF versus PF behavior.
