# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/pool.c

Purpose: implements AF_XDP pool bind/unbind for mlx5e queues. It maps UMEM DMA, tracks per-channel pool pointers, validates XSK geometry, and opens/closes live XSK RQ/SQ objects when the netdev is opened with XDP active.

Important APIs/types/functions: `mlx5e_xsk_setup_pool` is the `.ndo_bpf` callback. Internals include `mlx5e_xsk_map_pool`, `mlx5e_xsk_get_pools/put_pools`, `mlx5e_xsk_add_pool/remove_pool`, `mlx5e_xsk_is_pool_sane`, `mlx5e_build_xsk_param`, `mlx5e_xsk_enable_locked`, and `mlx5e_xsk_disable_locked`.

Control flow and state: public enable/disable wrappers hold `priv->state_lock`. Enable rejects duplicate pool binding and headroom/chunk sizes above 16 bits, allocates channel params, DMA maps the pool, stores it in `priv->xsk.pools[ix]`, builds XSK channel params, validates closed configurations, or opens `c->xskrq`/`c->xsksq` live. Live enable activates XSK, triggers ICOSQ/NAPI, updates RX resource steering, deactivates the regular RQ, and flushes it. Disable reverses by reactivating regular RQ, waiting for WQEs, updating RX steering, deactivating/closing XSK, removing pool, and unmapping DMA.

Dependencies and integration: uses `net/xdp_sock_drv.h`, mlx5e params/setup helpers, subdevice DMA lookup, RX resource updates, RQ state transitions, and XSK open/close from `setup.c`.

Risks and test signals: DMA map/unmap must balance all error paths; opened/no-XDP and closed validation paths must not leave stale pools; queue IDs must respect `num_channels`. Test bind/unbind closed, opened without XDP, opened with XDP, duplicate bind, invalid chunk/headroom, striding RQ oversized warning, and failure injection in map/open paths.
