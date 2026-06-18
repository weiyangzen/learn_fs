# sources/distributed-fs/ceph-client/security/landlock/net.c

## Purpose

`net.c` implements Landlock TCP port access control. It lets rulesets allow bind/connect rights for specific TCP ports and enforces these rules through socket bind/connect LSM hooks.

## Important APIs, Types, and Functions

`landlock_append_net_rule()` inserts a `LANDLOCK_KEY_NET_PORT` rule keyed by network-order port. `current_check_access_socket()` parses socket addresses, validates family/length consistency, builds audit network data, initializes per-layer masks, checks matching port rules, logs denials, and returns `-EACCES` when needed. `hook_socket_bind()` enforces `LANDLOCK_ACCESS_NET_BIND_TCP` for TCP sockets. `hook_socket_connect()` enforces `LANDLOCK_ACCESS_NET_CONNECT_TCP`. `landlock_add_net_hooks()` registers the socket hooks.

## Control Flow

Syscall code adds port rules with relative access rights upgraded to include unhandled net rights. At bind/connect time, non-TCP sockets are ignored. The checker handles `AF_UNSPEC`, IPv4, and IPv6 address forms, preserving network-stack error semantics for invalid family or length cases where possible. It finds the rule for the port, initializes layer masks for the requested right, unsets allowed layers via `landlock_unmask_layers()`, and denies/logs if any layer remains.

## State and Persistence Behavior

Network rules are stored in the ruleset red-black tree keyed by `htons(port)`. No per-socket Landlock state is stored. Audit data is transient.

## Dependencies and Integration Points

The file depends on `CONFIG_INET`, socket structures, IPv4/IPv6 sockaddr layouts, `sk_is_tcp()`, Landlock rulesets/credentials/audit, and LSM socket hooks. It is omitted with stubs when INET is disabled.

## Risks and Test Signals

Family handling is security and compatibility sensitive, especially `AF_UNSPEC`, IPv6 length checks, and non-TCP stream protocols. Tests should cover TCP bind/connect allow/deny, port byte order, IPv4/IPv6, invalid addrlen, `AF_UNSPEC`, MPTCP/SMC/SCTP non-enforcement, and audit records.
