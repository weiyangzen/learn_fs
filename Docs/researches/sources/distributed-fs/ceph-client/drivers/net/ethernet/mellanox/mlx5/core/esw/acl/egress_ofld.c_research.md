# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/egress_ofld.c

Purpose: configures eswitch egress ACLs for switchdev/offloads mode. It handles priority-tag pop rules, default or bond-driven forward-to-vport rules, bounce rule cleanup, and vport bond/unbond rewrites for passive representors.

Important APIs and functions: `esw_acl_egress_ofld_setup` creates the offload egress ACL table when fwd-to-vport or prio-tag support requires it. `esw_acl_egress_ofld_cleanup` removes all rules/groups/table. `mlx5_esw_acl_egress_vport_bond` redirects a passive vport to an active vport and removes forwarding from the active vport. `mlx5_esw_acl_egress_vport_unbond` restores default rules. `esw_acl_egress_ofld_bounce_rule_destroy` deletes one xarray-indexed bounce rule.

Control flow: setup exits if neither relevant capability is present or the vport is not VF/SF. It destroys stale rules, computes table size from supported features, creates the egress ACL table, creates a VLAN group for prio-tag rule and optional fwd group, then installs rules. In prio-tag mode it creates a VLAN rule for VLAN ID 0 that pops the tag and either allows or forwards. If a forward destination is supplied, it also creates a catch-all fwd-to-vport rule. Bonding recreates rules on active and passive vports with a destination of type vport plus VHCA ID.

State and dependencies: state lives under `vport->egress.offloads`: `fwd_rule`, `fwd_grp`, `bounce_grp`, and `bounce_rules` xarray, plus shared `vport->egress.acl`, `vlan_grp`, and `allowed_vlan`. Dependencies include firmware capability checks for prio tag and egress fwd-to-vport, eswitch vport lookup, mlx5 flow rules/groups, and shared ACL helpers.

Risks and test signals: risks include leaking xarray bounce rules, stale fwd rules after bond transitions, table size mismatch with conditional groups, ignoring errors when recreating active-vport rules, and using VHCA IDs incorrectly across devices. Test VF and SF vports, prio-tag-required firmware, fwd-to-vport-supported firmware, bond/unbond transitions, repeated cleanup, and error injection in group/rule creation.
