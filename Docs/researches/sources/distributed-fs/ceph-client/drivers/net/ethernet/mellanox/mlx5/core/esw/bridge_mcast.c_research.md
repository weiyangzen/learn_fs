# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/bridge_mcast.c

Purpose: Implements multicast bridge offload and MDB handling for mlx5 eswitch bridge acceleration. It handles MDB membership replication, per-port multicast flow tables, VLAN multicast pop rules, and global IGMP/MLD trap/skip rules.

Important APIs/types/functions: Public/internal-to-bridge exports include MDB init/cleanup, `mlx5_esw_bridge_port_mdb_attach()` and detach, MDB VLAN/bridge flushes, port multicast init/cleanup, VLAN multicast init/cleanup, and bridge multicast enable/disable. Internal helpers create MDB egress flows, per-port multicast tables/groups/flows, global IGMP/MLD groups and flow handles, and peer filter flows for merged eswitch.

Control flow: MDB attach requires multicast enabled, gets or creates an MDB entry keyed by multicast MAC plus VID, inserts the port in the entry xarray, and recreates the egress multicast flow with one destination per port. Detach removes a port and either deletes the entry or recreates the flow for the remaining ports. Multicast enable first creates shared ingress IGMP/MLD groups and rules if not already present, sets the bridge flag, and initializes each existing bridge port. Disable tears down port multicast state, clears the flag, and removes global rules only when no bridge still has multicast enabled.

State and persistence: MDB state lives in `bridge->mdb_ht` and `bridge->mdb_list`; each MDB entry owns a port xarray, port count, and egress flow handle. Per-port multicast state lives in `port->mcast` flow table, groups, filter rule, and forwarding rule. VLAN multicast state uses `vlan->mcast_handle`. Global IGMP/MLD state is stored in `br_offloads` ingress group and handle members.

Dependencies and integration: Depends on `bridge_priv.h` state, mlx5 flow steering, metadata matching, `FLOW_CONTEXT_UPLINK_HAIRPIN_EN`, hardware multipath and uplink hairpin capabilities checked by `bridge.c`, devcom peer owner lookup, ICMPv6 flex parser support for MLD, and bridge tracepoints.

Risks and test signals: Risks include failed flow recreation after membership changes leaving software MDB accepted but hardware stale, global multicast rule lifetime across multiple bridges, missing ICMPv6 parser support, and uplink hairpin/multipath capability mismatches. Test signals include multicast enable/disable, IGMP and MLD snooping traffic, MDB add/delete on several ports and VLANs, untagged VLAN multicast pop, merged-eswitch peer ports, and cleanup after bridge/VLAN/port removal.
