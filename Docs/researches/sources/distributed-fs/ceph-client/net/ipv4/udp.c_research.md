# sources/distributed-fs/ceph-client/net/ipv4/udp.c

## Purpose
This file is the main IPv4 UDP transport implementation. It owns UDP bind-port allocation, socket hash tables, unicast/multicast lookup, sendmsg/recvmsg, corking, checksum setup, receive queue memory accounting, tunnel encapsulation dispatch, proc/BPF iteration, per-net hash-table initialization, and the exported `udp_prot` protocol operations used by AF_INET datagram sockets.

## Important APIs, Types, and Functions
Key state is carried by `struct udp_table`, `struct udp_hslot`, `struct udp_sock`, `struct inet_sock`, `struct sk_buff`, `struct flowi4`, and per-net `net->ipv4.udp_table`. Important entry points include `udp_lib_get_port()`, `__udp4_lib_lookup()`, `udp_err()`, `udp_sendmsg()`, `udp_recvmsg()`, `udp_rcv()`, `udp_lib_unhash()`, `udp_lib_rehash()`, `udp_lib_setsockopt()`, `udp_lib_getsockopt()`, `udp_poll()`, `udp_abort()`, `udp_init()`, and proc iterator helpers.

## Control Flow
Bind flow chooses a random ephemeral port or validates a requested port under UDP hash locks, checks reuse/reuseport/device/source-address compatibility, then inserts the socket into primary and secondary hash chains. Lookup first tries exact four-tuple state, then secondary port-address chains, optional BPF socket lookup, wildcard sockets, and finally the primary hash to cover rehash races. Send flow resolves destination from `sendmsg()` or connected state, processes UDP/IP control messages and cgroup BPF, routes through IPv4, builds a UDP skb via `ip_make_skb()` or corked `ip_append_data()`, sets checksum/GSO state, and calls `ip_send_skb()`. Receive flow validates header length and checksum state, tries early-steal demux, dispatches multicast/broadcast fanout or unicast delivery, applies XFRM policy, encapsulation hooks, socket filter, pktinfo preparation, and queueing. `recvmsg()` drains the per-socket reader queue, validates or copies checksum, emits cmsgs, runs UDP4 recvmsg BPF address rewrite, and consumes/free skbs.

## State and Persistence Behavior
Persistent UDP state is the per-net/global hash table, per-socket port/address/four-tuple hash membership, reuseport group membership, cork state in `udp_sock`, cached RX dst, receive queues, per-NUMA producer queues, memory counters, tunnel callbacks, GRO state, and sysctl memory thresholds. Queue memory is explicitly moved between `sk_receive_queue` and `reader_queue`; forward allocation is reclaimed by UDP-specific destructors. Per-net init may allocate a private UDP hash table or fall back to the global one.

## Dependencies and Integration Points
The file integrates with IPv4 routing, IP options, ICMP errors, XFRM policy, netfilter-independent packet delivery, cgroup BPF hooks, socket filters, reuseport, RPS/NAPI busy poll, UDP tunnel callbacks, GRO/GSO helpers, procfs, BPF iterators, pernet operations, sysctls, and SNMP MIB accounting.

## Risks
The riskiest areas are lock ordering across primary/secondary/four-tuple hashes, reuseport detachment during rehash/unhash, receive memory accounting split across producer and reader queues, checksum validation during peek/truncate/error paths, tunnel encap return-code semantics, and correctness under connected-socket address changes. GSO rejects checksum-disabled and XFRM-transformed paths; changing these checks can create invalid wire packets.

## Test Signals
Useful signals include bind collision/reuseport tests, ephemeral port distribution, connected and wildcard lookup under address rehash, sendmsg with cork/GSO/IP options/BPF, ICMP PMTU and hard-error reporting, UDP GRO and tunnel encap receive, multicast fanout with device/source filters, checksum-drop accounting, proc/BPF socket iteration, per-net hash allocation fallback, and close/abort races.
