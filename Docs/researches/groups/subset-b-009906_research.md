# Research group subset-b-009906

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/kcc/kcc_periodic.c -->
# sources/user-network-fs/samba/source4/dsdb/kcc/kcc_periodic.c

Purpose: timer-driven KCC maintenance for Samba AD DC. It either invokes the Python `samba_kcc` topology generator or runs the older in-process "simple KCC", then performs deleted-object garbage collection, DNS record tombstoning, and DNS tombstone deletion.

Important APIs/functions: `kccsrv_periodic_schedule()` manages the `tevent_timer`; `kccsrv_periodic_run()` is the main maintenance body; `kccsrv_simple_update()` searches `nTDSDSA` objects and builds `repsFrom` candidates; `kccsrv_add_repsFrom()` persists `repsFrom` and prunes stale `repsTo`; `kccsrv_replica_flags()` chooses writable-vs-RODC flags; `kccsrv_samba_kcc()` launches the external KCC command with `samba_runcmd_send()`. DNS cleanup is delegated to `dns_tombstone_records()` and `dns_delete_tombstones()`.

Control flow/state: the scheduled handler clears the old timer, runs maintenance, then reschedules. Simple KCC gathers all peer NTDS DSAs, skips this DC's `ntds_guid`, uses `check_MasterNC()` to avoid non-master sources, updates connection objects with `kccsrv_apply_connections()`, and notifies `dreplsrv` by IRPC refresh when topology attributes change. Persistent state lives in DSDB attributes (`repsFrom`, `repsTo`, `hasPartialReplicaNCs`) and tombstone/delete effects; transient throttles are `last_deleted_check`, `last_dns_scavenge`, and `last_dns_tombstone_collection`.

Dependencies/integration: relies on LDB/SAMDB helpers, DRSUAPI blob formats, `kcc_connection`, `dreplsrv` IRPC, loadparm intervals, and AD DC role context. Risks include stale topology after failed writes, broad `repsFrom` generation in simple mode, asynchronous command timeout behavior, and cleanup timing being approximate. Test signals: check `kccsrv:*_interval`, RODC flag differences, GC partial NC additions, notification to `dreplsrv`, and DNS/deleted-object cleanup error logs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/kcc/kcc_periodic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/kcc/kcc_service.c -->
# sources/user-network-fs/samba/source4/dsdb/kcc/kcc_service.c

Purpose: registers and initializes the KCC task service for AD DCs. It owns startup role gating, SAMDB connection, partition discovery, periodic scheduling, and IRPC entry points for `DsExecuteKCC` and `DsReplicaGetInfo`.

Important APIs/functions: `server_service_kcc_init()` registers the `kcc` service; `kccsrv_task_init()` builds `struct kccsrv_service`; `kccsrv_init_creds()` obtains system session info; `kccsrv_connect_samdb()` opens local SAMDB, records this DC's NTDS GUID, and detects RODC mode; `kccsrv_load_partitions()` reads rootDSE `namingContexts` and `configurationNamingContext`; `kccsrv_execute_kcc()` handles manual KCC execution; `kccsrv_replica_get_info()` forwards to `kccdrs_replica_get_info()`.

Control flow/state: the task refuses standalone and domain-member roles, then initializes credentials, SAMDB, partition list, loadparm-driven periodic intervals, and `samba_kcc_code`. Manual `DsExecuteKCC` either runs `kccsrv_simple_update()` synchronously or starts `samba_runcmd_send()` and optionally defers the IRPC reply until `manual_samba_kcc_done()`. Persistent state is not directly stored here, but startup populates service fields consumed by periodic code.

Dependencies/integration: Samba task service framework, loadparm, IRPC generated DRSUAPI handlers, SAMDB helpers, roles library, and `kcc_periodic.c`. Risks include fatal task termination on startup failures, manual command concurrency returning `NT_STATUS_DS_BUSY`, and partition list loading only from rootDSE naming contexts. Test signals: AD DC-only startup, `kccsrv:samba_kcc` true/false paths, async/sync `DsExecuteKCC`, and failure behavior when SAMDB lacks NTDS metadata.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/kcc/kcc_service.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/kcc/kcc_service.h -->
# sources/user-network-fs/samba/source4/dsdb/kcc/kcc_service.h

Purpose: shared KCC service state definition and include hub for generated prototypes and KCC maintenance helpers.

Important types/APIs: `struct kccsrv_service` is the central in-memory state object. It stores the `task_server`, `startup_time`, `config_dn`, system session info, local partition DN list, SAMDB connection, immutable local `ntds_guid`, periodic timer state (`interval`, `next_event`, `te`, external-command `subreq`, and status), cleanup timestamps, RODC flag, and `samba_kcc_code`. It forward-declares `struct kcc_connection_list` and includes garbage collection, DNS scavenging, and generated service prototypes.

Control flow/state: this header does not execute logic but defines the mutable state consumed by `kcc_service.c` and `kcc_periodic.c`. The fields split persistent directory state from transient scheduling and throttling: actual topology and tombstones live in DSDB, while this struct caches timestamps and open handles for one task lifetime.

Dependencies/integration: DRSUAPI client NDR types, DSDB common utilities, tombstone and DNS scavenging headers, and generated `kcc_service_proto.h`. Risks are state-coupling risks: missing initialization of timer/timestamp fields changes cleanup cadence, and any new field must respect the service's single-task tevent lifetime. Test signals: startup initializes `config_dn`, `partitions`, `samdb`, `ntds_guid`, RODC status, and periodic timer before IRPC registration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/kcc/kcc_service.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/kcc/scavenge_dns_records.c -->
# sources/user-network-fs/samba/source4/dsdb/kcc/scavenge_dns_records.c

Purpose: implements DNS aging maintenance for AD-integrated zones. It tombstones expired `dnsRecord` values and later deletes tombstoned `dnsNode` objects after the configured tombstone interval.

Important APIs/functions: `dns_tombstone_records()` iterates zones and calls `dns_tombstone_records_zone()`; `dns_delete_tombstones()` removes aged tombstoned nodes; `copy_current_records()` copies only non-expired records. Tombstoning uses `dnsp_DnssrvRpcRecord` NDR decoding/encoding and writes a `DNS_TYPE_TOMBSTONE` record plus `dNSTombstoned=TRUE` when all live records expire.

Control flow/state: zone scavenging reads zone properties (`dwNoRefreshInterval`, `dwRefreshInterval`), computes the cutoff from the current DNS timestamp, searches with `DSDB_MATCH_FOR_DNS_TO_TOMBSTONE_TIME`, and modifies each node. Updates are constrained by leaving the old `dnsRecord` element as `MOD_DELETE` and adding a replacement element, so concurrent record changes fail instead of being overwritten. Deletion searches tombstoned nodes, validates the single tombstone record, handles older Samba tombstone time encoding, and deletes via `dsdb_delete()`.

Dependencies/integration: DNS server common zone discovery/properties, LDB custom matching rules, NDR DNS record formats, loadparm `dnsserver:dns_tombstone_interval`, DSDB delete/modify helpers, and KCC periodic/Python admin bindings. Risks include large tombstone searches, malformed DNS blobs, races causing modify failure, and time conversion edge cases. Test signals: zones without property sets are skipped, mixed live/expired multi-value nodes retain live records, all-expired nodes become tombstoned, and old-hour-format tombstones are tolerated.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/kcc/scavenge_dns_records.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/kcc/scavenge_dns_records.h -->
# sources/user-network-fs/samba/source4/dsdb/kcc/scavenge_dns_records.h

Purpose: declares the DNS scavenging entry points used by the KCC service and Python DSDB bindings.

Important APIs: `dns_tombstone_records(TALLOC_CTX *, struct ldb_context *, char **error_string)` tombstones expired dynamic DNS records across AD-integrated zones. `dns_delete_tombstones(...)` deletes tombstoned DNS nodes past the tombstone interval. `remove_expired_records(...)` is declared but not implemented in the paired source file in this subset, so callers should verify generated prototypes or other translation units before relying on it.

Control flow/state: the header carries no implementation state; it exposes functions that mutate DSDB DNS nodes and return `NTSTATUS`, with optional human-readable error strings allocated on the supplied talloc context. It includes loadparm, SAMDB, DSDB utility, and DNS server common headers because callers need concrete LDB and zone-related types.

Dependencies/integration: consumed by `kcc_periodic.c` for scheduled maintenance and by `pydsdb.c` for AD DC-only Python methods. Risks include API drift between the stale `remove_expired_records()` declaration and actual implementation, and callers needing to respect error string ownership. Test signals: compile coverage for AD DC and non-AD DC builds, and callers checking `NT_STATUS_IS_OK()` plus error-string fallbacks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/kcc/scavenge_dns_records.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/pydsdb.c -->
# sources/user-network-fs/samba/source4/dsdb/pydsdb.c

Purpose: Python C extension module `dsdb`, exposing selected Samba DSDB/SAMDB internals to Python provisioning, administration, tests, KCC tooling, and maintenance scripts.

Important APIs/functions: wrappers cover server site lookup, schema conversion and lookup (`attid`, LDAP display names, search/system/link flags, syntax OIDs, class mandatory attributes), DRSUAPI attribute conversion/normalization, NTDS GUID/invocation ID getters/setters, partition/NC/well-known DN helpers, RODC/PDC checks, RID set creation/allocation, DNS scavenging, tombstone garbage collection, GKDI root key creation, UDV loading, functional-level checks, DC OS version mapping, and many constants. `py_dsdb_methods[]` defines the exported names; `MODULE_INIT_FUNC(dsdb)` registers constants and strings.

Control flow/state: wrappers parse Python arguments, extract `ldb_context` or DN objects through pyldb helpers, allocate temporary talloc contexts, call DSDB primitives, translate `LDB`, `WERROR`, or `NTSTATUS` errors into Python exceptions, and return Python scalars, sets, DNs, ldb `MessageElement`s, or NDR Python objects. AD DC-only maintenance functions are gated by `AD_DC_BUILD_IS_ENABLED`; otherwise they raise `NotImplementedError`.

Dependencies/integration: Python C API, pyldb, NDR Python helpers, SAMDB/DSDB schema modules, KCC garbage/DNS cleanup, GKDI, flag mapping, loadparm Python conversion, and security/Kerberos constants. Risks include reference ownership mistakes, converting arbitrary Python bytes to schema syntaxes, privileged maintenance effects exposed to scripts, and build-configuration divergence. Test signals: Python import in AD DC/non-AD DC builds, exception translation, schema lookup error cases, RID/DNS/tombstone methods against provisioned test databases, and constant availability expected by Python code.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/pydsdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/drepl_extended.c -->
# sources/user-network-fs/samba/source4/dsdb/repl/drepl_extended.c

Purpose: schedules DRS extended operations as specialized `DsGetNCChanges` pulls against a role owner or source DSA, used by FSMO transfer, RID allocation, and secret replication.

Important APIs/functions: `drepl_request_extended_op()` is the public scheduler. `drepl_create_extended_source_dsa()` creates a temporary `dreplsrv_partition_source_dsa` with a synthetic partition, source DSA GUID/DNS name, outgoing connection, UDV, high-watermark copied from known partition state when available, and writable flags when allowed. `extended_op_callback()` unlinks the temporary source and forwards completion to the caller's callback.

Control flow/state: callers pass NC DN, source DSA DN, extended operation code, `fsmo_info`, minimum USN, and callback data. The file builds enough in-memory partition/source state to reuse the normal pull queue, schedules `dreplsrv_schedule_partition_pull_source()`, and immediately runs pending operations. Persistent effects are performed later by the pull helper and remote FSMO/RID/secret semantics; this file itself only constructs transient state.

Dependencies/integration: SAMDB GUID/NC-root lookup, UDV loading, `samdb_ntds_msdcs_dns_name()`, outgoing connection attachment, and the central DREPL queue. Risks include temporary object lifetime, using `min_usn` only indirectly/not in the visible source setup, failure to find source GUIDs, and callback correctness. Test signals: role transfer/RID/secret paths should schedule and complete callbacks, preserve existing high-watermarks, and clean up temporary source references.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/drepl_extended.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/drepl_fsmo.c -->
# sources/user-network-fs/samba/source4/dsdb/repl/drepl_fsmo.c

Purpose: handles IRPC requests to take FSMO roles by forwarding the appropriate DRS extended operation to the current role owner.

Important APIs/functions: `drepl_take_FSMO_role()` is the IRPC handler. It uses `dsdb_get_fsmo_role_info()` to find the FSMO object and owner NTDS DSA, maps `enum drepl_role_master` to `DRSUAPI_EXOP_FSMO_REQ_ROLE`, `DRSUAPI_EXOP_FSMO_RID_REQ_ROLE`, or `DRSUAPI_EXOP_FSMO_REQ_PDC`, checks whether this DC already owns the role with `samdb_dn_is_our_ntdsa()`, then calls `drepl_request_extended_op()`. `drepl_role_callback()` sets the output `WERROR` and sends the deferred IRPC reply.

Control flow/state: successful scheduling marks the IRPC message deferred; completion happens asynchronously after the DRS pull/extended op finishes. No local directory write is performed directly here; role changes are mediated by remote DRS behavior and later replication/application.

Dependencies/integration: DREPL IRPC registration in `drepl_service.c`, DSDB FSMO role utilities, extended operation scheduler, and tevent queue processing. Risks include trusted-IRPC panic for impossible role values, failure to identify current owner, and asynchronous failure propagation only through `out.result`. Test signals: already-owned roles return `WERR_OK`, each role maps to the correct exop, failed scheduling replies synchronously, and successful scheduling defers then replies from callback.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/drepl_fsmo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/drepl_notify.c -->
# sources/user-network-fs/samba/source4/dsdb/repl/drepl_notify.c

Purpose: implements outbound replication notifications. It detects when local partitions have new USNs and sends remote `DsReplicaSync` calls so partners pull changes from this DC.

Important APIs/functions: `dreplsrv_notify_schedule()` manages the notify timer; `dreplsrv_notify_check_all()` scans partitions; `dreplsrv_notify_check()` compares partition `uSNHighest`/`uSNUrgent` with per-source `notify_uSN`; `dreplsrv_schedule_notify_sync()` queues deduplicated notify operations; `dreplsrv_notify_run_ops()` runs one active notify; `dreplsrv_op_notify_send()` connects/binds, sends `DsReplicaSync`, and `dreplsrv_notify_op_callback()` updates status.

Control flow/state: timer run allocates a scratch context, queues notifications from `repsTo`, and calls `dreplsrv_run_pending_ops()`. Notify operations share the DREPL single-operation lane with pull operations. On success, the in-memory `notify_uSN` is advanced and `drepl_reps_update()` writes status timestamps/failure counts to `repsTo`; on failure, only status is updated. RODCs do not schedule notify service startup.

Dependencies/integration: outgoing DRSUAPI helper, partition/source lists, `dsdb_loadreps()`, `dsdb_load_partition_usn()`, `drepl_out_pull.c` status updater, and DRSUAPI RPC. Risks include starvation behind pull operations, notification dedupe missing changed flags, and typo-level maintainability (`huger` comment). Test signals: urgent flag when `notify_uSN < uSNUrgent`, no notify for unchanged USNs, status persistence in `repsTo`, RODC startup skip, and remote `DsReplicaSync` request fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/drepl_notify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/drepl_out_helpers.c -->
# sources/user-network-fs/samba/source4/dsdb/repl/drepl_out_helpers.c

Purpose: core asynchronous outgoing DRS implementation. It connects and binds to remote DRSUAPI, sends `DsGetNCChanges`, converts and commits replicated objects, retries for schema/parent/target issues, and refreshes remote `repsTo` with `DsReplicaUpdateRefs`.

Important APIs/functions: `dreplsrv_out_drsuapi_send/recv()` maintain cached DRSUAPI connections and `DsBind`; `dreplsrv_op_pull_source_send/recv()` drives a pull operation; `dreplsrv_op_pull_source_get_changes_trigger()` builds v10/v8/v5 requests with high-watermarks, UDV, PAS, exop, and flags; `dreplsrv_op_pull_source_apply_changes_trigger()` handles replies, schema cycles, object conversion, commit, retry, and update refs. Helpers build RODC/GC partial attribute sets and convert UDV formats.

Control flow/state: the tevent chain is connect -> bind -> GetNCChanges -> parse compressed/uncompressed level 1/6 replies -> convert -> commit -> loop on `more_data` -> optional retry original op after schema sync -> optional `UpdateRefs` -> done. Successful normal pulls copy the new `repsFrom1` high-watermark/invocation data back into the source DSA; `drepl_out_pull.c` later persists status. Schema replication is buffered until all chunks arrive so a working schema can convert objects safely.

Dependencies/integration: DCE/RPC, GENSEC session key, DRSUAPI NDR, SAMDB schema and replication conversion/commit code, partial replica rules, central queue, and loadparm credentials. Risks include protocol-version compatibility, large reply memory, schema mismatch retry complexity, ignoring `WERR_DS_DRA_BUSY` for `UpdateRefs`, and secret/RODC flag subtleties. Test signals: v10/v8/v5 negotiation, compressed replies, schema mismatch retry, missing-parent/target retries, full-sync behavior, RODC/GC PAS correctness, and `UpdateRefs` error handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/drepl_out_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/drepl_out_helpers.h -->
# sources/user-network-fs/samba/source4/dsdb/repl/drepl_out_helpers.h

Purpose: nominal header for outgoing DRS helper declarations.

Important APIs/types: in this snapshot the header only contains an include guard and no explicit declarations. The actual helper functions used by the service, such as `dreplsrv_out_drsuapi_send()`, `dreplsrv_op_pull_source_send()`, and `dreplsrv_op_pull_source_recv()`, are likely declared through generated `drepl_service_proto.h` included by `drepl_service.h`.

Control flow/state: none. This file exists to reserve/structure the helper interface but does not currently provide a compile-time contract of its own.

Dependencies/integration: included by `drepl_service.h`, so it is part of the public service include chain even while empty. Risks include reader confusion and missed prototypes if generated headers change; adding declarations here must avoid conflicts with generated prototypes. Test signals are compile-only: all DREPL translation units should still see the helper prototypes through the generated include chain.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/drepl_out_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/drepl_out_pull.c -->
# sources/user-network-fs/samba/source4/dsdb/repl/drepl_out_pull.c

Purpose: scheduling and queue execution for outbound pull replication operations.

Important APIs/functions: `drepl_reps_update()` updates `repsFrom` or `repsTo` status timestamps, result code, and consecutive failure counters; `dreplsrv_schedule_partition_pull_source()` creates a pending pull operation; `dreplsrv_schedule_pull_replication()` schedules all partition sources; `dreplsrv_run_pull_ops()` starts the next pull; `dreplsrv_pending_op_callback()` receives completion and invokes optional extended-op callbacks.

Control flow/state: periodic code enqueues all sources, IRPC/exop paths enqueue specific sources, and `dreplsrv_run_pull_ops()` enforces one active pull/notify at a time. Before starting, it records `last_attempt` and checks local inbound replication disablement unless forced. Success/failure status is persisted through `dsdb_savereps()` for normal pulls; extended operations skip normal `repsFrom` status persistence and report through callbacks.

Dependencies/integration: DLIST queues in `dreplsrv_service`, outgoing helper send/recv, SAMDB NTDS options, DSDB reps blob load/save, and notify queue interlock. Risks include duplicate scheduled pulls, a failure path that invokes callbacks without freeing `op` in the visible code path, disabled inbound replication blocking non-forced requests, and status-only persistence separate from high-watermark commit. Test signals: queue order, forced vs disabled inbound replication, callback completion for sync IRPC/exops, and `repsFrom` status field updates after failure/success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/drepl_out_pull.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/drepl_partitions.c -->
# sources/user-network-fs/samba/source4/dsdb/repl/drepl_partitions.c

Purpose: loads and refreshes DREPL partition/source topology and constructs reusable outgoing connections to source DSAs.

Important APIs/functions: `dreplsrv_load_partitions()` reads this NTDS Settings object's NC attributes; `dreplsrv_refresh_partitions()` reloads NC metadata, UDV, `repsFrom`, and `repsTo`; `dreplsrv_partition_find_for_nc()`, `_source_dsa_by_guid()`, `_source_dsa_by_dns()`, and `_source_dsa_temporary()` resolve replication targets; `dreplsrv_out_connection_attach()` caches DRSUAPI bindings; `dreplsrv_get_target_principal()` chooses Kerberos target SPNs.

Control flow/state: startup loads master/full/partial replica NCs, deduplicates partitions, then refreshes each partition. Refresh fills `partition->nc`, UDV, `sources` from `repsFrom`, and `notifies` from `repsTo` entries not already in sources. Parsed reps blobs become long-lived in-memory `dreplsrv_partition_source_dsa` entries attached to cached connections. The actual durable state remains in DSDB attributes.

Dependencies/integration: SAMDB reference searches, extended DNs, DRSUAPI reps blob NDR, dcerpc binding parser, Kerberos SPN validation, partial replica flags, and DREPL service state. Risks include silently tolerating absent remote server metadata, target-principal fallback complexity, never removing old source structs except updating/reusing matches, and temporary DSA use for first replication. Test signals: partition dedupe, RODC/partial flags, reps blob parse failures, target principal selection with/without `dNSHostName`, and refresh after KCC topology changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/drepl_partitions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/drepl_periodic.c -->
# sources/user-network-fs/samba/source4/dsdb/repl/drepl_periodic.c

Purpose: periodic scheduler for DREPL pull replication and RID allocation checks, plus the dispatcher for pending pull/notify operations.

Important APIs/functions: `dreplsrv_periodic_schedule()` manages the timer; `dreplsrv_periodic_run()` refreshes partitions, queues pull replication, checks RID pool needs, and runs the operation queue; `dreplsrv_run_pending_ops()` chooses between notify and pull queues; `dreplsrv_pendingops_schedule_pull_now()` schedules an immediate pull dispatch after manual `DsReplicaSync`.

Control flow/state: like KCC timers, zero intervals are coerced to one second and rescheduling avoids moving an existing timer later. Each periodic run refreshes topology first because KCC/admin tools may have changed `repsFrom`/`repsTo`, then schedules all source pulls and processes one operation. The dispatcher favors whichever pending notify/pull has the older `schedule_time`, with only one active op in the shared lane.

Dependencies/integration: tevent timers/immediates, partition refresh, pull scheduler, RID allocation, and notify/pull run functions. Risks include queue growth if periodic scheduling enqueues duplicates faster than they drain, single-lane throughput limits, ignored refresh/schedule errors in the visible periodic body, and timer termination on schedule failure. Test signals: interval handling, immediate pull from `DsReplicaSync`, operation ordering by `schedule_time`, and refresh before scheduling after topology changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/drepl_periodic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/drepl_replica.c -->
# sources/user-network-fs/samba/source4/dsdb/repl/drepl_replica.c

Purpose: placeholder handlers for forwarded `DsReplicaAdd`, `DsReplicaDel`, and `DsReplicaMod` requests.

Important APIs/functions: `drepl_replica_add()`, `drepl_replica_del()`, and `drepl_replica_mod()` log the incoming DRSUAPI request with `NDR_PRINT_FUNCTION_DEBUG()` and return `NT_STATUS_NOT_IMPLEMENTED`.

Control flow/state: no mutation is performed. These functions are called by IRPC wrappers in `drepl_service.c`, but the implementation stops at debug tracing.

Dependencies/integration: DRSUAPI generated structures, DREPL service type, Samba debug/NDR helpers, and IRPC registration through `drepl_service.c`. Risks are primarily feature gaps: callers expecting Add/Del/Mod topology management will receive not implemented despite the service registering handlers. Test signals: RPC/IRPC callers should see `NT_STATUS_NOT_IMPLEMENTED`; debug output should include the inbound request for diagnosis; no DSDB state should change.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/drepl_replica.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/drepl_ridalloc.c -->
# sources/user-network-fs/samba/source4/dsdb/repl/drepl_ridalloc.c

Purpose: detects low local RID pool state and requests a new pool from the RID Manager FSMO owner using DRS extended operation `DRSUAPI_EXOP_FSMO_RID_ALLOC`.

Important APIs/functions: `dreplsrv_ridalloc_check_rid_pool()` is the service check; `drepl_ridalloc_pool_exhausted()` inspects this DC's RID Set; `drepl_request_new_rid_pool()` schedules the extended op; `drepl_new_rid_pool_callback()` clears `rid_alloc_in_progress`; `dreplsrv_allocate_rid()` is the messaging hook triggered by samldb.

Control flow/state: RODCs and in-progress allocations return immediately. The check finds the RID Manager object, reads `fSMORoleOwner`, skips if this DC is the RID master, then treats no local RID Set or the second half of the previous allocation pool as needing a new pool. On scheduling success, `service->rid_alloc_in_progress` prevents duplicate requests until callback completion. Persistent RID changes are produced by remote FSMO behavior and replication, not direct writes here.

Dependencies/integration: SAMDB RID/FSMO helpers, DREPL extended operation scheduler, messaging `MSG_DREPL_ALLOCATE_RID`, and RID Set attributes (`rIDAllocationPool`, `rIDPreviousAllocationPool`, `rIDNextRid`). Risks include threshold assumptions, no direct caller status from the messaging hook, and stuck in-progress state if callbacks are lost. Test signals: RODC skip, RID-master skip, no-RID-set bootstrap request, half-pool threshold, and duplicate suppression while an exop is pending.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/drepl_ridalloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/drepl_secret.c -->
# sources/user-network-fs/samba/source4/dsdb/repl/drepl_secret.c

Purpose: triggers targeted replication of a user's secret attributes, typically after authentication code asks for a missing/stale secret.

Important APIs/functions: `drepl_repl_secret()` parses the user DN, finds its NC root and local partition, chooses the first source DSA, builds a source DSA DN from its GUID, and calls `drepl_request_extended_op()` with `DRSUAPI_EXOP_REPL_SECRET` and the source high-watermark. `drepl_repl_secret_callback()` logs success, access denial (`WERR_DS_DRA_SECRETS_DENIED`), or other failure.

Control flow/state: the request is fire-and-forget from the IRPC trigger in `drepl_service.c`; the service sends no IRPC reply. All state is transient except for replicated object commits performed by the pull helper. Source choice is deliberately simple: the first source in the partition list.

Dependencies/integration: DREPL service partition/source state, DSDB NC-root lookup, GUID DNS naming, extended operation scheduler, and auth-triggered IRPC. Risks include arbitrary first-source selection, no direct caller result, failure when a partition has no sources, and secret/RODC partial attribute flag subtleties in lower layers. Test signals: invalid DN handling, no-source partition logging, denied-secret logging, min-USN/high-watermark passed into exop setup, and successful application of fetched secret attributes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/drepl_secret.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/drepl_service.c -->
# sources/user-network-fs/samba/source4/dsdb/repl/drepl_service.c

Purpose: registers and initializes Samba's DSDB replication service task and exposes IRPC handlers for replication, refresh, FSMO, secret replication, and RID allocation triggers.

Important APIs/functions: `server_service_drepl_init()` registers the `drepl` service; `dreplsrv_task_init()` initializes service state; `dreplsrv_connect_samdb()` opens SAMDB, records NTDS GUID/RODC status, and populates DRS bind capabilities; `drepl_replica_sync()` handles forwarded `DsReplicaSync`; `dreplsrv_refresh()` reloads partitions; wrapper handlers forward ReplicaAdd/Del/Mod and secret triggers. `_drepl_schedule_replication()` schedules pull operations and coordinates deferred IRPC replies.

Control flow/state: startup is AD DC-only, then credentials, SAMDB, partitions, periodic timer, pending immediate, notify timer for writable DCs, IRPC names, and message handlers are registered. `drepl_replica_sync()` validates level/NC, finds a partition, decides async vs deferred reply, schedules all or one source DSA by GUID/DNS, creates temporary DSAs when needed, and schedules immediate pull execution. Completion callback counts outstanding operations and replies with the last failure.

Dependencies/integration: task service framework, loadparm, SAMDB/roles, DRSUAPI/IRPC generated interfaces, partition and queue modules, notify/RID/secret/FSMO code, and messaging. Risks include large bind capability surface, deferred reply accounting, temporary source handling, and unimplemented ReplicaAdd/Del/Mod despite registration. Test signals: role gating, bind info negotiation fields, async vs sync `DsReplicaSync`, `DRS_SYNC_ALL`, `DRS_SYNC_BYNAME`, temporary DSA path, refresh after KCC notification, and RODC notify skip.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/drepl_service.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/drepl_service.h -->
# sources/user-network-fs/samba/source4/dsdb/repl/drepl_service.h

Purpose: central type contract for the DSDB replication service.

Important types/APIs: `dreplsrv_drsuapi_connection` caches DCE/RPC pipe, binding handle, session key, remote bind info, and bind handle. `dreplsrv_out_connection` caches a binding per source host. `dreplsrv_partition_source_dsa` wraps one `repsFrom`/`repsTo` source, its `repsFrom1`, `notify_uSN`, and connection. `dreplsrv_partition` holds NC identity, UDV, source and notify lists, and partial/RODC replica flags. `dreplsrv_out_operation` and `dreplsrv_notify_operation` are queued work items. `dreplsrv_service` aggregates task, credentials, SAMDB, NTDS GUID, bind capabilities, timers/immediate, partitions, connections, operation queues, RID allocation flag, and RODC status.

Control flow/state: this header defines the in-memory model used by all DREPL implementation files. Durable replication state is stored in DSDB attributes and committed objects; this struct holds caches, queues, timers, and transient per-run flags. The callback typedef lets extended operations report asynchronously through the same pull machinery.

Dependencies/integration: generated DRSUAPI client types, IRPC, outgoing helper header, and generated service prototypes. Risks include tight cross-file coupling, single-lane queue assumptions baked into `ops.current`/`n_current`, and lifetime sensitivity of talloc-referenced source DSAs. Test signals: compile coverage for all DREPL modules, queue ownership/lifetime tests, and startup initialization of every field used by periodic, notify, pull, and extended-op paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/repl/drepl_service.h -->
