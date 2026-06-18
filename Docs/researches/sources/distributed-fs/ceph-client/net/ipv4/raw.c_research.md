# sources/distributed-fs/ceph-client/net/ipv4/raw.c

## Purpose
Implements IPv4 raw sockets: protocol hash registration, inbound fanout, ICMP error reporting, sends with and without `IP_HDRINCL`, receive, bind, ICMP filter sockopt, ioctls, proc listing, and raw socket sysctl initialization.

## Important APIs, types, and functions
Exports include `raw_v4_hashinfo`, `raw_hash_sk()`, `raw_unhash_sk()`, `raw_v4_match()`, `raw_local_deliver()`, `raw_icmp_error()`, `raw_rcv()`, `raw_abort()`, seq helpers, and `raw_prot`. Send helpers include `raw_send_hdrinc()`, `raw_probe_proto_opt()`, `raw_getfrag()`, and `raw_sendmsg()`. Receive/control helpers include `icmp_filter()`, `raw_v4_input()`, `raw_err()`, `raw_recvmsg()`, `raw_bind()`, sockopt handlers, and ioctls.

## Control flow
Inbound delivery hashes by protocol, walks matching sockets under RCU, checks receive buffer capacity, applies ICMP filter and multicast source filters, clones the skb, and queues through `raw_rcv()`. `raw_rcv()` performs XFRM policy checks, resets conntrack, adjusts skb data to include the IP header, and queues it. ICMP errors find matching raw sockets using reversed addresses and convert ICMP types/codes into socket errors and optional error queue entries.

Send validates length/flags, resolves destination, processes cmsgs/options, builds `flowi4`, probes ICMP type/code for route policy when not `IP_HDRINCL`, routes, checks broadcast permission, and either sends a user-supplied IP header or appends payload and pushes pending frames. `IP_HDRINCL` validates user IHL and fills missing source/id/checksum fields before local-out netfilter.

## State and persistence
Raw sockets live in `raw_v4_hashinfo` and protocol in-use counters. Per-socket state includes inet addresses, protocol, options, ICMP filter, queues, and pending frames. Proc entries are per namespace; l3mdev sysctl defaults are initialized per net when configured.

## Dependencies and integration points
Integrates with IPv4 input, ICMP errors, IP route output, IP options/cmsg, XFRM, netfilter local-out, multicast source filters, MROUTE ioctls, procfs, inet diag, and inet protocol operations.

## Risks
Raw socket ABI is sensitive around header validation, broadcast permission, checksums, and `IP_HDRINCL`. Inbound fanout clones while walking RCU hash buckets. Send must release routes/options on all errors and preserve legacy behavior.

## Test signals
Cover bind/connect/send/receive, `IP_HDRINCL` malformed and fill-in cases, cmsgs/source routes, ICMP_FILTER, MSG_ERRQUEUE, broadcast permission, PMTU errors, XFRM drops, multicast filters, proc listing, MROUTE ioctls, and namespace/l3mdev behavior.
