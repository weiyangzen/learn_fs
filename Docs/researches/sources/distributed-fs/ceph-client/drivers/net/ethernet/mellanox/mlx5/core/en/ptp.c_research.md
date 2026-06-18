# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/ptp.c

Purpose: implements the dedicated mlx5e PTP TX/RX channel, hardware timestamp reconciliation, PTP flow-steering rules, and PTP queue lifecycle.

Important APIs/functions: `mlx5e_ptp_open`, `mlx5e_ptp_close`, activate/deactivate, `mlx5e_ptp_get_rqn`, RX flow-steering allocation/free/manage, metadata tracking, and skb timestamp callback handling. Internal functions manage TX SQs, timestamp CQs, metadata freelists/maps, NAPI polling, unhealthy recovery, and PTP RX rules.

Control flow: open sets TX/RX state from params, adds NAPI, builds PTP-specific SQ/RQ params, opens TX CQs and timestamp CQs per TC, opens PTP SQs with `ts_cqe_to_dest_cqn`, and optionally opens a cyclic PTP RQ. TX packets needing PTP use metadata ids; normal TX CQ supplies a CQE timestamp while the timestamp CQ supplies a port timestamp. Once both are present, the code checks their delta and reports the port timestamp, or marks the SQ unhealthy on large divergence. RX activation installs rules for UDP v4/v6 PTP event port and L2 `ETH_P_1588`.

State and persistence: `struct mlx5e_ptp` holds data path queues, NAPI, state bits, and channel metadata. Each `mlx5e_ptpsq` owns a metadata freelist, skb map, pending timestamp CQE list, CQ stats, and recovery work. Flow-steering state is stored in `struct mlx5e_ptp_fs`.

Dependencies and integration: depends on mlx5e TX/RX queue creation, CQ polling, health reporter, flow-steering redirect helpers, hwtstamp config, PTP classifier constants, and netdev queue/NAPI APIs.

Risks: timestamp delivery uses two asynchronous CQ streams; late or missing port CQEs can exhaust metadata and trigger recovery. The skb control block is reused and must be initialized before timestamp tracking. Flow-steering set/unset protects against invalid add/remove while channels are open.

Test signals: PTP TX over L2 and UDP v4/v6, timestamp delta aborts, late/lost CQEs, metadata exhaustion recovery, RX rule activation/deactivation, open rollback at each queue stage, and multi-TC PTP TX.
