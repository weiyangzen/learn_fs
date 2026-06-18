<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/neighbour.h -->
# sources/distributed-fs/ceph-client/include/net/neighbour.h

## Purpose
`neighbour.h` is the generic neighbour-cache core interface shared by ARP, IPv6 NDISC, and other link-layer resolution users. It defines table, parameter, entry, proxy-entry, stats, lookup, update, output, sysctl, and sequencing contracts.

## Important APIs, types, and functions
Core types are `struct neigh_parms`, `struct neigh_statistics`, `struct neighbour`, `struct neigh_ops`, `struct pneigh_entry`, `struct neigh_hash_table`, `struct neigh_table`, and `struct neigh_seq_state`. APIs cover table init/clear, lookup/create/destroy, event sending, update, probe, address changes, interface teardown, output functions, parameter allocation/release, proxy neighbour operations, iteration, sysctl registration, reference helpers, and header-cache output helpers.

## Control flow
Protocol tables provide hash/equality/constructor/solicit/output callbacks. Lookups use RCU hash tables; creation initializes entries and queues unresolved packets. `neigh_event_send` updates usage and starts resolution when NUD state is not connected/delay/probe. Output chooses cached hardware header fast path when connected and available, otherwise calls the entry output op. GC, timers, managed lists, proxy queues, and sysctls are driven by the implementation.

## State and persistence
State is substantial and runtime-only: per-table hash/proxy tables, gc lists/work/timers, per-CPU stats, parameter lists and sysctls, per-neighbour NUD state, timers, skb queues, hardware address seqlock, refcounts, device trackers, and header cache. No persistent storage exists.

## Dependencies and integration points
It depends on netdevice, skb queues, timers, delayed work, RCU, refcount, seqlocks, rtnetlink, sysctl, seq_file, and `neighbour_tables.h`. It integrates with ARP, NDISC, bridge netfilter header-cache paths, and route output.

## Risks and test signals
Risks include RCU hash resize races, refcount underflow, NUD timer transitions, unresolved queue byte limits, header-cache headroom checks, sysctl parameter aliasing, device teardown with live entries, proxy queue handling, and lock ordering between table, neighbour, and device locks. Tests should cover lookup/create/update, GC thresholds, unresolved queue drops, output fast/slow paths, device down/carrier down, sysctl changes, proxy neighbours, and concurrent hash resize.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/neighbour.h` completely for this pass (617 lines, 17619 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/neighbour.h -->
