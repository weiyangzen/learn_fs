# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/vlan.h

Purpose: Declares VLAN action helper APIs shared by mirred and VLAN mangle parsing.

Important APIs: `mlx5e_tc_act_vlan_add_push_action()`, `mlx5e_tc_act_vlan_add_pop_action()`, and `mlx5e_tc_act_vlan_add_rewrite_action()`.

Control flow and state: The helpers mutate `mlx5_flow_attr`, parse attributes, action bits, and possibly output netdev pointers; this header defines their call contract.

Dependencies and integration: Includes flow offload and `tc_priv`; used by `mirred.c`, `vlan.c`, and `vlan_mangle.c`.

Risks and tests: Because helpers are called from multiple parsers, tests should cover both explicit VLAN actions and implicit VLAN push/pop through VLAN netdev forwarding.
