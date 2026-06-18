# sources/distributed-fs/ceph-client/net/tipc/name_table.h

## Purpose
`name_table.h` exposes the TIPC name table data structures and lookup/publish/subscribe API to sockets, message rerouting, name distribution, groups, broadcast, node cleanup, and netlink dump code.

## Important APIs, Types, And Functions
Key constants include `TIPC_ZM_SRV`, `TIPC_PUBL_SCOPE_NUM`, `TIPC_NAMETBL_SIZE`, and `TIPC_ANY_SCOPE`. `struct publication` records the service range, publishing socket address, scope, key, id, several list memberships, and RCU callback. `struct name_table` records service hash buckets, local node-scope and cluster-scope publication lists, locks, local publication count, replicast destination count, and sequence number. `struct tipc_dest` is a small node/port destination list item. The header declares the lookup, multicast, group-build, publish/withdraw, insert/remove, subscribe/unsubscribe, init/stop, netlink dump, and destination-list helper functions.

## Control Flow
The header has no direct control flow, but it defines how callers interact with the name table: bind paths publish, unbind paths withdraw, receive/reroute paths query anycast or multicast destinations, group creation builds members from publications, node failure removes remote publications, subscriptions attach to service types, and netlink dumps enumerate the table.

## State And Persistence
The persistent objects described here are per-net and RCU-managed. Publications may be reachable from socket binding lists, node cleanup lists, scope distribution lists, local/all publication lists, and temporary notification lists. The name table itself is stored under `tipc_net(net)->nametbl` and freed through RCU during namespace teardown.

## Dependencies And Integration Points
The header forward-declares subscription, plist/nlist, group, and user-address types to keep dependencies light. It is included by `name_table.c`, `name_distr.c`, `msg.c`, `netlink.c`, `netlink_compat.c`, `net.c`, and group/socket/broadcast code. Its constants and struct layout are shared with distribution and cleanup paths.

## Risks And Edge Cases
Because `struct publication` participates in many lists, every user must understand which list head it owns and when RCU freeing is safe. `TIPC_NAMETBL_SIZE` must remain a power of two for the hash function. Scope constants affect lookup semantics across legacy and non-legacy address modes. Destination list helpers allocate with atomic GFP in hot paths and can silently fail, so callers must handle incomplete destination sets.

## Test Signals
Compile-time coverage for all users, publication lifetime tests, socket bind/unbind cleanup, remote node purge, destination-list add/pop/delete duplicate behavior, scope matching, hash distribution, and RCU/list debug checks validate the header contract.
