# subset-b-007109 GlusterD RPC, services, quorum, and friend state-machine research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-rpc-ops.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-rpc-ops.c

## Purpose
Implements GlusterD outbound RPC operations and their callbacks for peer discovery, friend add/remove/update, cluster and mgmt-v3 locks, transaction stage/commit, brick/node operations, and CLI response packing. It is the bridge between the friend/op state machines and the RPC client programs registered for peer, management, management-v3, and brick protocols.

## Important APIs, types, and functions
`glusterd_op_send_cli_response()` builds `gf_cli_rsp` replies and serializes operation dictionaries. `glusterd_big_locked_cbk()` wraps callback execution under `priv->big_lock`. Peer callbacks include `__glusterd_probe_cbk()`, `__glusterd_friend_add_cbk()`, `__glusterd_friend_remove_cbk()`, and `__glusterd_friend_update_cbk()`. Transaction callbacks include cluster lock/unlock, mgmt-v3 lock/unlock, `__glusterd_stage_op_cbk()`, `__glusterd_commit_op_cbk()`, and `__glusterd_brick_op_cbk()`. Request senders are `glusterd_rpc_probe()`, `glusterd_rpc_friend_add()`, `glusterd_rpc_friend_remove()`, `glusterd_rpc_friend_update()`, `glusterd_cluster_lock()`, `glusterd_mgmt_v3_lock_peers()`, `glusterd_mgmt_v3_unlock_peers()`, `glusterd_cluster_unlock()`, `glusterd_stage_op()`, `glusterd_commit_op()`, and `glusterd_brick_op()`. The file exports `gd_peer_prog`, `gd_mgmt_prog`, `gd_mgmt_v3_prog`, and `gd_brick_prog`.

## Control flow
Probe responses decode `gd1_mgmt_probe_rsp`, update or merge peer hostnames, inject friend-state events, reply to the CLI when applicable, destroy the frame, then kick both friend and op state machines. Friend add/remove callbacks translate remote ACC/RJT responses into friend-state events and CLI responses. Transaction lock, unlock, stage, commit, and brick callbacks decode XDR replies, validate the sender against the peer list, update `opinfo` and per-transaction opinfo, then inject `GD_OP_EVENT_RCVD_ACC` or `GD_OP_EVENT_RCVD_RJT`. Stage/commit callbacks unserialize peer response dictionaries; commit merges profile and rebalance dictionaries into local op context for those operations. `glusterd_brick_op()` selects pending nodes, builds node or brick payloads, submits one request per pending target, and records `opinfo.brick_pending_count`.

## State and persistence behavior
The file mostly mutates runtime state: `opinfo`, transaction opinfo records, call-frame cookies, peer hostnames, peer UUIDs, and friend/op event queues. It serializes dictionaries into RPC payloads and deserializes response dictionaries back into temporary `dict_t` objects. Persistent effects are indirect through downstream state-machine handlers, peerinfo storage, volume operation commits, and brick/node services. CLI responses may add derived fields such as rebalance status, profile count, or `glusterd_workdir`.

## Dependencies and integration points
Depends on Gluster RPC client/server XDR types, `glusterd-sm.h`, `glusterd-op-sm.h`, peerinfo lookup, transaction opinfo helpers, brick/node payload builders, snapshot export/import helpers, rebalance/profile response mergers, and CLI transfer helpers. It is called by friend-state action functions and op-state fanout code through the exported `rpc_clnt_program` procedure tables.

## Risks and test signals
High-risk areas are frame/cookie lifetime, dictionary serialization ownership (`extra_stdfree` versus explicit `free()`), stale peerinfo pointers used under RCU read sections, global `opinfo` updates racing with transaction-specific state, missing state-machine progress after an RPC error, and partial brick-op fanout when one target lacks RPC. Tests should cover probe alias addition, duplicate hostname handling, friend ACC/RJT paths, deprobe with disconnected peers, lock/stage/commit decode failures, unknown-peer replies, mgmt-v3 transaction-id propagation, commit response dictionary merging, status-volume brick index injection, and cleanup of allocated hostnames/dicts/frames on all error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-rpc-ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-scrub-svc.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-scrub-svc.c

## Purpose
Manages the global bitrot scrub service named `scrub`: service vtable setup, initialization, volfile generation, start/stop decisions, and reconfiguration when the scrub graph changes.

## Important APIs, types, and functions
`glusterd_scrubsvc_build()` installs manager/start/stop hooks on a `glusterd_svc_t`. `glusterd_scrubsvc_init()` calls `glusterd_svc_init()` with `scrub_svc_name`. `glusterd_scrubsvc_manager()` initializes on demand, creates a scrub volfile, kills any old process, restarts the generic service, and reconnects its RPC connection unless bitd policy says it should stop. `glusterd_scrubsvc_stop()` delegates to `glusterd_svc_stop()`. `glusterd_scrubsvc_reconfigure()` compares old/new volfile contents and topology, then either notifies fetchspec or restarts through the manager.

## Control flow
The manager first ensures `svc->inited`, then branches on `glusterd_should_i_stop_bitd()`. Stop policy sends `SIGTERM`; otherwise it regenerates the global volfile with `build_scrub_graph`, stops the process with `SIGKILL`, starts with supplied flags, and calls `glusterd_conn_connect()`. Reconfigure avoids work when the generated volfile is byte-identical, sends a fetchspec notification for option-only changes, and restarts when topology changed or the service should stop.

## State and persistence behavior
Persistent state is the generated scrub volfile under the GlusterD workdir. Runtime state is held in the shared `glusterd_svc_t`: `inited`, process metadata, connection metadata, and service name. Failures emit `EVENT_SVC_MANAGER_FAILED`.

## Dependencies and integration points
Uses `glusterd-svc-mgmt`, generic service helpers, `glusterd-volgen`'s `build_scrub_graph`, bitrot policy helper `glusterd_should_i_stop_bitd()`, fetchspec notification, and Gluster event/logging APIs. It integrates with the broader daemon-service reconfigure path.

## Risks and test signals
Risks include unnecessary `SIGKILL` restarts for option-only changes, stale volfiles after failed generation, missed RPC reconnects after restart, and start/stop behavior when bitrot is disabled mid-reconfigure. Tests should exercise identical volfile no-op, topology-identical fetchspec notification, topology-changed restart, bitd-stop branch, failed volfile creation, and service-manager event emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-scrub-svc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-scrub-svc.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-scrub-svc.h

## Purpose
Declares the GlusterD scrub service wrapper and lifecycle API used to manage the bitrot scrub daemon.

## Important APIs, types, and functions
`glusterd_scrubsvc_t` wraps `glusterd_svc_t svc` plus a `gf_store_handle_t *handle`. Declared functions are `glusterd_scrubsvc_build()`, `glusterd_scrubsvc_init()`, `glusterd_scrubsvc_manager()`, `glusterd_scrubsvc_stop()`, and `glusterd_scrubsvc_reconfigure()`.

## Control flow
Callers build the service hook table, initialize it through the manager or explicit init, then use the manager/reconfigure entry points to converge process state with current bitrot and topology options.

## State and persistence behavior
The header exposes the scrub service state container but does not itself persist data. The handle field suggests compatibility with GlusterD store-backed service metadata, while the implementation mainly uses shared service process/connection state and generated volfiles.

## Dependencies and integration points
Includes `glusterd-svc-mgmt.h`; used by GlusterD service orchestration and the scrub service implementation. It sits alongside bitd/scrub volfile generation and service restart plumbing.

## Risks and test signals
Header drift between declarations and implementation would break daemon orchestration. Tests should compile lifecycle users and verify build/init/manager/reconfigure hooks are installed on the expected `glusterd_svc_t`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-scrub-svc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-server-quorum.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-server-quorum.c

## Purpose
Implements server-quorum validation and local brick start/stop reactions when the peer cluster gains or loses quorum. It decides which volume operations are blocked by quorum, computes active and required peer counts, and applies quorum status to each started volume.

## Important APIs, types, and functions
`glusterd_is_quorum_validation_required()` exempts get-like operations and quorum-option changes. `glusterd_validate_quorum()` blocks volume operations when the target volume uses server quorum and the node does not meet quorum. `glusterd_is_quorum_option()`, `glusterd_is_quorum_changed()`, `glusterd_get_quorum_cluster_counts()`, `does_quorum_meet()`, `does_gd_meet_server_quorum()`, `glusterd_is_volume_in_server_quorum()`, and `glusterd_is_any_volume_in_server_quorum()` provide policy helpers. `glusterd_do_volume_quorum_action()` starts or stops local bricks for one volume, and `glusterd_do_quorum_action()` applies this under the GlusterD cluster lock. `check_quorum_for_brick_start()` returns a three-way brick-start decision.

## Control flow
Validation skips status and set/reset of quorum keys, extracts `volname`, ignores nonexistent or non-server-quorum volumes, then checks current cluster quorum. Count calculation starts with self, iterates RCU-protected peers whose `quorum_contrib` is `QUORUM_UP` or `QUORUM_DOWN`, counts only `QUORUM_UP` as active, and derives the required count from `cluster.server-quorum-ratio` or strict majority. Quorum action marks `pending_quorum_action`, takes GlusterD lock, computes counts once, then updates every volume. A volume losing quorum stops local bricks; a volume regaining quorum starts local bricks that are not already start-triggered and stores volinfo because ports may change.

## State and persistence behavior
Runtime state includes peer `quorum_contrib`, volume `quorum_status`, brick `start_triggered`, and `conf->pending_quorum_action`. Persistent state changes occur when regained quorum restarts bricks and `glusterd_store_volinfo()` writes updated volume metadata, especially port changes. Event notifications report quorum lost/regained.

## Dependencies and integration points
Depends on GlusterD peer lists, volume/brick metadata, global options dict, store APIs, op-sm validation, syncop lock/unlock, and brick start/stop helpers. Friend state-machine transitions update quorum contribution and call this logic after peer views settle.

## Risks and test signals
Risks include incorrect percentage ceiling, treating `QUORUM_WAITING` peers as outside quorum, false reconfiguration detection when only one quorum option matches, stopping intentionally down bricks on unrelated peer events, and lock ordering around brick restart. Tests should cover default majority and ratio quorum, validation exemptions, non-server-quorum volumes, lost/regained quorum transitions, unchanged quorum reconnect behavior, volinfo store after restart, and operation rejection message propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-server-quorum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-server-quorum.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-server-quorum.h

## Purpose
Declares GlusterD server-quorum policy helpers and the public action entry point used by operation validation, peer-state changes, and brick start decisions.

## Important APIs, types, and functions
Defines `GLUSTERD_SERVER_QUORUM` as `"server"`. Declares `glusterd_is_quorum_changed()`, `glusterd_do_quorum_action()`, `glusterd_is_quorum_option()`, `glusterd_is_volume_in_server_quorum()`, `glusterd_is_any_volume_in_server_quorum()`, `does_gd_meet_server_quorum()`, and `does_quorum_meet()`.

## Control flow
Consumers use the option helpers during set/reset validation, use the volume helpers to determine whether quorum applies, call `does_gd_meet_server_quorum()` for current-node eligibility, and call `glusterd_do_quorum_action()` when peer connectivity or imported cluster view changes require service convergence.

## State and persistence behavior
The header stores no state. Its APIs operate on `glusterd_conf_t`, peer quorum contribution state, volume quorum status, and local brick process state in the implementation.

## Dependencies and integration points
Includes `glusterd.h` for volume and translator types. It is included by the friend state machine, quorum implementation, op-sm validation, and brick start paths.

## Risks and test signals
The exposed API is small but high impact: semantic changes affect whether writes and admin operations are allowed. Compile and integration tests should verify all declarations match implementation signatures and that quorum action is reachable from peer-state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-server-quorum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-shd-svc-helper.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-shd-svc-helper.c

## Purpose
Provides helper routines for per-volume self-heal daemon service paths, multiplexed service cleanup, and pidfile dictionary export.

## Important APIs, types, and functions
`glusterd_svc_build_shd_socket_filepath()` builds the SHD Unix socket path from the volume SHD rundir and local UUID, then shortens/normalizes it with `glusterd_set_socket_filepath()`. `glusterd_svc_build_shd_pidfile()` and `glusterd_svc_build_shd_volfile_path()` build per-volume pidfile and volfile paths. `glusterd_shd_svcproc_cleanup()` detaches a volume SHD service from its mux process, unrefs RPC clients, removes pidfiles, and marks service state uninitialized. `glusterd_svc_set_shd_pidfile()` adds the pidfile to a dict.

## Control flow
Path builders are leaf functions that return early if `THIS->private` is unavailable. Cleanup first drops the service's direct RPC ref, then under `conf->attach_lock` detaches list nodes, clears `svc_proc`, resets `inited`, unlinks the pidfile, and if the mux process has no services removes it from `conf->shd_procs`. The mux RPC unref is intentionally performed after releasing the attach lock.

## State and persistence behavior
Persistent filesystem effects are pidfile removal and use of generated workdir/rundir paths. Runtime state includes `shd->attached`, `svc->conn.rpc`, `svc->svc_proc`, `svc->inited`, `svc->mux_svc`, and mux-process lists. `glusterd_svc_set_shd_pidfile()` exports state to a dictionary for status or node operations.

## Dependencies and integration points
Depends on SHD path macros, generic service helper path shortening, RPC refcounting, GlusterD attach-lock discipline, and `glusterd-shd-svc.h` service structures. Used by SHD init/start/stop and management status paths.

## Risks and test signals
Risks include list corruption during detach, unrefing mux RPC while pending events still reference `svc_proc`, missing cleanup when `THIS->private` is null, and pidfile path truncation. Tests should cover cleanup of last and non-last service in a mux process, RPC ref release outside the lock, pidfile dict export, and socket/pid/volfile path construction for long volume names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-shd-svc-helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-shd-svc-helper.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-shd-svc-helper.h

## Purpose
Declares helper APIs used by SHD service management for path building, mux cleanup, attach-failure recovery, volfile generation, and pidfile export.

## Important APIs, types, and functions
Declared functions are `glusterd_svc_build_shd_socket_filepath()`, `glusterd_svc_build_shd_pidfile()`, `glusterd_svc_build_shd_volfile_path()`, `glusterd_shd_svcproc_cleanup()`, `glusterd_recover_shd_attach_failure()`, `glusterd_shdsvc_create_volfile()`, and `glusterd_svc_set_shd_pidfile()`.

## Control flow
The implementation file provides the path builders, cleanup, and pidfile export; `glusterd-shd-svc.c` provides attach-failure recovery and volfile generation. Callers use these helpers around SHD mux initialization, start, stop, and status payload construction.

## State and persistence behavior
The header itself holds no state. Its functions operate on `glusterd_volinfo_t`, `glusterd_shdsvc_t`, `glusterd_svc_t`, mux process state, generated volfiles, pidfiles, and dictionaries.

## Dependencies and integration points
Includes `glusterd-svc-mgmt.h`, which supplies service, volume, and dictionary-related types. It is the shared contract between SHD service implementation and generic GlusterD service helpers.

## Risks and test signals
Because some declarations are implemented outside the helper C file, signature drift can silently break service orchestration at compile time. Tests should include build coverage and start/stop/status paths that touch every declared function.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-shd-svc-helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-shd-svc.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-shd-svc.c

## Purpose
Manages per-volume `glustershd` self-heal daemon services, including mux-process initialization, volfile generation, process start/attach/detach, reconfiguration, restart across all volumes, and stop/cleanup behavior.

## Important APIs, types, and functions
`glusterd_shdsvc_build()` initializes service hooks. `glusterd_shdsvc_init()` prepares connection and process metadata for either an existing mux connection or a new mux process. `glusterd_shdsvc_create_volfile()` generates a self-heal volfile with forced heal options for compatible volumes or removes stale volfiles for incompatible volumes. `glusterd_svcs_shd_compatible_volumes_stopped()` inspects mux members. `glusterd_shdsvc_manager()` serializes SHD restarts with `conf->restart_shd`. `glusterd_new_shd_svc_start()`, `glusterd_recover_shd_attach_failure()`, `glusterd_shdsvc_start()`, `glusterd_shdsvc_reconfigure()`, `glusterd_shdsvc_restart()`, and `glusterd_shdsvc_stop()` implement lifecycle operations.

## Control flow
The manager skips snapshot volumes, waits for any existing SHD restart, refs the volume, stops incompatible initialized services, creates a volfile, initializes mux state, then stops when all compatible mux members are stopped or starts only when the volume is started. Start initializes mux state if needed, attaches to an existing running process when `shd->attached` is true, or launches a new `glusterfsd` process with self-heald client pid and local node UUID xlator option. Reconfigure compares generated volfile and topology with a graph-check dictionary, uses fetchspec notification for option-only changes, and delegates to the manager for topology changes. Stop removes the service from the mux list, stops the whole process if it was the last service, otherwise detaches only this volume, marks offline, unlinks the pidfile, and calls shared cleanup.

## State and persistence behavior
Runtime state spans `volinfo->shd`, `glusterd_svc_t`, mux process lists, RPC refs, `svc->online`, `svc->inited`, `shd->attached`, and the restart condition variable. Persistent state includes per-volume SHD volfiles, pidfiles, node-state store updates, and potentially process logs. Generated volfiles force background self-heal count to zero and data/metadata/entry self-heal on.

## Dependencies and integration points
Depends on generic svc/proc/conn management, mux service attach/detach APIs, volfile generation (`glusterd_shdsvc_generate_volfile`), volume compatibility checks, store APIs, fetchspec notification, and process command-line construction. It integrates with volume start/stop/reconfigure, peer detach cleanup, daemon restart on GlusterD restart, and status/node operations through SHD helper functions.

## Risks and test signals
Risks include a likely iterator bug in `glusterd_svcs_shd_compatible_volumes_stopped()` where `cds_list_entry(svc, ...)` uses the original service instead of `temp_svc`, races around mux attach/detach cleanup, leaked volume refs on attach failures, serialized restart condition not being broadcast, and stale pidfiles/volfiles for incompatible volumes. Tests should cover compatible and incompatible volume transitions, all-volumes-stopped behavior, attach failure recovery, detach from shared mux process, last-service stop, reconfigure identical/topology-identical/topology-changed cases, snapshot-volume skip, and restart across started volumes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-shd-svc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-shd-svc.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-shd-svc.h

## Purpose
Declares the self-heal daemon service wrapper and lifecycle API for per-volume `glustershd` management.

## Important APIs, types, and functions
`glusterd_shdsvc_t` contains a `glusterd_svc_t svc` and `gf_boolean_t attached` indicating mux/process attachment. Declared functions are `glusterd_shdsvc_build()`, `glusterd_shdsvc_init()`, `glusterd_shdsvc_manager()`, `glusterd_shdsvc_start()`, `glusterd_shdsvc_reconfigure()`, `glusterd_shdsvc_restart()`, and `glusterd_shdsvc_stop()`.

## Control flow
Volume initialization builds the service hooks; lifecycle callers then use manager/start/stop/reconfigure to converge the per-volume SHD service with volume status and compatibility.

## State and persistence behavior
The header exposes the service container and `attached` state but performs no persistence. The implementation persists volfiles, pidfiles, node-state store data, and process logs.

## Dependencies and integration points
Includes `glusterd-svc-mgmt.h` and forward-declares `glusterd_volinfo_t`. Used by volume metadata structures, SHD helper functions, and GlusterD service orchestration.

## Risks and test signals
Tests should verify lifecycle hook installation, attached-state transitions through start/stop, and compile-time agreement between this header and `glusterd-shd-svc.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-shd-svc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-sm.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-sm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-sm.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-sm.h

## Purpose
Defines the friend state-machine types, peerinfo structure, event/context payloads, quorum contribution enum, and public APIs for GlusterD peer orchestration.

## Important APIs, types, and functions
`gd_quorum_contrib_t` tracks quorum contribution as none, waiting, down, or up. `glusterd_friend_sm_state_t` enumerates peer states from default through request, accepted, rejected, connected, and unfriend states. `glusterd_peerinfo_t` stores peer UUID/hostname(s), state, connection/RPC program pointers, store handle, transition log, quorum flags, generation, and RCU cleanup fields. Context structs include `glusterd_peerctx_t`, `glusterd_friend_sm_event_t`, `glusterd_friend_req_ctx_t`, `glusterd_friend_update_ctx_t`, and `glusterd_probe_ctx_t`. Public functions create/inject/run the state machine, destroy contexts, name states/events, and broadcast friend deletion.

## Control flow
RPC callbacks and connection handlers allocate `glusterd_friend_sm_event_t`, fill peer identity and context, inject it, then call `glusterd_friend_sm()`. State-machine tables in the C file consume the enum values and action-function type declared here.

## State and persistence behavior
The header defines the in-memory peer model that is stored and restored by GlusterD store helpers. Peerinfo includes store handles and transition logs, plus RCU fields for safe deletion. Persistent volume and snapshot state is not defined here but is imported or cleaned by handlers using these contexts.

## Dependencies and integration points
Includes pthread, UUID compatibility, RPC client/server, call stubs, Gluster store, and GlusterD RCU. It is included by RPC ops, connection management, server quorum, op-sm integration, and peer utility code.

## Risks and test signals
Risks include enum/table ordering drift, incorrect context destructor selection for a new event type, RCU lifetime misuse of `glusterd_peerinfo_t`, and quorum contribution semantics changing without updating quorum code. Tests should compile all state-table initializers and exercise every event enum through name lookup and context cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-sm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-snapd-svc-helper.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-snapd-svc-helper.c

## Purpose
Builds per-volume snapshot daemon directory, socket, pidfile, and volfile paths used by `snapd` service management.

## Important APIs, types, and functions
`glusterd_svc_build_snapd_rundir()` returns the volume pid directory. `glusterd_svc_build_snapd_socket_filepath()` appends `run-<MY_UUID>` inside that rundir and passes it to `glusterd_set_socket_filepath()`. `glusterd_svc_build_snapd_pidfile()` builds `<rundir>/<volname>-snapd.pid`. `glusterd_svc_build_snapd_volfile()` builds `<volume-dir>/<volname>-snapd.vol`.

## Control flow
Each helper derives paths from `THIS->private` and volume macros. Socket construction protects against `snprintf()` overflow by clearing the intermediate path before shortening/normalizing it.

## State and persistence behavior
The functions do not mutate service state directly; they define the persistent filesystem locations for snapd sockets, pidfiles, and volfiles. Their outputs are later stored in `glusterd_svc_t` process and connection fields.

## Dependencies and integration points
Depends on `glusterd.h`, `glusterd-utils.h`, volume directory macros, local UUID formatting, and generic socket-path shortening. Used by `glusterd-snapd-svc.c` during init and start.

## Risks and test signals
Risks include path truncation, null `THIS->private` assumptions, and inconsistent path generation across init/start/status. Tests should cover long volume names, long workdirs, socket path shortening, and path agreement with snapd process metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-snapd-svc-helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-snapd-svc-helper.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-snapd-svc-helper.h

## Purpose
Declares snapd path-builder helpers shared by snapshot daemon service initialization and process startup.

## Important APIs, types, and functions
Declares `glusterd_svc_build_snapd_rundir()`, `glusterd_svc_build_snapd_socket_filepath()`, `glusterd_svc_build_snapd_pidfile()`, and `glusterd_svc_build_snapd_volfile()`.

## Control flow
The snapd service implementation calls these helpers during init to populate connection socket path, process pidfile, and volfile path before launching `glusterfsd`.

## State and persistence behavior
No state is stored in the header. The declared helpers determine the filesystem paths for runtime and persistent snapd artifacts.

## Dependencies and integration points
Relies on `glusterd_volinfo_t` being visible to includers. Used by `glusterd-snapd-svc.c` and any future status or cleanup code needing snapd paths.

## Risks and test signals
Header/implementation signature drift would break snapd service compilation. Tests should verify every declared path helper is used consistently by init/start and handles maximum path lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-snapd-svc-helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-snapd-svc.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-snapd-svc.c

## Purpose
Manages the per-volume snapshot daemon service `snapd`: service hook setup, connection/process initialization, start/stop decisions based on USS/snapd enablement and volume status, process launch, restart across volumes, and RPC connection notifications.

## Important APIs, types, and functions
`glusterd_snapdsvc_build()` installs manager/start/stop hooks. `glusterd_snapdsvc_init()` creates rundir, socket connection, pidfile, volfile, per-volume snapd log directory, logfile, volfile id, and process metadata. `glusterd_snapdsvc_manager()` starts or stops the daemon based on `glusterd_is_snapd_enabled()` and volume status. `glusterd_snapdsvc_start()` builds and runs the `glusterfsd` command line, assigns a brick port through `pmap_assign_port()`, and passes listen-port xlator options. `glusterd_snapdsvc_restart()` iterates started volumes. `glusterd_snapdsvc_rpc_notify()` updates online state and volume refs on RPC events.

## Control flow
Manager initializes once, checks snapd enablement, stops snapd if enabled but the volume is stopped, otherwise creates a snapd volfile, starts the process, refs the volume, and connects RPC. If snapd is disabled and the process is running, it stops and clears `volinfo->snapd.port`. Start is idempotent when the process is already running. If the volfile is missing, start regenerates it for nodes that were down when USS was enabled. It optionally prefixes Valgrind args, adds localtime logging when configured, assigns a port, appends brick-port/listen-port/no-mem-accounting options, and runs synchronously or asynchronously depending on flags.

## State and persistence behavior
Runtime state includes `svc->inited`, `svc->online`, connection socket path, process metadata, `volinfo->snapd.port`, and a volume ref held while RPC is connected. Persistent artifacts are snapd volfiles, pidfiles, log directories/logfiles, and pmap port assignment. `RPC_CLNT_DESTROY` releases the volume ref acquired before connecting.

## Dependencies and integration points
Depends on generic service, connection, and process management; snapd path helpers; snapshot utility enablement and volfile generation; pmap port allocation; runner command execution; GlusterD options for bind address and localtime logging; and event notifications for service connect/disconnect/failure.

## Risks and test signals
Risks include leaked volume refs if connect fails after partial startup, stale `snapd.port` after abnormal process death, race between `glusterd_proc_is_running()` and runner launch, missing volfile recovery failure, and incorrect command-line ordering for `glusterfsd`. Tests should cover enabled/disabled transitions, stopped-volume stop branch, missing-volfile regeneration, port exhaustion, localtime and Valgrind args, async versus sync launch, restart iteration, RPC connect/disconnect/destroy notifications, and port clearing on stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-snapd-svc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-snapd-svc.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-snapd-svc.h

## Purpose
Declares the per-volume snapshot daemon service wrapper and lifecycle API for `snapd`.

## Important APIs, types, and functions
`glusterd_snapdsvc_t` wraps `glusterd_svc_t svc`, a `gf_store_handle_t *handle`, and the assigned daemon `port`. Declared functions are `glusterd_snapdsvc_build()`, `glusterd_snapdsvc_init()`, `glusterd_snapdsvc_manager()`, `glusterd_snapdsvc_start()`, `glusterd_snapdsvc_restart()`, and `glusterd_snapdsvc_rpc_notify()`.

## Control flow
Volume setup builds hooks, manager initializes and starts/stops based on snapd enablement and volume status, start launches `glusterfsd`, restart applies the manager to all started volumes, and RPC notify maintains online/ref state.

## State and persistence behavior
The header exposes the service and port fields. Implementation persists volfiles, pidfiles, logs, and port assignment indirectly through process management and volume metadata.

## Dependencies and integration points
Includes `glusterd-svc-mgmt.h`, which provides service and connection types. Used by volume metadata, snapd service implementation, and any service orchestration code that restarts or observes snapd.

## Risks and test signals
Tests should compile all lifecycle users and verify the `port` field is updated and cleared by start/stop paths while RPC notify releases the correct volume reference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-snapd-svc.h -->
