# sources/distributed-fs/ceph-client/net/xfrm/xfrm_nat_keepalive.c

Purpose: `xfrm_nat_keepalive.c` sends NAT traversal keepalive packets for ESP-in-UDP XFRM states with `nat_keepalive_interval` configured. It periodically walks ESP states in a net namespace and emits one-byte UDP payload `0xff` to keep NAT mappings alive.

Important APIs and types: `struct nat_keepalive` snapshots net, family, addresses, UDP encapsulation ports, and mark from an XFRM state. Exported lifecycle functions are `xfrm_nat_keepalive_init()`, `xfrm_nat_keepalive_fini()`, `xfrm_nat_keepalive_net_init()`, `xfrm_nat_keepalive_net_fini()`, and `xfrm_nat_keepalive_state_updated()`. Per-CPU `sock_bh_locked` raw UDP sockets are allocated for IPv4 and optionally IPv6.

Control flow: State update schedules the namespace delayed work immediately when interval is nonzero. `nat_keepalive_work()` walks ESP states with `xfrm_state_walk()`. For each state, `nat_keepalive_work_single()` checks `lastused`, interval, and `nat_keepalive_expiration` under state lock, snapshots send parameters if due, and updates the earliest next run. Sending allocates a small skb, builds UDP header and payload, applies state mark, routes IPv4 with `ip_route_output_key()` and sends via `ip_build_and_send_pkt()`, or computes IPv6 UDP checksum, looks up dst, and sends via `ip6_xmit()`.

State and persistence: Per-net delayed work persists in `net->xfrm.nat_keepalive_work`. Per-state fields `nat_keepalive_interval`, `nat_keepalive_expiration`, and `lastused` drive scheduling. Per-CPU raw sockets persist for the address family until XFRM policy shutdown.

Dependencies and integration: Integrated with `xfrm_policy` net init/fini and AF init/fini, XFRM state update paths, `xfrm_user.c` NAT keepalive attribute, routing, raw control sockets, and socket net namespace switching.

Risks: Work scheduling must avoid stale namespace references. Sending after state lock release relies on a safe snapshot. Raw per-CPU socket net switching must be balanced. IPv6 checksum zero must be mangled. If intervals are too small across many SAs, the state walk and packet sends can become expensive.

Test signals: Configure ESP UDP-encap SAs with keepalive interval, verify one-byte UDP keepalives for IPv4 and IPv6, check no sends before interval after traffic updates `lastused`, namespace teardown cancellation, route failure skb freeing, mark propagation, and interval changes rescheduling work.
