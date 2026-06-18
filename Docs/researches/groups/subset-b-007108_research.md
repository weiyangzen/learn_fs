# Research Report: subset-b-007108

This grouped report covers the requested GlusterFS glusterd management files. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-op-sm.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-op-sm.h

Purpose: Declares the glusterd operation state machine contract used by CLI and peer-coordinated management operations. It names operation states/events, the per-transaction operation context, brick response conversion helpers, and the exported entry points for staging, committing, locking, unlocking, and responding to management operations.

Important APIs and types: `glusterd_op_sm_state_t` enumerates transaction phases such as lock sent, staged, commit sent, brick op sent, ack drain, and failure states. `glusterd_op_sm_event_type_t` enumerates incoming transition triggers. `glusterd_op_sm_event_t` carries queued events, context, event type, and transaction id. `glusterd_op_info_t` is the central per-transaction state object with pending counts, selected op, op context, request pointer, result/error fields, pending brick list, transaction generation, and `skip_locking`. Public APIs include `glusterd_op_txn_begin()`, `glusterd_op_sm()`, `glusterd_op_stage_validate()`, `glusterd_op_commit_perform()`, `glusterd_op_send_cli_response()`, `glusterd_op_bricks_select()`, and transaction opinfo dictionary helpers.

Control flow: Handlers create or inject `glusterd_op_sm_event_t` events, store operation metadata in `glusterd_op_info_t`, build payload dictionaries, run stage validation, commit local changes, optionally fan out brick operations, wait for acknowledgements, and finally send CLI responses. The state machine separates peer lock, stage, commit, brick commit, unlock, and cleanup phases, which lets legacy op-sm based commands share one transaction engine.

State and persistence: Runtime transaction state is held in opinfo objects keyed by transaction id, with `pending_count` and `brick_pending_count` tracking asynchronous peer/brick completion. The header also exposes `glusterd_set_txn_opinfo()`, `glusterd_get_txn_opinfo()`, `glusterd_clear_txn_opinfo()`, and dict init/fini routines, so persistence here is in-memory transaction bookkeeping rather than on-disk storage. Actual volume or node-state persistence is performed by operation implementations such as quota, rebalance, replace-brick, and reset-brick after commit.

Dependencies and integration points: Depends on Gluster core xlator/logging headers, `glusterd.h`, RPC request types, hooks, dictionaries, volume/brick types, and URCU list heads. Files in this group use it directly for quota, rebalance, replace-brick, and reset-brick operation stage/commit entry points. It also ties operation completion to hook execution through `glusterd_op_commit_hook()` and to CLI output through `glusterd_op_send_cli_response()`.

Risks: This header defines a broad ABI internal to glusterd; changes to enum ordering, opinfo fields, pending-count behavior, or transaction-id handling can break distributed transaction sequencing. Since contexts are `void *` and operation ids are stored as plain `int`, type safety relies on consistent call-site discipline. Failure to clear opinfo or free operation context risks stale transactions and memory leaks.

Test signals: Useful signals include multi-peer CLI operations that exercise lock/stage/commit/unlock, injected peer rejection, brick-op failure paths, transaction-id propagation, CLI response content, hook execution, and cleanup after failed or timed-out operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-op-sm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-peer-utils.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-peer-utils.c

Purpose: Implements helper routines for creating, finding, serializing, updating, and destroying glusterd peer records. It is the local utility layer around `glusterd_peerinfo_t`, hostname/address lists, peer state checks, peer dictionary payloads, and RCU-safe peer deletion.

Important APIs and functions: `glusterd_peerinfo_cleanup()` removes a peer from the RCU peer list, drops its RPC client, schedules deferred destruction, and triggers quorum action if needed. `glusterd_peerinfo_new()` allocates and initializes a peer with state, uuid, hostname, transaction log, quorum contribution, port, and generation. Lookup helpers include `glusterd_peerinfo_find_by_hostname()`, `glusterd_peerinfo_find_by_uuid()`, `glusterd_peerinfo_find()`, `glusterd_peerinfo_find_by_generation()`, `glusterd_hostname_to_uuid()`, and `glusterd_uuid_to_hostname()`. Address helpers include `glusterd_peer_hostname_new()`, `glusterd_peer_hostname_free()`, `gd_peer_has_address()`, and `gd_add_address_to_peer()`. Dict helpers include `gd_add_friend_to_dict()`, `gd_update_peerinfo_from_dict()`, `gd_peerinfo_from_dict()`, and `gd_add_peer_detail_to_dict()`.

Control flow: Hostname lookup first performs a direct case-insensitive match across each peer's saved hostname list, then resolves the input hostname and each stored address with `getaddrinfo()` and compares IPv4/IPv6 socket addresses. Creation initializes the peer, adds the first address, creates a state-machine transaction log, marks quorum contribution for befriended peers, initializes delete locking, and increments the glusterd generation counter. Cleanup tries `delete_lock`, drops RPC references, removes the peer from `priv->peers` with `cds_list_del_rcu()`, stores `THIS` in the embedded RCU head, and defers final free to `glusterd_peerinfo_destroy()`.

State and persistence: Peer state lives in `glusterd_conf_t->peers` and in each `glusterd_peerinfo_t`: uuid, hostname, hostname list, connection flag, friend state, port, generation, quorum contribution, cached uuid string, RPC pointer, delete mutex, and state-machine log. Destruction calls `glusterd_store_delete_peerinfo()`, so peer cleanup also removes the persisted peer store entry. Dict serialization preserves uuid, backward-compatible primary hostname, numbered hostnames, address counts, port, state id/name, and connection status.

Dependencies and integration points: Uses `glusterd-store` for peer persistence, `glusterd-server-quorum` for quorum action, `glusterd-utils` for local address checks and hostname update helpers, friend state-machine naming, liburcu RCU list iteration, atomics for generation, and POSIX `getaddrinfo()`. Replace/reset-brick prevalidation in this group calls `glusterd_peerinfo_find()` under RCU to ensure destination hosts are friends, connected, and befriended.

Risks: Several lookups return pointers observed under an RCU read lock without taking a reference; callers must use them carefully and generally under the expected glusterd locking/RCU discipline. Hostname resolution can block while scanning peers and the source comments call this out as a performance risk. `gd_add_friend_to_dict()` assumes the hostname list has an entry when taking `cds_list_entry()`. Cleanup depends on `delete_lock` and deferred callbacks to avoid double free and use-after-free.

Test signals: Peer probe/detach, hostname alias updates, IPv4/IPv6 hostname matching, peer store deletion, quorum transitions after peer removal, CLI peer status dictionary output, duplicate cleanup attempts, and replace/reset brick operations targeting remote hosts are strong coverage signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-peer-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-peer-utils.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-peer-utils.h

Purpose: Declares the public peer utility surface used by glusterd management code. It exposes peer lookup, lifecycle, address-list management, serialization, and peer-count helpers while keeping implementation details in `glusterd-peer-utils.c`.

Important APIs and types: The header forward-depends on `glusterd.h` for `glusterd_peerinfo_t`, `glusterd_peer_hostname_t`, `glusterd_volinfo_t`, and friend-state types. It declares cleanup/creation APIs, hostname and uuid lookups, peer-state predicates, address helpers, dict add/update/from-dict helpers, `gd_add_peer_detail_to_dict()`, generation lookup, and `glusterd_get_peers_count()`.

Control flow: There is no executable code in the header. It defines the callable interface by which peer FSM code, CLI handlers, brick validation, and management operations locate peers, check their connection state, and marshal peer metadata into dictionaries.

State and persistence: The header owns no state. It exposes functions that operate on the RCU-protected peer list in `glusterd_conf_t` and on persisted peer-store entries indirectly through cleanup/deserialization helpers.

Dependencies and integration points: Included by source files that need peer metadata access, including replace/reset brick validation and peer CLI/status paths. The dictionary helpers provide the data contract for peer exchange across management RPCs and CLI responses.

Risks: Callers must understand the RCU lifetime expectations of returned `glusterd_peerinfo_t *` pointers. The declared functions mix ownership styles: some return duplicated strings that callers must free, while lookup helpers return internal peer pointers.

Test signals: Build coverage of prototypes, peer add/remove/status operations, dictionary round-trips, and remote brick validation paths validate this header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-peer-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-pmap.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-pmap.c

Purpose: Implements the glusterd portmap service that maps brick paths and RPC transports to brick ports. It allocates ports, maintains the in-memory port registry, handles brick sign-in/sign-out RPCs, and updates local brick status when brick processes disconnect.

Important APIs and functions: `pmap_registry_get()` lazily creates `priv->pmap`. `pmap_port_alloc()` chooses a free port in the configured range. `pmap_assign_port()` removes stale mapping for an old path and allocates a new port. `pmap_registry_search()` finds a brick path and can mark it as destroyed in a whitespace-separated brick string. `pmap_registry_search_by_xprt()` finds by transport pointer. `port_brick_bind()` binds a brick to an existing or new port, supporting brick multiplexing by appending brick names. `pmap_add_port_to_list()`, `pmap_port_new()`, and `pmap_port_remove()` manage registry entries. RPC handlers implement `PORTBYBRICK`, placeholder `BRICKBYPORT`, `SIGNIN`, and `SIGNOUT`.

Control flow: `pmap_port_alloc()` starts at a pseudo-random port between `base_port` and `max_port` and probes ports by binding a temporary IPv4 socket. Brick sign-in decodes XDR, binds the provided brick and request transport to the port, then locates matching local brickinfo and marks `port_registered`. Sign-out decodes XDR, removes the mapping by brick/transport, marks `port_registered` false, unlinks the brick pidfile, sets brick status to stopped, and removes the brick from its brick process if it was killed outside the normal brick-op path.

State and persistence: Portmap state is in-memory in `struct pmap_registry` under `glusterd_conf_t->pmap`, with `struct pmap_ports` entries holding port, whitespace-separated brick names, and transport pointer. It updates in-memory `glusterd_brickinfo_t` fields (`port_registered`, `status`) and pidfiles under the glusterd runtime directory, but it does not write volume store data itself.

Dependencies and integration points: Uses glusterd utils for volume/brick lookup, pidfile macros, brick process removal, RPC service wrappers, XDR generated portmap types, `glusterd_big_locked_handler()` for serialized RPC execution, and the exported `gluster_pmap_prog` program table. Brick processes use sign-in/sign-out to register their actual port with glusterd.

Risks: Registry mutation is safe only under the expected glusterd big lock; helpers themselves do not take a local mutex. Brick multiplexing stores multiple paths in a single mutable string and removal whites out names before possibly deleting the entry, which is fragile if path matching or whitespace handling changes. `pmap_port_alloc()` checks only bind availability and can race another process binding the port after allocation. `pmap_port_remove()` always returns 0, hiding failed removal from callers.

Test signals: Brick process startup/shutdown, brick multiplex attach/detach, port lookup by brick, backend-killed brick cleanup, stale pidfile removal, snapshot brick lookup, and concurrent-looking sign-in/sign-out under big lock are useful test cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-pmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-pmap.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-pmap.h

Purpose: Defines the glusterd portmap registry data structures and helper prototypes. It is the internal contract for code that allocates, registers, searches, and removes brick port mappings.

Important APIs and types: `struct pmap_ports` holds one registry entry: list node, brick name string, RPC transport pointer, and port. `struct pmap_registry` holds the list head plus configured base/max port range. Declared helpers include `pmap_port_alloc()`, `pmap_registry_get()`, `pmap_add_port_to_list()`, `pmap_port_new()`, `pmap_port_remove()`, `pmap_registry_search()`, `port_brick_bind()`, `pmap_registry_search_by_xprt()`, and `pmap_assign_port()`.

Control flow: The header has no executable flow. Its declarations support port allocation before brick start, brick sign-in binding, and sign-out cleanup.

State and persistence: The structs describe in-memory state only. Registry contents are rebuilt through runtime brick registration and are not persisted to the volume store by this module.

Dependencies and integration points: Depends on URCU list definitions, Gluster xlator types, UUID compatibility, and `gf_boolean_t`. It is used by glusterd pmap RPC code and any brick lifecycle code that needs to assign or remove ports.

Risks: Exposing raw structs and list nodes means callers can mutate registry internals without synchronization if they bypass the intended helpers. The `void *xprt` transport field is untyped and lifetime-sensitive.

Test signals: Compile-time compatibility with `glusterd-pmap.c`, brick start/stop port allocation, multiplexed brick registration, and transport-based cleanup verify the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-pmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-proc-mgmt.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-proc-mgmt.c

Purpose: Provides generic process metadata initialization and PID-file based stop/status helpers for glusterd-managed daemons. It abstracts common service process fields and force-stop behavior used as daemon management is migrated toward `glusterd_proc_t`.

Important APIs and functions: `glusterd_proc_init()` copies process name, pidfile, log directory/file, volfile path, volfile id, and volfile server into a `glusterd_proc_t`. `glusterd_proc_stop()` checks a pidfile, sends the requested signal, optionally waits and escalates to `SIGKILL`, and removes the pidfile. `glusterd_proc_get_pid()` returns the pid found by `gf_is_service_running()`. `glusterd_proc_is_running()` is a boolean status wrapper.

Control flow: Stop first treats an absent/non-running pidfile as success. If the process is running, it sends `sig`; `ESRCH` is success, other kill errors are logged. For non-force stops, it returns after the first signal. For `PROC_STOP_FORCE`, it polls ten times with 100 ms sleeps, temporarily dropping `conf->big_lock` while sleeping, then sends `SIGKILL` if the process still exists.

State and persistence: State is carried in the `glusterd_proc_t` string fields and in service pidfiles. The helper updates persistence only by unlinking pidfiles; it does not update volume/node store files.

Dependencies and integration points: Uses `gf_is_service_running()`, `gf_unlink()`, Gluster logging/messages, `synclock_unlock()`/`synclock_lock()` on the glusterd big lock, POSIX `kill()`, and service pidfile conventions. It parallels older `glusterd_svc_stop()` behavior and is meant for daemon lifecycle code.

Risks: `snprintf()` truncation is not treated as an error when the return value exceeds the destination size; the function only checks negative return values. PID-file semantics can target stale or reused PIDs if `gf_is_service_running()` is fooled. Dropping and reacquiring the big lock during force-stop polling permits state changes by other management work.

Test signals: Stop already-stopped services, graceful stop, force kill after a process ignores SIGTERM, stale pidfile handling, pidfile unlinking, and lock-sensitive stop under concurrent service manager activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-proc-mgmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-proc-mgmt.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-proc-mgmt.h

Purpose: Declares the generic glusterd daemon process descriptor and lifecycle helper interface.

Important APIs and types: `enum proc_flags` names start/stop modes: `PROC_NONE`, `PROC_START`, `PROC_START_NO_WAIT`, `PROC_STOP`, and `PROC_STOP_FORCE`. `struct glusterd_proc_` stores process name, pidfile, log paths, volfile path/server, and volfile id. Declared functions are `glusterd_proc_init()`, `glusterd_proc_stop()`, and `glusterd_proc_is_running()`.

Control flow: The header contains no executable control flow. Its flags drive process lifecycle decisions in implementation code.

State and persistence: The struct mirrors runtime and filesystem paths for a managed process; the persistent artifact is the pidfile referenced by `pidfile`.

Dependencies and integration points: Requires standard constants such as `NAME_MAX` and `PATH_MAX` to be visible from including context. It integrates with glusterd service management and process lifecycle helpers.

Risks: The header does not declare `glusterd_proc_get_pid()` even though the C file defines it, limiting external use or risking missing-prototype warnings depending on build flags. Fixed-size char buffers make truncation behavior an integration concern.

Test signals: Build coverage for process-management callers and lifecycle tests using initialized `glusterd_proc_t` objects validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-proc-mgmt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-quota.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-quota.c

Purpose: Implements glusterd handling for volume quota and inode quota commands. It decodes CLI quota requests, validates cluster/version/volume state, manages quota option changes, writes and upgrades `quota.conf`, starts/stops quotad, creates auxiliary client mounts for limit/list operations, and launches background filesystem crawls for quota xattr initialization or cleanup.

Important APIs and functions: `glusterd_handle_quota()` and `__glusterd_handle_quota()` decode CLI RPCs and start the quota transaction. `glusterd_is_quota_supported()` gates commands by cluster op-version. `glusterd_op_stage_quota()` validates requests, creates auxiliary mounts, validates option values, and gathers GFIDs. `glusterd_op_quota()` commits enable/disable/limit/remove/list/timeout/default-soft-limit operations. Enable/disable helpers are `glusterd_quota_enable()`, `glusterd_inode_quota_enable()`, and `glusterd_quota_disable()`. Persistence helpers include `glusterd_store_quota_config()`, `glusterd_store_quota_conf_upgrade()`, `glusterd_update_quota_conf_version()`, and `glusterd_copy_to_tmp_file()`. Runtime helpers include `glusterd_quota_initiate_fs_crawl()`, `_glusterd_quota_initiate_fs_crawl()`, `glusterd_stop_all_quota_crawl_service()`, `glusterd_create_quota_auxiliary_mount()`, and `glusterd_remove_auxiliary_mount()`.

Control flow: CLI handling unserializes a dict, extracts `volname` and quota `type`, checks support, and enters glusterd op transaction flow. Stage validation ensures the volume exists and is started, quota/inode-quota is enabled for relevant commands, quota command is supported by op-version, and limit/remove/list commands have an auxiliary FUSE mount when running on the origin glusterd. For limit/remove, stage gathers backend GFIDs into the response dict. Commit updates volume option dict entries, writes xattrs through the auxiliary mount on the origin node, mutates `quota.conf`, updates volinfo and volfiles, manages quotad service state, and optionally launches background crawls.

State and persistence: Volume quota state is stored in `volinfo->dict` keys such as `features.quota`, `features.inode-quota`, `features.quota-deem-statfs`, timeout options, and default soft limit. `volinfo->quota_conf_version` and `quota_xattr_version` are incremented as needed. `quota.conf` is rewritten through store temp files, headers, GFID entries, checksum recomputation, and version/checksum save. Runtime state includes auxiliary mount dirs and pidfiles under `DEFAULT_VAR_RUN_DIRECTORY`, crawl pid directories under the volume workdir, crawl logs, and background `glusterfs`/`find`/`setfattr` processes.

Dependencies and integration points: Integrates with op-sm via `glusterd-op-sm.h`, volume store and checksum helpers, quotad service management, volfile generation, Gluster runner APIs, quota common utilities for `quota.conf` encoding, xattrs (`QUOTA_LIMIT_KEY`, `QUOTA_LIMIT_OBJECTS_KEY`, GFID xattr), `xlator_volopt_dynload()` for option validation, and glusterd service managers. It also depends on platform-specific xattr tools for quota cleanup.

Risks: The file crosses distributed transaction state, local filesystem xattrs, temporary mounts, child processes, and persistent store updates, so partial failure can leave aux mounts, stale pidfiles, or mismatched volinfo/quota.conf state. `quota.conf` parsing assumes record sizes match the versioned format and treats corruption as fatal. Background crawl double-fork logic and PID-file writing can race cleanup. Auxiliary mount creation deliberately drops the big lock and then waits for readiness; failure to do so can deadlock, but dropping the lock also opens interleavings.

Test signals: Quota enable/disable across mixed op-versions, inode quota enable, limit/remove/list for usage and objects, invalid hard/soft limit values, missing paths, quota.conf upgrade from pre-1.2 format, checksum/version updates, aux mount failure cleanup, quotad start/stop behavior when all quota volumes stop, and background crawl pid/log cleanup are key coverage points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-quota.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-quota.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-quota.h

Purpose: Declares the quota configuration persistence helper exported from `glusterd-quota.c`.

Important APIs and types: The only declaration is `glusterd_store_quota_config(glusterd_volinfo_t *volinfo, char *path, char *gfid_str, int opcode, char **op_errstr)`, which rewrites a volume's quota configuration file for enable, upgrade, limit, and remove operations.

Control flow: No executable control flow exists in the header. Callers use this API after validating quota operation context and, when required, resolving the GFID of the target path.

State and persistence: The declared function mutates `quota.conf`, quota configuration version, checksum, and associated store temp files for the supplied volume.

Dependencies and integration points: Depends on `glusterd_volinfo_t` being available from including context. It is an internal glusterd quota persistence contract used by quota operation code and potentially other volume-store paths.

Risks: The small header exposes a powerful persistence mutation API without wrapping the expected preconditions. Callers must pass valid opcode/path/GFID combinations and an initialized quota conf store handle.

Test signals: Compile coverage and quota operations that add/remove GFID records or upgrade `quota.conf` validate this declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-quota.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-quotad-svc.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-quotad-svc.c

Purpose: Implements the glusterd service wrapper for the quotad daemon. It builds, initializes, starts, stops, restarts, and reconfigures the service based on quota-enabled volume state and generated quotad volfiles.

Important APIs and functions: `glusterd_quotadsvc_build()` installs manager/start/stop callbacks into a `glusterd_svc_t`. `glusterd_quotadsvc_init()` initializes the generic service as `quotad`. `glusterd_quotadsvc_manager()` decides whether to stop or restart quotad. `glusterd_quotadsvc_start()` builds command-line dictionary arguments and calls `glusterd_svc_start()`. `glusterd_quotadsvc_reconfigure()` compares old/new volfiles and either sends a fetchspec notify or restarts via the manager.

Control flow: The manager lazily initializes the service, then stops quotad when all volumes are stopped or all quota-enabled volumes are stopped. Otherwise, if the triggering volume is relevant to quota, it creates the quotad volfile, stops any existing daemon, starts it with the requested flags, and connects the service RPC. Reconfigure first exits to manager if all quota volumes are stopped, then checks whether generated volfiles are byte-identical, topology-identical, or topology-changed to choose no-op, notify, or restart.

State and persistence: Service state lives in `glusterd_svc_t` fields such as `inited`, `name`, callbacks, and connection. Generated quotad volfiles are persisted under the glusterd workdir via `glusterd_svc_build_volfile_path()` and `glusterd_create_global_volfile()`.

Dependencies and integration points: Depends on generic service management (`glusterd-svc-mgmt`, `glusterd-svc-helper`), volfile generation (`build_quotad_graph`), Gluster run/dict helpers, quota volume predicates, fetchspec notify, connection management, and event reporting. `glusterd-quota.c` calls the quotad manager after enable/disable operations.

Risks: Incorrect quota-volume predicates can stop quotad while still needed or keep it running unnecessarily. Reconfigure correctness depends on volfile identity/topology comparison; a false topology match could notify when a restart is required. Startup uses dynamically built command-line dict keys with fixed small key buffers, so argument count assumptions matter.

Test signals: Enabling first quota volume starts quotad, disabling last quota volume stops it, volume option changes trigger fetchspec notify when topology is unchanged, topology changes restart quotad, and service-manager failures emit `EVENT_SVC_MANAGER_FAILED`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-quotad-svc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-quotad-svc.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-quotad-svc.h

Purpose: Declares the quotad service-management interface for glusterd.

Important APIs and types: Includes `glusterd-svc-mgmt.h` for `glusterd_svc_t` and declares `glusterd_quotadsvc_build()`, `glusterd_quotadsvc_init()`, `glusterd_quotadsvc_start()`, `glusterd_quotadsvc_manager()`, and `glusterd_quotadsvc_reconfigure()`.

Control flow: No executable flow is present. The declarations define the callback set installed into `glusterd_svc_t` and called from quota and service-management paths.

State and persistence: State is owned by the `glusterd_svc_t` instance in glusterd private config and by generated quotad volfiles; this header only exposes operations over that state.

Dependencies and integration points: Used by `glusterd-quota.c` and glusterd initialization/service code to manage quotad lifecycle when quota settings change.

Risks: The manager API accepts opaque `void *data` and flags, so callers must pass a `glusterd_volinfo_t *` or `NULL` consistently with implementation expectations.

Test signals: Build linkage, quotad init/build during glusterd startup, quota enable/disable lifecycle, and reconfigure calls after volfile-affecting changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-quotad-svc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-rcu.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-rcu.h

Purpose: Provides glusterd's small wrapper around liburcu headers and defines an RCU callback head that can carry the current xlator pointer into deferred callbacks.

Important APIs and types: Includes URCU bulletproof, RCU list, compiler, atomic, and call-rcu headers, optionally includes `rculist-extra.h` for older URCU, and defines `gd_rcu_head` with `struct rcu_head head` followed by `xlator_t *this`.

Control flow: There is no runtime logic in this header. Users embed `gd_rcu_head` in larger objects and pass `&obj->rcu_head.head` to `call_rcu()`. The callback can recover the containing object and restore `THIS` from the saved xlator pointer.

State and persistence: `gd_rcu_head` stores transient deferred-free metadata and the xlator pointer needed when the callback runs. It has no on-disk persistence.

Dependencies and integration points: Used by peer utilities in this group for deferred `glusterd_peerinfo_t` destruction. It integrates liburcu callback semantics with Gluster's global `THIS` convention.

Risks: The comment and implementation rely on `struct rcu_head` being the first member of `gd_rcu_head`; changing field order would break `caa_container_of()` usage in callbacks. Saved `THIS` must remain valid until callback execution.

Test signals: Peer cleanup under RCU, repeated peer detach, sanitizer/valgrind runs around deferred frees, and builds against both old and current URCU variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-rcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-rebalance.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-rebalance.c

Purpose: Implements glusterd rebalance and defrag command handling. It validates rebalance requests, starts and reconnects to rebalance processes, tracks rebalance IDs/status, handles mgmt-v3 and legacy op-sm stage/commit paths, and updates volume state after stop/status/start commands.

Important APIs and functions: `glusterd_handle_defrag_volume()` decodes CLI rebalance requests and selects legacy op-sm versus mgmt-v3 based on op-version. `glusterd_handle_defrag_start()` launches the rebalance `glusterfs` process. `glusterd_rebalance_rpc_create()` connects to the rebalance socket. `glusterd_defrag_notify()` handles RPC connect/disconnect/destroy. Stage/commit pairs include `glusterd_mgmt_v3_op_stage_rebalance()`, `glusterd_mgmt_v3_op_rebalance()`, `glusterd_op_stage_rebalance()`, and `glusterd_op_rebalance()`. Helpers include `glusterd_rebalance_cmd_validate()`, `glusterd_defrag_start_validate()`, `glusterd_set_rebalance_id_in_rsp_dict()`, `glusterd_rebalance_defrag_init()`, `glusterd_brick_validation()`, and `glusterd_defrag_event_notify_handle()`.

Control flow: CLI handling unserializes the request dict, adds `node-uuid`, maps status/stop to brick-volume defrag op and other commands to rebalance, then uses mgmt-v3 with a brick-op phase for op-version 6.0+ or legacy op-sm otherwise. Stage validates volume existence, distribute layout, started status, command string consistency, remove-brick brick lists, task-id presence/generation, and whether another defrag/remove-brick task blocks start. Commit for start resets stale status, stores/generates task id, decides whether the local node should start a rebalance process, passes commit hash, launches/restarts as needed, and stores node state. Stop clears task id/op and rolls back decommission flags before regenerating volfiles and storing volinfo.

State and persistence: State is stored under `volinfo->rebal`: `defrag`, `defrag_cmd`, `defrag_status`, `rebalance_id`, `op`, and `commit_hash`. Starting a rebalance creates a defrag directory, pidfile, Unix socket path, logfile, and process. Node rebalance state is persisted via `glusterd_store_perform_node_state_store()`, and decommission rollback persists through volfile regeneration and `glusterd_store_volinfo()`.

Dependencies and integration points: Depends on glusterd op-sm/mgmt-v3, volume store, volfile generation, RPC client creation, Unix transport options, runner APIs, service status helpers, DHT rebalance xlator options, remove-brick helpers, and event notification. Replace/reset brick operations update rebalance status to reset markers when brick changes invalidate an existing rebalance status.

Risks: Launch uses `runner_run_nowait()` followed by a fixed `sleep(5)` before RPC connect, which is timing-sensitive. Legacy and mgmt-v3 stage/commit implementations are duplicated, increasing divergence risk. Disconnect handling nulls `volinfo->rebal.defrag`, disables RPC, calls callbacks, and unrefs defrag; reference/lifetime bugs here can cause use-after-free. Stop must correctly rollback decommission flags to avoid leaving modified volfiles after aborted remove-brick/rebalance work.

Test signals: Rebalance start/layout-fix/force/status/stop on distribute and non-distribute volumes, stopped volume rejection, concurrent remove-brick interaction, op-version fallback to legacy op-sm, task-id propagation in CLI/XML responses, rebalance process crash/disconnect, glusterd restart with rebalance recovery, and decommission rollback after stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-rebalance.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-replace-brick.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-replace-brick.c

Purpose: Implements replace-brick CLI handling, prevalidation, commit execution, and mgmt-v3 phase orchestration for forced brick replacement. It validates source/destination bricks, coordinates peer locks, swaps brick metadata, restarts services, and persists the updated volume.

Important APIs and functions: `glusterd_handle_replace_brick()` and `glusterd_handle_reset_brick()` route CLI RPCs through `__glusterd_handle_replace_brick()`. `glusterd_op_stage_replace_brick()` validates replace-brick commit-force requests. `glusterd_op_perform_replace_brick()` performs the actual brick metadata replacement and starts the new brick. `glusterd_op_replace_brick()` is the commit handler. `glusterd_mgmt_v3_initiate_replace_brick_cmd_phases()` runs lockdown, payload build, pre-validation, commit, peer unlock, and CLI response. `glusterd_rb_check_bricks()` verifies staged source/destination consistency.

Control flow: The handler decodes the CLI dict, determines the glusterd op from the operation string, enforces minimum op-version except for compatible force operations, extracts source/destination bricks for commit operations, and starts mgmt-v3 phases. Stage obtains common brick prerequisites, rejects distribute-only volumes, validates server quorum, accepts only `GF_REPLACE_OP_COMMIT_FORCE`, warns about snapshots, prepares peer auth, builds and validates destination brickinfo, checks remote peer state under RCU or creates local brick path, records source/destination in `volinfo->rep_brick`, and reports local mount directory in the response dict. Commit resolves source and staged destination, updates destination port, stops services, performs replacement, marks rebalance status reset if needed, restarts services, notifies fetchspec, frees temporary destination brickinfo, clears `rep_brick`, and stores volinfo.

State and persistence: Temporary replacement state is held in `volinfo->rep_brick.src_brick` and `dst_brick` between stage and commit. Persistent volume state changes include replacing the brick list entry, carrying over brick id/port, updating mount dir, incrementing brick count before removal, regenerating volfiles, starting the new brick if the volume is started, and `glusterd_store_volinfo()` with version increment. Service state is stopped/restarted around the mutation.

Dependencies and integration points: Uses op-sm declarations, mgmt-v3 lock/prevalidate/commit/unlock APIs, quorum validation, peer lookup utilities, brick validation/path helpers, replace-brick destination helpers (`glusterd_get_rb_dst_brickinfo()`, `rb_update_dstbrick_port()`), replicate brick ops, service managers, volfile generation, fetchspec notify, and volume store. Reset-brick reuses `glusterd_op_perform_replace_brick()` from this file.

Risks: Only force replace is supported in this path; operation string mismatches fail late. Temporary `volinfo->rep_brick` state must be cleared on all relevant paths to avoid stale destination pointers. The replace operation mutates in-memory brick lists before calling remove-brick; failures after partial mutation need careful recovery. Remote peer validation returns internal peer pointers under RCU and must not outlive the lock. Snapshot warning explicitly says snapshots are not changed, so operators can create divergent live/snapshot expectations.

Test signals: Replace-brick commit-force on replicate volumes, distribute-only rejection, quorum rejection, local and remote destination validation, destination path creation, service stop/start failure injection, brick id/port preservation, volfile regeneration, volume store update, and rebalance status reset after replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-replace-brick.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-reset-brick.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-reset-brick.c

Purpose: Implements reset-brick prevalidation and commit handling. Reset-brick supports stopping a source brick for reset and committing the same brick path back after validation, reusing replace-brick mechanics for the final metadata/service update.

Important APIs and functions: `glusterd_reset_brick_prevalidate()` validates reset-brick start/commit/commit-force requests and fills response brick metadata. `glusterd_op_reset_brick()` executes reset-brick start by stopping the brick, or commit by resolving destination brickinfo, updating port, stopping services, invoking `glusterd_op_perform_replace_brick()`, restarting services, notifying fetchspec, and storing volinfo.

Control flow: Prevalidate first runs common brick prerequisites. `GF_RESET_OP_START` succeeds after those checks. Commit variants parse and validate destination brick info. If validation shows the destination is a new local brick, reset is rejected and the user is directed to replace-brick. If validation shows the same/occupied brick path, the source brick must already be stopped, and `force` may be required if a volume id xattr or uuid mismatch indicates existing brick content. Local destinations are path-created/validated with optional `ignore-partition`; remote destinations require friend, connected, and befriended peer state. The response dict receives mount dir and `brick_count`.

State and persistence: Like replace-brick, reset uses `volinfo->rep_brick` to stage source/destination brickinfo. Start changes runtime brick process state by stopping glusterfs for the source brick. Commit may stop the source brick on the destination host path, stops glusterd-managed services, replaces brick metadata through `glusterd_op_perform_replace_brick()`, marks rebalance status reset due to reset-brick, restarts services, clears staged state, and stores updated volinfo.

Dependencies and integration points: Shares headers and helpers with replace-brick: op-sm, geo-rep, store, utils, service management, volfile generation, messages, mgmt, peer lookup, brick validation/path helpers, destination brickinfo helpers, `rb_update_dstbrick_port()`, and `glusterd_op_perform_replace_brick()` from `glusterd-replace-brick.c`.

Risks: Reset-brick intentionally rejects new destination bricks, so correctness depends on nuanced return values from `glusterd_new_brick_validate()`. The code path checking whether to stop the source on commit uses uuid comparison and logs "I AM THE DESTINATION HOST", making host-selection mistakes risky. As with replace-brick, partial failures after service stop or brick-list mutation can leave service/volume state needing recovery. Force and ignore-partition options can override safety checks and need targeted validation.

Test signals: Reset-brick start stops the source brick; commit without prior stop is rejected; commit to a new brick suggests replace-brick; force commit with existing volume id xattr; local and remote destination peer validation; service restart failure; volinfo persistence; fetchspec notify; and rebalance status reset after commit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-reset-brick.c -->
