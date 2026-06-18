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
