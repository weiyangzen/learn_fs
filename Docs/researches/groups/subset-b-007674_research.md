# subset-b-007674 research

This grouped report covers the requested Lustre PTLRPC security core, configuration, context, garbage collection, debugfs, null policy, and plain policy source files. Each section is wrapped with the exact reconciliation markers required for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/sec.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/sec.c

Purpose: central shared implementation for Lustre secure PTLRPC. It registers security policies, maps configured wire flavors to policy modules, manages client and service security contexts, adapts imports and exports when security configuration changes, wraps and unwraps RPC messages and bulk descriptors, handles SELinux policy status caching, and initializes the security subsystem.

Important APIs/types/functions: `sptlrpc_register_policy()` and `sptlrpc_unregister_policy()` maintain the global `policies[]` table under `policy_lock`; `sptlrpc_wireflavor2policy()` resolves a wire flavor and can load `ptlrpc_gss` on demand; flavor helpers convert between names, base flavors, bulk settings, and flags; `sptlrpc_req_get_ctx()`, `sptlrpc_req_refresh_ctx()`, `sptlrpc_req_replace_dead_ctx()`, and `sptlrpc_req_set_flavor()` drive client context selection and per-request security state; `sptlrpc_import_sec_adapt()` creates or switches an import security object; `sptlrpc_target_export_check()` and `sptlrpc_target_update_exp_flavor()` enforce target-side flavor transitions; client/server wrapper APIs dispatch to policy ops; user descriptor and bulk checksum helpers provide common packet subformats; `sptlrpc_init()` and `sptlrpc_fini()` order GC, config, null/plain policies, and debugfs setup.

Control flow: client requests obtain the current import security with `import_sec_validate_get()`, look up a user or root context through policy `lookup_ctx`, derive request flags from opcode, allocate policy-specific buffers, optionally wait for or replace stale contexts, wrap bulk first, then sign/seal the RPC. Replies are unpacked, checked for matching policy, and verified/unsealed through the same context. Server receive starts by unpacking the outer message, resolving policy from `lm_secflvr`, calling policy `accept`, validating claimed source identity for GSS-authenticated traffic, checking export flavor authorization, allocating reply state, and authorizing the reply through policy `sops`. Flavor changes are deliberately tolerant: exports keep current, middle, and oldest flavors with expiration windows so in-flight and replayed RPCs can complete while reverse imports adapt.

State/persistence: process-global policy registration is protected by an rwlock. Each `ptlrpc_sec` has refcounts, flavor, import linkage, GC fields, optional cached SELinux policy state, and policy-owned context caches. Imports hold one installed `imp_sec` behind `imp_sec_lock` and an `imp_sec_expire` delayed-adapt timestamp. Exports keep current/old flavor snapshots and adaptation flags. Persistent on-disk state is not written here; configuration and SELinux state are in-memory reflections of MGS config logs or userspace helper/downcall data.

Dependencies/integration: depends on Lustre PTLRPC request/reply structures, OBD imports/exports/devices, LNet NIDs, request capsules, Lustre message packing, GSS error definitions, nodemap switching under server support, kernel crypto hash APIs, kernel module loading, RCU/kref for SELinux policy cache, and policy implementations from `sec_null.c`, `sec_plain.c`, and optional GSS modules. It integrates with `sec_config.c` for flavor selection, `sec_gc.c` for context cleanup, `sec_lproc.c` for observability/downcalls, and `ptlrpc_internal.h` declarations.

Risks/test signals: races around context replacement, request buffer switching, import teardown, and export flavor rollover are the main behavioral risks; many paths rely on refcount and list invariants enforced by `LASSERT`. Reply-offset handling for early replies, policy mismatch checks, user descriptor bounds, bulk checksum truncation, and `send_sepol` helper failures are protocol-sensitive. Existing comments and messages reference sanity-sec coverage for source spoofing; useful tests include config flavor changes during in-flight RPCs, failover context refresh, GSS `NO_CONTEXT` recovery, early reply checksum failure, bulk checksum send/receive fault injection, SELinux downcall caching, nodemap switch failures, and initialization unwind order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/sec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/sec_config.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/sec_config.c

Purpose: parses, stores, merges, and applies Lustre sptlrpc flavor configuration. It converts `conf_param` records into ordered rule sets, tracks per-filesystem and per-target rules from config logs, and lets clients and targets choose the active security flavor for a peer, direction, and network.

Important APIs/types/functions: `sptlrpc_part2name()` and `sptlrpc_target_sec_part()` map Lustre security participants; `sptlrpc_parse_flavor()` parses base flavors and the plain bulk hash syntax; `sptlrpc_parse_rule()` parses `network[.direction]=flavor`; `sptlrpc_rule_set_expand()`, `sptlrpc_rule_set_merge()`, `sptlrpc_rule_set_choose()`, and `sptlrpc_rule_set_extract()` manage ordered rule sets; `struct sptlrpc_conf` stores filesystem-wide rules and a target list of `struct sptlrpc_conf_tgt`; config log lifecycle hooks create, reset, mark-updated, and free per-filesystem configs; `sptlrpc_conf_choose_flavor()`, `sptlrpc_target_choose_flavor()`, `sptlrpc_conf_client_adapt()`, and `sptlrpc_conf_target_get_rules()` expose the resulting policy to runtime import/export code.

Control flow: a config record is validated as an `srpc.flavor` parameter, its target is resolved to a filesystem name or special `_mgs` scope, and the parsed rule is merged into either the filesystem rule set or a target-specific rule set. Merge order preserves specificity by network and direction, replacing matching rules or deleting them when the flavor is invalid. Runtime selection first tries target-specific rules, then filesystem rules, then falls back to `null`. After selection, `flavor_set_flags()` adds direction-derived flags such as root-only, user descriptors, and bulk protection. Client changes mark imports for delayed adaptation; target changes extract relevant rules and later update export flavor windows.

State/persistence: configuration lives in the process-global `sptlrpc_confs` list protected by `sptlrpc_conf_lock`. Each config tracks whether it came from MGS or a local target copy and whether it was modified during a log update. Rule arrays are heap allocated in slots of eight and freed on log stop or subsystem fini. The durable source is external Lustre config logs; this file maintains only the in-memory mirror.

Dependencies/integration: depends on Lustre config records, `lustre_cfg_string()`, `PARAM_SRPC_FLVR`, server-name and UUID helpers, LNet network parsing and NID checks, OBD device types, and flavor helpers from `sec.c`. It feeds `sptlrpc_import_sec_adapt()` on clients and `sptlrpc_target_update_exp_flavor()`/target export checking on servers through selected `struct sptlrpc_flavor` values and rule sets.

Risks/test signals: parsing mutates the input rule string in place, so callers must not reuse immutable strings. Rule ordering and deletion semantics are subtle because broad wildcard rules terminate searches for more-specific inserts. Loopback NIDs intentionally skip enforcement. Bad target names, missing config logs, invalid hash algorithms, or oversized filesystem names can silently fall back or fail depending on path. Tests should cover flavor string variants, invalid syntax, wildcard versus specific network/direction precedence, delete rules, target override precedence, log begin/end local-copy reset, client delayed adaptation, and target rule extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/sec_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/sec_ctx.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/sec_ctx.c

Purpose: provides small helpers for temporarily switching the current task filesystem context to an OBD run context and restoring it later. This is used by server-side or storage-facing code paths that need relative filesystem operations to run under a Lustre object device root.

Important APIs/types/functions: `ll_set_fs_pwd()` replaces `fs_struct->pwd` under the fs seqlock while taking and dropping path references; `push_ctxt()` saves the current pwd, mount, and umask into `struct lvfs_run_ctxt`, sets umask to zero, and switches to `new_ctx`; `pop_ctxt()` validates that the task is still in the pushed context, restores the saved pwd and umask, and releases references. Both public functions are exported.

Control flow: callers allocate a save context, call `push_ctxt(save, new_ctx)` before doing filesystem work, and must call `pop_ctxt(save, new_ctx)` afterward. If `new_ctx->dt` is non-NULL, both operations are no-ops because an underlying dt_device path does not need VFS cwd switching.

State/persistence: only per-task transient state is changed: `current->fs->pwd` and `current->fs->umask`. References are acquired with `dget()`/`mntget()` and released with `dput()`/`mntput()`. No persistent data is stored.

Dependencies/integration: depends on kernel VFS path/mount APIs, `fs_write_seqlock()`, Lustre `lvfs_run_ctxt`, OBD context magic checks, and the task's shared `fs_struct`. It is not policy-specific despite living near PTLRPC security code.

Risks/test signals: every successful push must be paired with pop on the same task, otherwise cwd or umask leaks into later work. Assertions catch mismatched context and missing references only in debug/assert-enabled builds. Tests or fault injection should cover push/pop balance, no-op dt path behavior, umask restoration, and error unwinds that occur between push and pop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/sec_ctx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/sec_gc.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/sec_gc.c

Purpose: implements asynchronous garbage collection for PTLRPC security contexts and policy-owned security objects. It lets policy code hand off contexts that must be released in sleepable context and periodically invokes per-policy context cache GC.

Important APIs/types/functions: `sptlrpc_gc_add_sec()` inserts a `ptlrpc_sec` with a policy `gc_ctx` operation and interval into the global sec GC list; `sptlrpc_gc_del_sec()` removes it and synchronizes with any in-progress scan; `sptlrpc_gc_add_ctx()` queues a client context for deferred release and wakes the worker; `sec_process_ctx_list()` drains deferred contexts; `sec_do_gc()` invokes policy `gc_ctx` when `ps_gc_next` expires; `sec_gc_main()` is the delayed work callback; `sptlrpc_gc_init()` schedules the worker and `sptlrpc_gc_fini()` cancels it.

Control flow: the delayed worker first drains the one-shot context handoff list, then iterates the registered security-object list under `sec_gc_mutex`. If a deletion is pending, it drops the mutex and restarts so `sptlrpc_gc_del_sec()` can complete quickly. After scanning it drains contexts again and reschedules itself for the fixed 30-minute interval. Direct context handoff uses `mod_delayed_work(..., 0)` to run promptly rather than waiting for the interval.

State/persistence: global state consists of `sec_gc_list`, `sec_gc_ctx_list`, their spinlocks, `sec_gc_mutex`, the delayed work item, and `sec_gc_wait_del`. It persists only for the module lifetime. Contexts placed on the GC list are expected to hold a single reference that the worker drops with `sptlrpc_cli_ctx_put(ctx, 1)`.

Dependencies/integration: depends on kernel workqueues, Lustre context refcounting from `sec.c`, policy `gc_ctx` callbacks, `ps_gc_interval`/`ps_gc_next` fields in `ptlrpc_sec`, and exported context release APIs. Policies with zero GC interval, such as null/plain in this subset, do not register periodic GC.

Risks/test signals: deletion synchronization is correctness-critical because a sec could otherwise be destroyed while the worker is iterating it. The worker uses a fixed interval rather than the nearest expiry, so GC may be delayed up to 30 minutes. Tests should exercise add/delete while GC is running, queued context release, fini cancellation, refcount expectations, and a policy `gc_ctx` callback that advances `ps_gc_next`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/sec_gc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/sec_lproc.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/sec_lproc.c

Purpose: exposes sptlrpc state through Lustre debugfs/lproc-style files and accepts SELinux policy downcalls from userspace. It gives operators visibility into active client security flavor/context state and a channel for `l_getsepol` results to update cached SELinux policy status.

Important APIs/types/functions: `sptlrpc_info_lprocfs_seq_show()` prints current import security flavor, flags, id, refcount, context count, and GC timing; `sptlrpc_ctxs_lprocfs_seq_show()` delegates context display to the active policy; `sptlrpc_sepol_update_needed()` and `sptlrpc_sepol_update()` maintain an RCU/kref cached `struct sptlrpc_sepol`; `ldebugfs_sptlrpc_sepol_seq_write()` validates `sepol_downcall_data` from userspace and updates the cache; `lprocfs_sptlrpc_sepol_seq_show()` displays cached mtime and policy string; `sptlrpc_lprocfs_cliobd_attach()` creates per-client files; `sptlrpc_lproc_init()` and `sptlrpc_lproc_fini()` create and remove the global `sptlrpc` debugfs directory and kobject.

Control flow: client OBD attach creates `srpc_info`, `srpc_contexts`, and write-only `srpc_sepol`. Reads take an import security reference, print fields or call policy display, then drop the reference. A userspace sepol downcall is copied into a bounded kernel buffer, checked for magic, length, and count consistency, then installed on the current import security if its mtime differs. Older downcall layout support is retained behind a Lustre version check. Global init creates aggregate page-pool debug entries and a sysfs kobject.

State/persistence: per-import SELinux policy status is stored in `imp_sec->ps_sepol` as an RCU pointer with kref lifetime and freed through `sptlrpc_sepol_put()` in `sec.c`. Debugfs files expose live in-memory state only. No on-disk persistence is performed here.

Dependencies/integration: integrates with Lustre debugfs helpers, sequence file APIs, OBD client imports, policy display callbacks, kernel user-copy APIs, RCU, kref, and the SELinux helper path in `sec.c`. Global symbols `sptlrpc_debugfs_dir` and `sptlrpc_kobj` are exported for other security code.

Risks/test signals: user input validation is security-sensitive; bad magic, truncated payloads, zero or oversized policy lengths, and stale imports must return errors without updating the cache. The `lprocfs_sptlrpc_sepol_seq_show()` path references `imp->imp_sec` while also holding an import-sec reference and should be tested across import teardown. Tests should cover debugfs attach filtering by OBD type, sepol update/no-update by mtime, old/new downcall formats where supported, and cleanup removing all debugfs entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/sec_lproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/sec_null.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/sec_null.c

Purpose: implements the `null` PTLRPC security policy. This policy performs no cryptographic protection, uses embedded Lustre messages directly, and provides the baseline unauthenticated security flavor while still fitting the shared policy/context/buffer API.

Important APIs/types/functions: global singletons `null_policy`, `null_sec`, `null_cli_ctx`, and `null_svc_ctx` represent all null-security state; `null_ctx_sign()` sets `lm_secflvr` and encodes the source security participant into high bits; `null_ctx_verify()` exposes replies directly and validates early-reply checksum; `null_create_sec()`, `null_kill_sec()`, and `null_lookup_ctx()` implement singleton refcount semantics; request/reply buffer ops allocate, free, and enlarge unwrapped Lustre messages; server ops `null_accept()`, `null_alloc_rs()`, `null_authorize()`, and `null_free_rs()` accept direct messages and prepare direct replies; `sptlrpc_null_init()` registers the policy after `null_init_internal()` initializes singletons.

Control flow: on the client, every lookup returns the eternal cached `null_cli_ctx`. Signing writes `SPTLRPC_FLVR_NULL`, optionally encodes client/target source part, and marks the full request buffer as sendable data. Server accept rejects non-null flavors, decodes source part, points `rq_reqmsg` at `rq_reqbuf`, and installs the singleton service context. Reply allocation places `ptlrpc_reply_state` before the Lustre reply buffer, and authorization sets the null flavor plus the reply offset used for adaptive-timeout early reply support.

State/persistence: the null policy is process-global and never truly destroys `null_sec`; all imports share one security object and one eternal client context. Refcounts still balance imports and requests, but there is no per-user, per-import, or persistent credential state. Request/reply buffers are transient heap or preallocated pool memory.

Dependencies/integration: depends on Lustre message packing/checksum helpers, OBD allocation macros, shared sptlrpc policy registration in `sec.c`, and PTLRPC request/reply state layout. It supplies `ptlrpc_sec_cops`, `ptlrpc_sec_sops`, and `ptlrpc_ctx_ops` consumed by generic wrapper code.

Risks/test signals: because null security trusts the message body, authorization depends entirely on higher layers and network trust. The high-bit source-part encoding is described as temporary and shares the flavor field namespace. Buffer enlargement updates pointers under `imp_lock` to avoid replay-list races. Tests should cover singleton refcount balance across multiple imports, direct buffer allocation/free including pool-backed requests, request enlargement, source-part encode/decode, early reply checksum mismatch, and invalid non-null flavor rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/sec_null.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/sec_plain.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/sec_plain.c

Purpose: implements the `plain` PTLRPC security policy. It wraps the real Lustre message in a fixed four-segment outer message, can carry a user descriptor, and can protect bulk transfers with configurable hash checksums, but it does not encrypt RPC bodies.

Important APIs/types/functions: `struct plain_sec` extends `ptlrpc_sec` with a rwlock-protected single cached client context; the fixed layout uses `PLAIN_PACK_HDR_OFF`, `PLAIN_PACK_MSG_OFF`, `PLAIN_PACK_USER_OFF`, and `PLAIN_PACK_BULK_OFF`; `struct plain_header` carries version, flags, source part, and bulk hash algorithm; `plain_generate_bulk_csum()` and `plain_verify_bulk_csum()` use `sptlrpc_get_bulk_checksum()`; `plain_ctx_sign()`/`plain_ctx_verify()` wrap and unwrap client messages; `plain_cli_wrap_bulk()`/`plain_cli_unwrap_bulk()` handle client-side bulk tokens; `plain_accept()`, `plain_alloc_rs()`, `plain_authorize()`, `plain_svc_unwrap_bulk()`, and `plain_svc_wrap_bulk()` implement service-side processing; `sptlrpc_plain_init()` computes early-reply offset and registers `plain_policy`.

Control flow: client request buffer allocation builds an outer `lustre_msg_v2` with header, embedded message, optional user descriptor, and optional bulk descriptor. Signing fills the plain header and flags after the embedded message is prepared. If this is a bulk write, the client computes and sends a checksum token; for bulk reads, the server computes the reply token and the client verifies it after data transfer. Server accept validates flavor base and bulk type, header version, hash algorithm, optional user descriptor bounds, and optional bulk descriptor before exposing the embedded request. Reply authorization wraps the embedded reply in the same fixed layout and sets early-reply offset when needed.

State/persistence: each plain security object is per import and owns at most one cached context, regardless of user, with refcounts tying context lifetime to `ps_refcount` and `ps_nctx`. Reverse securities preinstall the context during creation. No durable credential state is stored; user credentials are serialized into each request when `PTLRPC_SEC_FL_UDESC` is set. `plain_at_offset` is global runtime state derived from `lustre_msg_early_size`.

Dependencies/integration: depends on shared flavor parsing and flags from `sec_config.c`, generic context and buffer dispatch from `sec.c`, Lustre message v2 packing, user descriptor helpers, bulk descriptor validation, kernel page mapping for checksum fault injection, and OBD failure injection points `OBD_FAIL_OSC_CHECKSUM_SEND` and `OBD_FAIL_OSC_CHECKSUM_RECEIVE`.

Risks/test signals: plain provides integrity for selected bulk data but no confidentiality and no strong RPC-body authentication. Fixed segment assumptions are protocol-sensitive: wrong bufcount, header version, user descriptor length, bulk flags, or hash algorithm must fail closed. `plain_cli_unwrap_bulk()` adjusts iov lengths to transferred bytes for bulk reads, so short-transfer handling matters. Tests should cover request/reply wrapping with and without user descriptors, all supported bulk hash modes including null hash, checksum mismatch paths on client and server, early reply checksum validation, reverse-sec context installation, context cache flush-all behavior, request enlargement preserving embedded and wrapper messages, and invalid flavor/base/bulk-type rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/sec_plain.c -->
