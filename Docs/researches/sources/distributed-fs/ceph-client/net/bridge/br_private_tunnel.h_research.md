# sources/distributed-fs/ceph-client/net/bridge/br_private_tunnel.h

## Purpose
`br_private_tunnel.h` declares the bridge VLAN tunnel internal API. It connects netlink parsing/dumping to VLAN tunnel storage and data-plane ingress/egress handling.

## Important APIs, types, and functions
- `struct vtunnel_info` is the parsed netlink representation of a tunnel mapping.
- Netlink helpers: `br_parse_vlan_tunnel_info()`, `br_process_vlan_tunnel_info()`, `br_get_vlan_tunnel_info_size()`, `br_fill_vlan_tunnel_info()`, `vlan_tunid_inrange()`, and `br_vlan_tunnel_info()`.
- VLAN tunnel storage/data-plane helpers under `CONFIG_BRIDGE_VLAN_FILTERING`: `vlan_tunnel_init()`, `vlan_tunnel_deinit()`, `nbp_vlan_tunnel_info_add()`, `nbp_vlan_tunnel_info_delete()`, `nbp_vlan_tunnel_info_flush()`, `vlan_tunnel_info_del()`, `br_handle_ingress_vlan_tunnel()`, and `br_handle_egress_vlan_tunnel()`.
- When VLAN filtering is disabled, most helpers become no-ops returning success or `0`.

## Control flow
Netlink code parses requested mappings and delegates add/delete to VLAN tunnel helpers. Data-plane ingress/egress helpers attach or consume tunnel metadata when VLAN tunnel mode is active. Initialization/deinitialization hooks prepare per-VLAN-group tunnel hashes.

## State and persistence
Tunnel state is stored in `struct net_bridge_vlan_group::tunnel_hash` and each VLAN's `struct br_tunnel_info`. It is in-memory only and tied to bridge port/VLAN lifetime.

## Dependencies and integration points
The header depends on bridge VLAN filtering and tunnel metadata support. It integrates with `br_netlink.c`, `br_netlink_tunnel.c`, VLAN implementation files, and encapsulation devices such as VXLAN that use metadata destinations.

## Risks and edge cases
The no-op stubs under disabled VLAN filtering can hide configuration paths unless callers validate feature availability. Data-plane helpers must preserve skb metadata lifetime and correctly map between ingress tunnel IDs and VLAN IDs. Flush paths must remove tunnel metadata when the port flag is disabled.

## Test signals
Test VLAN tunnel mapping add/delete, port flag toggles, ingress metadata-to-VLAN mapping, egress VLAN-to-metadata mapping, range dumps, VLAN filtering disabled configs, and port/VLAN teardown.
