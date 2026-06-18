<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/net_namespace.h -->
# sources/distributed-fs/ceph-client/include/net/net_namespace.h

## Purpose
`net_namespace.h` defines `struct net`, network namespace reference helpers, pernet operation registration, namespace ID helpers, sysctl registration, route generation counters, and `possible_net_t` abstraction.

## Important APIs, types, and functions
Important types are `struct net`, `possible_net_t`, and `struct pernet_operations`. APIs include netns copy/get/put variants, ownership lookup, barriers, namespace lookup by fd/pid/id, pernet subsystem/device registration, net sysctl registration, route/fnhe genid helpers, ref tracker helpers, and namespace iteration macros.

## Control flow
Namespace creation clones or reuses `init_net` depending on CONFIG_NET_NS. Subsystems register pernet init/exit callbacks; cleanup runs device exits before subsystem exits, with batch exit for RCU-heavy teardown. References use `ns_ref_*` plus optional trackers. `possible_net_t` stores per-object net pointers only when namespaces are enabled.

## State and persistence
`struct net` is the central persistent runtime container for per-netns lists, devices, sockets, protocol namespaces, netfilter/conntrack/nftables state, BPF, XFRM, MPLS, MCTP, vsock, sysctls, IDR namespace IDs, ref trackers, and route generation counters. State persists for the lifetime of the network namespace and is freed after passive references drain.

## Dependencies and integration points
It depends on many per-protocol netns headers, ns_common, idr/xarray, notifier, skbuff, sysctl, user namespaces, ref trackers, and optional CONFIG blocks. It integrates every network subsystem into namespace lifecycle management.

## Risks and test signals
Risks include wrong pernet registration class, cleanup ordering with devices/sockets still present, netns ref leaks, missing `maybe_get_net` checks on dying namespaces, route-genid invalidation gaps, CONFIG_NET_NS stubs masking bugs, and tracker misuse. Tests should cover namespace create/destroy under traffic, pernet init failure unwinds, device cleanup ordering, sysctl registration, ID allocation, and refcount-tracker diagnostics.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/net_namespace.h` completely for this pass (594 lines, 15046 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/net_namespace.h -->
