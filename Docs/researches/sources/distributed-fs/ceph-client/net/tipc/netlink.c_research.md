# sources/distributed-fs/ceph-client/net/tipc/netlink.c

## Purpose
`netlink.c` registers the modern TIPC generic netlink family, defines the top-level and nested attribute policies, and maps each TIPC netlink command to its subsystem handler. It is the central user-space configuration and dump surface for bearers, sockets, publications, links, media, nodes, network identity, name tables, monitors, peer removal, optional UDP media, and optional crypto keys.

## Important APIs, Types, And Functions
The file defines `tipc_nl_policy[]` and exported nested policies including `tipc_nl_name_table_policy`, `tipc_nl_monitor_policy`, `tipc_nl_sock_policy`, `tipc_nl_net_policy`, `tipc_nl_link_policy`, `tipc_nl_node_policy`, `tipc_nl_prop_policy`, `tipc_nl_bearer_policy`, `tipc_nl_media_policy`, and `tipc_nl_udp_policy`. It defines the `tipc_genl_v2_ops[]` command table, the exported `tipc_genl_family`, and lifecycle functions `tipc_netlink_start()` and `tipc_netlink_stop()`.

## Control Flow
Module startup calls `tipc_netlink_start()`, which registers `tipc_genl_family`. User commands arrive through generic netlink, are validated according to the family policy and per-op relaxed validation flags, and dispatch to the corresponding subsystem handler. Dump commands use handlers such as `tipc_nl_bearer_dump()`, `tipc_nl_sk_dump()`, `tipc_nl_node_dump()`, `tipc_nl_net_dump()`, and `tipc_nl_name_table_dump()`. Shutdown unregisters the family.

## State And Persistence
The main persistent object is `tipc_genl_family`, marked `__ro_after_init`, with family name/version, max attribute, policy pointer, namespace support, module owner, operation table, and reserved operation start. Attribute policy arrays are global const state used by both modern netlink and compatibility transcoding.

## Dependencies And Integration Points
The file includes and dispatches into `socket`, `name_table`, `bearer`, `link`, `node`, `net`, and optionally `udp_media` and crypto functionality. `netlink.h` exposes the family and policies. `netlink_compat.c` uses the same policies and subsystem handlers to translate legacy TLV commands into modern nested attributes.

## Risks And Edge Cases
The operation table is user-space ABI. Adding, removing, or reassigning commands can break `tipc` tooling and the legacy compatibility layer. Many ops use `GENL_DONT_VALIDATE_STRICT` to preserve older behavior, so individual handlers must validate required nested attributes. Policy lengths for names, node IDs, and keys are security boundaries. Conditional UDP/crypto operations must compile and reserve consistent command space across configs.

## Test Signals
Generic netlink registration failure injection, `tipc` command-line get/set coverage for every op, malformed attribute fuzzing, namespace isolation, dump pagination, conditional builds with UDP media and crypto enabled/disabled, legacy compatibility command parity, and ABI regression tests for family name/version/commands validate this file.
