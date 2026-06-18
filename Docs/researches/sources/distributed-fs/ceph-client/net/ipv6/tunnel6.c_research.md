# sources/distributed-fs/ceph-client/net/ipv6/tunnel6.c

## Purpose
`tunnel6.c` is the generic IPv6 outer tunnel demultiplexer for IPv6-in-IPv6, IPv4-in-IPv6, and optional MPLS-in-IPv6. It lets tunnel implementations register prioritized handlers behind the IPv6 protocol numbers and provides ICMPv6 error dispatch plus optional xfrm input callbacks.

## Important APIs, types, and functions
Global RCU lists are `tunnel6_handlers`, `tunnel46_handlers`, and `tunnelmpls6_handlers`, protected for updates by `tunnel6_mutex`. Exported APIs `xfrm6_tunnel_register()` and `xfrm6_tunnel_deregister()` insert or remove `struct xfrm6_tunnel` handlers by address family and priority.

Receive functions are `tunnel6_rcv()`, `tunnel46_rcv()`, and `tunnelmpls6_rcv()`. Error dispatchers are `tunnel6_err()`, `tunnel46_err()`, and `tunnelmpls6_err()`. When `CONFIG_INET6_XFRM_TUNNEL` is enabled, `tunnel6_rcv_cb()` and `tunnel6_input_afinfo` integrate with xfrm input callbacks. Module lifecycle is `tunnel6_init()` and `tunnel6_fini()`.

## Control flow
Registration selects the handler list by family (`AF_INET6`, `AF_INET`, or `AF_MPLS`), walks it under the mutex, rejects duplicate priority, and inserts before the first lower-priority position. Deregistration finds the exact handler pointer, unlinks it, unlocks, and calls `synchronize_net()` so in-flight RCU readers complete before the handler can disappear.

Receive handlers first ensure enough bytes are present for the expected inner header, then walk the family-specific handler list under RCU. A handler consumes the skb by returning zero. If no handler accepts the packet, the code sends ICMPv6 destination-unreachable/port-unreachable and frees the skb. Error handlers similarly walk registered tunnel handlers until one accepts the error; otherwise they return `-ENOENT`.

Initialization registers IPv6 protocol handlers for `IPPROTO_IPV6`, `IPPROTO_IPIP`, and optional `IPPROTO_MPLS`, then registers xfrm input afinfo when configured. Failure unwinds previously registered protocols. Exit unregisters xfrm afinfo and all protocols, logging failures.

## State and persistence
State consists only of global in-memory RCU handler lists. Handler objects are owned by registering tunnel modules; this file owns list linkage and synchronization but not handler allocation. There is no persistence beyond module lifetime.

## Dependencies and integration points
The file integrates with `inet6_add_protocol()` / `inet6_del_protocol()`, ICMPv6 generation, xfrm tunnel handler structures, optional MPLS support, optional xfrm input afinfo, skb header pull helpers, RCU, and module export symbols used by tunnel drivers.

## Risks and edge cases
Priority collisions are rejected, so registering modules must coordinate priorities. Deregistration must pass the same family and handler pointer used at registration. Receive paths free skbs when no handler accepts them, so handlers must return zero only after taking ownership. MPLS protocol registration is conditional both on build support and runtime init branching. Error dispatch depends on each handler's `err_handler` being safe for the skb/error tuple.

## Test signals
Tests should register multiple mock tunnel handlers with different priorities, verify duplicate priority rejection, receive packets accepted by first matching handler, no-handler ICMPv6 unreachable generation, IPv4/IPv6/MPLS family separation, error-handler dispatch and `-ENOENT` fallback, deregistration with in-flight receive, and init failure unwind for protocol or xfrm afinfo registration.
