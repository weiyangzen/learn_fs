# sources/distributed-fs/lustre-release/lnet/lnet/peer.c

## Purpose
`peer.c` is the core LNet peer database and peer discovery implementation. It creates and destroys peer tables, peers, peer networks, and peer NIs; tracks Multi-Rail state, primary NIDs, preferred NIDs, route-related gateway state, peer health, and discovery state; handles ping/push discovery events; and exposes peer information to kernel/userspace callers.

The file is central to how LNet turns NIDs seen in traffic, DLC configuration, router configuration, and discovery ping buffers into a coherent peer graph. It also owns the discovery worker thread that serializes ping, push, merge, deletion, resend, and timeout handling.

## Important APIs, Types, And Functions
- `lnet_peer_tables_create`, `lnet_peer_tables_cleanup`, `lnet_peer_uninit`, and `lnet_peer_tables_destroy` allocate and tear down per-CPT peer hash tables and zombie tracking.
- `lnet_peer_ni_alloc`, `lnet_peer_net_alloc`, `lnet_peer_alloc`, `lnet_peer_attach_peer_ni`, `lnet_peer_add`, `lnet_peer_add_nid`, `lnet_peer_set_primary_nid`, and `lnet_peer_del_nid` implement the peer object model.
- `lnet_user_add_peer_ni`, `lnet_del_peer_ni`, `LNetAddPeer`, `LNetPrimaryNID`, `LNetLocalPrimaryNID`, `LNetPeerDiscovered`, and `lnet_peerni_by_nid_locked` are externally visible or cross-module entry points for configuring and resolving peers.
- `lnet_peer_queue_message`, `lnet_peer_queue_for_discovery`, `lnet_discover_peer_locked`, `lnet_peer_discovery_start`, `lnet_peer_discovery_stop`, and the `lnet_peer_discovery` kthread drive active discovery and message resend.
- `lnet_peer_push_event`, `lnet_discovery_event_handler`, `lnet_discovery_event_reply`, `lnet_discovery_event_ack`, `lnet_discovery_event_send`, and `lnet_discovery_event_unlink` process LNet EQ events for push and ping operations.
- `ping_iter_first`, `ping_iter_next`, `ping_info_count_entries`, `find_primary`, `lnet_peer_merge_data`, and `lnet_peer_data_present` parse ping buffers and reconcile NID lists.
- Preferred-path APIs include `lnet_peer_add_pref_nid`, `lnet_peer_clr_pref_nids`, `lnet_peer_add_pref_rtr`, `lnet_peer_clr_pref_rtrs`, `lnet_peer_is_pref_nid_locked`, and `lnet_peer_is_pref_rtr_locked`.
- Health and observability APIs include `lnet_notify`, `lnet_peer_ni_add_to_recoveryq_locked`, `lnet_peer_ni_set_healthv`, `lnet_get_peer_list`, `lnet_get_peer_ni_info`, `lnet_get_peer_info`, and `lnet_debug_peer`.

The key runtime types are `struct lnet_peer`, `struct lnet_peer_net`, `struct lnet_peer_ni`, `struct lnet_peer_table`, `struct lnet_ping_buffer`, `struct lnet_ping_iter`, and list-backed `struct lnet_nid_list` preference entries.

## Control Flow
Startup allocates `the_lnet.ln_peer_tables` per CPU partition. Each table has a hash array, a stable peer list, and a zombie list for peer NIs that have been unlinked from lookup paths but still have references. Peer NI allocation initializes TX queues, recovery lists, router preference lists, health, status, credits, and the optional link to a local `lnet_net`; if no matching local net exists, the NI is put on `ln_remote_peer_ni_list` so `lnet_peer_net_added` can attach credits when the network appears.

Peer creation usually flows through `lnet_add_peer_ni`. With only a primary NID it calls `lnet_peer_add`; with a primary and secondary NID it resolves the peer by primary and calls `lnet_peer_add_nid`. Attachment inserts the NI into the global hash, attaches it to the peer-net and peer, updates global peer lists and refcounts, sets flags such as `LNET_PEER_CONFIGURED`, `LNET_PEER_MULTI_RAIL`, and `LNET_PEER_LOCK_PRIMARY`, applies UDSP policy to the new peer-net/peer-NI, and drops the creation reference.

Traffic-created peers use `lnet_peerni_by_nid_locked` and `lnet_peer_ni_traffic_add`. The slow path drops the net lock, takes `ln_api_mutex`, creates a minimal non-configured peer, optionally records a non-MR preferred local NID, then reacquires the original lock. This avoids racing local net changes, DLC changes, and peer lookup.

Deletion first cancels outstanding discovery MDs, then unlinks peer NIs from hash lists and hierarchy under exclusive net lock. Peer NIs move to per-table zombie lists until references drain. Deleting a primary NID normally deletes the peer; forced router deletion can reassign the primary to another NI. Deleting Lustre-created locked-primary peers without force resets them back to only the primary rather than destroying the peer.

Discovery queues a peer by setting `LNET_PEER_DISCOVERING`, adding `lp_dc_list` to `ln_dc_request`, and holding a peer reference. The discovery thread waits on `ln_dc_waitq`, reposts or resizes the push target, resends globally queued messages, moves peers from request to working queues, and selects one action from the peer state: deletion, data merge, ping failure cleanup, push failure cleanup, send ping, send push, or mark discovered. Completion clears `DISCOVERING`, optionally sets rediscovery error state, wakes waiters, updates router discovery, and resends or finalizes messages that were blocked on discovery.

Ping and push state is event-driven. Active ping binds a receive MD through `lnet_send_ping`; replies validate and possibly byte-swap ping info, track discovery source/destination NIDs, update remote discovery/MR feature state, store a refcounted ping buffer, and set `DATA_PRESENT`. Active push binds the local ping target as a source MD and uses `LNetPut`; ACKs clear `PUSH_SENT` and store the remote sequence number. SEND and UNLINK events convert failures/timeouts into `PING_FAILED` or `PUSH_FAILED` so the thread can unlink outside the event handler.

`lnet_peer_merge_data` is the reconciliation pass. It builds current, add, and delete NID arrays from the peer and ping buffer, updates NI health statuses, adds newly reported NIDs, deletes absent NIDs unless discovery is disabled, moves the primary peer-net and peer-NI to the front of their lists, caches router feature state, calls `lnet_router_discovery_ping_reply` for gateways, and marks conflicts with DLC as non-fatal except for memory exhaustion. If a ping buffer reports a different primary, `lnet_peer_data_present` can update the current peer's primary, hand the data to an existing primary peer, consolidate routes, or merge peers.

## State And Persistence Behavior
All state is in kernel memory and anchored from `the_lnet`: peer tables, peer lists, remote peer NI list, discovery queues, resend list, push target buffers, monitor recovery queues, and routing-related lists. No persistent on-disk state is written here; persistence comes from higher-level configuration mechanisms that recreate configured peers and routes.

Reference management is explicit. Peer NIs use `kref`; peers and peer nets use atomic or custom refcounts. Unlinked peer NIs enter zombie lists so lookups stop before memory is freed. Ping buffers are refcounted and freed through `lnet_ping_buffer_free`. Pending messages are either resent after discovery, moved to `ln_msg_resend` during peer destruction, or finalized on discovery errors/shutdown.

Major state bits include `LNET_PEER_CONFIGURED`, `MULTI_RAIL`, `LOCK_PRIMARY`, `NO_DISCOVERY`, `DISCOVERING`, `DISCOVERED`, `NIDS_UPTODATE`, `DATA_PRESENT`, `FORCE_PING`, `FORCE_PUSH`, `PING_SENT`, `PUSH_SENT`, `PING_FAILED`, `PUSH_FAILED`, `REDISCOVER`, `MARK_DELETION`, `MARK_DELETED`, and router flags such as `RTR_DISCOVERY`, `RTR_DISCOVERED`, and `ROUTER_ENABLED`.

## Dependencies And Integration Points
`peer.c` depends on LNet core locking, CPT allocation, libcfs list/refcount helpers, ping buffer helpers, LNet MD/Get/Put APIs, LNet send/finalize paths, net and NI tunables, monitor recovery queues, route management in `router.c`, and UDSP application in `udsp.c`. It is called by DLC ioctl/config paths, traffic send/receive paths, router health checks, LND notification callbacks, and exported Lustre-facing APIs.

The file integrates tightly with `router.c`: gateway peers hold router refcounts, discovery responses update route aliveness, router discovery completion marks gateway state, and peer merges transfer or consolidate routes. It also integrates with UDSP because every new peer-net or peer-NI has selection policies applied during attachment.

## Risks
- Lock ordering is delicate. The code moves between `ln_api_mutex`, exclusive/shared net locks, per-peer spinlocks, per-peer-NI spinlocks, and event-handler contexts. Any future change must preserve the current unlock/relock patterns around allocation, user copies, MD unlinking, and LNet sends.
- Discovery is state-machine driven by bit flags rather than a single enum, so invalid flag combinations can cause repeated rediscovery, missed pushes, or stranded messages.
- Ping buffer parsing handles old NID4 and large-address formats; truncated or inconsistent buffers must keep the iterator bounds correct to avoid reading past the received data.
- Configured peers and discovery data intentionally conflict in some cases. DLC is treated as authoritative, which avoids churn but can mask remote topology changes until configuration is repaired.
- Primary NID locking and merge logic have subtle behavior for Lustre-created peers, routers, and peers discovered through alternate NIDs.
- `lnet_get_peer_ni_info` appears to populate `peer_min_rtr_credits` from `lpni_mintxcredits`, while `lnet_get_peer_info` uses `lpni_minrtrcredits`; that mismatch is a likely observability bug.
- Some `copy_to_user` loops rely on `ln_api_mutex` for list stability and on caller-provided size negotiation; size drift in exported structures can break user tools.

## Test Signals
Useful test signals include peer add/delete/reset through DLC, traffic-created peer lookup, MR peer discovery with NID add/delete, primary-NID locking, discovery-disabled remote peers, corrupted/truncated ping replies, push/ping timeout paths, route transfer during peer merge, router discovery failure, zombie refcount drain, and message resend after discovery. Existing selftest code in this subset exercises LNet traffic and control APIs indirectly, but this file needs dedicated kernel or integration tests for the discovery state machine and locking-sensitive peer mutations.
