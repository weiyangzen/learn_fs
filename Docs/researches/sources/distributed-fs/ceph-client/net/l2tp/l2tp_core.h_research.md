# sources/distributed-fs/ceph-client/net/l2tp/l2tp_core.h

## Purpose
Declares the internal L2TP core contracts shared by the core, management layer, pseudowire drivers, and IP encapsulation modules. It defines tunnel/session structures, configuration structures, statistics, callback interfaces, exported APIs, and small helpers.

## Important APIs and types
- `struct l2tp_stats` contains atomic TX/RX packet, byte, error, sequencing, cookie, out-of-order, and invalid counters.
- `struct l2tp_session_cfg` and `struct l2tp_tunnel_cfg` carry netlink or kernel-created configuration into core creation paths.
- `struct l2tp_session` stores IDs, cookies, L2-specific type, sequence state, reorder queue, list/hash nodes, callbacks, stats, and private pseudowire storage.
- `struct l2tp_tunnel` stores tunnel IDs, version, encapsulation, stats, namespace, tunnel socket, session list, refcount, and delete work.
- `struct l2tp_nl_cmd_ops` lets pseudowire modules plug session create/delete behavior into generic netlink.
- Export declarations cover tunnel/session lookup, lifecycle, RX/TX helpers, netlink pseudowire registration, IP-encap ioctl helper, and socket-to-tunnel lookup.

## Control flow contracts
The header documents that lookup APIs return referenced objects. Creation is two-phase: allocate/create then register. Destruction is asynchronous through delete helpers. Pseudowires receive packets through `recv_skb`, clean up through `session_close`, and optionally render debugfs-specific state through `show`.

## State and persistence behavior
The structures describe in-kernel runtime state only. There is no disk persistence. The `priv[]` flexible array allows pseudowire modules to attach session-local state with the same lifetime as the core session. Inline helpers compute L2-specific lengths, tunnel destination MTU, XFRM usage, and ensure optional v3 cookie/sublayer bytes are linear in an skb.

## Dependencies and integration points
The header depends on socket, dst, refcount, optional XFRM, skb, and L2TP UAPI definitions. It is the central integration point between `l2tp_core.c`, `l2tp_netlink.c`, `l2tp_debugfs.c`, `l2tp_eth.c`, `l2tp_ip.c`, `l2tp_ip6.c`, and PPPoL2TP.

## Risks and test signals
Contract risks include callers failing to drop lookup references, pseudowires deleting sessions without honoring asynchronous lifetime, and header-length/cookie/L2-specific configuration changes not followed by `l2tp_session_set_header_len`. Tests should check refcount balance, callback invocation, MTU/header computations, and v3 optional-data linearization on nonlinear skbs.
