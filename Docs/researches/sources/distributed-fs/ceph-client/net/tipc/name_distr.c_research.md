# sources/distributed-fs/ceph-client/net/tipc/name_distr.c

## Purpose
`name_distr.c` distributes cluster-scope TIPC service publications between nodes and consumes remote publication updates into the local name table. It turns local `struct publication` objects into `NAME_DISTRIBUTOR` messages, bulk-sends all current cluster publications to newly reachable peers, orders received updates by sequence number, and purges remote publications when a node is lost.

## Important APIs, Types, And Functions
The file exports `sysctl_tipc_named_timeout`, `tipc_named_publish()`, `tipc_named_withdraw()`, `tipc_named_node_up()`, `tipc_publ_notify()`, `tipc_named_rcv()`, and `tipc_named_reinit()`. Internal helpers include `publ_to_item()`, `named_prepare_buf()`, `named_distribute()`, `tipc_publ_purge()`, `tipc_update_nametbl()`, and `tipc_named_dequeue()`.

## Control Flow
Local publish inserts node-scope publications into `name_table.node_scope` without sending anything, while cluster-scope publications are appended to `name_table.cluster_scope`, encoded as a one-item `PUBLICATION` message, assigned `snd_nxt`, marked non-legacy, and returned for broadcast. Withdraw removes the publication from the scope list and, for cluster scope, returns a one-item `WITHDRAWAL` message. When a node comes up, `tipc_named_node_up()` adjusts the replicast destination count for peers lacking `TIPC_NAMED_BCAST`, snapshots the sequence number, walks `cluster_scope`, packs as many `distr_item` entries per MTU-sized message as possible, marks bulk and final-bulk flags, and unicasts the chain to the new peer.

Receive processing dequeues messages from the node broadcast/name queue. Legacy and bulk messages bypass sequence gating; non-legacy single updates wait until the stream is opened by the last bulk message and `rcv_nxt` matches the message sequence. Publications call `tipc_nametbl_insert_publ()` and then subscribe the publication to the source node for later purge. Withdrawals call `tipc_nametbl_remove_publ()`, unsubscribe, and free the publication via RCU. Node-loss notification walks the node publication list, purges each remote publication, and decrements `rc_dests` for peers that required replicast.

## State And Persistence
Name distribution state lives mostly in `struct name_table`: `node_scope`, `cluster_scope`, `cluster_scope_lock`, `snd_nxt`, and `rc_dests`. Per-peer receive state is stored by `node.c` in `bc_entry.namedq`, `named_rcv_nxt`, and `named_open`. Remote publications are linked into each node's `publ_list` via `publication.binding_node` so they can be withdrawn on node failure. `tipc_named_reinit()` rewrites local publication node addresses after network address changes and resets `rc_dests`.

## Dependencies And Integration Points
The file depends on `msg.h` wire helpers, `name_table.h` publication insertion/removal, `node.h` subscription and transmit helpers, link MTU lookup through `tipc_node_get_mtu()`, and broadcast/receive integration in `node.c`. It is called from socket bind/unbind paths indirectly through `tipc_nametbl_publish()`/`withdraw()`, from node-up/link-up handling, and from broadcast receive processing.

## Risks And Edge Cases
Bulk distribution assumes at least one message is queued before setting the final-bulk sequence; empty cluster-scope lists rely on callers tolerating no payload. Sequence gating must handle wraparound and avoid processing updates before the initial bulk snapshot completes. `rc_dests` accounting must match peer capability changes and node-loss cleanup. Publication purge holds the global name-table lock while removing from service structures, and lifetime relies on RCU freeing after unlinking from node subscriptions.

## Test Signals
Tests should cover node-scope versus cluster-scope publish/withdraw, bulk sync to a newly reachable node, MTU-limited multi-message bulk distribution, legacy peer handling, sequence wrap/reorder/drop behavior in `tipc_named_dequeue()`, remote publication purge on node down, `TIPC_NAMED_BCAST` capability toggling and `rc_dests` accounting, address reinitialization, duplicate withdraw warnings, and lockdep/RCU validation during concurrent publish and node failure.
