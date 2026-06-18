# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/egress_lgcy.c

Purpose: configures legacy eswitch egress ACL behavior for vports in VST VLAN/QoS mode. It creates an egress ACL table with an allowed VLAN rule and a drop-all rule, optionally counting drops, then tears it down when VLAN/QoS state no longer requires steering.

Important APIs and functions: `esw_acl_egress_lgcy_setup` is the main setup/update entry. `esw_acl_egress_lgcy_cleanup` destroys rules, groups, table, and drop counter. Static helpers create/destroy the drop rule group and remove existing legacy rules. It uses shared helpers `esw_acl_table_create`, `esw_acl_egress_vlan_grp_create/destroy`, `esw_egress_acl_vlan_create`, and `esw_acl_egress_table_destroy`.

Control flow: setup first reuses or creates a drop counter if egress ACL counters are supported, destroys old rules, and if both VLAN and QoS are zero it cleans up and exits. Otherwise it lazily creates the egress ACL table sized for two rules, creates the VLAN group at index 0 and drop group at index 1, adds an allow rule matching `vport->info.vlan`, optionally with VLAN pop in steering VST mode, then adds the drop rule with optional counter destination. Any failure calls full cleanup.

State and dependencies: state is stored under `vport->egress.acl`, `vport->egress.vlan_grp`, `vport->egress.allowed_vlan`, `vport->egress.legacy.drop_grp`, `drop_rule`, and `drop_counter`. It depends on eswitch capability macros, mlx5 flow table/group/rule APIs, vport VLAN/QoS info, and helper functions in `helper.c`.

Risks and test signals: risks are stale rule handles after setup retries, counter lifetime when ACL creation fails, table-size/group-index mismatches, and behavioral differences between VST steering and non-steering modes. Test with VF vport VLAN add/remove, QoS-only configuration, counter-supported and unsupported firmware, repeated setup updates, and cleanup after partial failures.
