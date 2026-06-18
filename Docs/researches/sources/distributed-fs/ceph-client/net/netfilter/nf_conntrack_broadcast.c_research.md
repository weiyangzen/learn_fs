# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_broadcast.c

## Purpose
`nf_conntrack_broadcast.c` is a helper utility for broadcast UDP-like protocols. It creates a permanent expectation for replies from hosts in the local broadcast subnet back to the originating local socket.

## Important APIs, Types, And Functions
The exported function is `nf_conntrack_broadcast_help()`. It inspects the skb route, socket/netns relationship, IPv4 broadcast address, primary interface address mask, master helper, and master conntrack helper extension. It allocates and installs an `nf_conntrack_expect` with `NF_CT_EXPECT_PERMANENT`.

## Control Flow
The helper only acts on locally generated original-direction packets whose route is marked `RTCF_BROADCAST` and whose socket net namespace matches the conntrack net. It finds the primary interface address whose broadcast address equals the packet destination, uses that mask for expected source addresses, copies the reply tuple from the master conntrack, narrows source UDP port to the helper's port when available, installs a permanent expectation, and refreshes the master timeout.

## State And Persistence
State is a permanent expectation linked to the master conntrack and global expectation table until removed with the master/helper lifecycle. No module-private persistent structures exist.

## Dependencies And Integration Points
The function depends on IPv4 routing, inet device address lists under RCU, conntrack helpers, expectations, zones, and net namespace helpers.

## Risks
The helper is IPv4-specific and assumes RCU-safe address iteration. Permanent expectations can be broad if masks are wrong; primary address selection and broadcast matching are important. It deliberately ignores non-local sockets, non-broadcast routes, and reply-direction packets.

## Test Signals
Test local broadcast traffic on primary/secondary addresses, namespace mismatch, non-broadcast route, reply-direction packet, missing helper pointer, expectation allocation failure, zone propagation, timeout refresh, and permanent expectation removal when the master dies.
