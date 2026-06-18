# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/params.c

Purpose: computes and builds mlx5e queue, CQ, RQ, SQ, XDP, XSK, SHAMPO, and ICOSQ parameters from device capabilities and netdev runtime settings.

Important APIs/functions: striding-RQ helpers such as `mlx5e_mpwrq_page_shift`, `mlx5e_mpwrq_umr_mode`, `mlx5e_mpwrq_log_wqe_sz`, `mlx5e_mpwqe_get_log_rq_size`, linear/nonlinear RX decisions, validation helpers, `mlx5e_build_rq_params`, `mlx5e_build_rq_param`, `mlx5e_build_sq_param`, `mlx5e_build_channel_param`, and `mlx5e_build_xsk_channel_param`.

Control flow: RX setup first chooses cyclic vs linked-list striding RQ based on feature flags, CQE compression capabilities, and whether striding RQ can produce acceptable skb layout. MPWRQ calculations derive page shift, UMR mapping mode, WQE size, stride size/count, RQ size, and UMR workqueue capacity. Legacy cyclic RQ builds fragment arrays and refill bulk parameters from MTU, headroom, XDP, and page size. Queue builders fill firmware contexts with CQ size, compression layout, WQ type/stride, PD, VLAN/FCS settings, stop room, NUMA placement, and ICOSQ sizing.

State and persistence: functions are mostly pure calculations into caller-provided parameter structs. They read capabilities and netdev params but persist no global state. The generated contexts become hardware queue creation inputs.

Dependencies and integration: depends on mlx5 capability macros, page pool/XDP socket constraints, DIM moderation, accel features such as kTLS/IPsec/PSP, and port link speed for slow PCI heuristics.

Risks: many calculations are capability-dependent and unsigned; warnings guard underflow and invalid stride combinations. XSK unaligned/oversized frame modes are especially sensitive because UMR entry size changes queue capacity. Incorrect stop-room or ICOSQ sizing can deadlock queue recovery or UMR posting.

Test signals: MTU extremes, XDP attach/detach, XSK aligned/unaligned/chunk-size variations, CQE compression layouts, SHAMPO/LRO, kdump defaults, slow PCI detection, and firmware capability matrices.
