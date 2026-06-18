# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/qp.c

## Purpose
This file implements the mlx4 InfiniBand queue pair, receive work queue, RSS indirection, work request posting, state transition, query, destroy, and drain paths. It is the main mlx4 verbs bridge between RDMA core QP/WQ objects and mlx4 firmware resources: QPN ranges, QP contexts, MTTs, doorbells, CQ linkage, SRQ linkage, steering state, RoCE MAC/VLAN state, and SR-IOV proxy/tunnel special QPs.

## Important APIs, types, and functions
- Public verbs entry points: `mlx4_ib_create_qp`, `mlx4_ib_destroy_qp`, `mlx4_ib_modify_qp`, `mlx4_ib_query_qp`, `mlx4_ib_post_send`, `mlx4_ib_post_recv`, `mlx4_ib_create_wq`, `mlx4_ib_modify_wq`, `mlx4_ib_destroy_wq`, `mlx4_ib_create_rwq_ind_table`, `mlx4_ib_drain_sq`, `mlx4_ib_drain_rq`, `mlx4_ib_qp_event_init`, and `mlx4_ib_qp_event_cleanup`.
- Core lifecycle helpers: `create_qp_common`, `destroy_qp_common`, `_mlx4_ib_modify_qp`, `__mlx4_ib_modify_qp`, `create_rq`, `create_qp_rss`, `destroy_qp_rss`, `bringup_rss_rwqs`, and `bring_down_rss_rwqs`.
- Posting helpers: `_mlx4_ib_post_send`, `_mlx4_ib_post_recv`, `mlx4_wq_overflow`, `set_data_seg`, `set_datagram_seg`, `set_tunnel_datagram_seg`, `build_mlx_header`, `build_sriov_qp0_header`, `build_tunnel_header`, `build_lso_seg`, and memory-registration segment builders.
- State and transport helpers: `to_mlx4_state`, `to_ib_qp_state`, `to_mlx4_st`, `to_mlx4_access_flags`, `_mlx4_set_path`, `handle_eth_ud_smac_index`, `create_qp_lb_counter`, and RoCE mode conversion.

## Control flow
QP creation validates type, flags, user command ABI, and capabilities, then sizes RQ/SQ rings, maps user memory or allocates kernel buffers, builds MTTs, maps/allocates doorbells, reserves a QPN, allocates the mlx4 QP, precomputes the doorbell QPN, links the QP into device and CQ reset-flow lists, and sets software state to RESET. Special paths exist for SMI/GSI proxy and tunnel QPs, RoCEv2 GSI shadow QPs, raw-packet WQs, XRC targets/initiators, netif steering QPs, and RSS QPs. Destruction reverses the state to RESET when needed, unregisters MAC/VLAN candidates, cleans kernel CQs, removes reset-flow links, frees QPN ranges, MTTs, buffers, WRID arrays, proxy buffers, and gid entries.

Modification is guarded by `qp->mutex` and RDMA-core transition validation. The low-level `__mlx4_ib_modify_qp` allocates a QP context, fills flags, state, service type, path MTU, queue sizes, CQs, PD, access bits, PSNs, retry timers, P_Key, Q_Key, SRQ number, RoCE mode, RSS context, counters, steering, MAC/VLAN indexes, and user UAR index, then calls `mlx4_qp_modify`. On success it updates cached state and side-effect ownership; on failure it unregisters candidates and rolls back steering/counters. QP0 state transitions also call `mlx4_INIT_PORT` or `mlx4_CLOSE_PORT`.

Posting sends locks `sq.lock`, rejects device internal error unless draining, checks overflow and SGE count, builds type-specific WQE segments, writes data segments in reverse order, uses write barriers before ownership and doorbell writes, rings the UAR doorbell, stamps prefetched WQEs invalid, and advances SQ head/next indices. Posting receives locks `rq.lock`, checks overflow and SGE count, writes scatter segments and proxy receive header entries, updates WRID, advances RQ head, and updates the doorbell record. Drain paths move the QP to ERR, post a synthetic WR, and wait for the CQ completion with special handling for direct polling and reset/internal-error CQ processing.

## State and persistence behavior
All persistent state is in kernel memory and firmware resources: `mlx4_ib_qp` caches queue heads/tails, SQ/RQ layout, flags, state, port, counters, MAC/VLAN registrations, RSS use counts, WQ ranges, and gid/steering lists. User QPs persist their queue memory in user umem and user doorbell mappings; kernel QPs own mlx4 buffers, WRID arrays, and doorbell pages. Firmware state is represented by allocated QPNs, QP contexts, MTTs, counters, steering registrations, and MAC/VLAN table entries. There is no disk persistence.

## Dependencies and integration points
The file integrates with RDMA core verbs, mlx4 core firmware commands/resource allocators, CQ cleanup, SRQ handling, XRC, RoCE GID/cache helpers, netdevice addressing, steering, multicast, counter tables, reset-flow lists, and SR-IOV special QP plumbing. It depends on `mlx4_ib.h`, `rdma/ib_cache.h`, `rdma/ib_pack.h`, `rdma/ib_addr.h`, `rdma/uverbs_ioctl.h`, and mlx4 kernel headers.

## Risks
The highest-risk areas are WQE layout and barriers, queue overflow accounting, QP state transition side effects, RoCE MAC/VLAN candidate rollback, SR-IOV proxy/tunnel header construction, GSI RoCEv2 shadow QP synchronization, RSS WQ use-count rollback, reset/internal-error races, and lock ordering between CQs and reset-flow lists. Bugs here can leak firmware resources, corrupt queues, misroute packets, hang drains, or expose invalid user ABI behavior.

## Test signals
Useful signals include RDMA CM/ibverbs QP lifecycle tests across RC/UC/UD/raw-packet/XRC, user and kernel QP creation with boundary capabilities, post-send/receive overflow and bad-SGE tests, RoCE v1/v2 GSI traffic, SR-IOV QP0/QP1 proxy traffic, RSS indirection table validation, QP query after transitions, reset/internal-error drain behavior, CQ cleanup after reset, MAC/VLAN registration leak checks, and lockdep/KASAN/KCSAN runs around concurrent modify/destroy/post paths.
