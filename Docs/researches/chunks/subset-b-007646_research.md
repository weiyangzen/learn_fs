# sources/distributed-fs/lustre-release/lnet/lnet/api-ni.c lines 1-9906

## Scope

This chunk covers almost all of `lnet/lnet/api-ni.c` through the beginning of the generic-netlink buffer command. It includes global LNet state setup, module parameters, library/module lifecycle, LNet NI startup/shutdown, ping/push target management, dynamic local network and NI configuration, the legacy ioctl control plane, and most generic-netlink handlers for local nets, peers, routes, ping/discover, peer distance/fail controls, recovery debug, fault injection, routing, and router-buffer configuration. The file continues after this chunk with the tail of `lnet_buffers_cmd()`, NUMA command handling, the `lnet_genl_ops` table/family definition, and public helper APIs, so command registration details are only partially visible here.

## Purpose

`api-ni.c` is the central API/control-plane implementation for Lustre LNet network interfaces. It owns the singleton `the_lnet`, initializes and tears down process-wide LNet resources, connects LNet to loadable network drivers (LNDs), exposes exported kernel APIs such as `LNetNIInit()`, `LNetNIFini()`, `LNetCtl()`, and LND registration, and translates admin requests from module parameters, legacy ioctls, and generic netlink into updates on local NIs, routes, peers, health state, recovery queues, router buffers, and fault rules.

The chunk is state-heavy: it creates slabs, per-CPT locks and containers, remote-net hashes, peer tables, message containers, portal state, ping/push MDs, monitor/discovery workers, acceptor threads, and callback lists. It also provides the outward-facing serialization and validation layer for network configuration, so many bugs here would show up as broken `lnetctl` behavior, incorrect ping/discovery output, failure to start/stop LNet, leaked NIs or MDs, stale peer state, or inconsistent health/recovery reporting.

## Important State And Tunables

- `struct lnet the_lnet` is the exported singleton for all runtime state. It is statically initialized with `ln_api_mutex`, `ln_ni_total`, and `ln_cpt_restricted_count` because module-parameter callbacks can run before full module init.
- Module parameters in this chunk include `networks`, deprecated `ip2nets`/`routes` for older Lustre versions, `rnet_htable_size`, removed `use_tcp_bonding`, `lnet_numa_range`, health sensitivity, recovery interval/limit/ping interval, `lnet_interfaces_max`, discovery disable, asymmetrical route drop, transaction timeout, retry count, response tracking, and `lock_prim_nid`.
- `lnet_lnd_timeout` is derived from `lnet_transaction_timeout` and `lnet_retry_count`. `lnet_set_lnd_timeout()` keeps the derived timeout at least one second.
- `lnet_dlc_seq_no` is incremented on dynamic local NI changes and is used by path selection code outside this chunk to notice that selected paths may need recomputation.
- Slab caches are created for MEs, small MDs, UDSPs, response trackers, and messages: `lnet_mes_cachep`, `lnet_small_mds_cachep`, `lnet_udsp_cachep`, `lnet_rspt_cachep`, and `lnet_msg_cachep`.
- Runtime lists initialized by `lnet_prepare()` include local nets, remote peer NI list, routers, fault rules, delayed discovery queues, local/peer recovery queues, UDSP policies, test peers, zombie nets/NIs, resend list, and NID update callbacks.
- Ping target state is stored in `the_lnet.ln_ping_target` and `ln_ping_target_md`; push target state is stored in `ln_push_target`, `ln_push_target_md`, `ln_push_target_nbytes`, and the associated event handlers.

## Key APIs And Functions

- Module-parameter setters:
  - `sensitivity_set()` validates `lnet_health_sensitivity`, disables retries if health is turned off, and updates under `ln_api_mutex`.
  - `max_recovery_ping_interval_set()` updates `lnet_max_recovery_ping_interval` and derives the count as a log2-like interval count.
  - `discovery_set()` toggles peer discovery, updates the ping feature bit when LNet is running, and pushes an update when discovery is disabled dynamically.
  - `transaction_to_set()` and `retry_count_set()` enforce timeout/retry constraints and recompute `lnet_lnd_timeout`.
  - `intf_max_set()`, `drop_asym_route_set()`, and `response_tracking_set()` validate simpler scalar inputs.
- Library lifecycle:
  - `lnet_lib_init()` verifies wire constants, binds LNet to the global CPT table, allocates per-CPT locks, registers the generic-netlink family, initializes global lists/hash sizing, and registers the loopback LND.
  - `lnet_lib_exit()` asserts no users remain, unregisters loopback, validates all LND slots are empty, destroys locks, checks callback-list emptiness, and unregisters the netlink family.
- LND integration:
  - `lnet_register_lnd()` and `lnet_unregister_lnd()` insert/remove LND driver descriptors from `the_lnet.ln_lnds[]` under `ln_lnd_mutex`.
  - `lnet_load_lnd()` returns a registered LND or requests the corresponding module when module loading is enabled.
  - LND callbacks used in this chunk include `lnd_startup`, `lnd_shutdown`, `lnd_accept`, `lnd_ctl`, `lnd_get_timeout`, `lnd_get_nid_metadata`, `lnd_tun_defaults`, `lnd_nl_get`, and `lnd_nl_set`.
- Core initialization:
  - `lnet_prepare()` allocates all core data structures before any LND startup: slabs, remote-net hash, counters, peer tables, message containers, EQ and MD containers, portals, and zombie resend queues.
  - `lnet_unprepare()` frees those resources after LNDs and users are gone. It also calls `lnet_fail_nid(&LNET_ANY_NID, 0)`, destroys portals and containers, uninitializes peers, frees router pools, destroys UDSPs, and destroys slabs.
  - `LNetNIInit()` is the main public startup entry. It handles refcounting, prepares state, creates loopback, parses module networks unless DLC suppressed them, starts LND nets, optionally parses legacy routes/router pools, starts acceptor, installs ping and push targets, starts monitor and discovery, initializes fault/debugfs support, completes `ln_started`, and waits for routers.
  - `LNetNIFini()` decrements references or performs full shutdown: marks stopping, finalizes fault/debugfs/discovery/monitor/push/ping targets, drops the refcount, stops acceptor, destroys routes, shuts down LND nets, and unprepares.
- Counters and resources:
  - `lnet_counters_get_common()`, `lnet_counters_get()`, and `lnet_counters_reset()` aggregate or clear per-CPT counters under the net lock.
  - `lnet_res_containers_create()`, `lnet_res_lh_lookup()`, and `lnet_res_lh_initialize()` manage per-CPT resource cookie namespaces for MD/ME/EQ style handles.
- Local NI and CPT helpers:
  - `lnet_net2ni_locked()`, `lnet_net2ni_addref()`, `lnet_get_net_locked()`, `lnet_nid_to_ni_locked()`, `lnet_nid_to_ni_addref()`, `lnet_islocalnet()`, and `lnet_islocalnid()` provide net/NID lookups with refcounting where needed.
  - `lnet_nid_cpt_hash()`, `lnet_cpt_of_nid_locked()`, `lnet_nid2cpt()`, and `lnet_cpt_of_nid()` map NIDs to CPTs, with fast paths when NI CPT arrays are immutable and safe to read without locking.
  - `lnet_count_acceptor_nets()` counts local nets that need the acceptor because their LND exposes `lnd_accept`.
- Ping and push targets:
  - `lnet_ping_buffer_alloc()/free()` allocate refcounted ping buffers sized to the flattened ping-info payload.
  - `lnet_ping_target_setup()`, `lnet_ping_target_update()`, `lnet_ping_target_install_locked()`, and `lnet_ping_target_fini()` create and publish the GET-based reserved-portal ping target that exposes local NI status, features, large NIDs, discovery/routing bits, and optional LND NID metadata.
  - `lnet_push_target_init()`, `lnet_push_target_resize()`, `lnet_push_target_post()`, `lnet_push_target_event_handler()`, and `lnet_push_target_fini()` create the PUT-based peer-push target used to receive peer updates and resize when larger incoming data requires more space.
  - `lnet_mark_ping_buffer_for_update()`, `lnet_update_ping_buffer()`, and `lnet_queue_ping_buffer_update()` defer ping-buffer rebuilds through a workqueue when non-routing paths need to refresh published local information.
- LND net/NI startup and shutdown:
  - `lnet_startup_lndni()` validates `lnet_interfaces_max`, starts an LND NI, detects duplicate NIDs, handles loopback specially, initializes NI credits and health, seeds randomness, and increments `ln_ni_total`.
  - `lnet_startup_lndnet()` either attaches to an existing network for multi-rail additions or loads/initializes a unique net, starts all NIs from `net_ni_added`, splices active NIs into the real net, marks them active, restores requested tunables, and adds unique nets to `ln_nets`.
  - `lnet_startup_lndnets()` marks LNet running and starts a parsed net list; on failure it shuts everything down.
  - `lnet_shutdown_lndni()`, `lnet_shutdown_lndnet()`, `lnet_shutdown_lndnets()`, `lnet_ni_unlink_locked()`, and `lnet_clear_zombies_nis_locked()` move NIs/nets out of active lists, clear lazy portal messages, wait for per-CPT NI refs to drain, invoke LND shutdown outside `ln_api_mutex`, free NI/net objects, cancel resend messages, and transition to shutdown.
- Dynamic local configuration:
  - `lnet_dyn_add_ni()` handles modern local NI addition and legacy ip2nets input. It validates LND type and CPTs, allocates net/NI objects, applies default tunables, and calls `lnet_add_net_common()` under `ln_api_mutex`.
  - `lnet_add_net_common()` rejects additions that would invalidate route config, starts the net/NI, builds a replacement ping target before publication, applies UDSPs to the net and its NIs, starts the acceptor if needed, notifies peer tables, publishes ping info, and calls registered NID-update callbacks.
  - `lnet_dyn_del_ni()` and `lnet_dyn_del_net()` forbid deleting loopback, build replacement ping info before teardown, send NID-update notifications, shut down selected NIs or whole nets, stop the acceptor if no acceptor nets remain, and publish the updated ping target.
  - `lnet_dyn_add_net()` and `lnet_dyn_del_net()` are deprecated unique-net APIs kept for older DLC users.
- Legacy ioctl control:
  - `LNetCtl()` dispatches `IOC_LIBCFS_*` commands for NI lookup, route add/delete/list, local NI config/stats, LNet counters, router/buffer config, NUMA range, local/peer health stats and recovery queues, peer add/delete/list/state, connection-per-peer tuning, route notification, distance calculation, fault injection, ping/discover, and UDSP add/delete/get operations.
  - The default ioctl path looks up a local NI by `ioc_net` and forwards unknown commands to the LND `lnd_ctl` callback if present.
- Generic netlink support:
  - `lnet_genl_send_scalar_list()` and `lnet_genl_parse_list()` emit schema/key-table messages that describe the nested scalar layouts used by LNet netlink commands.
  - `nla_extract_val()` and `nla_strnid()` centralize typed value extraction and NID string parsing with extack messages.
  - `lnet_net_conf_cmd()` configures or unconfigures the LNet stack, with flags to ignore module parameters and use large NIDs.
  - `lnet_cpt_of_nid_show_*()` dumps CPT mappings for requested NIDs.
  - `lnet_net_show_*()` dumps local net/NI configuration, interfaces, stats, UDSP info, message stats, health stats, tunables, LND tunables, device CPT, and CPT lists. Dump output is version-gated and can omit volatile data when exporting backup configuration.
  - `lnet_net_cmd()` and `lnet_genl_parse_local_ni()` parse net/NI create/delete/replace requests, including interface/NID selectors, common tunables, LND tunables, CPT lists, health replacement, and legacy ip2nets.
  - `lnet_peer_ni_cmd()`, `lnet_parse_peer_nis()`, and `lnet_peer_ni_show_*()` manage and dump peer primary NIDs, peer NIs, multi-rail state, peer state, UDSP info, credits, refcounts, traffic counters, and health metrics.
  - `lnet_route_cmd()` and `lnet_route_show_*()` add/delete/update/list routes, validate net/gateway/hop/priority/state/notify-time parameters, and present route state/type.
  - `lnet_ping_show_*()` and `lnet_ping_cmd()` implement netlink ping/discover request paths, collect successful peer NI results and failed targets, and emit either result tables or error tables.
  - `lnet_peer_dist_show_*()` computes and dumps distance/order for requested peer NIDs through `LNetDist()`.
  - `lnet_peer_fail_cmd()` configures fail thresholds for a peer NID through `lnet_fail_nid()`.
  - `lnet_debug_recovery_show_*()` dumps local or peer NI recovery queues, dynamically building a key table sized to the number of recovered NIDs.
  - `lnet_fault_show_*()` and `lnet_fault_cmd()` list and manage drop/delay fault rules through the LNet fault subsystem.
  - `lnet_routing_cmd()` toggles router pools on/off. `lnet_buffers_cmd()` begins parsing router-buffer adjustments in this chunk, but its tail is outside the line range.

## Control Flow

Startup begins in `lnet_lib_init()`, which prepares process-global locks and netlink registration but does not start local networking. Runtime networking starts when `LNetNIInit()` gets the first reference. It calls `lnet_prepare()`, creates loopback, optionally parses configured networks, starts all LND nets, configures legacy routes/router pools when compiled in, starts acceptor and target MDs, starts monitoring/discovery, then exposes the running state to routers and users. Later `LNetNIInit()` calls only increment the reference count.

Shutdown is the reverse but must handle live references and asynchronous MD events. `LNetNIFini()` only performs full teardown for the last reference. It marks LNet stopping, stops subsystems that can call back into the API before dropping the last ref, unlinks push and ping MDs and waits for buffer references, stops the acceptor, destroys routes, moves nets to zombie lists, shuts down each LND NI with references drained, cancels resend messages, marks state shutdown, and frees all core allocations through `lnet_unprepare()`.

Dynamic NI addition uses an allocate-start-publish sequence. User input is parsed into a temporary `lnet_net` with NIs on `net_ni_added`; `lnet_startup_lndnet()` starts each NI and splices them into the active net; `lnet_add_net_common()` builds replacement ping info after the new NI exists, applies UDSP policy, updates peer tables, starts the acceptor if required, publishes the new ping buffer, and notifies NID-update callbacks.

Dynamic deletion uses a publish-before-remove pattern for ping info sizing: it computes the bytes that will be removed, creates a replacement ping target, shuts down the NI/net, stops acceptor if applicable, then swaps the ping target and pushes updates. This reduces the window where peers can fetch stale or undersized ping information, but it means failure to allocate replacement ping info can block deletion.

Generic-netlink dump flows generally split into `start`, `dump`, and `done` callbacks. `start` validates state and input, builds a snapshot in a `genradix` list where needed, stores it in `cb->args[0]`, and may set `min_dump_alloc`. `dump` emits a schema/key table on the first call and then streams value messages from the stored index. `done` frees the snapshot. Net dumps are more live than route/peer snapshots because they traverse `ln_nets` under `lnet_net_lock()` and maintain an index across dump calls.

Ping/discover flows parse target NIDs, call `lnet_ping()` or `lnet_discover()` outside the shown implementations, then look up discovered peer metadata under `ln_api_mutex` to report primary NID and multi-rail state. Failures are accumulated and emitted as a replacement key table with error attributes rather than failing the entire dump.

## State, Locking, And Persistence Behavior

Persistent configuration in this chunk is mostly kernel memory and module-parameter state; it does not write on-disk config. Admin-visible persistence is through live kernel state: configured nets/NIs, route tables, peer tables, UDSP policy list, fault rules, router pools, health values, recovery queues, counters, and published ping/push MDs. Backup/export behavior is supported in netlink dumps through `NLM_F_DUMP_FILTERED`, which suppresses loopback and volatile status/stats in some paths.

The primary serialization lock is `the_lnet.ln_api_mutex`. It protects high-level lifecycle/config changes, module-parameter updates that affect runtime behavior, NID update callback registration, and many ioctl/netlink operations. Lower-level data structures use `lnet_net_lock()` or `lnet_net_lock_current()` for net/peer/router state and `lnet_res_lock` for resource handles. `ln_lnd_mutex` serializes LND registration, module loading, startup, shutdown, and module lifetime interactions.

The code carefully drops locks around operations that may block or call back into the API. Examples include waiting for old ping MD refs in `lnet_ping_target_update()` and invoking LND shutdown from `lnet_clear_zombies_nis_locked()`. Zombie NI cleanup explicitly releases `ln_api_mutex` and the net lock while sleeping for references, then reacquires them.

Reference state is important. NIs have per-CPT refs, active/zombie list membership, and `LNET_NI_STATE_*` transitions. Ping buffers are `kref`-managed because active MD events can outlive publication. Resource handles use cookies containing CPT and type bits to avoid collisions and stale-handle confusion. `ln_interface_cookie` is initialized from realtime nanoseconds to prevent delayed replies/ACKs from appearing valid after restart.

## Dependencies And Integration Points

- Linux kernel APIs: module parameters, `kmem_cache`, generic netlink, `nlattr` parsing, `sk_buff`, workqueues, krefs, atomics, spinlocks/mutexes/completions/wait queues, `request_module()`, `copy_to_user()`, and time conversion helpers.
- Libcfs/LNet internals: CPT tables/allocators, LNet locks, NID parsing/formatting, network parsing, LND descriptors, portal/ME/MD APIs, peer table APIs, route APIs, router-pool APIs, monitor/discovery threads, health/recovery queues, UDSP policy engine, fault injection subsystem, lazy portal cleanup, and message finalization.
- UAPI compatibility: legacy ioctl structs and generic-netlink scalar schemas must remain compatible with user tools. Several code paths preserve older behavior: deprecated `ip2nets`/routes, legacy NI info fillers, truncated tunable copies based on user-provided size, string-form CPT lists for old tools, version-gated netlink stats and UDSP data, and large-NID handling.
- LND-specific integration: each LND supplies startup/shutdown/control/tunables/metadata callbacks. LND netlink keys are inserted dynamically into the net dump schema when the base LND changes.
- Peer discovery/routing integration: ping target feature bits advertise discovery/routing/large-NID/metadata capabilities; push target receives peer updates; route changes and NI changes feed peer tables, path selection, and monitor recovery behavior.

## Risks And Edge Cases

- Several netlink parsers advance `struct nlattr *` variables inside nested loops. These paths are sensitive to malformed attribute ordering and rely on strict key/value alternation.
- Some clamp calls appear to discard their return value, for example health value parsing in `lnet_genl_parse_local_ni()` and `lnet_parse_peer_nis()`. If `clamp_t()` is a pure expression in this kernel, out-of-range values may not actually be clamped before assignment/use.
- `lnet_genl_parse_local_ni()` appends CPTs into `conf->lic_cpts` without a visible bound against the array length, only validating each value is less than `LNET_CPT_NUMBER`. A malicious or buggy netlink message with too many CPT attributes could be a memory-corruption risk unless upper layers bound the nested list elsewhere.
- `lnet_slab_setup()` returns immediately on an intermediate cache allocation failure without cleaning already-created caches. The caller failure path invokes `lnet_unprepare()` and `lnet_slab_cleanup()`, so this is safe only because all setup failures route through that cleanup.
- `lnet_startup_lndnet()` treats `lnet_startup_lndni()` returning `-EEXIST` unusually by adding the NI to `local_ni_list` before checking `rc != 0`. The surrounding comments imply duplicate handling, but this deserves care because the NI may already have had refs adjusted.
- Dynamic deletion depends on successfully allocating and attaching replacement ping MDs before removing NIs. Low-memory conditions can leave undesired NIs in place rather than deleting them.
- Many dump paths build a snapshot under locks but later report live state, or keep an index across multi-message dumps while the system can change. The API mutex/net lock reduce races in many places, but long dumps can still face state churn, especially for live net dumps.
- Error cleanup for netlink replies must cancel the correct header. Paths that call `genlmsg_cancel()` after a failed `genlmsg_put()` with a NULL header are conventional in this file but should be audited against kernel expectations.
- The chunk contains compatibility paths for old userspace. Bugs in size checks, tunable truncation, or NID4-only fillers can silently omit data or return partial information.
- Health/recovery manual mutation can enqueue local NIs for recovery and update published status. Incorrect health bounds or missing locking would affect monitor behavior and peer-visible availability.

## Test Signals

- Module/lifecycle tests should cover `lnet_lib_init()`/`lnet_lib_exit()` and repeated `LNetNIInit()`/`LNetNIFini()` refcount behavior, including failure injection at slab, lock, peer table, portal, ping target, push target, monitor, and discovery startup steps.
- Dynamic config tests should add/delete a single NI, multiple NIs on the same net, a whole net, duplicate interfaces/NIDs, invalid CPTs, too many interfaces, loopback deletion attempts, and low-memory ping-target replacement failure.
- Ping/push tests should verify ping-info feature bits, loopback-first validation, large-NID layout, metadata inclusion for LNDs that provide it, byte swapping, refcount wait behavior on MD unlink, and push-target resize/repost after larger peer updates.
- Control-plane compatibility tests should exercise legacy ioctls and netlink versions 0 through current for local net dumps, peer dumps, route dumps, ping/discover, UDSP info, LND tunables, backup export filtering, and string CPT output.
- Parser fuzzing should target generic-netlink key/value nesting for `lnet_net_cmd()`, `lnet_peer_ni_cmd()`, `lnet_route_cmd()`, `lnet_ping_cmd()`, `lnet_peer_fail_cmd()`, recovery debug, fault commands, routing, and buffers.
- Locking/concurrency tests should run route/peer/net dumps while adding/removing NIs, toggling discovery, changing health values, and stopping LNet, checking for deadlocks, use-after-free, leaked refs, and consistent extack errors.
- Health/recovery tests should set local and peer health to zero/full/intermediate values, verify status transitions, recovery queue insertion, recovery-list ioctls/netlink dumps, and monitor wakeups.
- Fault injection tests should list/add/delete/reset drop and delay rules, validate counters, and combine fault rules with ping/discover and health-sensitive retry paths.
- Router tests should toggle routing and adjust router pools through ioctl and netlink, then verify route state reporting, route notifications with realtime-to-monotonic conversion, and buffer-pool config reads.

## Cross-Chunk Notes

The line range ends inside `lnet_buffers_cmd()`, so the remainder of buffer parsing, NUMA generic-netlink handling, `lnet_genl_ops`, `lnet_family`, and public helper functions after line 9906 must be covered by the next chunk. The visible code references `lnet_ping()` and `lnet_discover()` prototypes and their call sites, but their implementations are after this range and should be reconciled with this chunk's ping/discover ioctl and netlink behavior during merge.
