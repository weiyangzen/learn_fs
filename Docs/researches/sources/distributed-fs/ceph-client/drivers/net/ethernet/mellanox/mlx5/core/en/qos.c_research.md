# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/qos.c

Purpose: connects mlx5 firmware QoS nodes to mlx5e transmit queues for HTB offload and mqprio rate limiting.

Important APIs/functions: `mlx5e_qos_bytes_rate_check`, `mlx5e_qos_max_leaf_nodes`, `mlx5e_qid_from_qos`, QoS SQ open/activate/deactivate/close helpers, all-queue lifecycle helpers, `mlx5e_reset_qdisc`, `mlx5e_htb_setup_tc`, and mqprio rate-limit allocation/init/cleanup/get-node helpers.

Control flow: HTB setup validates unsupported prio/quantum fields, creates/destroys the HTB object, dispatches TC HTB commands to `htb.c`, and returns qids for leaf queue allocation/query. QoS SQ opening allocates per-channel RCU arrays, creates stats storage, opens CQ/SQ with the firmware node id, and publishes the SQ pointer. Activation disables the netdev queue, updates `txq2sq` mappings with a write barrier, and starts the SQ. Deactivation removes mappings before queues are restarted. MQPRIO creates a firmware root and one capped-bandwidth leaf per TC.

State and persistence: stores QoS SQ arrays per channel, stats arrays in `priv`, HTB state in `priv->htb`, and mqprio firmware node ids in `struct mlx5e_mqprio_rl`. Firmware QoS nodes persist until cleanup.

Dependencies and integration: depends on `en/htb.h`, queue builders in `params.c`, mlx5 core QoS commands, TC setup callbacks, RCU state access, and netdev qdisc APIs.

Risks: queue index math changes when PTP SQs or DCB TCs are enabled. `txq2sq` updates rely on barriers and queue stopping. Partial SQ open failures are tolerated but require null checks throughout lifecycle paths.

Test signals: HTB command matrix, channel reopen with existing leaves, PTP enabled qid mapping, RCU/NAPI close synchronization, mqprio max-rate nodes, and SQ open failure injection.
