<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/tunnels.c -->
# sources/distributed-fs/ceph-client/net/ethtool/tunnels.c

## Purpose
Serves ethtool netlink tunnel offload information for UDP tunnel port tables, including dynamic NIC UDP tunnel tables and the static IANA VXLAN port convention.

## APIs, Types, and Functions
Defines `ethnl_tunnel_info_get_policy`, `struct ethnl_tunnel_info_dump_ctx`, and direct/dump handlers `ethnl_tunnel_info_doit()`, `ethnl_tunnel_info_start()`, and `ethnl_tunnel_info_dumpit()`. Helpers include `ethnl_udp_table_reply_size()`, `ethnl_tunnel_info_reply_size()`, and `ethnl_tunnel_info_fill_reply()`.

## Control Flow, State, and Persistence
Direct GET parses a device header, locks RTNL, computes reply size from `dev->udp_tunnel_nic_info`, allocates an ethtool reply, fills nested UDP port table attributes, unlocks, releases the device, and replies. Fill iterates NIC tunnel tables until a table with zero entries, emits table size, tunnel type bitset, and entries provided by `udp_tunnel_nic_dump_write()`. If the device advertises static IANA VXLAN support, a synthetic one-entry table for port 4789 and VXLAN type is appended. Dumps parse an optional device filter but then clear it, walk netdevs with an ifindex cursor, skip devices returning `-EOPNOTSUPP`, and return a partial skb length when `-EMSGSIZE` occurs after data was emitted.

## Dependencies and Integration
Depends on `udp_tunnel_nic_info`, UDP tunnel dump helpers, VXLAN IANA constants, compact ethtool bitsets, RTNL, and ethtool generic-netlink header helpers. Static asserts keep ethtool tunnel type IDs aligned with kernel UDP tunnel type bit positions.

## Risks and Test Signals
Risks include inconsistent dump behavior if a requested device filter is intentionally ignored, reply size drift versus tunnel dump helper output, static VXLAN table encoding with zero type bitset, and partial dump resume correctness. Test signals include no tunnel info extack, multi-table dump, static VXLAN support, compact type bitsets, direct GET, all-netdev dump skipping unsupported devices, and small-skb `-EMSGSIZE` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/tunnels.c -->
