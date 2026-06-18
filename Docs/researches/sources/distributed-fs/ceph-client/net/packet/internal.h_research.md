# sources/distributed-fs/ceph-client/net/packet/internal.h

## Purpose
`internal.h` defines the private AF_PACKET data model shared by the packet socket implementation and packet sock_diag module. It contains packet socket state, mmap ring descriptors, fanout group layout, rollover stats, multicast membership records, and flag helpers.

## Important APIs, types, and functions
`struct packet_mclist` tracks per-socket device memberships for multicast, promiscuous, allmulti, and unicast filters, including reference count and deferred removal list node. `struct tpacket_kbdq_core` is the TPACKET_V3 kernel block descriptor queue state: block array, current block, sequence, offsets, timeout, feature flags, and fill-in-progress lock. `struct packet_ring_buffer` abstracts RX/TX ring geometry, backing page vector, pending TX refcounts, and either V1/V2 RX owner map or V3 block queue.

`struct packet_fanout` represents a fanout group with net namespace, id, type, flags, member count, BPF program or round-robin counter, group packet hook, and flexible member socket array. `struct packet_rollover` stores rollover distribution counters and recent-flow history. `struct packet_sock` embeds `struct sock` first and adds packet-specific state including fanout pointer, stats, rings, bind and ring locks, flags, ifindex, protocol, rollover, multicast list, mapped VMA count, TPACKET settings, completion, cached netdev pointer, packet hook, and drop counter.

The header exports `fanout_mutex`, `PACKET_FANOUT_MAX`, `pkt_sk()`, `enum packet_sock_flags`, `packet_sock_flag_set()`, and `packet_sock_flag()`.

## Control flow and state
This header has no executable control flow beyond inline flag helpers. Its state definitions drive ownership and synchronization in `af_packet.c`: `packet_sock` lifetime is tied to socket lifetime, ring memory is swapped in/out under locks, V3 block queue state is updated under receive queue lock plus block fill rwlock, and fanout groups are protected by the global fanout mutex plus per-group spinlock.

## Dependencies and integration points
The structures use kernel networking primitives such as `struct sock`, `struct sk_buff`, `struct packet_type`, `struct net_device`, `possible_net_t`, RCU pointers, refcounts, hrtimers, completions, and UAPI TPACKET stats/version types. `diag.c` reads these fields to expose monitoring state.

## Risks and edge cases
Because these structures are shared across hot-path packet receive/transmit and diagnostics, layout or semantic changes can break cacheline-sensitive code, lock ordering, RCU access rules, or userspace-visible status behavior. The union in `packet_ring_buffer` means code must correctly distinguish V1/V2 owner maps from V3 block queues. `struct packet_sock` embeds `struct sock` first, so that invariant must be preserved for container casts.

## Test signals
Compile-time coverage should catch missing includes and layout references. Runtime validation comes indirectly from AF_PACKET socket creation, ring setup, fanout tests, sock_diag dumps, and stress tests that exercise close, mmap, fanout membership, and netdevice teardown.
