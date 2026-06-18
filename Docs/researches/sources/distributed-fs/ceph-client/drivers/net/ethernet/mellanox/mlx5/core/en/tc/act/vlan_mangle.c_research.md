# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/vlan_mangle.c

Purpose: Implements VLAN rewrite/mangle by translating VLAN VID modification into a pedit modify-header action.

Important API: `mlx5e_tc_act_vlan_add_rewrite_action()` validates VLAN protocol match and unchanged priority, creates a synthetic pedit action at `vlan_ethhdr.h_vlan_TCI`, and sets MOD_HDR. `mlx5e_tc_act_vlan_mangle` invokes it and updates FDB split state.

Control flow and state: The helper reads match criteria/value from the flow spec to ensure a VLAN tag is matched and prio is not changed. It then calls the shared pedit parser.

Dependencies and integration: Depends on VLAN header layout, match-header accessors, pedit parser, extack, and namespace selection.

Risks and tests: Endianness and mask construction are critical. Tests should cover missing VLAN match rejection, priority-change rejection, VID rewrite success, FDB split reset, and pedit duplicate-field collisions.
