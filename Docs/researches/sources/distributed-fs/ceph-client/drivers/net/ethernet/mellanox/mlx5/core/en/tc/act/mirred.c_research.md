# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/mirred.c

Purpose: Parses FDB mirred/redirect actions, including representor forwarding, tunnel encap destinations, VLAN device adjustment, OVS internal port forwarding, BareUDP/MPLS constraints, and LAG/bond handling.

Important APIs: Exports non-terminating `mlx5e_tc_act_mirred` and terminating `mlx5e_tc_act_redirect`. Validation is `tc_act_can_offload_mirred()`. Parsing is split into `parse_mirred_encap()`, `parse_mirred()`, and `parse_mirred_ovs_master()`.

Control flow: Validation rejects missing devices, unsupported MPLS/VLAN-eth combinations, duplicate or excessive output ports, invalid switch-parent relationships, and invalid filter-device contexts. Encap parsing stores duplicated tunnel info and optional MPLS info. Plain mirred resolves macvlan, bond/LAG, VLAN push/pop actions, validates uplink forwarding, resolves representor vport/mdev, and appends a destination. OVS master forwarding programs internal-port actions and resets `if_count`.

State and dependencies: Mutates parse state ifindex tracking, encap/MPLS flags, `parse_attr` tunnel/MPLS arrays, `esw_attr->dests`, `out_count`, VLAN actions, and flow action bits. Depends on eswitch representors, bonding/LAG, BareUDP, VLAN helpers, internal-port helpers, and tunnel encap helpers.

Risks and tests: Device topology and action-order interactions dominate risk. Tests should cover duplicate output rejection, max vports, VF-to-self, uplink-to-uplink capability gating, VLAN upper/lower devices, macvlan, bond active slave, encap redirect, MPLS push through BareUDP, OVS internal port, and filter-device mismatch replay.
