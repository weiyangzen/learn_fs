# Research: subset-b-007670

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/layout.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/layout.c

## Purpose
`layout.c` is the central PTLRPC request-layout registry. It defines the `RMF_*` request message fields, the `RQF_*` request formats that combine client and server field lists, and the `req_capsule` helpers that pack, size, grow, shrink, access, swab, and dump Lustre request/reply buffers. Almost every Lustre RPC path depends on these exported symbols to agree on wire field order, variable-length field sizing, byte swapping, and reply sizing.

## Important APIs, types, and data
The local `struct req_msg_field` records field name, flags, fixed or variable size, optional swabber, optional length-aware swabber, optional dumper, and a computed per-format/per-location offset table. `enum rmf_flags` distinguishes strings, no-size-check fields, structure arrays, and minimum-size/versioned fields. `struct req_format` names an RPC format and stores field arrays for `RCL_CLIENT` and `RCL_SERVER`.

The file exports many protocol descriptors: metadata fields such as `RMF_MDT_BODY`, `RMF_REC_REINT`, `RMF_MDT_MD`, security fields such as `RMF_SELINUX_POL`, OST fields such as `RMF_OST_BODY`, `RMF_OBD_IOOBJ`, `RMF_NIOBUF_REMOTE`, llog fields such as `RMF_LLOGD_BODY` and `RMF_LLOG_LOG_HDR`, HSM/LFSCK/batch-update fields, and optional server-only update fields under `CONFIG_LUSTRE_FS_SERVER`.

The `RQF_*` objects map operation families to field lists: MGS, FLD/SEQ, MDS get/reint/HSM/batch, LDLM lock/intent, OST object and BRW operations, llog-origin operations, LFSCK, and batch update. The top-level `req_formats[]` array is the authoritative registry used by `req_layout_init()`.

Key exported helpers include `req_layout_init()`, `req_capsule_init()`, `req_capsule_set()`, `req_capsule_server_pack()`, `req_capsule_client_pack()`, `req_capsule_client_get()`, `req_capsule_server_get()`, sized/swabbed variants, `req_capsule_set_size()`, `req_capsule_msg_size()`, `req_capsule_fmt_size()`, `req_capsule_extend()`, `req_capsule_shrink()`, `req_capsule_server_grow()`, `req_check_sepol()`, `req_capsule_subreq_init()`, and `req_capsule_set_replen()`.

## Control flow
Initialization walks every registered `RQF`, assigns `rf_idx`, validates limits and array element sizing, and fills each field's offset table with one-based offsets so zero means "not present". Request construction initializes a capsule, assigns a format, sets explicit sizes for variable fields, fills missing fixed sizes with `req_capsule_filled_sizes()`, then packs either a normal PTLRPC request/reply through `lustre_pack_request()`/`lustre_pack_reply()` or a batch sub-request through `lustre_init_msg_v2()`.

Field access flows through `__req_capsule_get()`: it validates the format, resolves the field offset from the precomputed table, chooses `lustre_msg_string()` for string fields or `lustre_msg_buf()` for other fields, computes the expected length from flags and `rc_area`, validates structure-array and minimum-size constraints, then calls `swabber_dumper_helper()`. The swabber helper handles whole fields, structure arrays, and length-aware versioned fields, marks each field swabbed once, and optionally emits protocol dumps.

Format mutation is deliberately narrow. `req_capsule_set()` allows only setting the same format once initialized; `req_capsule_extend()` permits changing to a super-format after checking that existing fields are preserved or are explicitly opaque. `req_capsule_shrink()` reduces an already packed buffer and updates reply lengths. `req_capsule_server_grow()` is the complex path: it may grow in place if the reply-state buffer has enough room, or repack into a larger reply state, copy previous buffers, grow the target field, transfer "difficult reply" lock accounting, and release the old reply state. Batch sub-request growth uses the parent `RMF_BUT_REPLY` field and enforces `BUT_MAXREPSIZE`.

`req_check_sepol()` is compiled for server builds and compares an optional client `RMF_SELINUX_POL` string with the export's nodemap policy, returning `-EACCES` on mismatch. `req_capsule_set_replen()` computes the expected reply size for full requests or stores the sub-request reply size in `lm_repsize`.

## State and persistence behavior
This file does not persist data directly. Its state is process-global protocol metadata: exported `RMF_*`/`RQF_*` objects and the offset tables populated by `req_layout_init()`. Per-request state lives in `struct req_capsule` (`rc_fmt`, `rc_area`, request/reply message pointers, and location) and in associated `ptlrpc_request` fields such as `rq_reqlen`, `rq_replen`, and `rq_reply_state`. Since field offsets and formats define the on-wire protocol, changes here are compatibility-sensitive even though no on-disk store is touched.

## Dependencies and integration points
The code depends on Lustre message packing (`lustre_pack_request`, `lustre_pack_reply`, `lustre_msg_*`), byte-swapping and dumping helpers from `lustre_swab.h` and `llog_swab.h`, PTLRPC request structures from `lustre_req_layout.h`, nodemap exports for SELinux policy checks, and batch update constants like `BUT_MAXREPSIZE`. It is consumed by client/server handlers throughout MDS, MDT, OST, LDLM, LLOG, LFSCK, OSP, and batch RPC paths. `llog_client.c` and `llog_server.c` in this subset directly depend on the llog `RQF_*`/`RMF_*` definitions.

## Risks and edge cases
The main risk is wire compatibility: field order, fixed sizes, flags, swabbers, and version guards must match peers. Variable-sized fields require callers to set sizes before packing; missing `req_capsule_set_size()` on server variable replies trips assertions or yields wrong reply lengths. `RMF_F_NO_SIZE_CHECK` is necessary for interoperability in several places but weakens validation. Structure-array fields can fail if buffer lengths are not exact multiples of element sizes. `req_capsule_server_grow()` is high risk because it reallocates reply state while preserving difficult-reply locks and batch sub-request offsets. The FLD_READ comment documents an intentional little-endian/flexible-array interoperability compromise. `req_check_sepol()` depends on correct nodemap lifetime and only runs for non-subrequests.

## Test signals
Useful validation includes layout initialization assertions, build coverage for both server and non-server configs, mixed-version protocol tests around `RMF_SWAP_LAYOUTS` and guarded MGS fields, RPC pack/unpack tests for every `RQF_*` family, big-endian or forced-swab tests for fixed, array, and length-aware fields, batch RPC tests that force `RMF_BUT_REPLY` growth and `BUT_MAXREPSIZE`, MDT paths that grow `RMF_MDT_MD`, `RMF_ACL`, or `RMF_NIOBUF_INLINE`, and nodemap SELinux policy tests covering missing, matching, and mismatching policies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/layout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/llog_client.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/llog_client.c

## Purpose
`llog_client.c` implements the client-side remote llog operations table. It adapts generic `llog_operations` callbacks to PTLRPC requests so a client can open an existing remote log, fetch next or previous blocks, and read the log header from a server-side llog origin.

## Important APIs, types, and functions
The exported object is `llog_client_ops`, with callbacks `llog_client_open`, `llog_client_next_block`, `llog_client_prev_block`, `llog_client_read_header`, and `llog_client_close`. The helper `llog_client_entry()` safely gets a referenced `obd_import` from `llog_ctxt::loc_imp` under `loc_mutex`; `llog_client_exit()` releases it and warns if the context import changed during the RPC.

Each RPC uses layout descriptors from `layout.c`: `RQF_LLOG_ORIGIN_HANDLE_CREATE`, `RQF_LLOG_ORIGIN_HANDLE_NEXT_BLOCK`, `RQF_LLOG_ORIGIN_HANDLE_PREV_BLOCK`, and `RQF_LLOG_ORIGIN_HANDLE_READ_HEADER`, with fields `RMF_LLOGD_BODY`, `RMF_NAME`, `RMF_MDT_BODY`, `RMF_EADATA`, and `RMF_LLOG_LOG_HDR`.

## Control flow
Open obtains the import, rejects `LLOG_OPEN_NEW` by assertion because remote creation is unsupported, allocates a create/open request, sets the variable name length even when no name exists so later fields are positioned correctly, packs the request, fills `llogd_body` with optional logid and context index (`loc_idx - 1`), copies the name, calls `do_pack_body()`, waits, and copies the returned logid to the handle.

`llog_client_next_block()` and `llog_client_prev_block()` allocate packed requests, fill `llogd_body` with log id, context index, header flags, block index, requested length, and for next-block the current saved index and offset. They set server `RMF_EADATA` size to the requested buffer length, set reply length, wait for the RPC, copy returned cursor state, then copy the returned data buffer into the caller's buffer. The next-block path has special handling for `-EBADR` and `-EIO`: those codes are accepted as remote EOF-like status only when the reply message status also carries the same value; otherwise the transport error is returned directly.

`llog_client_read_header()` requests the header, validates that the returned header length fits in `lgh_hdr_size`, copies it, updates `lgh_last_idx`, and checks header magic, tail length equality, power-of-two length, minimum chunk size, and maximum handle header size. Close is a no-op because servers close the local file after each remote llog RPC.

## State and persistence behavior
The file does not store persistent data directly. It reads persistent llog contents through server RPCs. It updates in-memory `llog_handle` state: `lgh_id`, `lgh_ctxt`, `lgh_hdr`, `lgh_last_idx`, cursor index, and cursor offset. Import references are acquired per operation and released before return.

## Dependencies and integration points
It depends on `obd_class` import lifetime helpers, PTLRPC allocation/packing/waiting, and generic llog interfaces. Its server peers are implemented in `llog_server.c`; its import is initialized by `llog_net.c`. The llog request/reply layouts come from `layout.c`.

## Risks and edge cases
The code assumes caller-provided buffers are at least `len` bytes and copies exactly `len` from `RMF_EADATA`; server-side lengths therefore must match client expectations. `body->lgd_ctxt_idx = loc_idx - 1` relies on consistent one-based context indexing in the local context and zero-based RPC field. EOF detection is subtle because `-EBADR` and `-EIO` can mean either remote end-of-log or lower-layer failure. Header validation catches corrupt or incompatible logs, but only after copying the advertised header length.

## Test signals
Tests should cover open by logid and by name, absent import retry behavior, next-block cursor advancement and EOF handling for both old `-EIO` and newer `-EBADR` servers, previous-block reads, corrupted header magic and invalid header sizes, import replacement during an operation, and no-op close semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/llog_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/llog_net.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/llog_net.c

## Purpose
`llog_net.c` is a small connector for remote OST/MDS recovery logging. It binds an llog context to the client import used for remote llog RPCs, preserving the invariant that a context should not switch between unrelated imports.

## Important APIs, types, and functions
The only exported API is `llog_initiator_connect(struct llog_ctxt *ctxt)`. It reads `ctxt->loc_obd->u.cli.cl_import`, stores a referenced import in `ctxt->loc_imp`, and uses `ctxt->loc_mutex` for synchronization. It uses `class_import_get()` and `class_import_put()` to manage import references.

## Control flow
The function asserts that `ctxt` exists and that an existing `loc_imp`, if present, is already the same import as the current client import. Under the context mutex, it compares `loc_imp` with `new_imp`; if they differ, it drops the old reference, takes a reference to the new import, and assigns it. It returns success after updating or confirming the binding.

## State and persistence behavior
No persistent data is written. The durable effect is the in-memory `llog_ctxt::loc_imp` reference used by `llog_client.c` when issuing remote llog operations. The function deliberately preserves one import per context and asserts on unexpected import changes.

## Dependencies and integration points
It depends on Lustre OBD client state (`loc_obd->u.cli.cl_import`), llog context locking, and import reference helpers. `llog_client_entry()` later consumes the import set here, while recovery and target connection setup code call this function when establishing logging connectivity.

## Risks and edge cases
The strict assertion on changed imports can expose unexpected reconnect or failover behavior if callers try to reuse a context with a different import. The function assumes `loc_obd` and its client import are valid. Since it only updates in-memory state, missed calls leave `llog_client_entry()` returning `-EINVAL` and warning that recovery will retry.

## Test signals
Validation should cover first-time connection, repeated connection with the same import, reference count balance when replacing a null import, warning/retry behavior in `llog_client.c` when no import was set, and failover scenarios that prove contexts are rebuilt or updated without violating the same-import assertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/llog_net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/llog_server.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/llog_server.c

## Purpose
`llog_server.c` implements server-side handlers for remote llog-origin RPCs. It opens existing local logs on behalf of a client, reads blocks or headers, writes results into the PTLRPC reply capsule, and closes the llog handle after each operation.

## Important APIs, types, and functions
The handlers are `llog_origin_handle_open()`, `llog_origin_handle_next_block()`, `llog_origin_handle_prev_block()`, and `llog_origin_handle_read_header()`. The local helper `llog_origin_close()` dispatches to `llog_cat_close()` for catalog logs and `llog_close()` otherwise. The handlers consume `struct llogd_body`, `struct llog_ctxt`, `struct llog_handle`, and PTLRPC capsule fields defined in `layout.c`.

## Control flow
Open reads the client `RMF_LLOGD_BODY`, packs the reply, optionally treats a nonzero log object id as a logid, reads optional `RMF_NAME`, validates the context index against `LLOG_MAX_CTXTS`, gets the context from the export OBD, opens the existing log by id or name, writes the opened logid into the server body, closes the handle, and drops the context reference.

Next-block and previous-block follow a similar pattern: read body, pre-size server `RMF_EADATA` to `LLOG_MIN_CHUNK_SIZE`, pack the reply, validate/get context, open the log, initialize the handle with flags from the request, mirror the request body into the reply body, get the reply data buffer, and call `llog_next_block()` or `llog_prev_block()`. Next-block passes saved index, target index, current offset, and fixed chunk length so the callee can update cursor state in the reply body.

Read-header reads body, packs a reply containing `RMF_LLOG_LOG_HDR`, validates/get context, opens and initializes the log, copies the in-memory log header into the reply field, logs diagnostic details, then closes and releases.

## State and persistence behavior
The handlers do not create new logs and do not persist changes themselves. They read persistent llog objects through `llog_open()`, `llog_init_handle()`, and block/header readers. Each operation opens and closes a handle, so persistent file lifetime is short and request-scoped. Reply state contains returned logid, block cursor state, data buffers, or header bytes.

## Dependencies and integration points
The code depends on the target export and OBD (`req->rq_export->exp_obd`), service-thread environment (`rq_svc_thread->t_env`), llog context lookup and reference management, local llog open/init/read/close operations, and PTLRPC capsule packing/accessors. Its client peer is `llog_client.c`, and opcode names are surfaced in `lproc_ptlrpc.c`.

## Risks and edge cases
Context index validation is critical because the request carries a zero-based context id. The server always sizes data replies to `LLOG_MIN_CHUNK_SIZE`, while the client can request arbitrary `len`; callers must keep those expectations aligned. The failpoint `OBD_FAIL_MDS_LLOG_UMOUNT_RACE` intentionally exercises context/umount races. All paths must release contexts and close handles on errors. Since remote creation is unsupported, clients expecting create semantics will fail before this server path.

## Test signals
Tests should cover valid and invalid context ids, missing contexts, open by name and id, catalog versus plain log close behavior, next/previous block success and EOF/error propagation, header reads, failpoint-driven unmount races, and leak checks for context references and log handles on every error path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/llog_server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/lproc_ptlrpc.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/lproc_ptlrpc.c

## Purpose
`lproc_ptlrpc.c` provides PTLRPC observability and tunables through debugfs/sysfs/lprocfs-style interfaces. It maps opcodes to names, registers service and OBD statistics, exposes request-buffer/thread/NRS controls, prints request history and timeouts, implements ping/import recovery controls, and publishes PTLRPC PM-QoS tunables.

## Important APIs, types, and functions
Opcode translation is handled by `ll_opcode2str()`, `ll_str2opcode()`, and `ll_eopcode2str()` over `ll_rpc_opcode_table` and `ll_eopcode_table`. Registration helpers include `ptlrpc_ldebugfs_register()`, `ptlrpc_sysfs_register_service()`, `ptlrpc_sysfs_unregister_service()`, `ptlrpc_ldebugfs_register_service()`, `ptlrpc_lprocfs_register_obd()`, `ptlrpc_lprocfs_unregister_service()`, `ptlrpc_lprocfs_unregister_obd()`, `ptlrpc_lproc_init()`, and `ptlrpc_lproc_fini()`.

Service tunable handlers expose `req_buffer_history_len`, `req_buffer_history_max`, `req_buffers_max`, `threads_min`, `threads_started`, `threads_max`, and `high_priority_ratio`. NRS visibility and control use `ptlrpc_lprocfs_nrs_policies_seq_show()` and `ptlrpc_lprocfs_nrs_policies_seq_write()`. Request history uses `struct ptlrpc_srh_iterator`, sequence/position conversion macros, and seq-file callbacks. Runtime actions include `ping_show()`, legacy `ping_store()`, `ldebugfs_import_seq_write()`, `pinger_recov_show()`, and `pinger_recov_store()`. PM-QoS module attributes mirror global variables defined in `niobuf.c`.

## Control flow
Stats registration allocates a counter array sized for extra counters plus Lustre opcodes, initializes global request counters, initializes extra counters for enqueue subtypes and BRW byte totals, then initializes one latency counter per opcode name. Service debugfs registration creates per-service directories with `timeouts`, `nrs_policies`, and `req_history`; sysfs registration attaches a kobject with tunable attributes.

Write-side tunables parse user input, validate ranges, and update service fields under `srv_lock` or import locks. History size is capped by either half of max request buffers or a total-RAM-derived bound. Thread minimum/maximum values are normalized per CPT and constrained against `PTLRPC_NTHRS_INIT`, current limits, and current init counts.

NRS policy show serializes against core registration with `nrs_core.nrs_mutex`, aggregates policy state from all service partitions under `nrs_lock`, verifies policy name/argument/fallback consistency across partitions, sums queued/active counters, and emits YAML-like regular and high-priority sections. NRS writes parse a bounded command buffer, optional `reg`/`hp` queue token, and arguments, then call `ptlrpc_nrs_policy_control()` under the same mutex.

Request history uses a 64-bit seq-file position that rotates CPT bits into the high bits so seq-file incrementing does not corrupt the CPT portion of Lustre history sequence numbers. Start/next iterate service partitions, lock each partition mutex and spinlock, seek the next request by history sequence, and show prints stable fields that were set before handler parsing, then calls the service-specific request printer if present.

Ping obtains the import under `with_imp_locked()`, prepares a ping request, forces full import send state, waits, and drops the request. Import writes accept `connection=<nid>@...::instance`, compare optional instance numbers to avoid obsolete-target reconnects, and call `ptlrpc_recover_import()` when needed. Module init creates `/sys/.../ptlrpc` attributes for PM-QoS controls; fini removes them.

## State and persistence behavior
The file does not persist configuration across reboots. It mutates live in-memory service configuration (`srv_hist_nrqbds_cpt_max`, `srv_nrqbds_max`, `srv_nthrs_cpt_init`, `srv_nthrs_cpt_limit`, `srv_hpreq_ratio`), import flags (`IMPF_NO_PINGER_RECOVER`), recovery targets, and PM-QoS globals. It maintains registered debugfs/sysfs dentries, kobjects, statistics objects, and counters that are cleaned up by unregister/fini paths.

## Dependencies and integration points
It depends on Lustre lprocfs/debugfs helpers, PTLRPC service and import internals, NRS scheduler internals, OBD stats, kobject/sysfs APIs, seq-file APIs, and opcode definitions from Lustre protocol headers. `niobuf.c` reads OBD service stats for PM-QoS duration decisions and exports PM-QoS globals that this file tunes. `llog_*` opcodes from this subset are mapped in the opcode table for stats and history output.

## Risks and edge cases
Several reads intentionally race with live request processing and therefore only print fields considered initialized before parsing. The static `unknown_opcode` buffer in `ll_opcode2str()` is shared and not reentrant. Write handlers must keep range checks strict; bad history or thread limits can cause memory pressure or starve services. NRS policy aggregation assumes all service partitions have the same policy set and can return `-EINVAL` if registration changes are inconsistent despite mutex serialization. Request-history iteration depends on `sizeof(loff_t) == sizeof(__u64)` and on CPT-bit encoding remaining stable. Import write parsing is strict and user-facing; malformed connection strings return `-EINVAL`.

## Test signals
Useful tests include opcode/name round trips and unknown opcode formatting, service sysfs registration/unregistration lifetime, each tunable's range checks, NRS show/write with regular-only and high-priority services, concurrent policy registration while reading, request-history reads across multiple CPTs and culled entries, ping success/failure, import reconnect parsing with matching and obsolete instances, pinger recovery toggling, stats increments for normal RPCs and BRW byte counters, and PM-QoS attribute updates being reflected in `niobuf.c` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/lproc_ptlrpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/niobuf.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/niobuf.c

## Purpose
`niobuf.c` is the PTLRPC/LNet buffer transport layer. It binds memory descriptors for request, reply, and bulk data, sends RPCs and replies, registers passive client bulk buffers, starts active server bulk transfers, aborts/unregisters bulk operations, computes adaptive reply timeout metadata, and lowers CPU resume latency around in-flight RPCs when PM-QoS is enabled.

## Important APIs, types, and functions
Global PM-QoS tunables are `ptlrpc_enable_pmqos`, `ptlrpc_pmqos_latency_max_usec`, `ptlrpc_pmqos_default_duration_usec`, and `ptlrpc_pmqos_use_stats_for_duration`. Internal helpers include `ptl_send_buf()`, `mdunlink_iterate_helper()`, `ptlrpc_at_set_reply()`, and `kick_cpu_latency()`.

Server-side bulk APIs under `CONFIG_LUSTRE_FS_SERVER` are `ptlrpc_prep_bulk_exp()`, `ptlrpc_start_bulk_transfer()`, and `ptlrpc_abort_bulk()`. Client/passive bulk APIs are `ptlrpc_register_bulk()` and `ptlrpc_unregister_bulk()`. Reply APIs are `ptlrpc_send_reply()`, `ptlrpc_reply()`, `ptlrpc_send_error()`, and `ptlrpc_error()`. The outbound client send path is `ptl_send_rpc()`, and server request receive buffers are posted by `ptlrpc_register_rqbd()`.

## Control flow
`ptl_send_buf()` constructs an LNet MD for a contiguous buffer, optionally carries a bulk cookie, binds it, bumps `ptlrpc_pending`, and issues `LNetPut()`. If `LNetPut()` fails, it unlinks the MD so the normal callback path completes the failed send and still returns success to the caller.

Server bulk preparation creates a descriptor for an already received request, references the export, sets server mode, and installs `server_bulk_callback`. `ptlrpc_start_bulk_transfer()` derives self and peer NIDs from the request path, computes match bits and MD count, binds each MD, then starts `LNetPut()` for server-to-client bulk put sources or `LNetGet()` for server pulls. On mid-loop errors it adjusts reference counts, unlinks posted MDs, and relies on callbacks for completion. `ptlrpc_abort_bulk()` unlinks all MDs and waits in one-second intervals with long-timeout warnings until callbacks mark the descriptor inactive.

`ptlrpc_register_bulk()` is the client/passive side. It resets reused descriptor state, validates match bits, attaches match entries on the reply portal for each bulk MD, attaches MDs with GET or PUT permissions according to bulk type, and records registration state. Attach failures unlink any partial state, mark request status `-ENOMEM`, and clear `bd_registered`. `ptlrpc_unregister_bulk()` clears registration, optionally sets an async unlink deadline under failpoint control, unlinks MDs, moves the request to `RQ_PHASE_UNREG_BULK` when it must wait, and either returns immediately for async or blocks until callbacks finish.

`ptlrpc_send_reply()` validates the reply state, converts failed-OBD replies to `-ENODEV`, sets reply type/status/opcode, packs pool reply data and adaptive-timeout fields, gets a connection, wraps the reply with security, removes the request from export tracking to avoid resend races, stamps send time, and sends through `ptl_send_buf()` with ACK only for difficult replies that need it. Error helpers allocate a minimal reply if needed and preserve selected non-fatal status codes as regular replies.

`ptl_send_rpc()` is the client outbound path. It handles failpoints, failed imports, connecting imports with non-uptodate peers, message handle/type/connection-count/header flags, resend XID rules for `-EINPROGRESS`, match-bit setup for bulk or reply-matchbits peers, resend callbacks, memalloc context, security wrapping, bulk registration, reply buffer allocation and reply ME/MD attachment, request state flag resets, request reference for send callback, stats, deadline calculation, request send through `ptl_send_buf()`, PM-QoS kick, and cleanup for request-send, reply-attach, and bulk-registration failures.

`ptlrpc_register_rqbd()` posts service request buffers by attaching an LNet ME to the service request portal and an MD over `rqbd_buffer`, using local CPT insertion when available.

## State and persistence behavior
No data is persisted. The file mutates live network state: LNet match entries and memory descriptors, bulk descriptor refs/failure/registration fields, request phases and flags, reply states and refcounts, import/request timestamps and deadlines, service request-buffer refcounts, OBD stats counters, and per-CPU PM-QoS requests/deadlines. Cleanup depends on LNet callbacks to drop pending refs and wake waiters.

## Dependencies and integration points
It depends on LNet APIs (`LNetMDBind`, `LNetPut`, `LNetGet`, `LNetMEAttach`, `LNetMDAttach`, `LNetMDUnlink`), PTLRPC callbacks, security wrapping (`sptlrpc_*`), adaptive timeout helpers, OBD import/export state, lprocfs service stats, CPU latency QoS infrastructure, and failure-injection macros. It is called from PTLRPC client queueing, server reply paths, OST/MDT bulk handlers, and GSS upcall code for no-reply RPC sends.

## Risks and edge cases
The code is concurrency-sensitive because MD callbacks can fire while registration loops are still running. Refcount and phase transitions must stay balanced on all partial-failure paths. `ptl_send_buf()` intentionally returns success after `LNetPut()` failure if unlink/callback will complete the request, which can surprise callers. Bulk match-bit arithmetic must stay aligned between client and server or buffers will not match. Async unregister can leave cleanup pending under deadlines. Reply sending must not lose difficult-reply lock accounting. PM-QoS code allocates per-CPU requests under locks and may return early on allocation failure, leaving later CPUs untouched. Failpoints cover many rare cleanup paths and should remain exercised.

## Test signals
Tests should cover client RPC send with and without replies, reply attach failure, bulk registration attach failure at different MD positions, server bulk put/get success and mid-loop failure, unregister sync and async paths, abort waits and long-unlink warnings, resend after `-EINPROGRESS` with new XID, failed OBD reply conversion, difficult reply ACK/no-ACK behavior, security wrap failures, request buffer posting failure, PM-QoS sysfs tuning effects, and failpoints named in this file (`OBD_FAIL_PTLRPC_*`, `OBD_FAIL_MDS_LLOG_UMOUNT_RACE` for related llog path).
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/niobuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_fileset_alt.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_fileset_alt.c

## Purpose
`nodemap_fileset_alt.c` manages alternative fileset mappings for Lustre nodemaps. It owns allocation, destruction, insertion, deletion, lookup, prefix matching, and memory resizing for `struct lu_fileset_alt` entries stored in a red-black tree keyed by fileset id.

## Important APIs, types, and functions
The exported API is `fileset_alt_init()`, `fileset_alt_create()`, `fileset_alt_destroy()`, `fileset_alt_destroy_tree()`, `fileset_alt_add()`, `fileset_alt_delete()`, `fileset_alt_search_id()`, `fileset_alt_search_path()`, `fileset_alt_path_exists()`, and `fileset_alt_resize()`. The local helper `get_first_free_id()` finds the lowest unused nonzero id, and `compare_by_id()` adapts id lookup to `rb_find()`.

Entries are `struct lu_fileset_alt` objects with `nfa_path`, `nfa_path_size`, `nfa_id`, `nfa_ro`, and `nfa_rb`. The containing nodemap stores `nm_fileset_alt` and `nm_fileset_alt_sz`; locking is external via `nm_fileset_alt_lock` in callers.

## Control flow
Creation allocates the struct, records the requested path buffer size, initializes id to zero and read-only false, then allocates the path buffer. `fileset_alt_create()` sizes the buffer to `strlen(path) + 1`, copies the path, and sets read-only state.

Insertion assigns the first free id when `nfa_id` is zero, rejects ids greater than `LUSTRE_NODEMAP_FILESET_NUM_MAX - 1`, walks the rb tree by id, rejects duplicates with `-EEXIST`, links/rebalances the node, and increments `nm_fileset_alt_sz`. Deletion erases the rb node, decrements the size, destroys the entry, and returns the deleted id or `-EINVAL` for null input.

Exact id lookup uses `rb_find()`. Path lookup walks the whole tree because the tree is ordered by id, not path. Exact lookup uses `strcmp()`. Prefix lookup accepts entries where the searched path begins with the alternate fileset path and is followed by `/` or `\0`, and returns the longest matching prefix. Tree destruction postorder-frees every entry, resets the root, and clears the size. Resize walks entries, allocates a smaller path buffer when the preallocated size exceeds `strlen(path) + 1`, copies the path, frees the old buffer, and keeps the old allocation if shrinking fails.

## State and persistence behavior
The file only mutates in-memory nodemap fileset-alt trees. Persistence is handled by callers in nodemap storage/config code; this file is used when storage reads preallocated fragments and later shrinks them. The assigned `nfa_id` values are stable while entries remain in the tree, and id zero is reserved for the primary fileset outside this alternate tree.

## Dependencies and integration points
It depends on Linux rb-tree helpers, Lustre allocation macros, `lustre_net.h`, and `nodemap_internal.h`. Callers in `nodemap_handler.c`, `nodemap_storage.c`, and `nodemap_lproc.c` hold `nm_fileset_alt_lock`, validate nodemap policy constraints, persist mapping changes, and query prefix matches during path/fileset handling.

## Risks and edge cases
The implementation assumes callers provide locking; none of the exported functions take locks themselves. Path lookup is O(n), so many alternate filesets increase lookup cost, though the configured max bounds it. Prefix matching repeatedly calls `strlen(tmp->nfa_path)` and uses `strstr(fileset_path, tmp->nfa_path) == fileset_path`; this requires null-terminated validated paths and treats only slash or end-of-string as a boundary. `fileset_alt_delete()` returns an `int` but returns an unsigned id on success, so ids must remain within signed range; the configured max check supports that. Allocation failure in resize leaves the larger buffer in place and logs an error.

## Test signals
Tests should cover allocation failure cleanup, automatic id assignment with gaps, explicit id insertion, max-id rejection, duplicate id rejection, delete-null and delete-existing behavior, tree destruction size/root reset, exact path lookup, longest-prefix lookup with boundary checks, read-only flag preservation, resize shrink success and allocation failure, and caller-side locking around concurrent nodemap reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_fileset_alt.c -->
