# sources/distributed-fs/ceph-client/include/net/ipv6.h

Purpose: Main internal IPv6 networking header for constants, address helpers, fragmentation helpers, stats macros, router alert chain, flow labels, tx options, socket controls, input/output prototypes, extension-header parsing, multicast, proc/sysctl hooks, and small socket setters.

Important APIs/types/functions: Defines Next Header constants, address type/scope bits, extension-header limits, `frag_hdr`, fragmentation iterator/state structs, `ipv6_txoptions`, `ip6_flowlabel`, `ipcm6_cookie`, flowlabel helpers, address compare/prefix/hash helpers, flowlabel generation, header manipulation helpers, and prototypes for IPv6 receive, transmit, routing lookup, output, forwarding, datagram connect, socket options, error queues, multicast, proc/sysctl, and conversion helpers.

Control flow: Packet send paths build `ipcm6_cookie`, merge tx options/flow labels, select route/dst, append or build skb data, fragment if needed, then call IPv6 output. Receive paths enter `ipv6_rcv`, parse extension headers, route/input/forward, and deliver protocols. Inline helpers gate source binding, RA acceptance, PMTU behavior, and auto flowlabel generation via per-net sysctls.

State and persistence: State includes per-socket IPv6 options and flowlabel lists, refcounted `ipv6_txoptions`, global router-alert chain protected by rwlock, per-net MIB counters, sysctl-controlled limits, and flowlabel refcounts/expiration. Header-owned state is mostly declarations; storage lives in implementation/netns structs.

Dependencies/integration: Integrates with sk_buffs, sockets, flow dissector, inet DSCP, SNMP/MIB, addrconf, route code, multicast, procfs, sysctl, and optional IPv6 build stubs.

Risks: Address helper assumptions on prefix length and unaligned 64-bit access must hold; tx option refcounts use RCU and can leak/use-after-free if mishandled; extension-header limits are security-sensitive; flowlabel generation must avoid leaking useful hash data. Test signals include address classification, extension-header limit drops, fragmentation/fraglist, flowlabel socket options, source preference setters, multicast joins, error queue delivery, IPv6-only bind rules, and IPv6 disabled stubs.
