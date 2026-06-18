# sources/distributed-fs/ceph-client/net/bridge/br_vlan_tunnel.c

## Purpose
Maintains per-port VLAN-to-tunnel metadata mappings for bridge VLAN tunnel mode, allowing ingress tunnel IDs to map to VLAN tags and egress VLAN tags to attach tunnel destination metadata.

## Important APIs, Types, And Functions
Key APIs are `nbp_vlan_tunnel_info_add`, `nbp_vlan_tunnel_info_delete`, `vlan_tunnel_info_del`, `nbp_vlan_tunnel_info_flush`, `vlan_tunnel_init`, `vlan_tunnel_deinit`, `br_handle_ingress_vlan_tunnel`, and `br_handle_egress_vlan_tunnel`. The file uses a tunnel-ID rhashtable keyed by `net_bridge_vlan.tinfo.tunnel_id`.

## Control Flow
Adding a mapping finds the port VLAN, builds `metadata_dst` with a tunnel key, marks it as TX bridge tunnel metadata, stores it under RCU, records the tunnel ID, and inserts the VLAN into the tunnel hash. Deletion removes the hash node and releases destination metadata. Ingress checks for tunnel info on untagged packets, looks up a VLAN by tunnel ID, drops old dst metadata, and pushes an accelerated bridge VLAN tag. Egress clears the hardware VLAN tag, then either constructs backup-nexthop metadata or reuses the VLAN's stored metadata with a safe dst hold.

## State And Persistence Behavior
Mappings live in the VLAN group's in-memory rhashtable and each VLAN's `tinfo` pointer/id fields. Updates require RTNL and use RCU pointer assignment/dereference for packet paths. Metadata references are held/released through dst lifetime rules; no disk persistence exists.

## Dependencies And Integration Points
Depends on `br_private_tunnel.h`, `net/dst_metadata.h`, `net/switchdev.h`, IP tunnel metadata helpers, VLAN tag helpers, bridge input control block fields, and the VLAN add/delete/option paths that call tunnel add/delete/flush.

## Risks And Test Signals
Risks include duplicate tunnel IDs, dst metadata lifetime races, failure rollback after hash insertion errors, handling QinQ by clearing only the accelerated outer tag, and preserving backup nexthop IDs. Useful tests cover netlink tunnel add/delete/range behavior, ingress untagged VXLAN-to-VLAN mapping, egress VLAN-to-tunnel metadata, duplicate mapping rejection, flush on VLAN removal, and QinQ payload preservation.
