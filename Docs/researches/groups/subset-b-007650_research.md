# subset-b-007650 Research

Grouped research report for Lustre LNet peer, router, UDSP, and selftest control/BRW sources. Each section preserves the source path in its title and is wrapped for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/lnet/peer.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/lnet/peer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/lnet/router.c -->
# sources/distributed-fs/lustre-release/lnet/lnet/router.c

## Purpose
`router.c` implements LNet routing configuration, gateway liveness evaluation, router health checking, router buffer pools, forwarding enable/disable transitions, and LND/user notifications of peer availability. It decides whether routes are usable, stores remote-network route lists, allocates forwarding buffers by CPT and payload class, and coordinates with peer discovery for Multi-Rail routers.

## Important APIs, Types, And Functions
- Module parameters: `forwarding`, `tiny_router_buffers`, `small_router_buffers`, `large_router_buffers`, `peer_buffer_credits`, `auto_down`, `check_routers_before_use`, `avoid_asym_router_failure`, `alive_router_check_interval`, `router_ping_timeout`, and deprecated router sensitivity knobs.
- Route APIs: `lnet_add_route`, `lnet_del_route`, `lnet_destroy_routes`, `lnet_get_route`, `lnet_find_rnet_locked`, `lnet_move_route`, `lnet_rtr_transfer_to_peer`, and `lnet_consolidate_routes_locked`.
- Liveness APIs: `lnet_is_gateway_alive`, `lnet_is_route_alive`, `lnet_router_discovery_ping_reply`, `lnet_router_discovery_complete`, `lnet_wait_router_start`, `lnet_router_checker_active`, `lnet_check_routers`, and `lnet_notify`.
- Router buffer APIs: `lnet_rtrpools_alloc`, `lnet_rtrpools_free`, `lnet_rtrpools_adjust`, `lnet_rtrpools_enable`, `lnet_rtrpools_disable`, `lnet_get_rtr_pool_cfg`, `lnet_new_rtrbuf`, `lnet_destroy_rtrbuf`, and pool adjustment helpers.
- Key structures are `struct lnet_route`, `struct lnet_remotenet`, `struct lnet_peer`, `struct lnet_peer_net`, `struct lnet_peer_ni`, `struct lnet_rtrbufpool`, and `struct lnet_rtrbuf`.

## Control Flow
Route addition validates the remote net, hop count, gateway NID, local gateway network, and duplicate state. It allocates a candidate route and remote-net object, resolves or creates the gateway peer NI through `lnet_nid2peerni_ex`, stores the gateway peer, creates the remote-net bucket when needed, and inserts the route into the remote net at a randomized offset. Randomized insertion is seeded from local NIDs and spreads route preference across nodes that share the same route list. Adding a route also adds the route to the gateway peer's route list, increments router references, updates remote-net versioning, sets next-ping times for the gateway peer nets, and wakes the monitor thread.

Route deletion resolves an optional gateway NID to the gateway peer primary NID, removes matching routes from one remote net or all remote-net hash buckets, decrements gateway router references, moves deleted route and remote-net objects to temporary zombie lists, drops locks, and frees memory outside the protected lists. Moving or transferring routes is used when discovery merges gateway peers; it deletes from the old remote-net list and re-adds the route under the new gateway when appropriate.

Liveness combines peer state, peer-net health, route topology, and feature flags. `lnet_is_gateway_alive` requires the gateway peer to be alive and every peer net to have at least one live peer NI. `lnet_is_route_alive` requires a live gateway, a live gateway interface on the local net, router-enabled state, and, when `avoid_asym_router_failure` applies to single-hop routes, a live gateway interface on the remote net. When discovery is disabled, route liveness falls back to cached `lr_alive`.

Router discovery replies are interpreted by `lnet_router_discovery_ping_reply`. It rejects gateways that report routing disabled, checks the local gateway net for each route, scans the ping buffer for the route's remote net, records whether the route appears single-hop, and sets `lr_alive` according to `avoid_asym_router_failure` and remote-net status. `lnet_router_discovery_complete` clears router-discovery state, sets `lp_alive`, and marks all gateway interfaces/routes down on discovery failure.

The monitor path uses `lnet_router_checker_active` and `lnet_check_routers`. It handles `LNET_ROUTING_STARTING` and `STOPPING` after minimum/maximum wait intervals, pings gateway peer nets whose `lpn_next_ping` expired, forces router discovery with ping/push flags, and updates local NI status when forwarding is enabled and no traffic has been seen before the alive timeout. If local NI status changes, it calls `lnet_push_update_to_peers(1)`.

Router buffer pool allocation parses forwarding mode and buffer counts, allocates per-CPT arrays with tiny/small/large pools, and fills them with zero-page-count tiny buffers, one-page small buffers, and MTU-sized large buffers. Adjustments allocate new buffers on a temporary list before joining the pool, lower requested counts for shrink operations, and schedule blocked messages when new buffers become available. Disable moves routing to a stopping state and advertises `LNET_PING_FEAT_RTE_DISABLED`; actual freeing waits for credits to return or a maximum delay.

`lnet_notify` is the external birth/death notification path. It validates that the notifying NI is on the same net, rejects future timestamps, honors `auto_down`, finds the peer NI, updates route aliveness for router peers when discovery is disabled, sets peer NI status/timestamp/notified state, updates health on reset, serializes overlapping notifications with `lpni_notifying`, and calls an LND `lnd_notify_peer_down` hook when present.

## State And Persistence Behavior
Route state is in memory under `the_lnet.ln_remote_nets_hash`, each `lnet_remotenet` route list, gateway peer `lp_routes`, and the global `ln_routers` list. Routing status is in `the_lnet.ln_routing` with disabled, starting, enabled, and stopping states. Buffer state lives in `the_lnet.ln_rtrpools`, with per-pool free buffers, blocked message lists, current credits, requested buffer count, actual buffer count, and minimum credits.

There is no disk persistence in this file. User/module configuration and higher-level startup rebuild routes and forwarding mode. Runtime decisions such as route liveness, `lr_single_hop`, `lp_alive`, NI statuses, and min-credit watermarks are transient telemetry.

## Dependencies And Integration Points
The file depends on peer lookup and discovery from `peer.c`, ping-buffer iterators, LNet monitor wakeups, LNet send scheduling for blocked routed messages, CPT allocators, Linux page allocation, kernel module parameters, and libcfs/LNet string and list helpers. It is the routing half of the peer-discovery contract: `peer.c` learns gateway topology, and `router.c` converts that into route aliveness.

It integrates with userspace through route and pool ioctl structures such as `lnet_ioctl_pool_cfg`, with LNDs through `lnet_notify`, and with LNet's ping target by setting or clearing the routing-disabled feature bit.

## Risks
- Route list mutation is protected by `ln_api_mutex` plus exclusive net lock; route merging/deletion paths that temporarily drop locks must preserve list and reference invariants.
- `avoid_asym_router_failure` depends on correct hop count and discovery data. Misconfigured single-hop routes with undefined hops can still select asymmetric gateways, and the code only warns.
- Buffer pool adjustment is not transactional across all pools/CPTs; comments note callers must revert if a later allocation fails.
- Disabling routing waits for credits to return but eventually forces disable after a maximum interval, so in-flight or blocked routed messages can be dropped.
- `lnet_notify` combines LND callbacks, peer status, route status, and health changes; stale timestamps and overlapping notification serialization are important for correctness.
- Module parameter validation accepts only exact forwarding strings; bad boot/module configuration prevents routing allocation.

## Test Signals
Test coverage should include route add/delete duplicates, invalid gateway/local-net combinations, peer merge route transfer, single-hop remote-net health behavior, discovery-disabled cached liveness, routing enable/disable transitions, buffer pool grow/shrink/failure paths, blocked-message rescheduling after buffer growth, `lnet_notify` stale/future timestamp handling, and LND down notification callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/lnet/router.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/lnet/udsp.c -->
# sources/distributed-fs/lustre-release/lnet/lnet/udsp.c

## Purpose
`udsp.c` implements LNet User Defined Selection Policies. UDSP rules let users bias LNet path selection by assigning priorities to local/remote networks and NIDs, or by building preferred local-NID and preferred-router lists for peer NIs. The file stores policies, applies them to existing constructs, applies them incrementally to new NIs/peer NIs/peer nets, and marshals policies to and from ioctl buffers.

## Important APIs, Types, And Functions
- `struct udsp_info` carries the current local NI, local net, peer NI, peer net, match/action descriptors, priority, action type, local/remote preference mode, and revert flag through callback-based application.
- Rule matching helpers include `lnet_udsp_expr_list_equal`, `lnet_udsp_nid_descr_equal`, `lnet_udsp_action_equal`, `lnet_udsp_equal`, `lnet_udsp_criteria_present`, and `lnet_udsp_is_net_rule`.
- Application helpers include `lnet_udsp_apply_rule_on_ni`, `lnet_udsp_apply_prio_rule_on_net`, `lnet_udsp_apply_rule_on_nis`, `lnet_udsp_apply_rule_on_lpni`, `lnet_udsp_apply_rule_on_lpn`, `lnet_udsp_apply_rule_on_lpnis`, `lnet_udsp_apply_rte_list_on_net`, `lnet_udsp_apply_rte_rule_on_nets`, and `lnet_udsp_apply_single_policy`.
- Public application entry points are `lnet_udsp_apply_policies`, `lnet_udsp_apply_policies_on_ni`, `lnet_udsp_apply_policies_on_net`, `lnet_udsp_apply_policies_on_lpni`, and `lnet_udsp_apply_policies_on_lpn`.
- Policy list management is handled by `lnet_udsp_get_policy`, `lnet_udsp_add_policy`, `lnet_udsp_del_policy`, `lnet_udsp_alloc`, `lnet_udsp_free`, and `lnet_udsp_destroy`.
- Introspection and serialization use `lnet_udsp_get_construct_info`, `lnet_get_udsp_size`, `lnet_udsp_marshal`, `lnet_udsp_demarshal_add`, `copy_nid_range`, `copy_ioc_udsp_descr`, `copy_exprs`, and `copy_range_info`.

## Control Flow
Policy application is organized around three callback classes: peer-side rules, NI priority rules, and router-on-net rules. `lnet_udsp_apply_policies_helper` applies one rule or all rules in reverse list order. Reverse order lets earlier list entries override later-applied state when priorities and preferred lists are reset/rebuilt.

`lnet_udsp_apply_single_policy` classifies a rule by which descriptors are present. Source plus destination means a NID-pair rule: matching destination peer NIs receive a preferred local-NID list built from the source descriptor. Destination plus router means a router rule: matching destination peer NIs receive a preferred-router list built from route gateways matching the router descriptor. Destination alone means remote peer priority. Source alone means local NI or local network priority. Router-on-net application can also add preferred routers to local nets.

Preferred-list rules clear existing preference lists once per matched construct before adding matched NIDs or gateway NIDs. Revert mode clears rather than re-adds policy-generated preferences, so deletion and destruction can undo effects. Priority rules use `-1` as the reverted/default priority and call local selection-priority setters for `lnet_net`, `lnet_ni`, `lnet_peer_net`, or `lnet_peer_ni`.

Adding a policy scans the current list for a semantically equal match. Equal criteria plus changed priority updates the existing priority in place for priority rules; exact duplicates return `-EALREADY`. Otherwise the new policy is inserted at the requested index or appended, and later indices are incremented. Deleting by nonnegative index removes one policy, applies it in revert mode, frees it, and decrements subsequent indices. Deleting with a negative index destroys all policies.

Marshalling computes the exact byte size of an ioctl policy plus three NID descriptors. Each descriptor includes a fixed header, optional net-number range, and address expressions/ranges. `lnet_udsp_marshal` requires the caller's bulk size to exactly match `lnet_get_udsp_size`, copies descriptors to user memory, and asserts the whole buffer was consumed. Demarshalling validates truncation at each step, verifies descriptor type tags (`SRC`, `DST`, `RTE`), allocates one contiguous backing block for descriptor expression lists/ranges, and then inserts the resulting policy.

## State And Persistence Behavior
Policies are transient kernel objects on `the_lnet.ln_udsp_list`, allocated from `lnet_udsp_cachep`. Descriptor expression memory is stored as one allocated block per descriptor and freed by remembering `ud_mem_size`. Applying policies mutates transient selection state on local nets/NIs and peer nets/NIs: priorities, preferred local NID lists, local-net preferred router lists, and peer-NI preferred router lists.

There is no file persistence here. Persistent policy intent must come from userspace configuration replay. The function `lnet_udsp_destroy(shutdown)` optionally skips revert during shutdown because all constructs are being torn down.

## Dependencies And Integration Points
`udsp.c` depends on `udsp.h`, LNet peer/net structures, `cfs_match_net`, `cfs_match_nid_net`, expression-list helpers, route lists in `the_lnet.ln_remote_nets_hash`, preference-list APIs implemented in peer/net code, and user-copy helpers. It is invoked from peer and net creation paths to apply existing policies incrementally, and from ioctl/control paths to add, delete, show, or reconstruct policy effects.

The selection algorithm described in the file header consumes the priorities and preferred lists that this file writes. Router rules integrate with `router.c` by scanning configured routes and matching gateway primary or constituent NIDs.

## Risks
- Some rule validation logs errors but returns success-like `0` for bad action combinations, which may make userspace think a malformed rule was harmlessly accepted or ignored.
- `lnet_udsp_add_policy` updates duplicate priority policies in place but does not itself reapply the changed priority; callers must ensure application happens after add/update.
- Preferred-list application deliberately drops the net lock while clearing/adding preference lists. The surrounding code relies on `ln_api_mutex` and helper locking to keep selection lists consistent.
- The descriptor type check prints shifted bytes in a way that may not display the expected tag clearly on all endian/order cases.
- `lnet_udsp_marshal` uses exact-size matching, so ABI changes in ioctl structures or descriptor sizing can produce `-ENOSPC` instead of partial output compatibility.
- Demarshalling allocates packed expression backing memory and stores list pointers into it; any future change to descriptor ownership must preserve that free model.

## Test Signals
Tests should cover source-priority, destination-priority, NID-pair preferred local NI, router preferred list, local-net preferred-router rules, insertion at index, duplicate/update behavior, deletion/revert behavior, shutdown destroy without revert, marshalling/demarshalling round trips, truncated user buffers, invalid descriptor tags, and applying policies to constructs created after policies already exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/lnet/udsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/Makefile -->
# sources/distributed-fs/lustre-release/lnet/selftest/Makefile

## Purpose
This Makefile builds the Lustre LNet selftest kernel module. It declares the `lnet_selftest.o` module target and lists the object files that compose it.

## Important APIs, Types, And Functions
- `obj-m += lnet_selftest.o` registers the module for kernel module builds.
- `lnet_selftest-objs := console.o conrpc.o conctl.o framework.o timer.o rpc.o module.o ping_test.o brw_test.o` defines the linked objects.
- `ifdef CONFIG_GCOV_PROFILE_LNET` enables `GCOV_PROFILE := y` when LNet GCOV instrumentation is configured.

## Control Flow
Kbuild reads the file, compiles each listed source object, and links them into `lnet_selftest.ko`. The conditional GCOV assignment enables coverage instrumentation for this directory when the kernel configuration requests it.

## State And Persistence Behavior
There is no runtime state in the Makefile. Build outputs are the compiled objects, module, and optional coverage artifacts generated by Kbuild.

## Dependencies And Integration Points
The file depends on Linux Kbuild conventions and on the selftest source files listed in `lnet_selftest-objs`. It integrates `conctl.c` and `brw_test.c` with the broader console, RPC, framework, timer, module, and ping-test selftest components.

## Risks
- Adding a new selftest source without updating this object list leaves it out of the module.
- Removing or renaming one of the listed sources breaks module linkage.
- GCOV behavior depends on `CONFIG_GCOV_PROFILE_LNET`, so coverage expectations differ between builds.

## Test Signals
A successful kernel module build is the primary signal. A GCOV-enabled build should also verify that coverage instrumentation is applied when `CONFIG_GCOV_PROFILE_LNET` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/brw_test.c -->
# sources/distributed-fs/lustre-release/lnet/selftest/brw_test.c

## Purpose
`brw_test.c` implements the LNet selftest bulk read/write test service and client operations. It allocates bulk buffers, fills them with deterministic magic patterns, sends or receives SRPC bulk transfers, validates returned data, supports older and newer bulk-length session formats, and optionally injects data corruption for negative testing.

## Important APIs, Types, And Functions
- Module parameters `brw_srv_workitems` and `brw_inject_errors` control server workitem capacity and random-ish corruption injection.
- Constants `BRW_POISON`, `BRW_MAGIC`, and `BRW_MSIZE` define data patterns and alignment.
- Client lifecycle: `brw_client_init`, `brw_client_fini`, `brw_client_prep_rpc`, and `brw_client_done_rpc`.
- Pattern helpers: `brw_inject_one_error`, `brw_fill_page`, `brw_check_page`, `brw_fill_bulk`, and `brw_check_bulk`.
- Server callbacks: `brw_server_handle`, `brw_bulk_ready`, `brw_server_rpc_done`, `brw_srpc_init`, and `brw_srpc_fini`.
- Exported registration objects: `struct sfw_test_client_ops brw_test_client`, `struct srpc_service brw_test_service`, and `brw_init_test_service`.

## Control Flow
Client initialization reads the test parameters from the session. For sessions without `LST_FEAT_BULK_LEN`, it uses the legacy page-count request and assumes offset zero. For newer sessions, it uses explicit byte length and offset. It rejects unaligned offsets, lengths greater than `LNET_MTU`, invalid read/write opcodes, and invalid check modes. Then it allocates one `srpc_bulk` buffer per test unit on the destination CPT and stores it in `tsu_private`.

For each client RPC, `brw_client_prep_rpc` creates an SRPC test RPC sized to the request's page count and length, copies the preallocated bulk descriptor into the RPC, fills WRITE bulks with `BRW_MAGIC` and READ bulks with `BRW_POISON`, and sets BRW request flags/opcode/length. Completion checks RPC transport status, handles byte-swapped replies, records BRW status failures in `sn_brw_errors`, and validates READ data against `BRW_MAGIC`.

The server allocates a maximum-MTU bulk buffer per server RPC during `brw_srpc_init`. `brw_server_handle` validates request magic/endian, opcode, check flags, session features, legacy alignment, and length. It initializes the server bulk as sink for writes or source for reads, fills READ data with `BRW_MAGIC`, and poisons WRITE receive buffers before bulk transfer. `brw_bulk_ready` validates WRITE data after transfer and sets `EBADMSG` in the reply on corruption. `brw_server_rpc_done` logs final bulk transfer status.

`brw_init_test_service` caps server workitems by available memory. It starts from one-sixteenth of total RAM, divides by the number of pages needed for an MTU-sized bulk, and lowers `sv_wi_total` if the module parameter would consume too much memory.

## State And Persistence Behavior
Runtime state is per selftest session, test instance, test unit, and SRPC. Client bulk buffers live in `tsu_private` and are freed in `brw_client_fini`. Server bulk buffers live in `srpc_server_rpc.srpc_bulk` and are freed by the service finalizer. Error counts are accumulated in the session's `sn_brw_errors`. The file persists no data to disk.

`brw_inject_errors` is mutable module parameter state. `brw_inject_one_error` decrements it when injection fires based on current nanosecond parity, so error injection is nondeterministic and global to the module.

## Dependencies And Integration Points
The file depends on `selftest.h`, the selftest framework (`sfw_test_instance`, `sfw_test_unit`, `sfw_session`), SRPC bulk and service APIs, LNet MTU and CPT helpers, kernel page memory, byte-swap helpers, and atomic session counters. The registration objects are consumed by the selftest framework and module initialization code linked by the Makefile.

## Risks
- The legacy feature path assumes `blk_npg * PAGE_SIZE` and explicitly notes it does not work for variable page size compatibility.
- Bulk offset and length must be aligned to `BRW_MSIZE` for pattern checking. Incorrect request construction is rejected, but future callers could bypass assumptions.
- `unsafe_memcpy` copies a flexible `srpc_bulk` descriptor into RPC storage using calculated `npg`; mismatches between allocation and `npg` would be memory-corruption prone.
- Fault injection is time-parity based, so repeated tests can be flaky unless the module parameter is controlled and expectations tolerate nondeterminism.
- Server reply status uses positive errno values in the protocol and client converts them to negative `crpc_status`; callers need to preserve that convention.
- Memory consumption is bounded in `brw_init_test_service`, but per-RPC maximum-MTU allocation can still be significant on large concurrency tests.

## Test Signals
Signals include successful READ and WRITE BRW selftests with `CHECK_NONE`, `CHECK_SIMPLE`, and `CHECK_FULL`; legacy and `LST_FEAT_BULK_LEN` sessions; endian-swapped request/reply handling; invalid opcode/flags/length rejection; injected corruption producing `EBADMSG` and incremented `sn_brw_errors`; and workitem cap behavior under constrained memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/brw_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/conctl.c -->
# sources/distributed-fs/lustre-release/lnet/selftest/conctl.c

## Purpose
`conctl.c` is the kernel control plane for LNet selftest console operations. It handles legacy libcfs ioctl requests and generic netlink commands for sessions and groups, validates user-provided parameters, copies names and request payloads between user and kernel memory, serializes access to `console_session`, and dispatches to console/session/group/batch/test/stat helpers.

## Important APIs, Types, And Functions
- Legacy ioctl handlers include `lst_debug_ioctl`, `lst_group_add_ioctl`, `lst_group_del_ioctl`, `lst_group_update_ioctl`, `lst_nodes_add_ioctl`, `lst_batch_add_ioctl`, `lst_batch_run_ioctl`, `lst_batch_stop_ioctl`, `lst_batch_query_ioctl`, `lst_batch_list_ioctl`, `lst_batch_info_ioctl`, `lst_stat_query_ioctl`, and `lst_test_add_ioctl`.
- `lstcon_ioctl_entry` is the notifier entry for `IOC_LIBCFS_LNETST`.
- Generic netlink session handling uses `lst_session_keys`, `lst_sessions_show_dump`, and `lst_sessions_cmd`.
- Generic netlink group handling uses `lst_node_state2str`, `lst_node_str2state`, `struct lst_genl_group_prop`, `struct lst_genl_group_list`, `lst_groups_show_start`, `lst_groups_show_dump`, and `lst_groups_show_done`.
- Netlink registration uses `lst_genl_ops`, `lst_mcast_grps`, `lst_family`, `lstcon_init_netlink`, and `lstcon_fini_netlink`.

## Control Flow
Legacy ioctl entry first verifies the command, extracts the operation from `ioc_u32[0]`, rejects payloads larger than a page, allocates a kernel buffer, copies the user payload into it, and locks `console_session.ses_mutex`. It updates `ses_laststamp`, rejects shutdown sessions, expires old sessions, requires an active session for all operations except session creation, resets transaction stats, dispatches by opcode, copies `ses_trans_stat` to the second user buffer, unlocks, frees the temporary buffer, and returns a notifier-encoded errno.

Each ioctl helper performs focused validation. Session keys must match `console_session.ses_key`. Names must be present and within `LST_NAME_SIZE`; node/test arrays and result pointers must be non-null; indices and counts must be nonnegative or positive as appropriate; optional test parameter blobs must fit in one page minus `struct lstcon_test`. Helpers allocate NUL-terminated name buffers, copy from user, call `lstcon_*` operations, copy output fields such as features, test return codes, indexes, or counts back to user, and free temporary allocations.

Session generic netlink supports dumping active session state and creating or ending sessions. `lst_sessions_cmd` locks the session, handles shutdown/expiry, treats non-create requests as session end, parses scalar-list config for `name` and `timeout`, honors `NLM_F_REPLACE` as force, calls `lstcon_session_new`, and replies with a scalar key table plus session attributes. `lst_sessions_show_dump` reports an active session's name, key, timestamp, console NID, and node count.

Group netlink dump start allocates a dump context backed by `genradix`. Without request parameters it snapshots all session groups and takes refs. With parameters it enables verbose mode, parses requested group names and optional status filters, finds groups, and records refs. Dump emits the scalar key table once, then emits each group name and, in verbose mode, nested node entries filtered by state. Done releases group refs, frees the radix, and clears callback context.

## State And Persistence Behavior
The file does not persist data itself. It mutates the in-memory `console_session` and objects owned by the selftest console subsystem: sessions, groups, batches, nodes, tests, transaction stats, and timestamps. All legacy ioctl dispatch is serialized by `console_session.ses_mutex`; netlink session commands also take the mutex. Group dump contexts hold temporary references to groups across multipart netlink dump callbacks and release them in `.done`.

Allocated temporary buffers are short-lived per request. Name buffers are generally allocated with `nmlen + 1` and NUL-terminated before dispatch. Netlink replies are built in `sk_buff` objects and freed on error when ownership is not transferred.

## Dependencies And Integration Points
`conctl.c` depends on `console.h`, libcfs ioctl structures, LNet/libcfs helpers, Linux user-copy APIs, generic netlink, `lnet_genl_send_scalar_list`, `genradix`, and many selftest console functions such as `lstcon_group_add`, `lstcon_nodes_add`, `lstcon_batch_run`, `lstcon_test_add`, `lstcon_session_new`, and `lstcon_group_find`. The Makefile links it into `lnet_selftest.o`.

It is the bridge between user tools and in-kernel selftest orchestration. Legacy ioctl and generic netlink are parallel control surfaces; netlink currently covers sessions and groups, while many batch/test/stat operations remain ioctl-only in this file.

## Risks
- User-copy and allocation error paths are numerous. A few helpers free using sizes derived from args even after partial validation; most are safe with NULL but size consistency should be kept tight.
- `lst_stat_query_ioctl` copies a group name without explicitly appending a NUL before calling `lstcon_group_stat`, unlike most name helpers.
- In `lst_group_add_ioctl`, the `copy_from_user` failure path frees `args->lstio_grp_nmlen` bytes instead of `nmlen + 1`, which is a small accounting mismatch for the allocation macro.
- `lst_sessions_cmd` declares `char name[LST_NAME_SIZE]` without an obvious default initialization before parsing; a create request missing `name` could pass uninitialized stack data to `lstcon_session_new` unless higher-level netlink policy always provides it.
- Netlink dump code must preserve multipart message cursor state. If a message fills mid-group, the current implementation advances `lggl_index` only after the loop and may need careful validation for very large groups.
- Legacy ioctl returns transaction stats even when the operation failed late, so callers must interpret both ioctl rc and transaction fields.

## Test Signals
Tests should cover each ioctl opcode with valid and invalid session keys, missing names, overlong names, bad counts/pointers, session expiry/shutdown, batch/test lifecycle, transaction-stat copying, and fault-injected user-copy failures. Netlink tests should cover session create/end/dump, force create, invalid scalar-list types, group list dump, verbose group dump with status filters, missing groups, multipart dump cleanup, and registration/unregistration through `lstcon_init_netlink` and `lstcon_fini_netlink`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/selftest/conctl.c -->
