# sources/distributed-fs/ceph-client/net/ipv6/udp.c

## Purpose
Implements UDP over IPv6 for the kernel INET6 stack. It supplies the `IPPROTO_UDP` IPv6 protocol handler, the `SOCK_DGRAM` protocol switch, socket operations through `udpv6_prot`, `/proc/net/udp6` support, UDPv6 receive demultiplexing, multicast delivery, ICMPv6 error processing, corked and uncorked sends, IPv4-mapped fallback, GSO setup, GRO-related receive controls, UDP tunnel encapsulation hooks, and BPF/cgroup integration.

## Important APIs, types, and functions
Key exported/public entry points are `udp6_ehashfn`, `__udp6_lib_lookup`, `udp6_lib_lookup_skb`, `udp6_lib_lookup`, `udpv6_recvmsg`, `udpv6_encap_enable`, `udpv6_sendmsg`, `udpv6_rcv`, `udp_v6_early_demux`, `udp6_proc_init`, `udp6_proc_exit`, `udpv6_init`, and `udpv6_exit`. Socket behavior is registered through `struct proto udpv6_prot` and `struct inet_protosw udpv6_protosw`; receive path dispatch is registered in `net_hotdata.udpv6_protocol`. Important helpers include `compute_score`, `udp6_lib_lookup1/2/4`, `udpv6_queue_rcv_one_skb`, `__udp6_lib_mcast_deliver`, `udp6_csum_init`, `udp_v6_send_skb`, and `udp_v6_push_pending_frames`.

## Control flow
Inbound packets enter `udpv6_rcv`, which validates UDP header length, trims excess payload, accepts jumbograms, initializes checksum state, attempts early-demux socket stealing, handles multicast through `__udp6_lib_mcast_deliver`, and otherwise does unicast socket lookup. Socket delivery runs XFRM policy checks, optional encapsulation receive hooks, cBPF/eBPF socket filters, checksum conversion, queue accounting, and receive-buffer error handling. Missing unicast sockets pass XFRM policy and checksum checks before incrementing no-port stats and emitting ICMPv6 port unreachable.

Socket lookup first tries destination-address hash chains and optional four-tuple hash acceleration, then reuseport/BPF sk_lookup, wildcard sockets, and a primary-hash fallback for receive-address-change races. Send path in `udpv6_sendmsg` validates sockaddr inputs, diverts IPv4-mapped destinations to IPv4 UDP when allowed, parses control messages and flow labels, runs cgroup BPF sendmsg hooks, resolves route/options, then either builds one skb on the lockless fast path or corks with `ip6_append_data`. `udp_v6_send_skb` writes the UDP header, validates UDP GSO constraints, computes hardware or software checksums, and submits with `ip6_send_skb`.

## State and persistence behavior
State is in sockets, net namespace UDP tables, per-socket UDP cork state (`udp_sock.pending`, `len`, GSO size), IPv6 destination cache, receive queues, stats counters, and static branch keys. No durable persistence exists. `udpv6_destroy_sock` flushes corked frames, marks dead sockets, calls encapsulation destroy hooks, decrements UDP encapsulation static branches, and cleans tunnel GRO state. `/proc/net/udp6` is generated dynamically from socket hash iteration.

## Dependencies and integration points
Depends on IPv6 routing, address selection, raw/protocol dispatch, netfilter IPv6 hooks, XFRM policy/input, BPF cgroup hooks and sk_lookup, reuseport, UDP tunnel encapsulation, GRO/GSO helpers, procfs seq files, ICMPv6, Segment Routing destination extraction, and common IPv4 UDP tables. Integration with UDP tunnels is through `udp_sk(...)->encap_*` callbacks and `udpv6_encap_needed_key`.

## Risks and test signals
Risk centers on checksum handling, zero-checksum tunnel policy, address/port hash races, reuseport rescoring, socket refcounting from early demux, cork state recovery, GSO size validation, and ICMP error matching for tunnels with non-symmetric ports. Test signals include IPv6 UDP send/receive, IPv4-mapped behavior with and without `IPV6_V6ONLY`, multicast fanout, zero-checksum tunnel sockets, UDP GSO/GRO, cork/MSG_MORE, BPF sendmsg/sk_lookup rewrite, PMTU/ICMP errors, `/proc/net/udp6` visibility, packet drops with UDP MIB counters, and XFRM-policy rejection.
