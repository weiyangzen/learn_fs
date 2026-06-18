## sources/distributed-fs/ceph-client/security/selinux/include/netnode.h

### Purpose
`netnode.h` declares the SELinux network-node SID cache API for IP address labels. These lookups are hot in per-packet checks, so implementation-side caching avoids repeated policy lookups.

### Important APIs, types, and functions
The interface has `sel_netnode_flush()` and `sel_netnode_sid(const void *addr, u16 family, u32 *sid)`.

### Control flow
Network receive, bind, and postroute checks call `sel_netnode_sid()` for source or destination addresses, then check node permissions such as `NODE__RECVFROM`, `NODE__SENDTO`, or socket `NODE_BIND`.

### State and persistence
The header has no state. The implementation maintains policy-derived, in-memory address-to-SID cache entries for IPv4/IPv6 families.

### Dependencies and integration points
It depends on Linux scalar types and is consumed by `hooks.c` networking and netfilter paths.

### Risks
Address family parsing and cache invalidation are correctness-sensitive. Unknown or malformed addresses can cause packet drops or unlabeled fallbacks depending on caller behavior.

### Test signals
Test IPv4 and IPv6 node labels, fragmented packet parsing, bind/connect/ingress/egress checks, policy reload flushing, and unknown address family handling.
