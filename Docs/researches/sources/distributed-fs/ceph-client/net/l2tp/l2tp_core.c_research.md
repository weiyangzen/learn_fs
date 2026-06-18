# sources/distributed-fs/ceph-client/net/l2tp/l2tp_core.c

## Purpose
Provides the L2TP core data plane and lifetime management shared by L2TP pseudowires and encapsulations. It owns tunnel/session registries, packet receive sequencing and reordering, transmit header construction, UDP encapsulation hooks, asynchronous teardown, and per-net cleanup.

## Important APIs, types, and functions
- Per-net `struct l2tp_net` contains tunnel IDR, v2/v3 session IDRs, a v3 collision hash table, and locks.
- `l2tp_tunnel_get`, `l2tp_tunnel_get_next`, `l2tp_session_get`, `l2tp_session_get_next`, and `l2tp_session_get_by_ifname` provide refcounted lookup APIs.
- `l2tp_tunnel_create`/`l2tp_tunnel_register` and `l2tp_session_create`/`l2tp_session_register` implement two-phase construction.
- `l2tp_tunnel_delete` and `l2tp_session_delete` schedule asynchronous workqueue teardown.
- `l2tp_udp_encap_recv` is the UDP tunnel receive hook installed on UDP sockets.
- `l2tp_recv_common` parses cookies, sequence numbers, offsets, and queues valid payloads for pseudowire callbacks.
- `l2tp_xmit_skb` builds L2TP/UDP/IP or L2TP/IP headers, transmits through the tunnel socket, and updates stats.

## Control flow
Registration first reserves an IDR slot, validates or creates a tunnel socket, optionally installs UDP tunnel callbacks, then publishes the tunnel through IDR replacement. Session registration locks both the tunnel list and per-net session registry, rejects sessions when the tunnel is closing, handles L2TPv3 session-id collisions for UDP encapsulation through a collision hlist, links the session to the tunnel list, and publishes it in the proper IDR.

Receive flow for UDP begins in `l2tp_udp_encap_recv`: the UDP header is pulled, the L2TP version and data/control bit are parsed, control frames pass to userspace, data frames look up the session, version and optional v3 cookie/sublayer linearity are checked, then `l2tp_recv_common` validates cookies, negotiates sequence behavior, handles v2 offset fields, pulls the payload, queues by sequence, and invokes the pseudowire `recv_skb` callback in order.

Transmit flow starts at a pseudowire calling `l2tp_xmit_skb`. The core grows headroom, prepends v2 or v3 L2TP headers, optionally prepends UDP, calculates checksum policy, checks socket state under the socket lock, queues to IPv4 or IPv6 output, and updates tunnel/session counters.

## State and persistence behavior
Runtime state is held in per-net IDRs and htables, per-tunnel session lists and stats, and per-session cookies, sequence numbers, reorder queues, callbacks, and stats. State is not persisted outside the kernel. Lifetime is controlled by refcounts plus RCU freeing. Deletion is idempotent through `dead` bits and completes on the `l2tp` workqueue. Namespace pre-exit queues tunnel deletions and flushes the workqueue twice to process tunnel then session work.

## Dependencies and integration points
The core integrates with UDP tunnel infrastructure, IPv4/IPv6 transmit paths, XFRM policy checks indirectly through sockets, net namespaces, IDR, RCU, workqueues, tracepoints, and pseudowire modules via callbacks in `struct l2tp_session`. `l2tp_netlink.c` drives management creation/deletion, `l2tp_eth.c` supplies an Ethernet pseudowire, `l2tp_ip.c`/`l2tp_ip6.c` supply plain IP encapsulation sockets, and PPPoL2TP uses the same exported APIs.

## Risks and edge cases
High-risk areas are concurrent teardown versus lookup, v3 session-id collision handling, socket ownership/state checks during transmit, malformed short packets before `pskb_may_pull`, reorder queue expiry and sequence resynchronization, and namespace cleanup leaks. The code includes lock ordering (`tunnel->list_lock` then per-net session lock), refcounted lookups, RCU list traversal, and WARNs for unexpected non-empty IDRs.

## Test signals
Tests should exercise tunnel/session create-register-delete under UDP and IP encapsulation, duplicate IDs, v3 collision behavior, UDP control-frame pass-through, data-frame delivery, cookie mismatch drops, sequence required/optional modes, reorder timeout behavior, TX stats/error stats, module unload, and net namespace teardown with empty IDR assertions.
