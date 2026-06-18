# Research: subset-b-007113

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-statedump.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-statedump.c

## Purpose
`glusterd-statedump.c` implements the glusterd private-state dumper registered from the glusterd xlator. It emits diagnostic state into GlusterFS's statedump framework for peer membership, peer RPC statistics, connected management clients, service online flags, port-map entries, management-v3 locks, and persisted daemon options.

## Important APIs, Types, and Functions
The only exported function is `glusterd_dump_priv(xlator_t *this)`. It is declared in `glusterd-statedump.h` and wired into glusterd's xlator callbacks as the private-state dump hook. File-local helpers include `glusterd_dump_peer()`, `glusterd_dump_peer_rpcstat()`, `glusterd_dump_client_details()`, and `glusterd_dict_mgmt_v3_lock_statedump()`. The `GLUSTERD_DUMP_PEERS` macro wraps RCU iteration over peer lists and dispatches the peer and optional RPC-stat dump.

## Control Flow
`glusterd_dump_priv()` obtains `this->private` as `glusterd_conf_t`, opens a statedump section named `xlator.glusterd.priv`, and then holds `priv->mutex` while reading most glusterd state. It writes identity and version fields first, then service online flags, peers, port-map brick ports, connected client transports, management-v3 lock state, and finally `priv->opts` via `dict_dump_to_statedump()`. Peer iteration uses RCU read-side locking; client transport iteration uses `conf->xprt_lock`.

`glusterd_dict_mgmt_v3_lock_statedump()` is intentionally specialized for the `mgmt_v3_lock` dictionary. For ordinary lock entries it treats `trav->value->data` as `glusterd_mgmt_v3_lock_obj` and dumps the lock owner UUID. For keys containing `debug.last-success-bt`, it dumps the value as a string.

## State and Persistence Behavior
The file does not persist or mutate durable state. It snapshots in-memory daemon state into the statedump output. The dump includes persisted options from `priv->opts`, but only by reading the dictionary. State exposure includes potentially sensitive auth or option values if they are present in `priv->opts`, because the function delegates dictionary dumping without filtering here.

## Dependencies and Integration Points
It depends on `glusterfs/statedump.h`, glusterd core structures, peer and service state from `glusterd_conf_t`, RPC transport accounting, and the management-v3 lock object layout from `glusterd-locks.h`. Its integration point is glusterd xlator diagnostics: operators or tests that trigger a process statedump use this code to inspect glusterd membership and service status.

## Risks and Edge Cases
The management-v3 lock dumper assumes dictionary values have the expected object type unless the key matches the debug backtrace pattern. Passing another dictionary is explicitly unsupported. The lock dump uses a fixed 64 KiB buffer and returns silently if formatting fails or stops producing progress, so oversized lock dictionaries can truncate diagnostic signal. `glusterd_dump_peer_rpcstat()` assumes RPC transport fields are valid while peer RCU iteration is active; this depends on surrounding lifetime rules. The port-map dump reuses the same `glusterd.brick_port` and `glusterd.brickname` keys for every entry, so consumers must understand statedump duplicate-key behavior.

## Test Signals
Useful validation is mostly integration-oriented: trigger a statedump on a glusterd with multiple peers and confirm peer UUIDs, hostnames, quorum fields, RPC counters, service flags, and client transport min/max op-version fields appear. A focused regression should include a held management-v3 lock and a `debug.last-success-bt` entry to exercise both dictionary value interpretations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-statedump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-statedump.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-statedump.h

## Purpose
`glusterd-statedump.h` is the public declaration point for glusterd's private statedump hook.

## Important APIs, Types, and Functions
It includes `glusterfs/xlator.h` and declares `int glusterd_dump_priv(xlator_t *this);`. No types are defined locally.

## Control Flow
There is no runtime control flow. The header allows glusterd's xlator setup code to register the implementation in `glusterd-statedump.c`.

## State and Persistence Behavior
The header has no state or persistence behavior. It exposes an API that reads in-memory glusterd state during a statedump.

## Dependencies and Integration Points
The only dependency is the `xlator_t` declaration. Integration is with glusterd's xlator callback table and the GlusterFS statedump subsystem.

## Risks and Edge Cases
The header does not document ownership or locking expectations. Callers must rely on the implementation to handle locking and tolerate a missing `this->private`.

## Test Signals
Build coverage is the primary signal: code that includes this header should compile and link against `glusterd_dump_priv()`. Runtime behavior is tested through `glusterd-statedump.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-statedump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-store.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-store.c

## Purpose
`glusterd-store.c` is glusterd's durable metadata layer. It writes and restores the on-disk representation of global daemon identity and op-version, volumes, bricks, rebalance node state, snapshots, missed-snapshot ledgers, peer membership, options, quota checksum/version files, and snapshot brick mount state. The code is the bridge between in-memory glusterd objects and files under `priv->workdir`.

## Important APIs, Types, and Functions
The central write API is `glusterd_store_volinfo(glusterd_volinfo_t *volinfo, glusterd_volinfo_ver_ac_t ac)`, which optionally changes the volume version, creates needed directories and store handles, writes volume and brick metadata to temp files, atomically renames them, writes node-state, and recomputes checksums. Related writers include `glusterd_store_snap()`, `glusterd_store_peerinfo()`, `glusterd_store_options()`, `glusterd_store_global_info()`, `glusterd_store_max_op_version()`, `glusterd_store_update_missed_snaps()`, and `glusterd_store_save_quota_version_and_cksum()`.

The restore side starts from `glusterd_restore()`, which initializes options, retrieves volumes, peers, snapshots, resolves bricks, cleans incomplete snapshots, and recreates snapshot brick mounts. Lower-level readers include `glusterd_store_retrieve_volume()`, `glusterd_store_update_volinfo()`, `glusterd_store_retrieve_bricks()`, `glusterd_store_retrieve_snapd()`, `glusterd_store_retrieve_node_state()`, `glusterd_store_retrieve_peers()`, `glusterd_store_retrieve_snaps()`, and quota/op-version retrieval helpers.

Important internal helpers are `_storeopts()` for buffered key-value dictionary serialization, path builders for volume, brick, snap, node-state, quota, and peer files, and atomic update helpers such as `glusterd_store_volume_atomic_update()`.

## Control Flow
Volume persistence flows from `glusterd_store_volinfo()` under `ctx->cleanup_lock` and `volinfo->store_volinfo_lock`. It applies the requested version action, ensures volume and pid directories exist, creates store handles for volume info and node state, writes volume info and brick files through temp handles, atomically renames brick files and the volume file, writes node-state, and computes the checksum. Failure paths remove temp files and roll back the version when the atomic volume update fails.

Volume restore flows from directory enumeration in `glusterd_store_retrieve_volumes()`. Each volume directory is converted into a `glusterd_volinfo_t`, populated from the `info` file by `glusterd_store_update_volinfo()`, populated with brick objects from the brick directory by `glusterd_store_retrieve_bricks()`, augmented with snapd and quota/checksum data, and then linked into either `priv->volumes` or a snapshot's volume list. After volume retrieval, node-state is read; if missing, a compatibility path creates a new node-state file.

Snapshot restore enumerates `$workdir/snaps`, reads per-snapshot `info`, retrieves snap volumes, loads missed-snapshot entries, resolves bricks after peer retrieval, removes or reverts incomplete snapshots, and remounts snap-backed brick paths where needed.

Peer persistence writes peer UUID, state, and hostnames into `$workdir/peers`. Restore skips non-UUID filenames, rebuilds `glusterd_peerinfo_t`, calls `glusterd_friend_add_from_peerinfo()`, and creates RPC clients for restored peers.

## State and Persistence Behavior
The on-disk schema is key-value files. Volume metadata is under `vols/<volname>/info`, brick metadata under `vols/<volname>/bricks/<hostname>:<path-with-slashes-replaced>`, rebalance state under `node_state.info`, snapd port state under `snapd.info`, peers under `peers/<uuid>`, snapshots under `snaps/<snapname>/info`, and global identity/op-version under glusterd global info files. Deletes are generally implemented by renaming volume or snapshot directories into a workdir trash directory and then removing trash.

Writes use the `gf_store` temp-and-rename pattern for most files. Dictionary writes are buffered in `glusterd_volinfo_data_store_t` and flushed when the fixed buffer fills. Volume option writes validate known glusterd options unless `key_check` is disabled for gsync secondaries. Restore contains compatibility behavior for old volume types, missing op-version, missing node-state, legacy geo-replication `slave*` keys, missing brick IDs, missing `real_path`, and missing brick fsids.

## Dependencies and Integration Points
The file depends heavily on `gf_store_*`, `dict_t`, GlusterFS list/RCU helpers, glusterd volume/peer/snapshot utilities, snapshot plugin operations, quota helpers, sys wrappers, and checksum functions. Callers include volume, brick, quota, geo-replication, snapshot, rebalance, server quorum, ganesha, and management-operation code paths. Startup integration is through `glusterd_restore()` from glusterd initialization.

## Risks and Edge Cases
The code is schema-critical: new or renamed keys must preserve restore compatibility. Many restore conversions use `atoi`, `atoll`, or `sscanf` with limited validation, so malformed store files can silently produce zero-like values in some fields. Path construction is mostly guarded by `snprintf` bounds, but the schema encodes brick paths into filenames by replacing slashes with hyphens, so filename collisions remain a conceptual risk if host/path combinations collide after encoding. `glusterd_store_delete_brick()` appears to return success when `gf_unlink()` reports nonzero and failure when it reports zero, which is worth verifying against `gf_unlink()` semantics. In thin-arbiter brick restore, the UUID branch parses into `brickinfo->uuid` rather than `ta_brickinfo->uuid`, which looks suspicious and deserves targeted review. Atomicity is per file or small group, not an all-object transaction; crashes between volume info, brick info, node-state, quota checksum, and missed-snapshot updates can require compatibility repair at next restore.

## Test Signals
High-value tests are restart/restore scenarios: create volumes of each layout, set options, add thin arbiters, run rebalance, enable USS/snapd, create and restore snapshots, create missed-snapshot entries, add peers with multiple hostnames, then restart glusterd and compare in-memory state and checksums. Fault-injection tests around temp-file rename failures, malformed key-value files, missing node-state, missing snapd info, and legacy `slave*` geo-replication keys would exercise the compatibility paths. Static review should track every `GLUSTERD_STORE_KEY_*` writer against a corresponding reader.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-store.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-store.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-store.h

## Purpose
`glusterd-store.h` defines the durable-store schema constants and public API for glusterd metadata persistence and restore.

## Important APIs, Types, and Functions
It defines `glusterd_volinfo_ver_ac_t` for no-change, increment, and decrement actions on volume versions. It defines store directory and file names such as `vols`, `peers`, `snapd.info`, `info`, `bricks`, `node_state.info`, and `missed_snaps_list`. It also defines the key strings used in volume, brick, snapshot, peer, rebalance, migration, quota, and ganesha store files.

The important type is `glusterd_volinfo_data_store_t`, which carries a `gf_store_handle_t`, current buffer length, key-validation flag, and a fixed serialization buffer for dictionary writes.

The header exports the write and restore APIs implemented in `glusterd-store.c`: volume, snap, peer, brick, global info, options, quota, and missed-snap persistence helpers; `glusterd_restore()`; and utility functions such as `glusterd_replace_slash_with_hyphen()`.

## Control Flow
The header itself has no control flow, but it defines the public surface used by operation-state-machine and utility code to persist metadata after cluster operations and restore metadata during daemon startup.

## State and Persistence Behavior
The constants in this header are the stable on-disk contract. Changing any key or file-name constant can break restore of existing clusters unless migration logic is added.

## Dependencies and Integration Points
It includes `compat-uuid.h`, `logging.h`, and `glusterd.h`, so it exposes store APIs in terms of glusterd core types. It is included by management operations, volume operations, snapshot code, quota code, and startup restore code.

## Risks and Edge Cases
The header mixes public function declarations with a large schema catalog. This makes key reuse convenient but also makes accidental schema changes easy to propagate. The buffer size constant `VOLINFO_BUFFER_SIZE` bounds batched option serialization; callers adding large option values need to account for flush behavior and key/value formatting length.

## Test Signals
Schema tests should verify that every public store key has a writer and reader where appropriate. ABI/build tests should include callers across volume, peer, snapshot, and quota modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-store.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-svc-helper.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-svc-helper.c

## Purpose
`glusterd-svc-helper.c` contains policy helpers for glusterd-managed auxiliary services. It coordinates reconfiguration, start/stop management, volfile comparison, and multiplexed self-heal daemon attach/detach behavior.

## Important APIs, Types, and Functions
Top-level service orchestration APIs are `glusterd_svcs_reconfigure()`, `glusterd_svcs_stop()`, and `glusterd_svcs_manager()`. Volfile comparison helpers include `glusterd_svc_check_volfile_identical()`, `glusterd_svc_check_topology_identical()`, `glusterd_volume_svc_check_volfile_identical()`, and `glusterd_volume_svc_check_topology_identical()`.

Multiplexing helpers include `glusterd_svcprocess_new()`, `glusterd_is_svcproc_attachable()`, `__gf_find_compatible_svc()`, `__gf_find_compatible_svc_from_pid()`, and `glusterd_shd_svc_mux_init()`. Runtime attach/detach is handled by `glusterd_attach_svc()`, `glusterd_detach_svc()`, and `__glusterd_send_svc_configure_req()`.

## Control Flow
`glusterd_svcs_reconfigure()` recreates service volfiles and notifies fetchspec consumers. It handles NFS when built, volume-level SHD when a volume is supplied, and skips quotad/bitd/scrub when the cluster op-version is still at minimum. `glusterd_svcs_manager()` starts or reconciles services in a similar order and ignores `-EINVAL` from optional service managers as a disabled-service signal. Snapshot volumes are skipped.

Volfile comparison helpers generate a temporary volfile with `mkstemp`, call the appropriate graph builder, then compare either full file content or topology with the existing service volfile.

For SHD multiplexing, `glusterd_shd_svc_mux_init()` decides whether a volume-level SHD service can attach to an existing process. It handles abnormal death cleanup, stale pidfiles, compatible process lookup, creation of a new `glusterd_svc_proc_t`, list linking, and SHD-specific initialization.

`__glusterd_send_svc_configure_req()` sends a brick-program RPC request to attach or detach a service. Attach requests read the volfile content, optionally serialize a dictionary from `build_volfile_path()`, install callback state in a frame, and submit the XDR request. `glusterd_attach_svc()` and `glusterd_detach_svc()` retry up to 15 times, temporarily releasing `big_lock` while sleeping so the connection can progress.

## State and Persistence Behavior
This file does not write durable metadata directly. It mutates runtime service state: `svc->online`, `svc->inited`, `svc->svc_proc`, `volinfo->shd.attached`, multiplex process lists, and atomic blocker counters. It reads generated volfiles from disk for comparison and attach payloads, so it depends on persistence and volgen layers having already produced those files.

## Dependencies and Integration Points
It integrates global services (`nfs`, `quotad`, `bitd`, `scrub`) and volume-level `glustershd`. It depends on service-specific modules, `glusterd-svc-mgmt.c` for process/RPC primitives, volfile generation and comparison functions, RPC/XDR infrastructure, snapshot utilities, and glusterd locks/condition variables. Callers are volume, brick, replace/reset-brick, geo-replication, op-sm, and startup paths that need service reconciliation after metadata changes.

## Risks and Edge Cases
The attach/detach retry loop deliberately unlocks `big_lock`, which is called out in comments as risky but necessary for connection progress. Any change here needs careful deadlock and stale-volume analysis. Attach callback code currently logs success with a message ID named like failure, which can confuse log analysis. The attach path reads the whole volfile into memory based on `st_size`; large or concurrently replaced volfiles need bounds and consistency consideration. Temporary volfile paths are under `/tmp/g<svc>-XXXXXX` and are cleaned up, but tests should verify all error paths close descriptors and unlink. Multiplexed SHD assumptions are narrow; comments state the generic mux notifier currently assumes glustershd.

## Test Signals
Test service manager behavior across enabled and disabled optional services, minimum op-version, snapshot volumes, and volume-level SHD. For volfile comparisons, verify both content changes and topology-only changes. For multiplexing, test clean attach to existing SHD, stale pidfile cleanup, abnormal SHD death followed by re-init, stale volume deletion during attach retries, and detach RPC failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-svc-helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-svc-helper.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-svc-helper.h

## Purpose
`glusterd-svc-helper.h` exposes higher-level service orchestration and multiplexing helpers for glusterd-managed daemons.

## Important APIs, Types, and Functions
It declares service-wide reconfigure, stop, and manager entry points; global and volume-specific volfile/topology comparison helpers; `glusterd_volume_svc_build_volfile_path()`; compatible mux process lookup helpers; `glusterd_svcprocess_new()`; `glusterd_shd_svc_mux_init()`; attach/detach entry points; and the low-level configure request sender.

## Control Flow
The header has no implementation flow, but its declarations split responsibilities: orchestration helpers are used after cluster metadata changes, comparison helpers support deciding whether a service needs restart or graph reconfiguration, and attach/detach helpers support runtime service multiplexing.

## State and Persistence Behavior
The APIs mutate runtime service and SHD attachment state but do not define persistent store state. Some functions consume generated volfiles from disk.

## Dependencies and Integration Points
It includes `glusterd.h`, `glusterd-svc-mgmt.h`, and `glusterd-volgen.h`, so callers can pass volume info, service structs, dictionaries, and graph builders.

## Risks and Edge Cases
The exported `__...` functions expose implementation-level hooks and make it easier for callers to bypass higher-level policy. Attach/detach callers must respect locking and lifetime expectations around `volinfo`, `svc`, and RPC clients.

## Test Signals
Compile coverage should include all service-specific modules. Runtime coverage belongs with `glusterd-svc-helper.c`, especially SHD multiplexing and volfile comparison behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-svc-helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-svc-mgmt.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-svc-mgmt.c

## Purpose
`glusterd-svc-mgmt.c` implements the reusable low-level process and RPC management layer for auxiliary glusterd services. Service-specific modules use it to initialize paths, start and stop `glusterfs` service processes, build service volfile/log/pid paths, and track RPC connectivity.

## Important APIs, Types, and Functions
Public APIs include `glusterd_svc_create_rundir()`, `glusterd_svc_init()`, `glusterd_svc_start()`, `glusterd_svc_stop()`, path builders for pidfiles, volfiles, logfiles, service dirs and rundirs, `glusterd_svc_reconfigure()`, `glusterd_svc_common_rpc_notify()`, `glusterd_muxsvc_common_rpc_notify()`, `glusterd_muxsvc_conn_init()`, and `glusterd_genericsvc_start()`. File-local helpers include `glusterd_svc_init_common()`, `glusterd_svc_build_volfileid_path()`, and `svc_add_args()`.

## Control Flow
Initialization builds a service name, creates its run directory, creates a Unix-socket path, initializes `glusterd_conn_t`, builds pidfile/volfile/logfile/volfile-id values, resolves the volfile server from `transport.socket.bind-address` or `localhost`, and initializes `glusterd_proc_t`.

`glusterd_svc_start()` locks `priv->attach_lock`, avoids duplicate starts if the process is already running, verifies the volfile exists, builds a `runner_t` command for `SBIN_DIR/glusterfs` with volfile-id, pidfile, logfile, and socket path, adds optional valgrind, localtime logging, daemon log level, global threading, IO engine, and caller-supplied command-line args, then runs synchronously or asynchronously. Synchronous run temporarily releases `big_lock`.

`glusterd_svc_stop()` stops the process, disconnects RPC, clears `online`, unlinks the service socket, and logs success. RPC notify callbacks set `online` on connect and clear it on disconnect. Multiplexed notify walks every attached service in a mux process and updates shared status.

`glusterd_muxsvc_conn_init()` builds a Unix transport RPC client for a mux process and registers `glusterd_muxsvc_conn_common_notify`. `glusterd_genericsvc_start()` builds common command arguments for bitd/scrub-like daemons and delegates to `glusterd_svc_start()`.

## State and Persistence Behavior
The file does not write glusterd metadata. It creates runtime directories and pid/socket/log paths and launches processes using generated volfiles from the workdir. Runtime state includes `svc->name`, `svc->conn`, `svc->proc`, `svc->online`, mux-process `status`, and RPC client references.

## Dependencies and Integration Points
It depends on glusterd process management, connection management, RPC transport, runner utilities, global command arguments, and SHD-specific path building for volume-level service volfiles. Service-specific modules such as NFS, quotad, bitd, scrub, SHD, snapd, and gfproxyd layer their own policy on top of these primitives.

## Risks and Edge Cases
The start path depends on the generated volfile being present and stable. It uses `attach_lock` around process launch and service attach activity, so changes can affect deadlock behavior. Some path builder functions assert `len == PATH_MAX`, which restricts safe reuse with smaller buffers. The mux notifier is explicitly glustershd-oriented, so adding other multiplexed services requires revisiting event names and service-name assumptions. `glusterd_svc_init_common()` only checks negative `snprintf()` returns for `svc->name`, not truncation.

## Test Signals
Tests should validate command construction under valgrind, localtime logging, daemon log-level, global threading, IO engine, and extra cmdline dictionaries. Process lifecycle tests should assert idempotent start, missing volfile failure, synchronous and no-wait start paths, stop cleanup of sockets and `online`, and RPC connect/disconnect event state transitions. Mux tests should validate all attached services update on shared connect/disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-svc-mgmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-svc-mgmt.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-svc-mgmt.h

## Purpose
`glusterd-svc-mgmt.h` defines the common service-management abstractions used by glusterd auxiliary daemons.

## Important APIs, Types, and Functions
The header defines service callback typedefs for build, manager, start, stop, reconfigure, and mux notification functions. `gf_svc_status_t` models mux process lifecycle states: starting, started, stopping, disconnected, and died. `glusterd_svc_proc_t` represents a multiplexed process with a process-list node, attached service list, notify callback, RPC client, opaque data, and status. `glusterd_svc_t` represents an individual service with connection management, callbacks, mux linkage, process metadata, name, online flag, and init flag.

It declares low-level lifecycle APIs implemented in `glusterd-svc-mgmt.c`: run directory creation, service init/start/stop, path builders, reconfigure, RPC notify callbacks, mux connection initialization, pid lookup, and generic service start.

## Control Flow
The header provides the object model that service-specific modules fill in during build/init and later drive through manager/start/stop/reconfigure callbacks. Runtime event flow is from RPC notifications into `online` and mux status updates.

## State and Persistence Behavior
The structs hold runtime process and connection state only. Persistent service configuration is represented indirectly by generated volfiles and glusterd store files outside this header.

## Dependencies and Integration Points
It includes process management, connection management, and RCU/list support. It forward-declares `glusterd_volinfo_t` to avoid pulling all volume internals into every service-management user.

## Risks and Edge Cases
Because `glusterd_svc_t` embeds both callback policy and mutable runtime state, service modules must initialize all fields consistently. Mux process status must remain synchronized with process liveness and RPC events, or attach decisions can target dead or stopping processes.

## Test Signals
Build tests should cover all service modules embedding or using `glusterd_svc_t`. Runtime tests should assert state transitions for standalone and multiplexed services, including connect, disconnect, stop, abnormal death, and reattach decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-svc-mgmt.h -->
