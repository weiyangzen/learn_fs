# sources/distributed-fs/ceph-client/net/ipv6/raw.c

Purpose: Implements IPv6 raw sockets: demultiplexing inbound packets to raw sockets, receiving ICMPv6 errors, sending raw payloads or header-included IPv6 packets, socket options/ioctls, proc reporting, and protocol registration.

Important APIs, types, and functions: `raw_v6_hashinfo` is the raw socket hash table. `raw_v6_match()`, `raw6_local_deliver()`, `raw6_icmp_error()`, and `rawv6_rcv()` are externally relevant receive-path helpers. `rawv6_sendmsg()`, `rawv6_send_hdrinc()`, `rawv6_push_pending_frames()`, `rawv6_recvmsg()`, `rawv6_bind()`, sockopt helpers, and `rawv6_prot` define socket behavior. Optional Mobile IPv6 hooks register `mh_filter`.

Control flow: Inbound delivery hashes by protocol, scans matching sockets under RCU, applies address/device/multicast filters, enforces receive buffer limits, applies ICMPv6 or MH filters, clones the skb, and queues through `rawv6_rcv()`. Receive validates xfrm policy, resets conntrack, handles checksum state including raw checksum offsets, then queues to the socket. `recvmsg` handles error queue and PMTU notifications, copies/csum-validates data, fills `sockaddr_in6`, and emits control messages.

Send flow: `rawv6_sendmsg()` validates address/protocol/scope and flow label, processes control messages/options, selects source/destination/final destination, classifies security flow, looks up route, handles `MSG_CONFIRM`/`MSG_PROBE`, and either sends a user-supplied IPv6 header through `rawv6_send_hdrinc()` or appends data with `ip6_append_data()` and pushes pending frames with checksum insertion. Header-included send allocates an skb, copies the full packet from userspace, sets metadata, applies l3mdev output, and sends via local-output netfilter.

State and persistence: Per-socket state includes raw checksum enable/offset, ICMPv6 filter bitmap, bound device/address, IPv6 options, corked write queue, and drop counters. Global state includes the raw hash table and optional MH filter pointer. Proc entries are per-net when enabled.

Dependencies and integration: Depends on IPv6 routing/output, datagram controls, xfrm policy, netfilter local-output, raw socket common code, multicast membership checks, ICMPv6 error conversion, IPv6 mroute ioctls, procfs, and protocol switch registration.

Risks and test signals: High-risk areas include checksum offset validation/insertion across fragmented corked skbs, HDRINCL MTU and userspace header handling, scope/bind validation, RCU socket traversal, MH filter lifetime, and error queue semantics. Tests should cover ICMPv6 filter masks, checksum offsets including invalid odd/too-large values, HDRINCL sends, corked multi-fragment sends, PMTU/redirect errors, multicast delivery, bound-device matching with sdif, proc listing, compat ioctls, and concurrent socket close during delivery.
