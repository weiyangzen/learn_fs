# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/vlan.c

Purpose: Parses VLAN push/pop, VLAN ethernet push/pop, and helper-generated VLAN adjustments for VLAN upper/lower devices in FDB offload.

Important APIs: `mlx5e_tc_act_vlan` parse/post-parse vtable. Shared helpers `mlx5e_tc_act_vlan_add_push_action()` and `mlx5e_tc_act_vlan_add_pop_action()` synthesize VLAN actions for mirred paths. `parse_tc_vlan_action()` handles VLAN depth, firmware support, push/pop action bits, eth push/pop parse-state flags, and VLAN metadata.

Control flow: Direct VLAN push after VLAN pop is converted into VLAN rewrite. Regular parsing records VLAN push/pop actions and resets FDB split/if_count. Post-parse replaces VLAN pop with priority-tag rewrite when firmware requires prio tags.

State and dependencies: Mutates `attr->esw_attr` VLAN fields, total VLAN depth, Ethernet header fields, action bits, parse-state eth flags, split count, and if_count. Depends on VLAN netdev helpers, firmware VLAN capabilities, pedit-based VLAN rewrite, and match-header accessors.

Risks and tests: VLAN depth and action-order interactions are easy to break. Tests should cover nested VLAN devices, pop+push rewrite, prio-tag-required rewrite, VLAN eth push only after L3-to-L2 decap, eth pop only with MPLS push, firmware unsupported depth, and split_count updates.
