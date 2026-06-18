# sources/distributed-fs/ceph-client/include/uapi/linux/tipc_netlink.h

Purpose: Defines the generic netlink ABI for TIPC v2 management. It names the family (`TIPCv2`), version, commands, and nested attribute IDs used by userspace tools and kernel TIPC netlink handlers to inspect and mutate bearers, media, links, sockets, publications, nodes, network identity, monitors, peers, and crypto keys.

Important APIs/types/functions: The main command enum includes legacy dispatch plus bearer enable/disable/get/set/add, socket/publication/link/media/node/net/name-table/monitor queries, peer removal, UDP remote IP lookup, key set/flush, and legacy address get. Top-level `TIPC_NLA_*` attributes wrap nested bearer, socket, publication, link, media, node, net, name-table, monitor, and monitor-peer data. Per-object enums describe typed netlink attributes such as bearer name/domain/UDP opts, socket addr/ref/connection/stat/group, link MTU/state/stats, media properties, node ID/key/rekeying, network ID/address/nodeid, publication range/scope/key, monitor peer maps, socket-group state, connection peer/type/instance, socket stats, link/media/bearer properties, and detailed link statistics.

Control flow: This header has no executable flow beyond enum values. Runtime flow is generic-netlink request/response: userspace sends one `TIPC_NL_*` command with nested `TIPC_NLA_*` payloads; the kernel validates nested attribute policy, reads command-specific attributes, and returns multicast or dump-style nested replies for GET commands or mutates TIPC state for SET/ADD/REMOVE/FLUSH commands.

State and persistence behavior: The ABI exposes live in-kernel TIPC state. Bearer/media/link properties and net/node/key fields can alter kernel networking behavior, but this header itself stores no state. Persistence is external to the caller or service that replays configuration.

Dependencies and integration points: Integrates with Linux generic netlink, the TIPC subsystem, TIPC tooling such as `tipc`, and socket diagnostics. Attribute comments encode expected payload types (`u32`, `u64`, string, flag, nested, TLV, `sockaddr_storage`) and must remain synchronized with kernel netlink policies.

Risks: ABI numbers are stable once released; reordering breaks userspace. Nested attribute parsing must reject malformed lengths and missing mandatory fields. Key-management and bearer commands affect network reachability and security. Stats and state dumps need consistent padding and 64-bit alignment for cross-architecture callers.

Test signals: Validate with `tools/net/tipc` or equivalent netlink tests covering each command, malformed/nested attributes, dump requests, legacy address mode, UDP bearer options, key set/flush, and link-stat reset. Compile-time UAPI tests should verify max constants and userspace inclusion.
