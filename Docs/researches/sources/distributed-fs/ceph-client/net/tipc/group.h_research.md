# sources/distributed-fs/ceph-client/net/tipc/group.h

## Purpose

`group.h` declares the socket-facing TIPC group API and keeps `struct tipc_group` and `struct tipc_member` opaque. It is the contract between group implementation, sockets, node distribution, and diagnostics.

## Important APIs, Types, and Functions

The header declares creation/join/delete, member addition, destination-list access, self service-range lookup, loopback exclusion, receive filtering, member event processing, protocol receive processing, broadcast member/window updates, unicast and broadcast congestion checks, receive-window updates, broadcast send sequence lookup, member credit update, and socket diag filling.

## Control Flow

Sockets create a group from `struct tipc_group_req`, join it after binding/publishing, call congestion helpers before sending, pass inbound data/protocol/member events to the relevant handlers, update broadcast member state after sends, and delete the group on socket teardown. Diagnostics call the fill helper when dumping a grouped socket.

## State and Persistence Behavior

The header has no storage, but its opaque pointers protect the per-socket group and member state owned by `group.c`. The `bool *group_is_open` pointer passed to create is intentionally shared back to socket state so flow-control changes can wake or block users.

## Dependencies and Integration Points

It includes `core.h` and references TIPC service ranges, group requests, skb queues, messages, net namespaces, and netlink/socket diag skb output. It is included by socket code and the group implementation.

## Risks and Edge Cases

The API assumes callers serialize access with the owning socket/node locks used by the TIPC stack. Passing null groups is tolerated by some implementation functions but not all helpers. The shared `group_is_open` pointer must outlive the group.

## Test Signals

Compile tests catch signature drift. Runtime coverage comes from grouped socket send/receive, member publish/withdraw events, congestion wakeups, and SOCK_DIAG dumps that include group fields.
