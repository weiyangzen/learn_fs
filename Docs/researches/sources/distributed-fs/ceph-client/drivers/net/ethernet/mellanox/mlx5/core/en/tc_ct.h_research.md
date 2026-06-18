# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_ct.h

Purpose: declares the mlx5 TC conntrack offload interface and the metadata-register layout used to carry CT zone, state, mark, labels, flow-table id, and restore-zone information through mlx5 hardware pipelines.

Important APIs and types: `struct mlx5_ct_attr` is embedded in flow attributes and records zone, CT action bits, nf_flowtable pointer, labels mapping id, action-miss mapping, miss cookie, offload state, and zone flow-table pointer. Macros `zone_to_reg_ct`, `ctstate_to_reg_ct`, `mark_to_reg_ct`, `labels_to_reg_ct`, `fteid_to_reg_ct`, `zone_restore_to_reg_ct`, and `nic_zone_restore_to_reg_ct` define precise metadata fields. `MLX5_CT_ZONE_BITS` and `MLX5_CT_ZONE_MASK` expose the usable zone width. The header exports init/cleanup, match add/delete, action parsing, flow offload/delete, restore, no-track match setup, and validation helpers.

Control flow: callers include the TC parser and flow lifecycle code. Match parsing fills a `mlx5_flow_spec` using the register macros and records label mappings in `mlx5_ct_attr`. Action parsing stores the CT action contract. Flow offload uses the populated `mlx5_ct_attr` to install CT pipeline jumps, and delete reverses it. Restore uses the zone restore metadata from RX completion paths.

State and persistence: this header owns no runtime state, but its register mappings are persistent ABI-like contracts inside the driver. Any change to bit widths or offsets must remain consistent with `tc_ct.c`, mapping definitions, post-action handling, and hardware match/set capabilities.

Dependencies and integration points: depends on TC action definitions, mlx5 flow steering structures, and `en.h`. It hides implementation details behind `struct mlx5_tc_ct_priv` and `struct mlx5_ct_ft`. When `CONFIG_MLX5_TC_CT` is disabled, inline stubs either no-op, reject CT features with extack messages, or fail restore for nonzero zone ids.

Risks and test signals: register collisions are the main risk, especially the C5 low-byte reservation for packet color and different restore-zone placement for NIC mode. Test signals include build coverage with CT enabled and disabled, extack behavior when disabled, and hardware flow dumps verifying that CT zone/state/mark/label fields land in the expected registers.
