# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/hv_vhca_stats.c

Purpose: exports per-channel mlx5e RX/TX packet and byte counters to a Hyper-V vHCA statistics agent.

Important APIs/functions: `mlx5e_hv_vhca_stats_create` allocates the backing buffer and registers an `MLX5_HV_VHCA_AGENT_STATS` agent; `mlx5e_hv_vhca_stats_destroy` unregisters it. Internal helpers size the buffer, fill `struct mlx5e_hv_vhca_per_ring_stats`, process control-block commands, and run the delayed stats work.

Control flow: Hyper-V calls the control callback with an update command. A zero command cancels work; `MLX5_HV_VHCA_STATS_UPDATE_ONCE` queues a single immediate write; other commands are interpreted as 100 ms units and requeue periodic work. The work clears the buffer, snapshots `priv->channel_stats`, writes to the vHCA agent, and requeues if a period remains.

State and persistence: stores `stats_agent.buf`, `stats_agent.agent`, `stats_agent.work`, and `stats_agent.delay` in `mlx5e_priv`. The buffer layout is fixed version 1 and sized from `priv->stats_nch`; no persistent storage exists outside the Hyper-V shared agent.

Dependencies and integration: uses `lib/hv_vhca.h`, `lib/hv.h`, `priv->wq`, and channel stats. The header compiles this away unless `CONFIG_PCI_HYPERV_INTERFACE` is enabled.

Risks: stats are sampled without explicit per-counter synchronization and can be transient. Buffer sizing depends on `stats_nch` staying compatible with the registered agent. Failed writes stop the current periodic chain by returning before requeue.

Test signals: Hyper-V-enabled builds, agent create/destroy failures, update-once and periodic control commands, channel-count changes across open/close, and vHCA write error logging.
