# subset-b-006284

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_rpc_xdr.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_rpc_xdr.c

Purpose: implements the XDR encoder and decoder for the kernel GSS proxy `accept_sec_context` RPC. It translates between the in-kernel RPCSEC_GSS server code and the gss-proxy protocol objects defined in `gss_rpc_xdr.h`, with special handling for large input tokens carried in pages and for Linux credential data returned as a gssproxy option.

Important APIs/types/functions: exported entry points are `gssx_enc_accept_sec_context()` and `gssx_dec_accept_sec_context()`. The helper layer covers primitive booleans and buffers (`gssx_enc_bool`, `gssx_dec_bool`, `gssx_enc_buffer`, `gssx_dec_buffer`), page-backed tokens (`gssx_enc_in_token`), option arrays (`gssx_enc_option`, `gssx_dec_option`, `dummy_*_opt_array`, `gssx_dec_option_array`), Linux credential decoding (`gssx_dec_linux_creds`), status/name/context/credential/channel-binding objects (`gssx_dec_status`, `gssx_enc_call_ctx`, `gssx_enc_name`, `gssx_dec_name`, `gssx_enc_cred`, `gssx_enc_ctx`, `gssx_dec_ctx`, `gssx_enc_cb`). The file uses `struct svc_cred`, `struct gssx_ctx`, `struct gssx_status`, and `struct gssp_in_token`.

Control flow: the request encoder writes call context first, always asking for `linux_lucid_v1` exported contexts and `linux_creds_v1` returned credentials. It conditionally emits the current context handle, credential handle, page-backed input token, optional channel bindings, delegation boolean, and empty options, then installs reply pages into the receive buffer with `xdr_inline_pages`. The response decoder allocates a scratch folio, decodes status, optional context handle, optional output token, rejects delegated credential handles because the kernel does not support them, and finally decodes options. Option decoding recognizes only `linux_creds_v1`; unrecognized options are consumed and discarded.

State and persistence behavior: this file persists no state. It allocates transient buffers for decoded protocol fields, a scratch folio for XDR decoding, optional `svc_cred` and group lists, and caller-provided reply pages. Error paths free partially decoded name, status, and context buffers before returning. Linux credential data from gssproxy is host-endian by protocol convention and is converted to kernel ids in `init_user_ns`.

Dependencies/integration points: integrated directly with `svcauth_gss.c` through `gss_rpc_upcall` data structures. It depends on SUNRPC XDR stream helpers, page/folio allocation, `groups_alloc` and `groups_sort`, and GSS proxy protocol constants in `gss_rpc_xdr.h`. The credentials it decodes are later imported into RPCSEC_GSS server context cache entries.

Risks: many decode helpers intentionally ignore unsupported fields by consuming them into dummy objects, so size accounting and XDR cursor movement must remain correct. `gssx_dec_option_array()` preallocates one option slot and one `svc_cred`; failures after partial credential parsing must not leak group info. `gssx_dec_linux_creds()` rejects oversized group vectors and invalid supplementary gids, but uid/gid mapping is fixed to `init_user_ns`. `gssx_enc_call_ctx()` does not check the first `xdr_reserve_space()` result before storing the option count, which is a small but real encode-path fragility. The response decoder rejects delegated credentials, so a gssproxy behavior change could break context setup.

Test signals: exercise gssproxy-backed RPCSEC_GSS context creation for success, continuation, and failure statuses; include large input tokens that span head and page data; verify returned Linux creds with zero, many, and invalid groups; inject short XDR buffers to hit `-ENOSPC`; and confirm unsupported delegated credentials fail. KUnit-style XDR tests should validate every optional `value_follows` branch and cleanup path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_rpc_xdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_rpc_xdr.h -->
# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_rpc_xdr.h

Purpose: declares the subset of the GSS proxy RPC/XDR model used by the kernel server-side RPCSEC_GSS implementation. It defines protocol-facing GSSX objects, the kernel-only page-backed input token carrier, argument/result structures for `accept_sec_context`, and size estimates used by SUNRPC procedure tables.

Important APIs/types/functions: aliases `gssx_buffer`, `utf8string`, and `gssx_OID` map to `struct xdr_netobj`. Protocol structures include `gssx_option`, `gssx_status`, `gssx_call_ctx`, `gssx_name`, `gssx_cred`, `gssx_ctx`, `gssx_cb`, `gssx_arg_accept_sec_context`, and `gssx_res_accept_sec_context`. The only implemented RPC procedures are declared as `gssx_enc_accept_sec_context()` and `gssx_dec_accept_sec_context()`; all other GSSX procedure encoder/decoder macros are set to `NULL`, with argument/result sizes set to zero.

Control flow: consumers build a `gssx_arg_accept_sec_context` with optional context and credential handles, a `gssp_in_token`, optional channel bindings, output pages, and option arrays. `gss_rpc_xdr.c` encodes it and decodes into `gssx_res_accept_sec_context`, filling status, optional returned context, optional output token, and returned options such as Linux credentials.

State and persistence behavior: the header owns no state. It defines memory ownership contracts implicitly: many fields are `xdr_netobj` buffers whose data is allocated or provided by callers, and `gssp_in_token` uses page refs for large input data. Size macros are compile-time estimates, not runtime limits for all objects.

Dependencies/integration points: depends on SUNRPC XDR, client, and socket transport headers. The constants `LUCID_OPTION`, `LUCID_VALUE`, `CREDS_OPTION`, and `CREDS_VALUE` define the negotiation strings shared with gssproxy. The header is consumed by both the GSS proxy upcall client and server auth code.

Risks: the structure set mirrors a protocol that is larger than the kernel-supported subset. Unsupported procedures are represented as `NULL`, so any procedure table wiring must not invoke them. The size macros are deliberately approximate and include arbitrary maximums for status strings, principals, tokens, and credentials; underestimation can produce buffer sizing failures, while overestimation increases allocation pressure.

Test signals: build coverage should include configurations with and without SUNRPC debug. Procedure table tests should confirm only `accept_sec_context` is wired. Runtime context creation through gssproxy is the main integration signal that size constants, optional handles, and credential option names match the userspace daemon.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_rpc_xdr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/svcauth_gss.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/svcauth_gss.c

Purpose: implements server-side RPCSEC_GSS authentication for SUNRPC services. It handles context initiation through either the legacy text upcall cache or synchronous gss-proxy, verifies incoming RPC_AUTH_GSS credentials and verifiers, manages replay windows, unwraps integrity/privacy request bodies, wraps replies, and registers per-network-namespace GSS auth caches and proc controls.

Important APIs/types/functions: externally visible functions include `svcauth_gss_flavor()`, `svcauth_gss_register_pseudoflavor()`, `gss_svc_init_net()`, `gss_svc_shutdown_net()`, `gss_svc_init()`, and `gss_svc_shutdown()`. The `auth_ops` implementation is `svcauthops_gss` with `accept`, `release`, `set_client`, `pseudoflavor`, and `domain_release`. Key structures are `struct gss_svc_data`, `struct rsi` for `auth.rpcsec.init`, `struct rsc` for `auth.rpcsec.context`, `struct gss_svc_seq_data`, and `struct gss_domain`.

Control flow: INIT and CONTINUE_INIT requests are decoded by `svcauth_gss_proc_init()`, which verifies a NULL verifier and dispatches to legacy `svcauth_gss_legacy_init()` or `svcauth_gss_proxy_init()` based on per-net `use_gss_proxy`. Legacy mode keys the `rsi_cache` by incoming handle and token, defers to userspace via the generic cache upcall, then encodes an init response. Proxy mode copies the input token into pages, calls `gssp_accept_sec_context_upcall()`, and on `GSS_S_COMPLETE` saves a new `rsc` context with a generated 64-bit handle. DATA and DESTROY requests search `rsc_cache`, verify the RPC header MIC and sequence number, then either unhash the context or prepare the request for service dispatch. Integrity and privacy requests are unwrapped before the service sees arguments; replies are wrapped in `svcauth_gss_release()`.

State and persistence behavior: state is per network namespace in `sunrpc_net`: `rsi_cache`, `rsc_cache`, `use_gss_proxy`, gssproxy client state, and proc entries. Context entries contain service credentials, imported mechanism context, replay window bits, and expiry. Cache entries are refcounted and RCU-freed; context destruction unhashes `rsc` entries and calls `gss_delete_sec_context`. Sequence replay state is in-memory only and protected by `sd_lock`. No on-disk persistence is performed.

Dependencies/integration points: depends on the generic SUNRPC cache framework, RPC service XDR helpers, auth domain registry, GSS mechanism registry/import/wrap/MIC operations, gssproxy upcall code, `netns.h` per-net storage, procfs, and rpcgss tracepoints. NFS server export selection integrates through `svcauth_unix_set_client()` and GSS pseudoflavors such as krb5, krb5i, and krb5p.

Risks: replay-window correctness is security-sensitive; off-by-one behavior in `gss_check_seq_num()` can cause false drops or replay acceptance. Deferred requests skip repeated MIC/unwrapping work via `rq_deferred`, so buffer state must be preserved accurately. Privacy wrapping moves tail data and adds slack in a single page; malformed sizes can lead to wrap failure. Proxy mode assumes returned creds are present on complete contexts and converts expiry relative to boottime. The proc knob for gssproxy can be set only once per namespace; races are guarded by `cmpxchg`, but operational ordering matters.

Test signals: run NFS server RPCSEC_GSS with legacy gssd and gssproxy modes; cover INIT, CONTINUE_INIT, DATA, DESTROY, bad verifier, bad credential version, wrong service, duplicate and too-old sequence numbers, integrity and privacy unwrap/wrap, deferred cache resolution, context expiry and flush, pseudoflavor registration duplication, and per-net namespace create/destroy. Tracepoints under `rpcgss` should show sequence, MIC, unwrap, wrap, and accept-upcall failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/svcauth_gss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/trace.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/trace.c

Purpose: instantiates the RPCSEC_GSS tracepoint definitions by defining `CREATE_TRACE_POINTS` and including `trace/events/rpcgss.h`. The file provides the compilation unit that emits tracepoint storage for GSS client/server authentication events.

Important APIs/types/functions: no callable functions are defined. The important interface is the generated tracepoint set from `<trace/events/rpcgss.h>`, which is used by files such as `svcauth_gss.c` to report MIC, wrap, unwrap, sequence-number, and upcall events.

Control flow: normal compilation includes SUNRPC and GSS headers, defines `CREATE_TRACE_POINTS`, and then includes the trace event header exactly once. At runtime, calls to `trace_rpcgss_*` in other files hit the generated tracepoint code if enabled.

State and persistence behavior: tracepoint state is managed by the kernel tracing subsystem. This file writes no persistent state and owns no runtime objects beyond generated tracepoint metadata.

Dependencies/integration points: depends on SUNRPC client, scheduler, service, transport, auth_gss, and GSS error headers so trace event prototypes can reference the right types. It integrates with ftrace/perf/BPF trace consumers.

Risks: the file must remain the single `CREATE_TRACE_POINTS` owner for `rpcgss.h`; duplicate definitions would break linking, while removing it would leave tracepoint references unresolved. Header dependency drift can break tracepoint type compilation.

Test signals: build with `CONFIG_SUNRPC` and tracing enabled, then verify `rpcgss` events appear under tracing event lists. Runtime RPCSEC_GSS tests should emit expected events when tracepoints are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_null.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/auth_null.c

Purpose: implements the AUTH_NULL client authentication flavor for SUNRPC. It supplies a singleton auth handle and singleton credential that marshal empty credential and verifier bodies and accept only empty NULL reply verifiers.

Important APIs/types/functions: exported operation table is `authnull_ops`; the static credential ops table is `null_credops`. Core functions are `nul_create`, `nul_destroy`, `nul_lookup_cred`, `nul_destroy_cred`, `nul_match`, `nul_marshal`, `nul_refresh`, and `nul_validate`. State objects are static `null_auth` and `null_cred`.

Control flow: client creation increments the singleton auth refcount and returns `null_auth`. Credential lookup returns a reference to `null_cred`; matching always succeeds. Request marshalling reserves four XDR words for AUTH_NULL credential and AUTH_NULL verifier, both with zero length. Refresh simply sets `RPCAUTH_CRED_UPTODATE`. Reply validation decodes two words and requires flavor `rpc_auth_null` and length zero.

State and persistence behavior: all state is process-global static kernel memory. There is no per-user credential allocation, no cache, and no persistent state. Destroy hooks are no-ops because the singleton objects are never dynamically freed.

Dependencies/integration points: plugs into the generic `rpcauth` framework through `struct rpc_authops` and `struct rpc_credops`. It uses `rpcauth_wrap_req_encode` and `rpcauth_unwrap_resp_decode` for pass-through request/response body handling.

Risks: because `nul_match()` always returns true, any caller selecting AUTH_NULL gets no identity isolation. The reply verifier parser is intentionally strict; servers returning non-empty verifiers fail validation. Singleton refcounts must remain initialized high enough for static lifetime assumptions.

Test signals: send NULL and ordinary RPC calls using AUTH_NULL and verify the credential/verifier fields are zero-length AUTH_NULL. Negative tests should feed non-NULL or nonzero reply verifiers and expect `-EIO`. Refcount/lifetime tests should repeatedly create and release AUTH_NULL clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_null.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_tls.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/auth_tls.c

Purpose: implements the special AUTH_TLS client credential used only to probe whether a remote peer supports RPC-over-TLS STARTTLS negotiation. It behaves like a singleton credential flavor with a custom `.ping` operation that sends a probe and validates the STARTTLS response token.

Important APIs/types/functions: exported auth operation table is `authtls_ops`, with `.ping = tls_probe`. Static objects include `tls_auth`, `tls_cred`, `rpcproc_tls_probe`, and `rpc_tls_probe_ops`. Core functions are `tls_probe`, `tls_create`, `tls_lookup_cred`, `tls_marshal`, `tls_refresh`, and `tls_validate`.

Control flow: when an RPC client using AUTH_TLS is pinged, `tls_probe()` runs a soft, soft-connection RPC task with `tls_cred`. The call prepare hook clears `RPC_TASK_NO_RETRANS_TIMEOUT` and starts the normal RPC call FSM. Request marshalling emits an AUTH_TLS credential with zero body and an AUTH_NULL verifier. Reply validation requires an AUTH_NULL verifier followed by an opaque `STARTTLS` token of exactly eight bytes.

State and persistence behavior: state is limited to static singleton auth and credential objects plus immutable `STARTTLS` constants. No per-principal credential or persistent storage exists. Probe task state is normal transient `rpc_task` state.

Dependencies/integration points: integrates with `rpc_create()`/`rpc_ping()` through the authops `.ping` hook, the generic rpc task scheduler, and RPC-over-TLS transport setup code that interprets a successful probe as STARTTLS support. It uses the same pass-through wrap/unwrap helpers as AUTH_NULL.

Risks: `authtls_ops.au_name` is `"NULL"` despite flavor `RPC_AUTH_TLS`, which could confuse diagnostics. The validation path is intentionally narrow; any server returning a different verifier flavor or token length is treated as `-EPROTONOSUPPORT`. The empty procedure encoder/decoder assumes the STARTTLS signal lives in the verifier stream, not in procedure payload.

Test signals: probe a server that supports RPC-over-TLS and confirm `STARTTLS` validation succeeds; test servers that omit the token, return wrong length, wrong flavor, or wrong bytes and expect `-EPROTONOSUPPORT` or `-EIO`. Confirm probe tasks are soft and do not retain no-retrans-timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_tls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_unix.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/auth_unix.c

Purpose: implements AUTH_UNIX/AUTH_SYS client authentication. It allocates per-credential objects from current task credentials, marshals nodename, fsuid, fsgid, and a bounded supplementary group list, validates server verifiers, and provides a small mempool for async allocation fallback.

Important APIs/types/functions: exported auth table is `authunix_ops`; lifecycle helpers are `rpc_init_authunix()` and `rpc_destroy_authunix()`. Credential ops are `unix_credops` with `unx_lookup_cred`, `unx_destroy_cred`, `unx_match`, `unx_marshal`, `unx_refresh`, and `unx_validate`. State is static `unix_auth` and `unix_pool`.

Control flow: auth creation returns the singleton auth handle. Credential lookup allocates `struct rpc_cred` with the task GFP mask, falling back to `unix_pool` for async lookups. Matching compares fsuid, fsgid, and up to `UNX_NGROUPS` supplementary gids. Marshalling writes AUTH_UNIX flavor, credential length placeholder, zero stamp, client nodename, uid, gid, group array, fixes credential length, and appends an AUTH_NULL verifier. Reply validation accepts NULL, UNIX, or SHORT verifiers up to `RPC_MAX_AUTH_SIZE` and adjusts auth reply slack/alignment to the verifier size.

State and persistence behavior: per-call credentials hold a ref to kernel `struct cred`; destruction runs through RCU and frees via the mempool. Singleton auth state stores dynamic reply verifier sizing after validation. No state is persisted beyond kernel memory.

Dependencies/integration points: plugged into the generic SUNRPC auth framework and used by NFS and other AUTH_SYS clients. It depends on user namespace id mapping from `clnt->cl_cred->user_ns` or `init_user_ns`, group info ordering, XDR stream helpers, and rpc task allocation context.

Risks: AUTH_UNIX is identity assertion rather than cryptographic authentication. Group comparison truncates to `UNX_NGROUPS`, matching wire format limits; callers with more groups can collide after truncation. `unx_validate()` mutates `au_verfsize`, `au_rslack`, and `au_ralign` on the shared auth object based on server verifier size, so concurrent clients using the singleton must tolerate this dynamic sizing. Allocation fallback depends on `rpc_init_authunix()` having created `unix_pool`.

Test signals: marshal users with no groups, exactly `UNX_NGROUPS`, and more than `UNX_NGROUPS`; verify namespace id mapping; validate NULL/UNIX/SHORT reply verifiers and reject oversized or malformed verifiers; stress async credential lookup under allocation pressure; and test RCU credential destruction under repeated client create/release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_unix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/backchannel_rqst.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/backchannel_rqst.c

Purpose: manages preallocated SUNRPC backchannel request objects and XDR buffers for transports that receive server-initiated callback RPCs, such as NFSv4 callbacks. It provides generic wrappers that dispatch to transport operations and a default implementation for request allocation, lookup, completion, enqueue, reuse, and destruction.

Important APIs/types/functions: exported functions are `xprt_bc_max_slots`, `xprt_svc_destroy_nullify_bc`, `xprt_setup_backchannel`, `xprt_destroy_backchannel`, and `xprt_enqueue_bc_request`. Core implementation helpers include `xprt_setup_bc`, `xprt_destroy_bc`, `xprt_lookup_bc_request`, `xprt_complete_bc_request`, `xprt_free_bc_request`, `xprt_free_bc_rqst`, `xprt_alloc_bc_req`, and `xprt_get_bc_request`. State lives in `rpc_xprt` fields such as `bc_pa_list`, `bc_pa_lock`, `bc_alloc_count`, `bc_alloc_max`, `bc_slot_count`, `bc_serv`, and request `rq_bc_pa_state`.

Control flow: setup clamps requested slots to `BC_MAX_SLOTS`, allocates `rpc_rqst` objects with one receive page and one send page, then splices them into the transport preallocation list under lock. Incoming callbacks use `xprt_lookup_bc_request()` to find a matching xid/connect-cookie request or allocate/reuse one, `xprt_complete_bc_request()` removes it from the free list, marks it in use, records copied bytes, and queues it to the backchannel service list. When processing finishes, `xprt_free_bc_rqst()` clears in-use state and either returns the request to the free list or frees it if all sessions were destroyed.

State and persistence behavior: all state is in-memory per transport. Preallocated request counts and slot counts are protected by `bc_pa_lock`; request in-use state uses bit operations and barriers. Requests hold a transport reference while queued to the service and release it when freed. No persistent state exists.

Dependencies/integration points: depends on `struct rpc_xprt` transport ops (`bc_setup`, `bc_destroy`, `bc_free_rqst`), XDR buffer helpers, service pools (`svc_pool_wake_idle_thread`), lightweight queues, and RDMA/socket receive paths that call lookup/complete helpers.

Risks: list/count consistency under `bc_pa_lock` is critical. `xprt_enqueue_bc_request()` takes a transport ref before checking `bc_serv`; if no service exists, the request is not enqueued here and correct later release depends on caller behavior. Allocation failure during setup must free both XDR pages. Connect-cookie matching prevents stale callbacks from reusing current slots; ordering barriers around `RPC_BC_PA_IN_USE` protect reuse.

Test signals: create/destroy backchannel sessions repeatedly with varying slot counts; inject allocation failures; receive duplicate xid callbacks; destroy sessions while requests are in use; verify requests are requeued or freed according to `bc_alloc_max`; and run NFSv4 callback traffic over TCP/RDMA with lockdep and refcount debug enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/backchannel_rqst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/cache.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/cache.c

Purpose: provides the generic SUNRPC authentication cache framework used by server and client auth subsystems. It implements RCU hash-table lookup/update, expiry and flushing, user-space upcall/downcall channels, deferred request revisit, text qword encoding/parsing, `/proc/net/rpc` cache files, and rpc_pipefs cache directory operations.

Important APIs/types/functions: exported cache APIs include `sunrpc_cache_lookup_rcu`, `sunrpc_cache_update`, `cache_check_rcu`, `cache_check`, `sunrpc_init_cache_detail`, `sunrpc_destroy_cache_detail`, `cache_flush`, `cache_purge`, `qword_add`, `qword_addhex`, `sunrpc_cache_pipe_upcall`, `sunrpc_cache_pipe_upcall_timeout`, `qword_get`, `cache_seq_start_rcu`, `cache_seq_next_rcu`, `cache_seq_stop_rcu`, `cache_initialize`, `cache_register_net`, `cache_unregister_net`, `cache_create_net`, `cache_destroy_net`, `sunrpc_cache_register_pipefs`, `sunrpc_cache_unregister_pipefs`, and `sunrpc_cache_unhash`. Internal state includes global `cache_list`, delayed `cache_cleaner`, deferred request hash/list, and per-`cache_detail` queues and hash tables.

Control flow: lookup first searches under RCU, skips expired valid entries, and inserts a new pending entry if absent. Updates either fill a not-yet-valid entry in place or allocate a replacement entry and expire the old one. `cache_check_rcu()` determines validity, triggers upcalls for pending or half-aged entries, defers requests if data is not ready, and returns status. Upcalls create `cache_request` records readable from `channel`; writes parse downcalls through the cache-specific parser. Freshening an entry clears `CACHE_PENDING`, revisits deferred requests, and dequeues completed upcall records. Periodic cleaner work scans registered caches for expired or flushed entries.

State and persistence behavior: cache contents are in-memory only. Per-net cache instances are cloned from templates and registered into global cleaner state. User-space communication is via procfs or rpc_pipefs files (`channel`, `content`, `flush`), but those are runtime interfaces, not persistent storage. Cache entries are refcounted, RCU-unhashed, and freed through cache-specific `cache_put`.

Dependencies/integration points: used by RPCSEC_GSS caches, IP map and unix gid caches, and other SUNRPC auth helpers. It integrates with procfs, rpc_pipefs, wait queues, poll/ioctl, module refcounts, trace/events/sunrpc, fault injection via `fail_sunrpc.ignore_cache_wait`, and namespace state in `sunrpc_net`.

Risks: cache entry lifetime is highly concurrency-sensitive: hash locks, queue locks, RCU reads, refcounts, and pending bits must be ordered correctly. `cache_check_rcu()` can return timeout if deferral fails, so service requests may be dropped during userspace daemon outages. `cache_limit_defers()` randomly discards deferred requests above `DFR_MAX`. Qword parsing has fixed destination buffers and returns `-1` on malformed data; cache-specific parsers must validate lengths. Flush intentionally ignores user-supplied timestamps to avoid races.

Test signals: test lookup/update of valid, negative, expired, and flushed entries; userspace read/write of `channel`, `content`, and `flush`; absence and restart of cache daemons; deferred request revisit and overflow; fault injection for immediate deferral; procfs and pipefs registration/unregistration; and lockdep/RCU stress during concurrent upcalls, downcalls, purge, and namespace teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/clnt.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/clnt.c

Purpose: implements the high-level SUNRPC client interface and call finite-state machine. It creates, clones, registers, switches, and destroys RPC clients and transports; runs synchronous/asynchronous tasks; encodes and decodes RPC headers; handles credential refresh, binding, connection, retransmission, timeout policy, backchannel replies, pings, address helpers, and multi-transport trunking.

Important APIs/types/functions: exported client APIs include `rpc_create`, `rpc_clone_client`, `rpc_clone_client_set_auth`, `rpc_switch_client_transport`, `rpc_clnt_iterate_for_each_xprt`, `rpc_killall_tasks`, `rpc_cancel_tasks`, `rpc_clnt_disconnect`, `rpc_shutdown_client`, `rpc_release_client`, `rpc_bind_new_program`, `rpc_run_task`, `rpc_call_sync`, `rpc_call_async`, `rpc_prepare_reply_pages`, `rpc_call_start`, address/payload helpers, `rpc_force_rebind`, restart helpers, NULL call helpers, transport add/probe/manage helpers, connect timeout setters, xprt switch helpers, and optional swap helpers. The FSM actions are `call_start`, `call_reserve`, `call_refresh`, `call_allocate`, `call_encode`, `call_bind`, `call_connect`, `call_transmit`, `call_status`, and `call_decode`.

Control flow: `rpc_create()` builds or reuses a transport, creates a switch, constructs `rpc_clnt`, registers pipefs/debugfs/sysfs/auth state, optionally pings, and adds extra transports for `nconnect`. `rpc_run_task()` allocates a task, attaches client/transport/message, and starts the FSM. A normal call reserves a slot, refreshes credentials, allocates buffers, XDR-encodes the RPC header and auth-wrapped payload, binds through rpcbind if needed, connects, transmits, waits for a reply, decodes the RPC reply header and verifier, unwraps the response, and exits. Errors feed back into credential refresh, re-encode, reconnect/rebind, retry, or final task failure based on soft/hard flags and timeout state.

State and persistence behavior: clients are runtime objects with refcounts, task lists, selected xprt, xprt iterator, auth handle, metrics, sysfs/debugfs/pipefs entries, and namespace list membership. `rpc_clids` allocates integer ids. Client release first drops auth, unregisters from namespace lists, frees metrics and iterators, then schedules work to destroy sysfs/debugfs/pipefs and drop transport refs. Task state tracks request slot, transport, retry counters, XID, buffers, credentials, and status. No durable state is written.

Dependencies/integration points: central integration point for rpc scheduler, transports, rpcbind, auth framework, XDR, rpc_pipefs notifier, debugfs/sysfs, metrics, net namespaces, backchannel support, trace/events/sunrpc, and NFS client features such as trunking, callbacks, swap-over-NFS, and RPC-over-TLS auth pings.

Risks: the FSM is race-prone around retransmit, receive-queue enqueueing, transport switching, and shutdown. Client lifetime spans parent/clone trees and asynchronous work, so refcount transitions must preserve GSS context release semantics. `rpc_decode_header()` handles stale credentials, bad verifiers, auth denial, garbage replies, and out-of-sequence RPCSEC_GSS by selecting different retry paths; regressions can cause livelock or silent authentication failure. Multi-transport removal/addition must keep switch unique-address counts correct. Timeout policy differs for soft, softconn, no-retrans-timeout, and hard calls.

Test signals: create clients for TCP, UDP, local, TLS probe, backchannel, and multi-connect configurations; run sync and async calls through success, auth refresh, rpcbind failure, connection failure, retransmit, bad verifier, stale credential, garbage reply, and timeout paths. Exercise clone and program binding, live transport switch, shutdown with outstanding tasks, trunked transport add/offline/probe/remove, rpc_pipefs mount/umount notifier handling, debugfs/sysfs cleanup, and swap activation when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/clnt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/debugfs.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/debugfs.c

Purpose: implements SUNRPC debugfs visibility for RPC clients and transports, plus optional SUNRPC fault-injection controls. It creates `/sys/kernel/debug/sunrpc/rpc_clnt` and `/sys/kernel/debug/sunrpc/rpc_xprt` directories, per-client task listings, per-transport info files, symlinks from clients to transports, and `fail_sunrpc` knobs when configured.

Important APIs/types/functions: exported functions include `rpc_clnt_debugfs_register`, `rpc_clnt_debugfs_unregister`, `rpc_xprt_debugfs_register`, `rpc_xprt_debugfs_unregister`, `sunrpc_debugfs_init`, and `sunrpc_debugfs_exit`; `fail_sunrpc` is exported under `CONFIG_FAIL_SUNRPC`. Key file ops are `tasks_fops` and `xprt_info_fops`, with seq helpers `tasks_start/next/stop/show` and `xprt_info_show`.

Control flow: init creates the top-level directories and initializes fault injection. Client registration creates a directory named by client id, adds a `tasks` file, and creates symlinks to all current transports. Opening `tasks` takes a client ref and seq iteration walks `cl_tasks` under `cl_lock`. Transport registration allocates a monotonically increasing debug id and creates an `info` file. Opening `info` takes a transport ref and prints netid, address, port, state, net namespace inode, and optional source address.

State and persistence behavior: debugfs dentries are runtime-only pointers stored in `rpc_clnt` and `rpc_xprt`. Top-level directory pointers are static globals. Fault injection booleans live in exported `fail_sunrpc`. No persistent state is stored.

Dependencies/integration points: integrates with `clnt.c` client/transport lifecycle, `rpc_clnt_iterate_for_each_xprt`, debugfs, seq_file, xprt refcounting, and `fail.h` fault injection consumers in cache and transport code.

Risks: seq iteration holds `cl_lock` while rendering task rows and prints footer data in `tasks_stop`; long debugfs reads can contend with task list updates. Symlink name buffers are fixed-size and silently fail on overflow. Debugfs creation errors are mostly ignored, so absence of files is not fatal. Fault-injection knobs can deliberately alter cache wait and disconnect behavior and should not be enabled accidentally in production tests.

Test signals: mount debugfs, create RPC clients/transports, verify client directories, task rows, xprt symlinks, transport info, open/release refcounts during client destruction, and cleanup on unregister/exit. With `CONFIG_FAIL_SUNRPC`, toggle `ignore-client-disconnect`, `ignore-server-disconnect`, and `ignore-cache-wait` and confirm corresponding fault-injection paths observe them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/fail.h -->
# sources/distributed-fs/ceph-client/net/sunrpc/fail.h

Purpose: declares the optional SUNRPC fault-injection control structure shared by debugfs setup and runtime fault sites. It is compiled when kernel fault injection support is enabled.

Important APIs/types/functions: `struct fail_sunrpc_attr` contains a generic `struct fault_attr` plus booleans `ignore_client_disconnect`, `ignore_server_disconnect`, and `ignore_cache_wait`. The global `fail_sunrpc` is declared for consumers and defined/exported in `debugfs.c` under the appropriate config.

Control flow: runtime code includes this header and, when `CONFIG_FAULT_INJECTION` or related SUNRPC failure config is enabled, checks the booleans or `should_fail(&fail_sunrpc.attr, ...)` to alter behavior. Debugfs creates files that mutate these fields.

State and persistence behavior: state is in-memory global fault-injection configuration exposed through debugfs. It is reset on module/kernel lifetime and not persisted.

Dependencies/integration points: depends on `<linux/fault-inject.h>`. It is consumed by cache deferral fault paths and SUNRPC transport/server disconnect fault paths, and configured through `debugfs.c`.

Risks: the header only declares `fail_sunrpc` when fault injection is enabled; consumers must use matching `IS_ENABLED` guards. Fault settings can mask disconnects or force cache wait behavior, so tests must clean up debugfs settings after use.

Test signals: build with fault injection enabled and disabled to catch guard mismatches. Runtime tests should toggle each debugfs boolean and verify affected SUNRPC paths change behavior only under configured fault conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/fail.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/netns.h -->
# sources/distributed-fs/ceph-client/net/sunrpc/netns.h

Purpose: defines SUNRPC per-network-namespace state shared across client, server, rpc_pipefs, auth cache, rpcbind, and GSS proxy code. It centralizes the `struct sunrpc_net` layout stored under `sunrpc_net_id`.

Important APIs/types/functions: `struct sunrpc_net` contains procfs root `proc_net_rpc`, cache pointers (`ip_map_cache`, `unix_gid_cache`, `rsc_cache`, `rsi_cache`), pipefs state (`pipefs_sb`, `gssd_dummy`, `pipefs_sb_lock`, `pipe_users`, `pipe_version`), client registry (`all_clients`, `rpc_client_lock`), local rpcbind clients and locks, GSS proxy state (`gssp_lock`, `gssp_clnt`, `use_gss_proxy`, `use_gssp_proc`, `gss_krb5_enctypes`), and exported `sunrpc_net_id`. It declares `ip_map_cache_create()` and `ip_map_cache_destroy()`.

Control flow: code obtains the namespace state with `net_generic(net, sunrpc_net_id)`. `clnt.c` registers clients in `all_clients` and uses pipefs state; `svcauth_gss.c` creates/destroys `rsc_cache`, `rsi_cache`, and proc entries; cache registration uses `proc_net_rpc`; rpcbind and gssproxy code use the local client fields and locks.

State and persistence behavior: all fields are per-net runtime state. Namespace initialization and teardown create and destroy caches, proc entries, pipefs references, and clients. No persistent storage is represented here.

Dependencies/integration points: depends on network namespace generic storage and forward-declared `struct cache_detail`. It is a coordination header for SUNRPC modules across `net/sunrpc`, especially cache, client, rpc_pipefs, rpcbind, and auth_gss.

Risks: field lifetime is tied to network namespace teardown; users must clear pointers before destroying referenced objects and hold the appropriate lock for client, rpcbind, pipefs, or gssproxy fields. Because many subsystems share this struct, layout changes can have wide build and lifetime impacts.

Test signals: create and destroy network namespaces while running RPC clients, rpcbind lookups, GSS server auth, and pipefs mounts. Verify all per-net caches and proc entries appear and disappear, and run with KASAN/lockdep to catch stale namespace pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/netns.h -->
