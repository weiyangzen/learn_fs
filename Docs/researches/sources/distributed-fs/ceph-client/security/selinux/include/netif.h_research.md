## sources/distributed-fs/ceph-client/security/selinux/include/netif.h

### Purpose
`netif.h` declares the SELinux network-interface SID cache API. Network devices do not carry SELinux security blobs, so SELinux maintains a separate namespace/interface-index to SID mapping.

### Important APIs, types, and functions
The interface has `sel_netif_flush()` and `sel_netif_sid(struct net *ns, int ifindex, u32 *sid)`.

### Control flow
Network hook paths call `sel_netif_sid()` during ingress/egress checks to obtain the interface SID and then perform `NETIF__INGRESS` or `NETIF__EGRESS` AVC checks. Policy reset paths call `sel_netif_flush()`.

### State and persistence
The header stores no state. The implementation maintains an in-memory cache derived from policy, keyed by network namespace and ifindex.

### Dependencies and integration points
It includes `net/net_namespace.h` and is used by `hooks.c` netfilter and socket receive paths.

### Risks
Interface rename/reindex and network namespace lifetime handling must be correct in the implementation. Stale entries after policy reload would mislabel network checks.

### Test signals
Exercise packet ingress/egress with labeled interfaces, network namespaces, interface creation/destruction, and policy reload cache flushing.
