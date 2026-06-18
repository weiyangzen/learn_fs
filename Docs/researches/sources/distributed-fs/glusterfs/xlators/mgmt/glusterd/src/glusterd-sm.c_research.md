# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-sm.c

## Purpose
Implements GlusterD's friend/peer state machine. It queues and processes peer events, drives probe/friend-add/friend-remove/friend-update RPC actions, compares imported cluster data, updates peer state and store records, performs peer-detach cleanup, and triggers quorum/daemon actions when peer connectivity affects server quorum.

## Important APIs, types, and functions
Public helpers include `glusterd_friend_sm_state_name_get()`, `glusterd_friend_sm_event_name_get()`, context destructors, `glusterd_broadcast_friend_delete()`, `glusterd_friend_sm_new_event()`, `glusterd_friend_sm_inject_event()`, `glusterd_friend_sm()`, and `glusterd_friend_sm_init()`. Action handlers include `glusterd_ac_friend_probe()`, `glusterd_ac_friend_add()`, `glusterd_ac_reverse_probe_begin()`, `glusterd_ac_send_friend_remove_req()`, `glusterd_ac_send_friend_update()`, `glusterd_ac_update_friend()`, `glusterd_ac_handle_friend_add_req()`, `glusterd_ac_handle_friend_remove_req()`, and `glusterd_ac_friend_remove()`. Transition tables cover default, probe-received, connected-received, connected-accepted, request-sent, request-received, befriended, request-sent-received, rejected, request-accepted, and unfriend-sent states.

## Control flow
Actions submit RPCs through the procedure tables initialized in `glusterd-rpc-ops.c`. Probe actions build a transient dict containing hostname, port, and peerinfo; friend add exports local volumes, snapshots, and missed snapshots; friend update broadcasts current cluster view to connected eligible peers. Incoming friend-add requests update the peer UUID, compare volume versions and snapshots under `conf->import_volumes`, inject local accept/reject events, capture the peer's view of this node's hostname, and reply to the requester. The main `glusterd_friend_sm()` loop dequeues events, finds current peer state, runs the table handler outside the RCU read section to avoid deadlocks, transitions state unless the event is remove-related, stores peerinfo, cleans context, and may pause when a connection is awaited.

## State and persistence behavior
Runtime state includes the global `gd_friend_sm_queue`, per-peer state, hostname lists, connected flag, RPC program pointers, transition logs, quorum contribution, and event contexts. Persistent state changes occur through `glusterd_store_peerinfo()`, peer cleanup, stale volume deletion on detach, snapshot cleanup, daemon reconfiguration, and imported volume/snapshot state from friend comparison. `local_node_hostname` records the hostname by which a peer sees the local node.

## Dependencies and integration points
Depends on RPC procedure tables, peerinfo lookup/cleanup, RCU locking, GlusterD store, volume/snapshot compare/import helpers, service reconfiguration, snapd/SHD/gfproxyd stop hooks, server-quorum logic, op-sm progression, and daemon spawn synctasks. It is tightly coupled with `glusterd-rpc-ops.c`, which injects most events from RPC callbacks.

## Risks and test signals
Risks include event context ownership mismatches, handlers mutating peerinfo after dropping RCU protection, queue events referencing peerinfo removed by earlier events, transition-table mistakes, stale volume deletion on detach, deadlocks around import-volume and RCU locks, and quorum actions firing before cluster views settle. Tests should cover simultaneous probe crossing, reverse probe, friend add accept/reject from volume/snapshot conflicts, friend update to only eligible peers, deprobe of connected and disconnected peers, stale volume cleanup, service stop/reconfigure during detach, transition-log updates, stored peerinfo after state changes, and quorum action after befriended connected peers settle.
