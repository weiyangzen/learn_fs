# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rx_res.c

Purpose: Manages all mlx5e receive steering resources for an interface: default and auxiliary RSS contexts, per-channel direct RQTs/TIRs, PTP direct RQT/TIR, packet-merge state, XSK RQ switching, multi-vHCA RQN mapping, and TLS TIR creation.

Important APIs: `mlx5e_rx_res_create()`/`destroy()`, channel activate/deactivate, `mlx5e_rx_res_xsk_update()`, RSS init/destroy/count/index/get/configuration functions, direct/RSS/PTP TIRN and RQTN getters, `mlx5e_rx_res_packet_merge_set_param()`, and `mlx5e_rx_res_tls_tir_create()`.

Control flow: Creation allocates RQN/vHCA arrays, initializes default RSS with TIRs, creates a direct RQT/TIR pair for every max channel, and creates the PTP TIR/RQT. Activation populates `rss_rqns` from regular or XSK channel RQNs, enables all RSS contexts, redirects each direct RQT, and redirects PTP if supported. Deactivation disables RSS and points direct/PTP RQTs back to the drop RQ. XSK updates swap one channel's RQN then re-enable RSS and the direct RQT.

State and persistence: `struct mlx5e_rx_res` owns feature flags, max channel count, drop RQN, packet-merge parameters protected by `rw_semaphore`, RSS context pointers, active RSS RQNs/vHCA IDs, direct channel objects, and PTP object. Hardware RQTs/TIRs persist while the resource exists.

Dependencies and integration: Uses `channels.h` for RQNs, `params.h`, RSS, RQT, TIR builders, TLS TIR builder mode, packet merge, PTP feature flags, and multi-vHCA support. Reporters and flow-steering code query its TIR/RQTN getters.

Risks: Activation iterates `chs->num` for RSS but only `mlx5e_channels_get_num()` for direct activation, so channel-count semantics must remain consistent. Packet merge modification can partially fail across RSS and direct TIRs. RSS destroy can fail when refcounts remain and logs warnings during destroy-all. Tests should cover init unwind, max_nch sizing, XSK updates, multi-vHCA IDs, PTP absent/present, packet merge update failures, TLS TIR creation under concurrent packet-merge changes, and RSS auxiliary lifecycle.
