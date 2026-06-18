# subset-b-007673 research

This grouped report covers the requested Lustre PTLRPC scheduler, wire-packing, pinger, daemon, recovery, and internal interface files. Each file section is wrapped with the exact reconciliation markers and preserves the source path as the section title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nrs_tbf.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/nrs_tbf.c

Purpose: implements the server-side Network Request Scheduler token bucket filter policy named `tbf`. It classifies requests by configurable key fields, assigns each class to the newest matching rate-limit rule, and dispatches queued requests only when the class has tokens.

Important APIs/types/functions: exports `nrs_conf_tbf` under server builds through `ptlrpc_internal.h`. Core policy hooks are `nrs_tbf_start()`, `nrs_tbf_stop()`, `nrs_tbf_ctl()`, `nrs_tbf_res_get()`, `nrs_tbf_res_put()`, `nrs_tbf_req_get()`, `nrs_tbf_req_add()`, `nrs_tbf_req_del()`, and `nrs_tbf_req_stop()`. Internal state centers on `nrs_tbf_head`, `nrs_tbf_client`, `nrs_tbf_rule`, `nrs_tbf_cmd`, conjunction/expression condition lists, an `rhashtable` of client classes, an LRU of idle classes, a `binheap` ordered by deadline, and an `hrtimer`.

Control flow: policy start parses the optional type string such as generic or `nid+jobid+uid`, builds the heap/hash/LRU state, and installs the default `*` rule with `tbf_rate` and `tbf_depth`. For every request, `nrs_tbf_res_get()` derives a `nrs_tbf_key` from the request message, reuses or allocates a class, and refreshes rule binding if the rule sequence or generation changed. Enqueue adds the request to the class FIFO and inserts the class into the deadline heap if needed. Dequeue reads the heap root, calculates elapsed tokens from `tc_check_time`, `tc_rpc_rate`, `tc_depth`, and realtime residual accounting, then either removes the first request or arms the hrtimer and marks the NRS head throttled. The timer clears throttling and wakes the service partition.

State/persistence: state is in-memory only. Rule definitions are mutable at runtime through debugfs `nrs_tbf_rule`; class mappings are cached in an RCU-protected hash and aged through an LRU bounded by `tbf_jobid_cache_size`. Rule references are `kref` managed; classes use `refcount_t`, RCU free, heap/LRU state bits, and per-rule linkage. No on-disk persistence exists, so rules disappear on module/service restart.

Dependencies/integration: integrates with the PTLRPC NRS core, service partition locks/wait queues, Lustre request capsules, `lustre_msg_get_*()` identity accessors from `pack_generic.c`, LNet NID parsing/matching, opcode name conversion, debugfs sequence operations, kernel hrtimers, RCU, rhashtable, and Lustre CPT allocation helpers.

Risks/test signals: token math is sensitive to zero or extreme rates, realtime residual handling, and hrtimer rearming. Rule parsing has strict syntax (`start name field={values} rate=N rank=... realtime=...`) and must reject invalid type fields, oversized names, unknown opcodes, malformed NIDs, empty ID lists, and illegal rates. Concurrency risks include class insertion races, LRU hit/delete races, rule stop while classes still reference a rule, and heap relocation under service locks. Tests should cover default policy startup, rule precedence/ranking/change/stop, type-specific classification, UID/GID/projid fallback paths for old clients, throttling and forced dequeue, HP and regular queues, debugfs read/write behavior, and cleanup with busy and idle classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nrs_tbf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/pack_generic.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/pack_generic.c

Purpose: provides generic PTLRPC wire-message packing, unpacking, buffer access, reply-state allocation, message metadata accessors, job/projid packing, asynchronous set-info request construction, byte-swapping for Lustre wire structures, and request debug dumping.

Important APIs/types/functions: message sizing and initialization are handled by `lustre_msg_hdr_size()`, `lustre_msg_size_v2()`, `lustre_msg_size()`, `lustre_packed_msg_size()`, and `lustre_init_msg_v2()`. Request/reply packing uses `lustre_pack_request()`, `lustre_pack_reply_v2()`, `lustre_pack_reply_flags()`, and `lustre_pack_reply()`. Buffer mutation uses `lustre_msg_buf()`, `lustre_msg_buflen()`, `lustre_shrink_msg()`, and `lustre_grow_msg()`. Metadata APIs include `lustre_msg_get/set_*()` helpers for flags, opc, status, transno, versions, timeouts, uid/gid, projid, jobid, checksums, and mbits. Swab coverage includes PTLRPC body, connect data, OST/MDT/MGS/LDLM/quota/layout/HSM/batch/lfsck/orphan/ladvise structures.

Control flow: new messages are always packed as `LUSTRE_MSG_MAGIC_V2`, with 8-byte-rounded header and segment lengths. Reply packing allocates a secure PTLRPC reply state, initializes callbacks and lists, attaches it to the request, then initializes the reply message. Unpack validates minimum header size, magic, buffer count, per-buffer lengths, total length, and swabbed magic; request/reply body unpack then swabs the PTLRPC body once and validates the PTLRPC version. Accessors locate the PTLRPC body segment and read or update fields in place.

State/persistence: the file manages transient in-memory message buffers and `ptlrpc_reply_state` lifetimes. `lustre_msg_early_size` is initialized during module startup. Optional `RS_DEBUG` keeps reply states on a debug LRU. No durable persistence occurs, but fields such as transno, last committed, jobid, uid/gid, and projid become part of the network protocol.

Dependencies/integration: used by client, server, pinger, recovery, TBF classification, security PTLRPC allocation/free paths, request capsule layout, LNet callbacks, CRC32 support, debug logging, and many Lustre subsystems whose wire structures must be endian-correct.

Risks/test signals: malformed message lengths can cause out-of-bounds access if validation regresses; grow/shrink callers must not retain stale segment pointers. Compatibility depends on not reading fields beyond older `ptlrpc_body_v2` unless flags/lengths prove they exist. Swab functions must track wire-structure evolution and avoid swapping opaque or string fields. Tests should cover V2 sizing/alignment, invalid magic/count/length rejection, swabbed request/reply bodies, string termination checks, uid/gid/projid/jobid packing, reply-state refcount/free invariants, checksums, and representative swab round trips for each exported wire helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/pack_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/pack_server.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/pack_server.c

Purpose: contains server-side byte-swapping helpers for object update request/reply formats and OUT update buffer headers.

Important APIs/types/functions: `lustre_swab_object_update()` swaps a single `object_update` and its variable parameter array. `lustre_swab_object_update_request()` swaps an `object_update_request`, optionally validates a supplied buffer length, and swaps each embedded update. `lustre_swab_object_update_reply()` swaps reply metadata, per-result lens, and fixed result fields. `lustre_swab_out_update_header()` and `lustre_swab_out_update_buffer()` are exported for OUT update transport structures.

Control flow: request swabbing first converts magic/count fields, then computes a conservative minimum size from the update count and parameter count when `len > 0`; overflow or malformed embedded update lookup returns an error before continuing. Reply swabbing computes the expected header/lens/result footprint, validates it against `len`, then iterates results and swabs each result header.

State/persistence: no retained state or persistence. The functions mutate caller-owned network buffers in place after receive or before local interpretation.

Dependencies/integration: depends on Lustre update helpers such as `object_update_request_get()`, `object_update_result_get()`, `object_update_param_size()`, LU FID swabbing, and the server-side update protocol used by target/OUT code.

Risks/test signals: size validation is intentionally minimal for variable-length parameters and must remain consistent with object update layout helpers. Tests should cover zero-length validation bypass, overflow detection, malformed update/result lookup returning `-EPROTO`, multi-update requests, multi-result replies, and exported OUT header/buffer swab behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/pack_server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/pers.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/pers.c

Purpose: fills an LNet memory descriptor for one PTLRPC bulk descriptor segment, including empty descriptors used to send only an LNet header.

Important APIs/types/functions: `ptlrpc_fill_bulk_md(struct lnet_md *md, struct ptlrpc_bulk_desc *desc, int mdidx)` is the only function. It maps `ptlrpc_bulk_desc` fields `bd_md_max_brw`, `bd_md_count`, `bd_iov_count`, `bd_mds_off`, `bd_is_rdma`, `bd_enc_vec`, and `bd_vec` into `lnet_md` fields.

Control flow: assertions verify the descriptor index and I/O vector count. If `mdidx` is beyond `bd_md_count`, the function emits a zero-length KIOV descriptor. Otherwise it sets GPU address options for RDMA bulk, computes the vector start and length from `bd_mds_off`, marks the MD as KIOV-backed, and points at encrypted or plain vectors depending on `bd_enc_vec`.

State/persistence: mutates only the passed `lnet_md`; no retained state. The descriptor references existing bulk vectors and does not own their lifetime.

Dependencies/integration: integrates PTLRPC bulk transfer descriptors with LNet memory descriptor posting. It is used by bulk I/O paths that split large BRW vectors across multiple network descriptors.

Risks/test signals: off-by-one errors in `bd_mds_off` or `bd_md_count` would post wrong page ranges. Tests should cover first/middle/last segment length calculation, zero-length header-only descriptors, encrypted vector selection, RDMA GPU option propagation, and assertion coverage for invalid `mdidx` or excessive vector counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/pers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/pinger.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/pinger.c

Purpose: manages periodic import pinging, reconnect triggering, ping suppression for pingless imports, idle disconnects, and the server-side ping evictor thread that evicts exports whose clients stop sending traffic.

Important APIs/types/functions: exported helpers include `ptlrpc_pinger_suppress_pings()`, `ptlrpc_obd_ping()`, `ptlrpc_pinger_ir_up()`, `ptlrpc_pinger_ir_down()`, `ptlrpc_pinger_add_import()`, `ptlrpc_pinger_del_import()`, `ping_evictor_wake()`, `ping_evictor_start()`, and `ping_evictor_stop()`. Internal flow uses `ptlrpc_prep_ping()`, `ptlrpc_ping()`, `ptlrpc_update_next_ping()`, `ptlrpc_pinger_process_import()`, delayed work `ping_work`, global `pinger_imports`, and ping evictor globals `pet_*`.

Control flow: pinger start creates a CPT-bound workqueue and schedules immediate processing. Each run scans registered imports under `pinger_mutex`, skips imports not due, starts recovery for disconnected active imports, avoids pings when recovery is disabled or the import is inactive, and sends async OBD_PING requests through `ptlrpcd_add_req()` when appropriate. It computes the nearest next wakeup from `imp_next_ping`. The evictor thread waits for OBDs queued by `ping_evictor_wake()`, scans sorted timed exports, logs and optionally dumps debug data, then calls `class_fail_export()` for expired clients.

State/persistence: maintains in-memory import list membership and refcounts, global IR state, optional module parameter `suppress_pings`, a delayed workqueue, and an evictor kthread/list. No durable state is written; import deadlines and next-ping times are runtime state.

Dependencies/integration: depends on PTLRPC request packing, async daemon queues, import state transitions, adaptive timeout data, OBD import/export events, LDLM namespace reference counts for idle detection, LNet NID logging, failure injection, and Lustre environment setup for the evictor.

Risks/test signals: races around import removal, pinger wakeup after stop, pingless suppression, and forced verification can affect recovery latency. Evictor correctness depends on export deadline ordering and reference handling while dropping OBD locks. Tests should cover pinger start/stop idempotence, adding/removing imports, disconnected import reconnect, idle disconnect, pingless IR suppression, force-next-verify behavior, async ping queuing, evictor wake/refcount lifecycle, and timed export eviction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/pinger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/ptlrpc_internal.h -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/ptlrpc_internal.h

Purpose: internal PTLRPC header that shares declarations and inline helpers across the PTLRPC implementation without exposing them as public Lustre APIs.

Important APIs/types/functions: declares global service/NRS state, NRS policy configs, `ptlrpcd_start()`, client request cache and resend helpers, portal init/fini, recovery helpers, lproc/sysfs service hooks, NRS core operations, pinger lifecycle, security PTLRPC module lifecycle, target/nodemap server module hooks, and pack helpers. Inline helpers include `nrs_svcpt_has_hp()`, `nrs_svc_has_hp()`, `nrs_svcpt2nrs()`, `nrs_pol2cptid()`, `nrs_pol2svc()`, `nrs_pol2svcpt()`, `nrs_pol2cptab()`, `nrs_request_resource()`, `nrs_request_policy()`, `ptlrpc_recoverable_error()`, request initialization helpers, connect/disconnect opcode predicates, and `do_pack_body()`.

Control flow: the header encodes common access patterns used by service code and NRS policies. Request initialization sets locks, refcounts, lists, wait queues, and role-specific flags before request objects enter client or server flows. NRS inline helpers translate between policy, service partition, CPT, and resource objects. `do_pack_body()` populates MDT body identity/capability fields for set-info style requests.

State/persistence: no direct storage beyond external declarations. The inline initializers establish in-memory request state contracts; misuse can leave list heads, wait queues, or refcounts uninitialized.

Dependencies/integration: ties together LDLM internals, heap support, Lustre compatibility headers, request capsules, PTLRPC daemon, pinger, security, NRS, lprocfs/sysfs, target, nodemap, client, service, and event modules.

Risks/test signals: changes here have broad blast radius because many C files rely on the exact initialization and inline accessor contracts. Tests should cover client/server request allocation paths, NRS policy resource selection, HP queue detection, connect/disconnect classification, recovery error predicates, and set-info body packing with current credentials.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/ptlrpc_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/ptlrpc_module.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/ptlrpc_module.c

Purpose: module lifecycle entry point for Lustre PTLRPC, lock management, security PTLRPC, NRS, and optional server target/nodemap support.

Important APIs/types/functions: `ptlrpc_init()` is registered with `late_initcall_sync()`, and `ptlrpc_exit()` is registered with `module_exit()`. Module metadata declares author, description, version, and GPL license.

Control flow: initialization asserts wire constants, initializes global mutexes and XID/early-message sizing, then brings up libcfs support, request layouts, high-resolution timeout support, request cache, portals, lprocfs, connection cache, pinger, LDLM, security PTLRPC, NRS, and optional target/nodemap modules. Each failure path unwinds previously initialized layers in reverse order. Exit tears down optional server modules, NRS, security, LDLM, pinger, portals, request cache, high-resolution support, connection/lprocfs, and request layouts.

State/persistence: establishes process-global kernel-module state and subsystem registrations. No durable state is written, but initialization order controls availability of all PTLRPC runtime services.

Dependencies/integration: depends on wire-test constants, `req_layout_init()`, portal/event setup, pinger, LDLM, SPTLRPC, NRS policy registration, target and nodemap modules under `CONFIG_LUSTRE_FS_SERVER`, and shared mutexes declared in `ptlrpc_internal.h`.

Risks/test signals: teardown order must mirror initialization, especially for pinger/portal/request-cache interactions and server-only modules. Tests should cover successful load/unload, injected failures at every init stage with leak-free unwinding, server and non-server builds, repeated load/unload, and verification that NRS and pinger globals are usable after startup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/ptlrpc_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/ptlrpcd.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/ptlrpcd.c

Purpose: implements PTLRPC daemon threads that own never-ending request sets for asynchronous RPCs, plus a dedicated recovery daemon so recovery can progress even if normal async threads are blocked.

Important APIs/types/functions: exported entry points are `ptlrpcd_wake()`, `ptlrpcd_add_req()`, `ptlrpcd_start()`, `ptlrpcd_stop()`, `ptlrpcd_free()`, `ptlrpcd_addref()`, and `ptlrpcd_decref()`. Internal state includes per-CPT `struct ptlrpcd`, per-thread `struct ptlrpcd_ctl`, global `ptlrpcds`, CPT index maps, recovery control `ptlrpcd_rcv`, and module parameters `max_ptlrpcds`, `ptlrpcd_bind_policy`, `ptlrpcd_per_cpt_max`, `ptlrpcd_partner_group_size`, and `ptlrpcd_cpts`.

Control flow: the first `ptlrpcd_addref()` initializes a recovery thread and per-CPT regular thread groups. Requests added through `ptlrpcd_add_req()` get job info packed into the request message, handle stale set membership, then route to the recovery thread if not in `LUSTRE_IMP_FULL` send state or to a round-robin CPT-local thread otherwise. Each daemon thread binds to its CPT, allocates a request set, initializes LU contexts, waits on the set waitqueue, moves new requests into active requests, runs `ptlrpc_check_set()`, frees completed requests, and can steal new work from partner threads in the same group. Stop marks flags, wakes the set, optionally aborts in-flight RPCs, drains, and frees set/partner state.

State/persistence: runtime-only thread, request-set, partner, CPT mapping, and user-reference state. `ptlrpcd_users` controls lazy startup/shutdown. No persistent storage exists.

Dependencies/integration: integrated with PTLRPC request sets, client resend/recovery, pinger async pings, events portal startup (`ptlrpcd_addref()`), LU context/session infrastructure, CPT binding/allocation, kernel kthreads, wait queues, and lprocfs-tuned module parameters.

Risks/test signals: daemon callbacks must not block on synchronous RPCs because they can deadlock recovery. Races around invalid request sets, stop/free ordering, partner stealing, and CPT subset parsing are high risk. Tests should cover addref/decref nesting, CPT pattern parsing, obsolete parameter translation, recovery-thread routing, normal round-robin routing, partner work stealing, forced stop aborts, request completion cleanup, and daemon behavior under timeout and LU environment refill failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/ptlrpcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/recover.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/recover.c

Purpose: coordinates client import recovery by selecting replay requests, resending in-flight requests after replay, waking delayed requests, reacting to abrupt disconnects, and activating/deactivating imports.

Important APIs/types/functions: key functions are `ptlrpc_replay_next()`, `ptlrpc_resend()`, `ptlrpc_wake_delayed()`, `ptlrpc_request_handle_notconn()`, `ptlrpc_set_import_active()`, `ptlrpc_import_in_recovery_disconnect()`, `ptlrpc_recover_import()`, and `ptlrpc_import_in_recovery()`. It manipulates import fields such as `imp_committed_list`, `imp_replay_list`, `imp_sending_list`, `imp_delayed_list`, `imp_replay_cursor`, `imp_last_replay_transno`, `imp_peer_committed_transno`, `imp_known_replied_xid`, and import flags.

Control flow: replay starts by freeing newly committed requests, then picks the next committed-open replay request or normal replay-list request whose transno exceeds the last replayed transno. Resend replay marks `MSG_RESENT`, ensures the request is on the unreplied list, updates known replied XID, clears the resend flag, and calls `ptlrpc_replay_req()`. After replay completes, `ptlrpc_resend()` walks the sending list in `LUSTRE_IMP_RECOVER` state and resends eligible timed-out or disallowed-during-replay requests. Not-connected handling marks the import disconnected, starts reconnect if allowed, and marks the failed request for resend. Explicit activation clears deactive state and invokes recovery; deactivation sets deactive state, sends events, and invalidates the import.

State/persistence: all state is in-memory import/request state. Recovery progress is tracked by transaction numbers, list cursors, flags, and wait queues; no durable log is written here.

Dependencies/integration: depends on import state transitions, OBD events, PTLRPC replay/resend/unreplied helpers, message flag accessors from `pack_generic.c`, request wait queues, pinger-driven reconnects, and administrative interfaces such as lctl activation/deactivation.

Risks/test signals: replay ordering and cursor handling are correctness-critical for recovery after reconnects. Races with repeated manual recovery, committed-list cleanup, and not-connected failures can cause duplicate or skipped requests if flags/lists are mishandled. Tests should cover committed-list replay before normal replay, resend replay of the last transno, unreplied-list repair, sending-list resend rules, delayed wakeups, import deactivation invalidation, activation wait timeout, new UUID connection priority, and recovery-state predicates with and without disconnect counted as recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/recover.c -->
