# subset-b-009707 research

Grouped research report for the subset B work item. Each section is delimited for deterministic reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/rquota_setquota.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/rquota_setquota.c

Purpose: implements the RQUOTA `SETQUOTA` RPC handler for both the legacy and extended rquota protocol versions. The public entry point `rquota_setquota()` decodes the version-specific argument shape, normalizes it into path, quota id, quota type, and `sq_dqblk`, then delegates to `do_rquota_setquota()`.

Important APIs and types: `nfs_arg_t`, `nfs_res_t`, `setquota_rslt`, `sq_dqblk`, `fsal_quota_t`, `struct svc_req`, `struct gsh_export`, `check_handle_lead_slash()`, `get_gsh_export_by_tag()`, `get_gsh_export_by_pseudo()`, `get_gsh_export_by_path()`, `set_op_context_export()`, `nfs_req_creds()`, and `exp->fsal_export->exp_ops.set_quota()`.

Control flow: the handler defaults to user quota, chooses extended arguments when `req->rq_msg.cb_vers == EXT_RQUOTAVERS`, otherwise uses the legacy `sqa_uid` style. The helper initializes the result to `Q_EPERM`, validates and normalizes the quota path, locates an export by tag, pseudo path, or real path depending on the supplied path and `mount_path_pseudo`, installs the export into `op_ctx`, obtains request credentials, copies wire quota fields into an FSAL quota structure, calls the FSAL `set_quota` operation, maps `ERR_FSAL_NO_QUOTA` to `Q_NOQUOTA`, and on success copies returned quota values into `qres` with `Q_OK`.

State and persistence: it does not persist state directly. Durable state is owned by the FSAL/backend quota implementation. It mutates request-local `op_ctx` by setting the export and depends on the surrounding request cleanup to release it.

Dependencies and integration points: integrates RQUOTA protocol dispatch with export manager lookup, NFS credential extraction, `op_ctx`, FSAL quota operations, and protocol XDR types from `rquota.h`. It assumes the selected export supports `set_quota`.

Risks: path/export lookup failures leave status at `Q_EPERM` but return `NFS_REQ_OK`, so callers receive a protocol-level success with quota-level denial. `rq_curfiles` is not copied from the input or output in this handler even though XDR carries it. Correct authorization depends on `nfs_req_creds()` and the FSAL implementation. The extended protocol accepts arbitrary quota type integers and passes them through.

Test signals: exercise legacy and extended setquota requests, tag/pseudo/path export lookup modes, missing export, credential failure, FSAL success, FSAL `ERR_FSAL_NO_QUOTA`, and backend error cases. Verify result status and all returned quota fields on success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/rquota_setquota.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/CMakeLists.txt

Purpose: defines the `nfs_mnt_xdr` object library that contains XDR encode/decode implementations for mount, NFSv2/v3, NFSv4.1, NLM, NSM, NFSACL, and optionally RQUOTA protocol data.

Important APIs and targets: `nfs_mnt_xdr_STAT_SRCS`, `add_library(nfs_mnt_xdr OBJECT ...)`, `add_sanitizers(nfs_mnt_xdr)`, `set_target_properties(... -fPIC)`, feature variables `USE_RQUOTA` and `USE_LTTNG`, and the generated LTTng dependency `gsh_trace_header_generate`.

Control flow: the file builds the static source list with the core XDR files, appends `xdr_rquota.c` only when `USE_RQUOTA` is enabled, creates an object library, attaches sanitizer instrumentation, forces position-independent compilation, and wires trace header generation when LTTng support is configured.

State and persistence: no runtime state. Build output is an object library consumed by higher-level ganesha targets.

Dependencies and integration points: integrates protocol XDR objects into the larger build. Conditional RQUOTA compilation must align with protocol dispatch and headers. LTTng dependencies must align with generated trace headers so trace-aware files compile after generation.

Risks: adding a protocol XDR file without updating this list omits symbols at link time. Enabling `USE_RQUOTA` without matching headers/protocol sources can break builds. Because this is an object library, consumers inherit object files rather than linking a standalone archive.

Test signals: configure builds with `USE_RQUOTA` on and off, with `USE_LTTNG` on and off, and verify `nfs_mnt_xdr` object files and dependent final targets link without missing XDR symbols.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_mount.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_mount.c

Purpose: provides rpcgen-style XDR routines for the MOUNT protocol data structures, especially MOUNT v3 status, file handles, directory paths, groups, exports, mount lists, and mount results.

Important APIs and types: `xdr_mountstat3()`, `xdr_fhandle3()`, `xdr_dirpath()`, `xdr_name()`, `xdr_groups()`, `xdr_exports()`, `xdr_mountlist()`, `xdr_mountres3_ok()`, `xdr_mountres3()`, `groupnode`, `exportnode`, `mountbody`, and `mountres3`. It uses inline helpers such as `inline_xdr_enum()`, `inline_xdr_bytes()`, and `inline_xdr_string()`.

Control flow: scalar/string wrappers serialize bounded fields. Linked-list routines encode/decode/free non-recursively: they emit a boolean presence marker, allocate or reference the node with `xdr_reference()`, and advance to the next pointer, remembering the next node during `XDR_FREE`. `xdr_mountres3()` serializes the status first and only serializes the success union arm when status is `MNT3_OK`.

State and persistence: no service state. During decode and free, XDR may allocate or release linked list nodes through the RPC runtime.

Dependencies and integration points: depends on mount/NFS protocol definitions from `nfs23.h` and file handle constants from `nfs_fh.h`. Used by mount daemon dispatch and duplicate request response cleanup through protocol free functions.

Risks: linked-list decode relies on valid remote length termination; malformed streams can fail mid-list and leave partial allocations for the caller/free path. Path and name bounds are enforced by `MNTPATHLEN`, `MNTNAMLEN`, and `NFS3_FHSIZE`. Auth flavor arrays use `XDR_ARRAY_MAXLEN`, so tests should cover very large advertised arrays.

Test signals: round-trip mount success/failure responses, export and mount lists of length zero/one/many, XDR_FREE on decoded lists, oversized names/paths/file handles, and malformed list presence markers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_mount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_nfs23.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_nfs23.c

Purpose: implements hand-maintained XDR routines for NFSv2 and NFSv3 wire types, including scalar wrappers, file handles, attributes, weak cache consistency data, all major NFSv3 operation arguments/results, read/write payloads, and optimized directory listing encoders.

Important APIs and types: NFSv2 helpers such as `xdr_nfspath2()`, `xdr_fhandle2()`, `xdr_nfsdata2()`; NFSv3 helpers such as `xdr_nfs_fh3()`, `xdr_fattr3()`, `xdr_sattr3()`, `xdr_wcc_data()`, and per-operation functions for `GETATTR`, `SETATTR`, `LOOKUP`, `ACCESS`, `READ`, `WRITE`, `CREATE`, `MKDIR`, `SYMLINK`, `MKNOD`, `REMOVE`, `RMDIR`, `RENAME`, `LINK`, `READDIR`, `READDIRPLUS`, `FSSTAT`, `FSINFO`, `PATHCONF`, and `COMMIT`. It also exports `xdr_encode_entry3()`, `xdr_encode_entryplus3()`, `xdr_dirlist3_uio_release()`, and `xdr_dirlistplus3_uio_release()`.

Control flow: most routines serialize fields in protocol order and switch on status or discriminator fields before handling union arms. `xdr_fattr3()` translates between FSAL internal file types/modes and NFSv3 `ftype3`/Unix mode on encode/decode. Request argument decoders update `struct nfs_request_lookahead` through `xdrs->x_public` for read, write, create, remove, rename, readdir, and commit so upper layers can make cacheability and scheduling decisions. Directory response handling supports normal linked-list XDR and a zero-copy-ish `xdr_uio` path through `xdr_putbufs()`.

State and persistence: no durable state. It mutates decoded structures, request lookahead counters, and `xdr_uio` reference counts. UIO release avoids freeing RDMA buffers when `op_ctx->is_rdma_buff_used` is set.

Dependencies and integration points: depends on `nfs23.h`, FSAL attribute conversion helpers, file handle definitions, `op_ctx`, `gsh_free`, and ntirpc XDR extensions. Duplicate request cache logic consumes lookahead flags produced here, especially to decide NFSv4 duplicate caching behavior.

Risks: attribute type conversion logs bogus values but may continue with partially initialized locals for unexpected types. Directory UIO reference/release behavior must match async send completion; premature or missing release leaks or double-frees buffers. Bounds for NFSv3 strings use `XDR_STRING_MAXLEN`, while file handles cap at 64 bytes. Lookahead updates depend on `xdrs->x_public` having the expected layout.

Test signals: XDR round trips for every NFSv3 operation success/failure union, fattr encode/decode for all file types, read/write payloads, readdir/readdirplus linked-list and UIO encodings, RDMA buffer release behavior, and lookahead flag/counter assertions after decoding relevant operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_nfs23.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_nfsacl.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_nfsacl.c

Purpose: implements XDR routines for the NFSACL v3 extension: attribute wrapper, POSIX ACL entries, ACL vectors, getacl arguments/results, and setacl arguments/results.

Important APIs and types: `xdr_attr3()`, `xdr_posix_acl_entry()`, `xdr_posix_acl()`, `xdr_getaclargs()`, `xdr_getaclresok()`, `xdr_getaclres()`, `xdr_setaclargs()`, `xdr_setaclresok()`, `xdr_setaclres()`, `posix_acl`, `posix_acl_entry`, `getaclargs`, `getaclres`, and `setaclargs`.

Control flow: `xdr_attr3()` serializes a boolean and optional NFSv3 attributes. `xdr_posix_acl()` reads/writes a count, rejects counts over 4096, then serializes exactly that many fixed entries with `xdr_vector()`. Get/set result routines switch on `NFS3_OK` and only serialize success payloads for success. ACL pointer handling uses `xdr_reference()` when memory is already supplied or on decode paths that need allocated storage, and `xdr_pointer()` when nullable semantics are desired.

State and persistence: no persistent state. Decode/free may allocate and free ACL buffers sized as `sizeof(posix_acl) + count * sizeof(posix_acl_entry)`.

Dependencies and integration points: depends on NFSv3 XDR helpers from `xdr_nfs23.c` and ACL protocol definitions in `nfsacl.h`. This bridges NFSACL protocol dispatch to FSAL ACL handling elsewhere.

Risks: count-derived allocation sizes can become large even with the 4096 cap; callers must ensure decoded ACL counts match allocated entry arrays. `xdr_vector()` expects contiguous entries, so structure layout must match the protocol definition. Setacl decode forces allocation even if counts are zero, so free paths should be covered.

Test signals: getacl/setacl success and error round trips, null and non-null ACL pointers, zero ACL counts, maximum allowed count, count above 4096 rejection, and XDR_FREE on decoded ACLs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_nfsacl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_nfsv41.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_nfsv41.c

Purpose: placeholder compilation unit for NFSv4.1 XDR routines with external linkage. The file documents that most Ganesha NFSv4.1 XDR routines are inline definitions in `nfsv41.h`.

Important APIs and types: includes `config.h` and `nfsv41.h`; it does not define callable routines in the current source.

Control flow: no runtime control flow. The unit exists to provide a stable file for non-inline decoder routines if needed and to keep the build list aligned with protocol organization.

State and persistence: none.

Dependencies and integration points: participates in the `nfs_mnt_xdr` object library. Its main integration value is ensuring NFSv4.1 XDR headers compile in this target and leaving a place for future external XDR symbols.

Risks: because most behavior is in headers, changes to `nfsv41.h` can affect many translation units without this file changing. Test and coverage tools may show this file as empty even though it represents an important build edge.

Test signals: build coverage is the main signal. Full NFSv4.1 XDR behavior should be tested through the inline routines and protocol compound encode/decode paths, not through this file directly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_nfsv41.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_nlm4.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_nlm4.c

Purpose: rpcgen-style XDR implementation for NLMv4 lock manager protocol structures: status/results, lock descriptors, test replies, lock/cancel/test/unlock arguments, share reservations, free-all requests, and NSM notify arguments used by locking recovery.

Important APIs and types: `xdr_nlm4_stats()`, `xdr_nlm4_stat()`, `xdr_nlm4_res()`, `xdr_nlm4_holder()`, `xdr_nlm4_testrply()`, `xdr_nlm4_testres()`, `xdr_nlm4_lock()`, `xdr_nlm4_lockargs()`, `xdr_nlm4_cancargs()`, `xdr_nlm4_testargs()`, `xdr_nlm4_unlockargs()`, `xdr_nlm4_share()`, `xdr_nlm4_shareargs()`, `xdr_nlm4_shareres()`, `xdr_nlm4_free_allargs()`, and `xdr_nlm4_sm_notifyargs()`.

Control flow: routines serialize fields in NLM protocol order. `xdr_nlm4_testrply()` switches on status and only includes `nlm4_holder` when the test is denied. Lock and share structures include caller names, file handles and owner handles as netobjs, process id, offsets, lengths, modes, and access masks.

State and persistence: no local state. Decode/free state is owned by XDR netobj/string allocation and the caller.

Dependencies and integration points: includes `nlm4.h` and `nfs_fh.h`; used by NLM dispatch and recovery code when serializing network lock manager traffic. It is conditionally relevant when NLM support is enabled in the build.

Risks: bounded strings use `LM_MAXSTRLEN`, `LM_MAXNAMELEN`, and `SM_MAXSTRLEN`; malformed or oversized caller names must fail cleanly. Netobj sizes are delegated to `xdr_netobj()`, so upstream limits matter for memory pressure. Offsets and lengths are 64-bit and should be validated by lock logic after decode.

Test signals: round-trip all NLMv4 request/response forms, denied test replies with holder data, free-all and notify arguments, oversized strings/netobjs, and XDR_FREE for decoded variable fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_nlm4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_nsm.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_nsm.c

Purpose: provides XDR routines for Network Status Monitor structures used with NLM recovery and host monitoring.

Important APIs and types: `xdr_res()`, `xdr_sm_stat_res()`, `xdr_sm_stat()`, `xdr_my_id()`, `xdr_mon_id()`, `xdr_mon()`, `xdr_notify()`, and protocol types from `nsm.h`.

Control flow: routines encode/decode enum results, state integers, monitor identity fields, program/version/procedure callback identity, monitor payload private bytes, and notify messages in fixed protocol order. Strings are bounded by `SM_MAXSTRLEN`; monitor private data is fixed-size opaque bytes.

State and persistence: no local state. State numbers are protocol data used by recovery/monitoring layers elsewhere.

Dependencies and integration points: depends on ntirpc XDR and `nsm.h`. Integrates with NLM/NSM code that tracks client reboot notifications and lock reclamation.

Risks: NSM identity strings and callback program values are trusted only after higher-layer validation. Decode failures must release any allocated strings through the normal XDR free path.

Test signals: round-trip monitor, notify, stat, and stat result structures; oversized monitor names; corrupted opaque private payload length; and XDR_FREE after decoded strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_nsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_rquota.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_rquota.c

Purpose: hand-updated rpcgen-derived XDR routines for RQUOTA get/set quota arguments and results, including the extended protocol that carries quota type separately from id.

Important APIs and types: `xdr_sq_dqblk()`, `xdr_getquota_args()`, `xdr_setquota_args()`, `xdr_ext_getquota_args()`, `xdr_ext_setquota_args()`, `xdr_rquota()`, `xdr_qr_status()`, `xdr_getquota_rslt()`, `xdr_setquota_rslt()`, `sq_dqblk`, `rquota`, `getquota_rslt`, and `setquota_rslt`.

Control flow: quota block and quota result structures use optimized inline encode/decode paths for fixed 8-word and 10-word payloads, with scalar XDR fallback and generic XDR_FREE handling. Argument routines serialize bounded path strings, ids, qcmd, optional type, and quota blocks. Result routines serialize status first and include the quota union arm only for `Q_OK`; `Q_NOQUOTA` and `Q_EPERM` carry no payload and unknown statuses fail.

State and persistence: no local state. XDR decode may allocate path strings through `xdr_string()` and XDR_FREE releases them.

Dependencies and integration points: included only when RQUOTA build support is enabled. It feeds the RQUOTA protocol handlers such as `rquota_setquota.c` and must match structures in `rquota.h`.

Risks: all quota quantities are 32-bit wire values, so backend 64-bit quota values may be truncated elsewhere. Inline paths assume exact field counts and byte order helpers. Paths are bounded by `RQ_PATHLEN`, but handler-side export resolution still determines semantic validity.

Test signals: round-trip fixed quota blocks through inline and fallback XDR paths, legacy and extended get/set args, each result status, unknown status rejection, maximum path lengths, and XDR_FREE for decoded path strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_rquota.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/RPCAL/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/RPCAL/CMakeLists.txt

Purpose: defines the `rpcal` object library for RPC abstraction layer code: connection management, metrics, duplicate request cache, RPC tools, and optional GSS credential support.

Important APIs and targets: `rpcal_STAT_SRCS`, `add_library(rpcal OBJECT ...)`, `add_sanitizers(rpcal)`, `set_target_properties(... -fPIC)`, feature variables `_HAVE_GSSAPI` and `USE_LTTNG`, and generated trace dependency wiring.

Control flow: builds the base RPCAL source list, appends `gss_credcache.c` and `gss_extra.c` only when GSSAPI support is configured, creates an object library, enables sanitizers, compiles as PIC, and orders LTTng trace header generation when tracing is enabled.

State and persistence: no runtime state; build-time composition controls which RPCAL symbols are available.

Dependencies and integration points: connects RPC transport helpers, duplicate request cache, and connection-manager code into the larger server target. Optional GSS sources must align with headers, Kerberos libraries, and authentication feature gates.

Risks: feature-gate mismatches can produce missing authentication or duplicate symbol/link errors. Since this is an object library, every consumer receives the same object set; compile flags and generated trace dependencies must be correct at this level.

Test signals: configure builds with and without GSSAPI and LTTng, verify final ganesha targets link, and run unit/integration tests covering duplicate requests, connection manager metrics, and GSS startup only in matching builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/RPCAL/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/RPCAL/connection_manager.c -->
# sources/user-network-fs/nfs-ganesha/src/RPCAL/connection_manager.c

Purpose: implements a connection manager that attempts to ensure a client is connected to only one Ganesha server at a time, supporting local draining, remote drain/register callbacks, transport lifecycle hooks, metrics, and tracepoints.

Important APIs and types: `connection_manager__callback_set()`, `connection_manager__callback_clear()`, `connection_manager__client_init()`, `connection_manager__client_fini()`, `connection_manager__drain_and_disconnect_local()`, `connection_manager__connection_init()`, `connection_manager__connection_started()`, `connection_manager__connection_finished()`, `connection_manager__init()`, `connection_manager__client_t`, `connection_manager__connection_t`, callback context types, and state/result enums.

Control flow: each client moves through `DRAINED -> ACTIVATING -> ACTIVE -> DRAINING` with guarded transitions in `change_state()`. Starting a managed connection obtains/creates the `gsh_client`, initializes the connection object from transport custom data, and under the client mutex either activates a drained client by invoking the registered remote drain callback, waits for another activator, accepts an already active client, or cancels an ongoing drain. Registration happens through callbacks under a global rwlock; if the client drains while registration is in flight, the connection is deregistered and refused. Local drain marks connections destroyed, sets TCP linger to force fast close, calls `SVC_DESTROY()`, waits on a condition variable, and classifies success, timeout, stuck, or failed.

State and persistence: per-client state lives in `gsh_client->connection_manager` with mutex, condition variable, connection list, and count. Per-connection state lives in `xprt` custom data. Callback context is global under `callback_lock`. No durable persistence.

Dependencies and integration points: integrates with `client_mgr`, `xprt_handler`, `nfs_param.core_param.enable_connection_manager`, `connection_manager_metrics`, LTTng tracepoints, socket APIs, and ntirpc transport lifecycle (`SVC_DESTROY`, `svc_getrpccaller`).

Risks: correctness relies on lock ordering between client mutex and callback rwlock, plus careful unlock/relock around remote callbacks. Default callbacks refuse management, so startup ordering matters. Loopback connections are never managed. Forced linger can affect client-visible TCP behavior. The code reads `client` after `put_gsh_client()` in logging paths, which should be reviewed for lifetime safety depending on `gsh_client` retention.

Test signals: concurrent connection starts for the same client, remote drain success/failure, local drain with zero/active/stuck connections, drain cancellation by a new connection, non-managed loopback behavior, callback set/clear assertions, metrics emission, and transport-finish deregistration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/RPCAL/connection_manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/RPCAL/connection_manager_metrics.c -->
# sources/user-network-fs/nfs-ganesha/src/RPCAL/connection_manager_metrics.c

Purpose: registers and updates monitoring metrics for connection-manager client states, connection-start latencies, and local-drain latencies.

Important APIs and types: `connection_manager_metrics__init()`, `connection_manager_metrics__client_state_inc()`, `connection_manager_metrics__client_state_dec()`, `connection_manager_metrics__connection_started_done()`, `connection_manager_metrics__drain_local_client_done()`, `connection_manager__metrics_t`, and the metric handles declared in the companion header.

Control flow: init registers one gauge per client state and histograms per connection-start result and drain result, using enum ordinals as array indexes and labels generated by stringify helpers. Completion functions compute elapsed milliseconds from a captured `struct timespec` using `now()` and `timespec_diff()`, then observe the matching histogram.

State and persistence: static process-global `metrics` stores monitoring handles. Metric values are held by the monitoring subsystem, not this file.

Dependencies and integration points: depends on `connection_manager.h`, `monitoring.h`, `now()`, `NS_PER_MSEC`, and enum sizes ending in `__LAST`. Called from connection manager state transitions and completion paths.

Risks: enum reordering or missing `__LAST` alignment breaks label-to-index mapping. Unknown enum values call `LogFatal()`. Metrics must be initialized before connection-manager operations update gauges/histograms.

Test signals: initialize metrics once, transition every client state, record both connection-start results, record every drain result, verify labels and units in monitoring output, and validate fatal behavior or assertions for invalid enum inputs in controlled tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/RPCAL/connection_manager_metrics.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/RPCAL/connection_manager_metrics.h -->
# sources/user-network-fs/nfs-ganesha/src/RPCAL/connection_manager_metrics.h

Purpose: declares the metric handle container and update API used by the connection manager.

Important APIs and types: `connection_manager__metrics_t`, `gauge_metric_handle_t clients[]`, `histogram_metric_handle_t connection_started_latencies[]`, `histogram_metric_handle_t drain_local_client_latencies[]`, plus declarations for init, gauge increment/decrement, and histogram completion functions.

Control flow: no implementation control flow. Array dimensions are tied to `CONNECTION_MANAGER__CLIENT_STATE__LAST`, `CONNECTION_MANAGER__CONNECTION_STARTED__LAST`, and `CONNECTION_MANAGER__DRAIN__LAST`.

State and persistence: describes in-memory metric handles managed by `connection_manager_metrics.c` and the monitoring subsystem.

Dependencies and integration points: includes `connection_manager.h` for enums and `monitoring.h` for handle types. This header is consumed by `connection_manager.c` and metrics implementation.

Risks: no include guard is visible in this header, so repeated inclusion depends on current include patterns not causing duplicate typedef issues. Enum count changes require corresponding stringify support and registration loops in the `.c` file.

Test signals: compile all translation units including this header, run builds with strict warnings, and verify enum additions fail review unless metrics registration and labels are updated.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/RPCAL/connection_manager_metrics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/RPCAL/gss_credcache.c -->
# sources/user-network-fs/nfs-ganesha/src/RPCAL/gss_credcache.c

Purpose: manages Kerberos/GSS machine credential acquisition and cleanup for Ganesha callbacks, including keytab discovery, principal caching, credential cache creation, and supported-mechanism checks.

Important APIs and types: `gssd_init_cred_cache()`, `gssd_shutdown_cred_cache()`, `gssd_refresh_krb5_machine_credential()`, `gssd_check_mechs()`, `gssd_clear_cred_cache()`, `struct gssd_k5_kt_princ`, `ccachesearch[]`, `gssd_get_single_krb5_cred()`, `find_keytab_entry()`, `gssd_search_krb5_keytab()`, and Kerberos/GSS functions such as `krb5_get_init_creds_keytab()`, `krb5_cc_initialize()`, and `gss_indicate_mechs()`.

Control flow: refresh initializes a krb5 context, resolves the configured keytab, finds or creates a principal-list entry either from an explicit `ple` or by hostname/service keytab lookup, then obtains credentials if the cached ccache is missing/expired. Keytab selection tries AD machine account, `root`, `nfs`, and `host` by default unless a specific service is requested; it tries target realm, default realm, exact host principals, and any-instance service principals. Successful credentials are stored in a `MEMORY:` or `FILE:` ccache under `ccachesearch[0]`, and the GSS mechanism is pointed at that ccache via `gss_krb5_ccache_name()` or `KRB5CCNAME`.

State and persistence: global `gssd_k5_kt_princ_list` caches principal, realm, ccache name, and ticket end time under `ple_mtx`. FILE ccaches may persist on disk until cleared or overwritten; MEMORY ccaches are process-local. `gssd_clear_cred_cache()` walks the global list, destroys krb5 ccaches when a context can be created, and frees entries.

Dependencies and integration points: depends on MIT/Heimdal Kerberos compatibility macros, `nfs_param.krb5_param.keytab`, `ccachesearch`, name resolution helpers, Ganesha memory/logging utilities, and callback/authentication code that needs machine credentials.

Risks: global principal entries are protected only while finding/adding/clearing entries; individual `ple` updates in credential refresh are not separately locked. `ccachesearch[0]` must be initialized and writable for FILE caches. Hostname canonicalization and realm lookup can block or fail DNS. Environment-variable ccache selection is process-global. Cleanup proceeds even if ccache destruction fails, which avoids memory leaks but can leave FILE ccaches behind.

Test signals: MIT and Heimdal builds, keytab with exact host principal, any-instance fallback, AD machine-account fallback, missing keytab, expired versus valid cached creds, MEMORY and FILE cache modes, ccache cleanup, DNS failure, and `gss_indicate_mechs()` failure/empty set.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/RPCAL/gss_credcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/RPCAL/gss_extra.c -->
# sources/user-network-fs/nfs-ganesha/src/RPCAL/gss_extra.c

Purpose: provides small GSS/RPCSEC_GSS utility functions for logging and debugging.

Important APIs and types: `log_sperror_gss()` converts GSS major/minor status values into a combined string, and `str_gc_proc()` maps `rpc_gss_proc_t` values to symbolic names.

Control flow: `log_sperror_gss()` calls `gss_display_status()` first for the GSS major code and then for the mechanism minor code, formats fallback messages when translation fails, and releases GSS buffers. `str_gc_proc()` switches over RPCSEC_GSS procedure constants and returns `"unknown"` for unrecognized values.

State and persistence: no persistent state. It writes into caller-supplied `outmsg`.

Dependencies and integration points: supports both Heimdal and non-Heimdal include paths, uses GSSAPI, RPC auth GSS types, and Ganesha logging-related headers. Called by authentication paths that need human-readable GSS diagnostics.

Risks: `log_sperror_gss()` uses `sprintf()` with no explicit output buffer length, so caller buffer sizing is critical. It only consumes one display-status message from each status chain, not necessarily all continuation messages. Returned strings from `str_gc_proc()` must remain aligned with RPCSEC_GSS constants.

Test signals: translate known major/minor GSS failures, force major/minor display failure paths, validate buffer sizing at call sites, and cover all RPCSEC_GSS procedure enum values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/RPCAL/gss_extra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/RPCAL/nfs_dupreq.c -->
# sources/user-network-fs/nfs-ganesha/src/RPCAL/nfs_dupreq.c

Purpose: implements the NFS duplicate request cache (DRC), used to detect retransmitted RPC requests and either replay cached responses, queue duplicates while the original is in progress, or bypass caching for non-cacheable operations.

Important APIs and types: `dupreq2_pkginit()`, `dupreq2_cleanup()`, `nfs_dupreq_start()`, `nfs_dupreq_finish()`, `nfs_dupreq_delete()`, `nfs_dupreq_rele()`, `nfs_dupreq_put_drc()`, `for_each_tcp_drc()`, `get_tcp_drc_recycle_qlen()`, `drc_t`, `dupreq_entry_t`, `nfs_request_t`, object pools `dupreq_pool`, `nfs_res_pool`, and `tcp_drc_pool`.

Control flow: package init creates pools, a shared UDP DRC, and TCP DRC recycle structures. Request start checks whether the function is cacheable, DRC is enabled, and NFSv4 request lookahead permits caching. It obtains a shared UDP or per-connection TCP DRC, builds a key from xid, program, version, procedure, client address for UDP, and TI-RPC checksum, then searches an rb-tree partition. A hit increments duplicate count, queues unfinished duplicates up to `DUPREQ_MAX_DUPES`, returns existing completed responses, or drops excess in-flight dupes. A miss allocates a response, inserts a START entry, and gives it two references. Finish marks the entry complete, queues it for FIFO retirement, drains the retire window, and removes old completed entries when high-water or max-size conditions require. Delete removes failed uncached entries unless duplicate waiters need retry. Release resumes queued duplicates, drops request references, releases DRC references, and releases RPC auth.

State and persistence: all state is in memory. UDP has one shared DRC. TCP DRCs can outlive transports via a recycle rb-tree and FIFO queue keyed by client address, with refcounts, recycle flags, and expiry. Dupreq entries own cached `nfs_res_t` responses and duplicate wait queues.

Dependencies and integration points: integrates with ntirpc transports (`xp_u2`, `rq_u1`, `rq_u2`, resume callbacks), protocol function descriptor tables, NFSv3/v4/MOUNT/NLM/RQUOTA/NFSACL dispatch descriptors, CityHash, rb-tree partitions, object pools, and request lookahead populated by XDR decoders.

Risks: concurrency is delicate: DRC mutexes, global recycle mutex, rb-tree partition locks, and per-entry mutexes have explicit lock-order workarounds. TCP DRC refcounts can rise from zero during recycle reuse. Magic `rq_u1` sentinel values must never alias real pointers. Replaying cached responses requires protocol free functions to match response ownership. NFSv4.1 caching is intentionally bypassed because sessions have slot reply caches.

Test signals: UDP and TCP duplicate detection, completed response replay, in-flight duplicate queuing and resume, excess duplicate drop, failed request delete/retry paths, TCP DRC recycle reuse after reconnect, expiry under high water, disabled DRC mode, NFSv4 non-cacheable lookahead cases, and stress tests under concurrent retransmits/disconnects.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/RPCAL/nfs_dupreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/RPCAL/rpc_tools.c -->
# sources/user-network-fs/nfs-ganesha/src/RPCAL/rpc_tools.c

Purpose: provides RPC utility helpers, mainly transport type stringification, transport-address copying, and `io_data` XDR encode/decode/free support for scatter/gather NFS payloads.

Important APIs and types: `xprt_type_to_str()`, `copy_xprt_addr()`, `xdr_io_data()`, `release_io_data_copy()`, `io_data`, `struct xdr_uio`, `struct xdr_vio`, and ntirpc XDR extension macros such as `xdr_putbufs()`, `XDR_FILLBUFS()`, `XDR_IOVCOUNT()`, and RDMA data-position helpers.

Control flow: `xdr_io_data()` dispatches by XDR operation. Encode writes the data length, builds an `xdr_uio` over caller-provided iovecs, handles XDR 4-byte rounding by either extending the last buffer if capacity permits or adding an inline zero-padded extra buffer, optionally preserves a release callback copy for async sends, and submits buffers with `xdr_putbufs()`. Decode reads the length, handles zero-length data with an empty iovec, computes the stream/RDMA data position, either copies into one allocated buffer when iov count exceeds `IOV_MAX` or maps XDR buffers into iovecs, advances the stream past rounded data, and sets release behavior. Free invokes any release callback and frees the iovec.

State and persistence: no durable state. UIO reference counts and release callbacks control buffer lifetime across asynchronous transport send completion. Decode can point iovecs directly into XDR receive buffers unless it falls back to copying.

Dependencies and integration points: used by NFS READ/WRITE XDR in `xdr_nfs23.c` and likely NFSv4 payload paths. Integrates with `op_ctx->is_rdma_buff_used`, Ganesha allocation helpers, ntirpc transport buffer APIs, and duplicate request response free paths.

Risks: zero-copy decode ties iovec lifetime to XDR buffer lifetime; callers must finish before receive buffers disappear. Encode padding manipulates the last iovec tail and must respect `last_iov_buf_size`. Release callback ownership is subtle for async sends and RDMA buffers. Large iov counts trigger copy fallback and memory pressure.

Test signals: encode/decode zero-length, aligned, and unaligned payloads; multi-iovec payloads; last-buffer extension versus extra-padding-buffer path; copy fallback over `IOV_MAX`; RDMA buffer mode; release callback invocation exactly once; and XDR_FREE cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/RPCAL/rpc_tools.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/9p_owner.c -->
# sources/user-network-fs/nfs-ganesha/src/SAL/9p_owner.c

Purpose: manages the 9P lock-owner hash table used by the state abstraction layer to identify lock owners by 9P client address and process id.

Important APIs and types: `Init_9p_hash()`, `get_9p_owner()`, `display_9p_owner()`, `display_9p_owner_key_val()`, `compare_9p_owner()`, `_9p_owner_value_hash_func()`, `_9p_owner_rbt_hash_func()`, `ht_9p_owner`, `state_owner_t`, and `STATE_LOCK_OWNER_9P`.

Control flow: initialization creates `ht_9p_owner` with display, compare, and hash callbacks. Lookup builds a stack `state_owner_t` key with type, refcount, proc id, and copied client address, then delegates to generic `get_state_owner(CARE_ALWAYS, ...)`. Display formats type, pointer, address, proc id, and refcount. Compare checks nulls, pointer identity, and process id; address comparison is compiled out. Hashing adds proc id to IPv4 `sin_addr.s_addr` and uses that for bucket and rb-tree hash.

State and persistence: in-memory hash table only. Owner lifetime and refcounting are managed by generic SAL owner code.

Dependencies and integration points: depends on SAL state-owner infrastructure, Ganesha hash table, logging, display helpers, and 9P feature-gated build inclusion through SAL CMake.

Risks: address comparison is disabled, so owners with the same process id can compare equal even from different clients despite hashing including address. Hashing assumes IPv4 layout and has TODOs noting IPv6 limitations. The stack key sets refcount to 1 for lookup, but actual lifetime is owned by generic owner logic.

Test signals: initialize table, look up same proc/client twice and verify sharing/refcount behavior, look up same proc from different clients to expose compare semantics, IPv6 client address behavior, display output, and hash distribution under many proc ids.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/9p_owner.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/SAL/CMakeLists.txt

Purpose: defines the SAL object library source composition for state management, NFSv4 client/session/lease/recovery logic, optional NLM and 9P state support, and optional RADOS recovery module.

Important APIs and targets: `sal_STAT_SRCS`, `add_library(sal OBJECT ...)`, `add_sanitizers(sal)`, `set_target_properties(... -fPIC)`, feature variables `USE_NLM`, `USE_9P`, `USE_RADOS_RECOV`, and `USE_LTTNG`, plus module target `ganesha_rados_recov`.

Control flow: starts with core SAL sources, appends NLM owner/state sources when NLM is enabled, appends `9p_owner.c` when 9P is enabled, builds the `sal` object library, attaches sanitizer and PIC properties, and wires trace header dependencies. If RADOS recovery is enabled, it builds a separate module from RADOS recovery sources, links it against `ganesha_nfsd`, system/RADOS libraries, and disallow-undefined flags, includes RADOS headers, sets SOVERSION, and installs it.

State and persistence: no runtime state. Build-time feature selection determines which state-management implementations and recovery plugins are available.

Dependencies and integration points: central build integration point for SAL, NFSv4 recovery, optional NLM/9P, LTTng, and RADOS recovery. Must match config headers and runtime feature assumptions.

Risks: feature gates must align with source references elsewhere; enabling `USE_9P`, `USE_NLM`, or `USE_RADOS_RECOV` without dependencies can fail compilation/linking. The RADOS module links against the main daemon and external libraries, so ABI and undefined-symbol handling are important.

Test signals: matrix builds for NLM/9P/RADOS/LTTng combinations, final target link checks, module install verification for RADOS recovery, and startup tests confirming the selected state/recovery backends initialize.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/nfs41_session_id.c -->
# sources/user-network-fs/nfs-ganesha/src/SAL/nfs41_session_id.c

Purpose: manages the NFSv4.1 session-id table, session reference lifecycle, session/connection association, backchannel teardown, and destruction of all transports associated with a session.

Important APIs and types: `nfs41_Init_session_id()`, `nfs41_Build_sessionid()`, `_inc_session_ref()`, `_dec_session_ref()`, `nfs41_Session_Set()`, `nfs41_Session_Get_Pointer()`, `nfs41_Session_Del()`, `nfs41_Session_PrintAll()`, `check_session_conn()`, `nfs41_Session_Add_Connection()`, `nfs41_Session_Remove_Connection()`, `nfs41_Session_Destroy_Backchannel_For_Xprt()`, `nfs41_Session_Destroy_All_Connections()`, `nfs41_session_t`, `connection_xprt_t`, `ht_session_id`, `nfs41_session_pool`, and `global_sequence`.

Control flow: session IDs combine the clientid with an atomically incremented global sequence. The hash table uses the sequence portion for bucket/rb hashes and full 16-byte comparison for equality. `Session_Set` inserts a new session if absent, relying on create-session code to supply initial references. `Session_Get_Pointer` looks up with a latch, increments the session reference, then releases the latch. Ref decrement unlinks the session from the client, drops the clientid reference, destroys slot locks and slot state, destroys locks/conds, tears down backchannel state, frees callback security parameters, frees slot arrays, and returns the session to the pool. Deletion releases all session connections before removing the hash entry and dropping a reference. `check_session_conn()` validates whether the request transport is already associated, optionally upgrades from read to write lock to associate a new transport, adds session-to-xprt and xprt-to-session links, and updates SAL metrics. Removal and destruction paths release held SVCXPRT references.

State and persistence: all state is in memory: session hash table, global sequence, session refcounts, per-session connection list, slot tables, callback channel, and callback security parameter allocations. Recovery/persistence is handled elsewhere.

Dependencies and integration points: integrates with NFSv4 clientid records, state pools, hash table latching, xprt session hooks (`add_nfs41_session_to_xprt`, `remove_nfs41_session_from_xprt`), `SVC_REF/RELEASE/DESTROY`, callback RPC channel teardown, LTTng tracepoints, and SAL metrics.

Risks: session lifetime depends on correct refcount balancing across hash table, client list, requests, and transports. Connection association upgrades locks and must avoid races with session destruction. `session_id_value_hash_func()` does pointer arithmetic on `void *` as a compiler extension. Maximum connection limit logs but does not stop adding in this code path. Callback GSS security parameters are logged as unsupported during free.

Test signals: create/get/delete session, duplicate insertion rejection, refcount-to-zero cleanup, session id uniqueness under concurrency, connection association with existing and new xprts, disallowed association failure, remove non-bound connection during destroy race, backchannel destroy for matching/nonmatching xprt, destroy-all-connections behavior, and SAL metric updates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/nfs41_session_id.c -->
