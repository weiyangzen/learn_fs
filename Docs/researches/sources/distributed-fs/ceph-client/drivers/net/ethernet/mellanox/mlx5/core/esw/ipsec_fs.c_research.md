# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/ipsec_fs.c

Purpose: Provides eswitch/FDB-specific flow steering glue for mlx5e IPsec offload. It maps IPsec RX object IDs into metadata, selects FDB flow levels and destinations, and restores uplink destinations for TC flows affected by IPsec.

Important APIs/types/functions: `mlx5_esw_ipsec_rx_create_attr_set()` and TX equivalent fill flow-creation attributes for FDB crypto priorities and levels. `mlx5_esw_ipsec_rx_status_pass_dest_get()` returns chain table 0/1 as pass destination. `mlx5_esw_ipsec_rx_setup_modify_header()` allocates a mapped ID and modify-header action in reg C1. `mlx5_esw_ipsec_rx_rule_add_match_obj()` matches that mapped ID. Mapping removal/search helpers manage `ipsec->ipsec_obj_id_map`. `mlx5_esw_ipsec_restore_dest_uplink()` walks representor TC flows and restores IPsec destinations.

Control flow: RX SA setup allocates a compact xarray ID for a hardware IPsec object, writes it into metadata reg C1 using tunnel bit fields, installs the modify header, and later matches status rules on the shifted mapped ID. On modify-header allocation failure the ID is erased. Restore-destination scans loaded representors and their TC flow hash tables, and for each non-multipath flow calls `mlx5_eswitch_restore_ipsec_rule()`.

State and persistence: State lives in each SA entry's `rx_mapped_id`, the global `ipsec_obj_id_map`, modify-header handles installed in flow actions, and existing TC flow rules. Flow levels are constants scoped to FDB crypto ingress/egress priority lanes.

Dependencies and integration: Depends on FDB chains, mlx5e IPsec structures, TC flow tables under CLS_ACT, eswitch TC restore helpers, xarray allocation under BH context, and metadata register layout shared with tunnel fields.

Risks and test signals: Risks include mapped ID exhaustion, missing erase on teardown, metadata bit overlap with tunnel fields, chain table reference expectations, and iterating TC flows while representors unload. Test signals include IPsec RX SA install/remove, status rule matching, mapped object lookup from RX path, TC offload coexistence, and restore after uplink destination changes.
