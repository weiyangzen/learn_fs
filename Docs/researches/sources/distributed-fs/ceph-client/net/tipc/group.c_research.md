# sources/distributed-fs/ceph-client/net/tipc/group.c

## Purpose

`group.c` implements TIPC socket group membership, group unicast/multicast/broadcast filtering, member events, receive-window flow control, broadcast sequence handling, and group diagnostics. It lets group sockets discover members through topology subscriptions, exchange group protocol messages, and prevent any one member from exhausting receive buffers.

## Important APIs, Types, and Functions

`struct tipc_member` tracks a member in an RB tree keyed by node/port, list membership for active/pending/small-window queues, deferred receive queue, state, advertised/window credits, and broadcast sequence/ack state. `struct tipc_group` owns member RB tree/lists, destination nlist, net/type/instance/scope/port metadata, member counts, active limits, broadcast send/ack state, and flags for loopback/events/open.

Public APIs include `tipc_group_create()`, `tipc_group_join()`, `tipc_group_delete()`, `tipc_group_add_member()`, `tipc_group_dests()`, `tipc_group_self()`, `tipc_group_exclude()`, `tipc_group_filter_msg()`, `tipc_group_member_evt()`, `tipc_group_proto_rcv()`, `tipc_group_update_bc_members()`, `tipc_group_cong()`, `tipc_group_bc_cong()`, `tipc_group_update_rcv_win()`, `tipc_group_bc_snd_nxt()`, `tipc_group_update_member()`, and `tipc_group_fill_sock_diag()`.

## Control Flow

Creation initializes lists/RB tree, destination list, flags, and a kernel topology subscription. Join sends `GRP_JOIN_MSG` to known members and initializes advertised windows. Topology publish/withdraw events flow through `tipc_group_member_evt()`, creating or retiring members and emitting optional user events. Group protocol messages flow through `tipc_group_proto_rcv()`, which handles joins, leaves, advertisements, broadcast ACKs, reclaim/remit exchange, and wakeup decisions.

Data receive enters `tipc_group_filter_msg()`. It validates group membership and sender state, sorts multicast/broadcast messages by group broadcast sequence into the member deferred queue, delivers in-order messages to the socket input queue, sends ACKs when requested, drops mismatched multicast instances, and updates receive windows. Send-side congestion checks use `tipc_group_cong()` and `tipc_group_bc_cong()` to compare requested length against member windows and to send extra advertisements when needed.

## State and Persistence Behavior

All state is per group socket and in memory. Member state transitions include joining, published, joined, pending, active, reclaiming, remitted, and leaving. The group maintains active receiver admission control using `max_active`, `active_cnt`, active/pending lists, and `ADV_IDLE`/`ADV_ACTIVE` windows. Broadcast persistence is sequence based: `bc_snd_nxt`, per-member `bc_rcv_nxt`, `bc_syncpt`, `bc_acked`, and group `bc_ackers`.

## Dependencies and Integration Points

The file depends on TIPC address, broadcast, topology server, socket, node, name table, subscription, message, skb queue, RB tree, and netlink attribute helpers. It integrates with socket send/receive paths for congestion and filtering, with topology server kernel subscriptions for membership, with `tipc_node_distr_xmit()` for protocol messages, and with socket diagnostics via `tipc_group_fill_sock_diag()`.

## Risks and Edge Cases

Ordering and flow control are the main risks. Broadcast/multicast messages can be bypassed by unicasts, so deferred sorting and sequence comparisons must be correct. Window arithmetic uses `u16` and credit blocks; underflow or stale advertisement can deadlock senders or overrun receivers. Reclaim/remit transitions are subtle under active-member churn. Member deletion must clean all lists and deferred queues and update `dests` only when the last member on a node leaves.

## Test Signals

Test group join/leave with and without loopback, node-scope versus cluster-scope groups, many members to trigger active/pending/reclaim logic, broadcast requiring ACKs, multicast instance mismatch, member withdraw while messages are deferred, and socket diag output for group attributes. Congestion tests should observe `open` flag transitions and SOCK_WAKEUP behavior in socket code.
