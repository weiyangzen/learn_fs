# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/en_accel.h

Purpose: central inline composition layer for mlx5e transmit/receive accelerations, including kTLS, IPsec, PSP, MACsec, and Geneve software parser offload fields.

Important APIs/types/functions: `mlx5_geneve_tx_allowed`, `mlx5e_tx_tunnel_accel`, `struct mlx5e_accel_tx_state`, `mlx5e_accel_tx_begin`, `mlx5e_accel_tx_ids_len`, `mlx5e_accel_tx_eseg`, `mlx5e_accel_tx_finish`, `mlx5e_accel_init_rx/cleanup_rx`, and `mlx5e_accel_init_tx/cleanup_tx`.

Control flow and state: TX begin may emit preparatory WQEs and can drop/fail the SKB when an acceleration-specific handler cannot prepare state. ID length is selected from active PSP/IPsec state. ESEG build adds protocol-specific metadata/checksum/trailer fields before the WQE is posted. TX finish writes final WQE fields such as TLS TIS or IPsec inline trailer. Init/cleanup orders PSP flow steering and kTLS setup/teardown.

Dependencies and integration: compile-time gated by feature configs; depends on TLS/IPsec/PSP/MACsec helpers, `xfrm_offload`, TLS offload markers, and mlx5e TX WQE layout. Geneve handling depends on SWP support and packet header parsing.

Risks and test signals: ordering matters when several offloads are present; incorrect ESEG metadata breaks hardware parsing. Test each feature enabled/disabled, mixed tunnel checksum cases, IPsec with GSO/checksum, TLS TX, PSP, MACsec, and Geneve encapsulation with VLAN.
