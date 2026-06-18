# sources/distributed-fs/ceph-client/include/net/netns/ipv6.h

Purpose: Defines per-network-namespace IPv6 sysctl, routing, neighbor/control socket, address label, multicast routing, Segment Routing, IOAM, and optional defrag state.

Important APIs/types/functions: `struct netns_sysctl_ipv6` stores route/ICMP/fragment/xfrm sysctl headers and IPv6 behavior knobs. `struct netns_ipv6` stores `ip6_dst_ops`, device configs, peer/fqdir pointers, null entries, route stats/timers/tables/walkers/locks, fib rule state, control sockets, address hash/list state, multicast route tables, generation counters, Segment Routing and IOAM pernet data, notifier ops, address label table, and flowlabel counters. `struct netns_nf_frag` stores IPv6 netfilter defrag fqdir when enabled.

Control flow: IPv6 protocol and route paths consult sysctls and route tables, timers drive fib GC, address config uses delayed work, and control sockets serve NDISC/TCP/IGMP-like functionality.

State and persistence: Runtime per-net state protected by spinlocks, rwlocks, atomics, timers, and delayed work. No durable storage.

Dependencies/integration: Depends on IPv6 route/dst ops, sysctl, fragments, fib rules, multicast routing, addrconf, Segment Routing, IOAM, notifiers, and optional netfilter defrag.

Risks/test signals: Test route GC timers, sysctl isolation, address hash locking, fib6 generation counters, multicast route cleanup, flowlabel controls, defrag fqdir cleanup, IPv6 disabled/optional configs, and namespace teardown.
