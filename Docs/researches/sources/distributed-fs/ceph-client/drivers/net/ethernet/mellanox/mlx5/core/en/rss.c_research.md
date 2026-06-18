# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rss.c

Purpose: Implements an RSS context around one indirect RQT, per-traffic-type TIRs, hash parameters, indirection table, optional inner TIRs, enable/disable redirection, and ethtool RSS mutation.

Important APIs: `mlx5e_rss_init()`, `mlx5e_rss_cleanup()`, refcount helpers, `mlx5e_rss_enable()`/`disable()`, `mlx5e_rss_get_rxfh()`/`set_rxfh()`, `mlx5e_rss_get_hash_fields()`/`set_hash_fields()`, `mlx5e_rss_packet_merge_set_param()`, `mlx5e_rss_obtain_tirn()`, and TIR/RQTN getters. `rss_default_config` maps mlx5 traffic types to default L3/L4 and hash fields.

Control flow: Initialization allocates an RSS object and indirection table, seeds Toeplitz hash and default fields, creates an RQT initially pointing at the drop RQ, and optionally creates all outer and inner TIRs. Enable redirects the RQT through `mlx5e_rqt_redirect_indir()`. Disable points it back to the drop RQ. `set_rxfh()` snapshots the old RSS object, applies requested hfunc/key/indir/symmetric changes, redirects the RQT when enabled, rolls back on redirect failure, and modifies TIR RSS state when hash parameters changed.

State and persistence: The RSS object owns hash params, indirection table allocation, per-traffic-type `rx_hash_fields`, TIR pointers, the RQT, `enabled`, and `refcnt`. Hardware TIR/RQT objects persist until cleanup or destroy. Refcount prevents cleanup unless the owner has exclusive reference.

Dependencies and integration: Uses RQT, TIR builder/modify APIs, mlx5 traffic type constants, ethtool hash constants, packet merge configuration from RX resources, and capability flags supplied by `rx_res`. `reporter_rx.c` diagnoses TIR/RQTN state through these getters.

Risks: `mlx5e_rss_copy()` shallow-copies then restores the indirection pointer; future fields with owned allocations require care. Hash field updates can partially update outer TIR before inner TIR fails; the code attempts best-effort rollback. `set_rxfh()` ignores return from `mlx5e_rss_update_tirs()` after successful RQT change. Tests should cover lazy TIR creation, inner FT unsupported errors, hfunc validation, rollback after RQT redirect failure, packet merge updates, refcounted cleanup, and ethtool RSS changes while enabled and disabled.
