# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/helper.c

Purpose: shared ACL utility layer for mlx5 eswitch ingress/egress ACL code. It creates vport ACL flow tables, creates/destroys egress VLAN allow rules and VLAN flow groups, and destroys common ingress/egress ACL tables/rules.

Important APIs and functions: `esw_acl_table_create` checks ingress or egress ACL table support, resolves the vport flow namespace, sets table size and `MLX5_FLOW_TABLE_OTHER_VPORT` when needed, and creates a vport flow table. `esw_egress_acl_vlan_create` creates one allowed VLAN rule matching outer cvlan tag and first VID, with caller-supplied action and optional destination. `esw_acl_egress_vlan_grp_create/destroy` manages the matching group for VLAN rules. `esw_acl_egress_table_destroy`, `esw_acl_ingress_table_destroy`, and `esw_acl_ingress_allow_rule_destroy` are common cleanup helpers.

Control flow: helpers allocate firmware command/spec buffers with `kvzalloc`, fill match criteria using `MLX5_SET` macros, call mlx5 flow steering APIs, store handles on the vport, and clear pointers after destroy. Error paths free allocated buffers and leave handle fields NULL when rule creation fails.

State and dependencies: state is entirely in `struct mlx5_vport` ingress/egress fields: ACL table pointers, `allowed_vlan`, `vlan_grp`, and ingress allow rule. Dependencies include eswitch capability macros, `mlx5_get_flow_vport_namespace`, `mlx5_create_vport_flow_table`, `mlx5_create_flow_group`, `mlx5_add_flow_rules`, and destroy/delete counterparts.

Risks and test signals: risks are duplicate `allowed_vlan` attempts returning `-EEXIST`, wrong namespace/capability selection, missing `OTHER_VPORT` flag for non-uplink or ECPF cases, and match criteria mismatches for VLAN tag/VID. Test ingress and egress ACL table creation on supported/unsupported firmware, vport 0/ECPF/nonzero vports, VLAN allow rule lifecycle, group creation failure cleanup, and repeated destroy calls.
