# sources/distributed-fs/ceph-client/net/tipc/bcast.c

## Purpose
This file implements TIPC broadcast and multicast send/receive behavior, including broadcast-link state, bearer selection, replicast versus broadcast method selection, broadcast ACK/sync handling, netlink configuration, and multicast duplicate filtering.

## Important APIs, Types, And Functions
Key state is `struct tipc_bc_base`, containing the broadcast send link, socket wakeup input queue, per-bearer destination counts, primary bearer, broadcast/replicast capability flags, forced mode flags, and ratio-derived threshold. Exported functions include `tipc_bcast_init()`, `tipc_bcast_stop()`, `tipc_bcast_xmit()`, `tipc_mcast_xmit()`, `tipc_bcast_rcv()`, `tipc_bcast_ack_rcv()`, `tipc_bcast_sync_rcv()`, peer add/remove, bearer destination count updates, netlink setters, nlist helpers, and multicast filtering.

## Control Flow
Initialization allocates `tipc_bc_base`, initializes the broadcast lock, and creates a broadcast link. Destination count changes recalculate the primary bearer and MTU. Broadcast transmit queues packets through the broadcast link under `bclock`, then emits through the primary bearer or clones across all bearers. Multicast can clone locally, choose replicast or broadcast based on capabilities/configuration/threshold, send a sync message when switching methods, and deliver local copies to sockets. Receive paths validate net id and link state, feed broadcast protocol or data into link handlers, send any retransmit queue, and drain socket wakeups.

## State And Persistence
Broadcast state is per net namespace and volatile. The broadcast link tracks peer ACK state and windows. Netlink-set properties such as mode, ratio, and window live in memory until changed or namespace teardown.

## Dependencies And Integration Points
The file depends on TIPC socket delivery, messages, link layer, name table destination lists, bearer transmit helpers, netlink attributes, and sysctl `sysctl_tipc_bc_retruni`. It integrates tightly with node/link management.

## Risks And Test Signals
Risks include MTU shrinkage across bearers, inconsistent transient destination counts, broadcast/replicast duplicate ordering, ACK/gap retransmission handling, congestion accounting, and lock ordering around `bclock`. The source snapshot also shows duplicated lines in `tipc_bcast_xmit()` and peer removal that should be build-checked. Test signals include multicast to local and remote destinations, broadcast across multiple bearers, forced mode and auto-select netlink changes, ACK/NACK retransmission, peer add/remove under traffic, and duplicate SYN filtering when method changes.
