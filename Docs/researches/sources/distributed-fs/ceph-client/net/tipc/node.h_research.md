# sources/distributed-fs/ceph-client/net/tipc/node.h

## Purpose
`node.h` exposes TIPC peer-node capability bits and the node/link management API used by bearer, discovery, link, broadcast, name distribution, socket, crypto, netlink, and namespace cleanup code.

## Important APIs, Types, And Functions
The header defines capability bits such as `TIPC_SYN_BIT`, `TIPC_BCAST_SYNCH`, `TIPC_BCAST_STATE_NACK`, `TIPC_BLOCK_FLOWCTL`, `TIPC_BCAST_RCAST`, `TIPC_NODE_ID128`, `TIPC_LINK_PROTO_SEQNO`, `TIPC_MCAST_RBCTL`, `TIPC_GAP_ACK_BLOCK`, `TIPC_TUNNEL_ENHANCED`, `TIPC_NAGLE`, and `TIPC_NAMED_BCAST`, then combines them as `TIPC_NODE_CAPABILITIES`. It declares node lifecycle, lookup/accessor, creation, address trial, discovery validation, link deletion/property/name lookup, transmit/broadcast, publication subscription, connection tracking, MTU/up/capability queries, netlink node/link/monitor/peer/key handlers, optional crypto accessors, and `tipc_node_pre_cleanup_net()`.

## Control Flow
The header has no executable flow. It defines how callers progress from discovery (`tipc_node_try_addr()`, `tipc_node_check_dest()`), to link establishment and data movement (`tipc_node_xmit*()`, `tipc_rcv()` through `node.c`), to cleanup (`tipc_node_delete_links()`, `tipc_node_stop()`, `tipc_node_pre_cleanup_net()`), and to user-space control through netlink handlers.

## State And Persistence
The private `struct tipc_node` is intentionally opaque here. Persistent state is managed in `node.c`, while this header exposes only references and APIs for obtaining IDs, addresses, capabilities, crypto handles, link names, and status.

## Dependencies And Integration Points
The header includes `addr.h`, `net.h`, `bearer.h`, and `msg.h`, reflecting that node logic sits between addressing/network identity, bearer media, and message/link protocol. Optional crypto declarations are gated by `CONFIG_TIPC_CRYPTO`. Netlink prototypes connect `node.c` to the operation table in `netlink.c`.

## Risks And Edge Cases
Capability bit definitions are wire-visible negotiation state; changing `TIPC_NODE_CAPABILITIES` affects cluster feature decisions such as broadcast mode, named broadcast, tunnel behavior, and gap ACK support. The API mixes reference-counted node pointers, RCU traversal assumptions, RTNL-locked netlink calls, and optional crypto pointers, so callers must respect locking/lifetime rules documented in implementations.

## Test Signals
Compile tests across crypto and non-crypto builds, capability negotiation tests with mixed-version peers, discovery/link setup tests, node transmit/receive API coverage, netlink operation table coverage, and namespace cleanup tests validate the exported contract.
