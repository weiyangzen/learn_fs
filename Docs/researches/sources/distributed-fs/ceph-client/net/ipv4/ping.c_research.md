# sources/distributed-fs/ceph-client/net/ipv4/ping.c

## Purpose
Implements Linux ping sockets, allowing ICMP echo traffic without raw socket privileges for users in the namespace ping group range. It covers permission checks, identifier allocation, bind/connect/send/receive, ICMP error delivery, IPv4 plus shared IPv6 hooks, and `/proc/net/icmp`.

## Important APIs, types, and functions
Core globals are `ping_table` and `pingv6_ops`. `ping_get_port()` allocates or binds ICMP identifiers. `ping_lookup()` finds sockets by namespace, identifier, bound address, family, and device. `ping_init_sock()` enforces `ping_group_range`. `ping_bind()`, `ping_v4_sendmsg()`, `ping_recvmsg()`, `ping_rcv()`, and `ping_err()` implement behavior. `ping_prot` is the protocol operations table.

## Control flow
Socket init checks effective and supplementary groups against the configured range. Bind validates addresses, rejects invalid multicast/broadcast cases, may adjust scoped IPv6 device binding, allocates an ICMP identifier, stores local address, and resets dst cache. Send consumes the user ICMP header, accepts only echo/extended echo request types with code zero, applies cmsg/options, routes, checks broadcast permission, builds a fake header using `inet_sport` as echo id, appends payload, finalizes checksum, and pushes frames. Receive dequeues datagrams and fills source/control messages. Input restores the ICMP header, looks up by id, and queues or drops. Error handling maps ICMP/ICMPv6 errors to socket errors and optional error queue entries.

## State and persistence
State is in per-net `ping_port_rover`, the global ping hash table, socket inet fields, and receive queues. Hash-table writers use a spinlock; lookup is RCU-based. Proc init randomizes the namespace rover.

## Dependencies and integration points
Integrates with ICMP receive/error paths, IPv4 routing, cgroup BPF connect hooks, socket memory accounting, inet datagram helpers, IP options/cmsg, IPv6 through `pingv6_ops`, and procfs seq_file.

## Risks
Identifier allocation/reuse is security-sensitive because ping sockets rely on ICMP id. Permission checks must correctly handle group ranges. Bind can temporarily modify `sk_bound_dev_if` and must restore on failure. Send mutates the msghdr iterator by consuming the ICMP header. Lookup must respect namespace, bound address, and device.

## Test signals
Cover permission allow/deny, automatic/explicit identifiers, reuse, bind to local/nonlocal/broadcast/multicast, cgroup hook rejection, echo and extended echo sends, invalid type/code, broadcast permission, PMTU/error queue, receive truncation/control messages, no-socket drops, proc listing, and IPv6 when enabled.
