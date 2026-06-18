<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mctp.h -->
# sources/distributed-fs/ceph-client/include/net/mctp.h

## Purpose
`mctp.h` defines the kernel Management Component Transport Protocol core ABI: packet header helpers, socket state, tag/key lifetime rules, route and neighbour structures, and subsystem init/exit entry points.

## Important APIs, types, and functions
Important types are `struct mctp_hdr`, `struct mctp_sock`, `struct mctp_sk_key`, `struct mctp_skb_cb`, `struct mctp_flow`, `struct mctp_route`, `struct mctp_dst`, and `struct mctp_neigh`. Helpers classify EIDs, access skb headers/control blocks, allocate local tags, look up routes, send local output, add/remove local routes, manage default networks, and initialize route/neighbour/device subsystems.

## Control flow
Sockets bind local/peer EID and message type, allocate tags for request/response flows, and use `mctp_sk_key` lookup across per-socket and per-netns lists. Routing resolves destination network/EID to either direct device addressing or a gateway. Incoming packets set skb control metadata, match keys for sockets or reassembly, and may release device flow state through MCTP device operations.

## State and persistence
State is per-socket bind/tag lists and expiry timers, per-key reassembly skb chains and refcounts, per-netns route/key lists, per-device flow state, default network IDs, and RCU/refcounted routes/neighbours. Nothing is persisted outside runtime kernel objects.

## Dependencies and integration points
It depends on net namespaces, sockets, skb control blocks/extensions, netdevices, MCTP UAPI, timers, RCU, refcounts, and `mctpdevice.h`. It integrates sockets, routes, neighbours, and physical bindings.

## Risks and test signals
Risks include key lock ordering with netns `keys_lock`, tag expiry races, reassembly cleanup after socket unhash, skb control-block magic assumptions, route RCU lifetime, local/gateway route ownership, and MCTP flow extension leaks. Tests should cover tag allocation/drop, reply reassembly, socket close during reassembly, route add/remove on netdev unregister, extended address recvmsg, and broadcast/null/unicast EID checks.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mctp.h` completely for this pass (360 lines, 9743 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mctp.h -->
