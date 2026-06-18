# sources/distributed-fs/ceph-client/net/l2tp/l2tp_netlink.c

## Purpose
Implements the generic netlink management interface for L2TP. It lets privileged userspace create, delete, modify, get, and dump tunnels and sessions, emits multicast notifications, and dispatches pseudowire-specific session creation/deletion through registered command ops.

## Important APIs, types, and functions
- `l2tp_nl_family` defines the generic netlink family, policies, operations, namespace support, and multicast group.
- `l2tp_nl_cmd_ops[]` maps pseudowire type to `struct l2tp_nl_cmd_ops` registered by modules such as `l2tp_eth`.
- Tunnel commands: `l2tp_nl_cmd_tunnel_create`, `_delete`, `_modify`, `_get`, `_dump`.
- Session commands: `l2tp_nl_cmd_session_create`, `_delete`, `_modify`, `_get`, `_dump`.
- `l2tp_nl_tunnel_send` and `l2tp_nl_session_send` serialize live kernel state and stats into netlink attributes.
- `l2tp_nl_register_ops` and `l2tp_nl_unregister_ops` export pseudowire registration.

## Control flow
Tunnel creation validates required IDs, protocol version, encapsulation, and either a userspace fd or static source/destination address attributes. It allocates and registers a core tunnel, then multicasts a create notification. Delete/get/modify first acquire a referenced tunnel from the core and then notify, delete, or serialize it.

Session creation validates tunnel existence, local/peer session IDs, pseudowire type, L2TPv2 PPP-only restriction, optional v3 L2-specific/cookie/ifname settings, sequence flags, LNS mode, and reorder timeout. It autoloads a pseudowire module when possible, calls the registered pseudowire `session_create`, looks up the newly created core session, and emits a notification. Delete finds by ifname or tunnel/session ID, notifies, then calls the pseudowire delete op when available. Modify updates sequence, LNS, and timeout fields and recomputes header length when send sequencing changes.

## State and persistence behavior
The file owns the runtime pseudowire ops table under the genl lock but stores tunnel/session state in L2TP core. Netlink dumps persist cursor keys in `cb->ctx`. Notifications are transient multicast messages. No disk persistence exists.

## Dependencies and integration points
Depends on generic netlink, L2TP UAPI attributes/commands, net namespaces, L2TP core lifecycle and lookup APIs, UDP/IP socket address accessors, optional IPv6 handling, and pseudowire modules. All mutating management operations require `GENL_UNS_ADMIN_PERM`; noop is unprivileged.

## Risks and test signals
Risks include incomplete strict validation because ops use `GENL_DONT_VALIDATE_STRICT`, attribute combinations that create invalid static tunnel sockets, pseudowire module autoload races, session deletion after notification failure, stats serialization buffer limits, and stale dump cursors during concurrent deletion. Test signals include netlink create/delete/get/dump for UDP and IP tunnels, IPv4/IPv6 address attributes, session creation for Ethernet and PPP types, module autoload, permission failures, multicast notifications, and dump consistency under concurrent changes.
