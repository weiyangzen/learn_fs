# subset-b-009850 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/mdssvc.c -->
# sources/user-network-fs/samba/source3/rpc_server/mdssvc/mdssvc.c

Purpose: implements the common Samba Spotlight metadata service engine behind the `mdssvc` RPC endpoint. It unmarshals opaque Spotlight RPC blobs, dispatches command names to local handlers, manages per-tree-connect query state, normalizes macOS UTF-8 paths, and delegates actual search execution to a configured backend.

Important APIs and functions: `mds_init_ctx()` creates a per-share `struct mds_ctx`, checks `lp_spotlight()`, selects `mdsscv_backend_noindex` or `mdsscv_backend_es`, opens NFC/NFD iconv handles, creates an in-memory `dbwrap_rbt` inode map, and creates a VFS connection wrapper. `mds_dispatch()` unpacks a `mdssvc_blob` with `sl_unpack()`, finds a command via `slrpc_cmd_by_name()`, changes to the share root, calls the handler, and packs the reply with `sl_pack_alloc()`. Command handlers cover `fetchPropertiesForContext:`, `openQueryWithParams:forContext:`, `fetchQueryResultsForContext:`, `storeAttributes:forOIDArray:context:`, attribute-name/value fetches, and query close. `mds_add_result()` is the backend-facing result ingestion API.

Control flow: clients open mdssvc on a share, then send named Spotlight commands inside blobs. `slrpc_open_query()` converts the query string from NFD to NFC, extracts context IDs, scope, requested attributes, and optional CNID restrictions, creates a result handle, links the `sl_query` into `mds_ctx->query_list`, and calls `backend->search_start()`. `slrpc_fetch_query_results()` renews the timeout, serializes queued results, and resumes the backend if the query had reached `SLQ_STATE_FULL`. Close and timer expiry free `sl_query`, which removes it from the active list and drops backend/private mappings.

State and persistence: process-wide `mdssvc_ctx` is static and reused by multiple binds. Each `mds_ctx` owns active `sl_query` objects and a transient inode-to-path map. Inode map entries are talloc-refcounted across queries and removed from `dbwrap_rbt` by destructors. There is no persistent Spotlight index here; fake CNIDs are derived from VFS file IDs.

Dependencies and integration points: this file integrates generated `mdssvc` NDR blobs, `dalloc` marshalling, Samba loadparm, VFS pathref/access checks, authenticated pipe impersonation, dbwrap, talloc destructors, tevent timers, and backend vtables from `mdssvc_noindex.c` and optionally `mdssvc_es.c`.

Risks: malformed dalloc blobs can drive many error paths; several return `true` with error payloads to match protocol behavior. `mds_add_result()` impersonates the pipe user and panics on identity mismatch, so callback identity handling is security critical. Query result state is mutable across async callbacks and client fetches; backend code must respect state transitions and talloc lifetime rules. Fake CNID identity via inode/file ID can be unstable across filesystems or remounts.

Test signals: parser/mapping behavior is covered separately by `test_mdsparser_es.c`; runtime coverage should exercise open/fetch/close, timeout cleanup, CNID filtering, Unicode normalization, access-denied result suppression, and both noindex and ES backend paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/mdssvc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/mdssvc.h -->
# sources/user-network-fs/samba/source3/rpc_server/mdssvc/mdssvc.h

Purpose: declares the shared mdssvc data model, backend interface, constants, debug helper, and public entry points used by the mdssvc RPC server and search backends.

Important APIs and types: `slq_state_t` defines query lifecycle states from `SLQ_STATE_NEW` through running/results/full/done/end/error. `struct sl_query` is the central per-query object and carries backend-private data, context IDs, requested attributes, optional CNID restrictions, path scope, result buffers, timers, and list links. `struct sl_rslts` stores queued CNIDs and file metadata arrays. `struct sl_inode_path_map` backs later attribute fetches by mapping fake CNID/inode values to fake share paths and stat data. `struct mdssvc_ctx` is process-level backend state, while `struct mds_ctx` is per-tree-connect state including share path, authenticated SID/uid, iconv handles, VFS connection wrapper, query list, and inode map. `struct mdssvc_backend` is the backend vtable with `init`, `connect`, `search_map`, `search_start`, `search_cont`, and `shutdown`.

Control flow and integration: `mds_init()`, `mds_shutdown()`, `mds_init_ctx()`, `mds_dispatch()`, and `mds_add_result()` are exported to server glue and backends. Backends are expected to transition `sl_query` state and call `mds_add_result()` for filesystem paths that may be returned to clients.

State and persistence: the header makes clear that query and inode map state are per `mds_ctx`, not global durable data. The public constants cap result volume (`MAX_SL_RESULTS`, `SL_PAGESIZE`), runtime (`MAX_SL_RUNTIME`), and async timeout behavior.

Dependencies: includes mdssvc generated NDR definitions, marshalling/dalloc helpers, dlinklist, and works around GLib `TRUE`/`FALSE` macro conflicts before backend headers may include GLib users.

Risks: the header encodes ownership expectations but not locking; async backends must preserve talloc lifetimes. The `search_map` vtable member exists but is not assigned by the noindex/ES backends in this subset, so callers should not assume every function pointer is populated.

Test signals: compile-time tests should catch layout/API drift; behavioral tests should focus on state transition correctness and backend result ingestion through `mds_add_result()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/mdssvc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/mdssvc_es.c -->
# sources/user-network-fs/samba/source3/rpc_server/mdssvc/mdssvc_es.c

Purpose: implements the Elasticsearch-backed mdssvc search backend. It translates Spotlight query syntax to Elasticsearch query-string syntax, maintains an HTTP(S) connection to an ES server, pages results, and feeds matching `path.real` values back into the common mdssvc result path.

Important APIs and functions: `mdssvc_es_init()` loads JSON mappings from `elasticsearch:mappings` or the Samba datadir default and records `elasticsearch:default_fields`. `mds_es_connect()` creates per-bind `struct mds_es_ctx` and starts async HTTP connection setup. `mds_es_search()` maps the Spotlight query with `map_spotlight_to_es_query()`, allocates `struct sl_es_search`, sets page size and max results, links it to the queue, and triggers dispatch. `mds_es_search_send()` builds a POST to `/<index>/_search`, using `MDSSVC_ELASTIC_QUERY_TEMPLATE` with `_source` limited to `path.real`. `mds_es_search_http_read_done()` parses JSON responses and calls `mds_add_result()` for each hit.

Control flow: backend init is process-level; `connect` is per mdssvc bind/share and asynchronously connects to ES using loadparm `elasticsearch:address`, `port`, `use tls`, and credentials. Searches are queued in `mds_es_ctx->searches`, with only the list head pending on the HTTP channel. Completion updates the common `sl_query` state: no total or max reached becomes `DONE`, a full page in the client queue becomes `FULL`, otherwise the search is requeued for another page. `search_cont()` re-adds the search when the client drains results.

State and persistence: `mdssvc_es_ctx` persists mappings/default fields for the process. `mds_es_ctx` stores the HTTP connection and active queue per bind. `sl_es_search` stores paging counters, max result cap, and translated ES query. ES itself is the persistent index; Samba stores only transient cursors.

Dependencies: tevent, Samba HTTP client, TLS parameter setup, credentials, Jansson, loadparm, generated ES parser, mdssvc core, and the common VFS/access path in `mds_add_result()`.

Risks: the JSON query is assembled with `talloc_asprintf()`, so correctness relies on mapper escaping. HTTP reconnect marks the query error and reconnects the shared channel. A pending search survives `sl_query` destruction by clearing `slq`; lifetime rules are subtle. Response size is bounded by `SL_PAGESIZE * 8192`, which may truncate unusually large hits. `mdssvc_es_shutdown()` does not explicitly decref mappings, relying on talloc/process cleanup, so allocator ownership deserves attention.

Test signals: `test_mdsparser_es.c` verifies query mapping. Integration tests should cover ES 6/7 total-hit formats, paging, max result caps, TLS/non-TLS connection, missing `path.real`, non-200 responses, reconnect paths, and client-close while HTTP is pending.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/mdssvc_es.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/mdssvc_es.h -->
# sources/user-network-fs/samba/source3/rpc_server/mdssvc/mdssvc_es.h

Purpose: declares private state structures and the exported backend vtable for the Elasticsearch mdssvc backend.

Important APIs and types: `struct mdssvc_es_ctx` is process/global backend state with the owning `mdssvc_ctx`, anonymous HTTP credentials, loaded Jansson mapping tree, and default ES search fields. `struct mds_es_ctx` is per RPC bind/share state with a pointer back to `mds_ctx`, a pointer to global ES state, an HTTP connection, and queued searches. `struct sl_es_search` is per query request state with dlist links, pending flag, event context, owning bind state, parent `sl_query`, result totals, paging fields, and the translated ES query string. `mdsscv_backend_es` is exported for selection by `mds_init_ctx()`.

Control flow and integration: the types mirror the backend contract in `mdssvc.h`. `mds_ctx->backend_private` points at `mds_es_ctx`; `sl_query->backend_private` points at `sl_es_search`. The queue/pending fields support serialized HTTP use while retaining multiple client query cursors.

State and persistence: only the mapping JSON and default field string are process-level state. Search cursors are per bind and per query. Persistent metadata lives outside Samba in Elasticsearch.

Dependencies: includes Jansson and assumes mdssvc core types are visible from including translation units. Consumers must also link against the generated parser/mapping support used by `mdssvc_es.c`.

Risks: the header exposes raw pointers for async state without locking primitives; lifetime is governed by talloc parentage and destructors in the C file. Any future concurrent HTTP dispatch would need stronger invariants around `pending`, list head ordering, and `slq` nulling.

Test signals: compile tests should catch backend-vtable availability under `HAVE_SPOTLIGHT_BACKEND_ES`; runtime tests need to inspect transitions of `mds_ctx->backend_private` and `sl_query->backend_private`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/mdssvc_es.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/mdssvc_noindex.c -->
# sources/user-network-fs/samba/source3/rpc_server/mdssvc/mdssvc_noindex.c

Purpose: implements the fallback mdssvc backend for shares with Spotlight enabled but no real search index. It satisfies the backend contract while returning no indexed search results.

Important APIs and functions: `mdssvc_noindex_init()`, `mdssvc_noindex_shutdown()`, and `mds_noindex_connect()` all return success without allocating persistent state. `mds_noindex_search_start()` and `mds_noindex_search_cont()` set the common `sl_query` state to `SLQ_STATE_DONE`, causing fetches to return an empty completed result set. `mdsscv_backend_noindex` exports these callbacks.

Control flow: when `mds_init_ctx()` selects `SPOTLIGHT_BACKEND_NOINDEX`, query open still parses request metadata and creates common result structures. The backend immediately marks the query done. Client fetch then runs through normal serialization in `mdssvc.c`, which includes the usual status/result container but no paths.

State and persistence: no backend-private state is created. All state remains in the common query object and is freed by normal mdssvc close/timeout/destructor paths.

Dependencies: only `includes.h` and `mdssvc.h`. This makes it a low-risk baseline implementation and a useful fallback for builds without ES support.

Risks: because this backend reports successful empty searches, clients may see Spotlight capability but no search matches. That is intentional but can mask configuration mistakes if administrators expected ES indexing.

Test signals: basic mdssvc RPC tests should verify noindex open/fetch/close success, `DONE` state, empty CNID arrays, and no backend-private allocations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/mdssvc_noindex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/mdssvc_noindex.h -->
# sources/user-network-fs/samba/source3/rpc_server/mdssvc/mdssvc_noindex.h

Purpose: exposes the noindex backend vtable to the mdssvc core.

Important API: declares `extern struct mdssvc_backend mdsscv_backend_noindex;`, which is selected by `mds_init_ctx()` and initialized/shutdown by the process-level mdssvc setup.

Control flow and integration: this header lets `mdssvc.c` compile the fallback backend unconditionally. The backend implements enough callbacks to satisfy normal query lifecycle without external services.

State and persistence: no declarations introduce additional state; all state is managed by the common mdssvc structures.

Dependencies: relies on `struct mdssvc_backend` from `mdssvc.h` being visible before use.

Risks: the include guard close comment says `_MDSSVC_VOID_H_`, which is cosmetic but misleading. API surface is intentionally tiny.

Test signals: build coverage is sufficient for the header; behavior is tested via the C backend and mdssvc core.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/mdssvc_noindex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/srv_mdssvc_nt.c -->
# sources/user-network-fs/samba/source3/rpc_server/mdssvc/srv_mdssvc_nt.c

Purpose: provides the generated-compatible server-side RPC handlers for the mdssvc pipe and bridges DCERPC requests to the common mdssvc engine.

Important APIs and functions: `create_mdssvc_policy_handle()` creates an `mds_ctx` with `mds_init_ctx()` and stores it in a policy handle. `_mdssvc_open()` resolves the requested share, initializes the context, returns a fake `/<share>` path, and treats `NT_STATUS_WRONG_VOLUME` as Spotlight-disabled rather than a hard fault. `_mdssvc_unknown1()` returns fixed status/flags for a valid handle. `_mdssvc_cmd()` validates the policy handle, session SID, effective uid, and fragment limits before calling `mds_dispatch()`. `_mdssvc_close()` frees the `mds_ctx` and closes the policy handle. Server init/shutdown wrappers call `mds_init()` and `mds_shutdown()` before/after generated boilerplate.

Control flow: the client opens mdssvc for a share, receives a policy handle, sends opaque Spotlight command blobs through `_mdssvc_cmd()`, and closes the handle. Invalid empty handles are treated leniently in some methods to match client expectations; non-empty invalid handles set protocol faults.

State and persistence: the policy handle owns the per-share `mds_ctx`; freeing the handle tears down queries, inode map, and VFS connection via mdssvc destructors. Process-level backend state is managed by mdssvc init/shutdown.

Dependencies: generated mdssvc NDR compatibility glue, DCE/RPC server core, policy-handle helpers, global messaging/event contexts, loadparm share lookup/path substitution, security token/SID checks, and smbd globals.

Risks: `_mdssvc_cmd()` relies on effective uid already matching the authenticated mdssvc uid and panics on mismatch. Fragment checks prevent oversize blobs, but mdssvc currently does not implement mdssvc-layer fragmentation. SID equality is enforced against the opening SID to prevent handle reuse across users.

Test signals: tests should cover opening Spotlight-enabled and disabled shares, invalid handles, SID mismatch, oversize blobs, close cleanup, and end-to-end dispatch of a known Spotlight command.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/srv_mdssvc_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/srv_mdssvc_nt.h -->
# sources/user-network-fs/samba/source3/rpc_server/mdssvc/srv_mdssvc_nt.h

Purpose: declares mdssvc service lifecycle entry points for the RPC service layer.

Important APIs: `init_service_mdssvc(struct messaging_context *msg_ctx)` and `shutdown_service_mdssvc(void)` are declared for service registration/lifecycle integration. The implementation in this subset instead provides generated endpoint init/shutdown wrappers in `srv_mdssvc_nt.c`, so these declarations likely correspond to broader Samba service registration code.

Control flow and integration: consumers include this header when setting up the mdssvc RPC pipe. The message context parameter indicates initialization may need Samba messaging integration.

State and persistence: the header declares lifecycle hooks only; persistent state is in `mdssvc.c` (`mdssvc_ctx`) and per-policy `mds_ctx` objects.

Dependencies: forward use of `struct messaging_context`; actual definition comes from included Samba headers in consumers.

Risks: if declarations drift from generated/server registration symbols, build or link errors will expose it. The header contains no behavioral safeguards.

Test signals: build/link coverage of mdssvc service registration is the primary signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/srv_mdssvc_nt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/test_mdsparser_es.c -->
# sources/user-network-fs/samba/source3/rpc_server/mdssvc/test_mdsparser_es.c

Purpose: cmocka test program for Spotlight-to-Elasticsearch query mapping used by the mdssvc ES backend.

Important APIs and functions: static `map[]` enumerates expected successful translations for wildcard text search, metadata fields, content-type mappings, dates, numeric fields, path escaping, negation, comparison, boolean operators, and `InRange()`. `map_ignore_failures[]` covers cases where unsupported predicates can be ignored when `elasticsearch:test mapping failures` is enabled. `test_mdsparser_es()` loads the same mapping JSON path used by runtime code and checks `map_spotlight_to_es_query()` output. `main()` initializes Samba command-line/loadparm context, sets log level, parses common options, and runs cmocka with subunit output.

Control flow: the test initializes Samba locale/config, obtains mapping file path from loadparm or datadir default, loads it with Jansson, iterates all required cases with `assert_true()` and `assert_string_equal()`, optionally iterates ignored-failure cases, then decrefs mappings and frees the talloc frame.

State and persistence: test state is local to a talloc stackframe. It reads the installed/source mapping JSON and does not write data.

Dependencies: cmocka, Jansson, Samba cmdline/loadparm/talloc utilities, `es_parser.tab.h`, and the mapper implementation linked into the test binary.

Risks: expected strings are tightly coupled to escaping behavior and mapping JSON contents; legitimate mapping changes require synchronized test updates. Some wide date cases are only compiled on LP64, so 32-bit coverage differs. The optional ignored-failure block is disabled by default unless smb.conf parameters request it.

Test signals: this is the main unit signal for ES query translation. It should be run whenever parser grammar, lexer escaping, mapping JSON, or ES backend query construction changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/mdssvc/test_mdsparser_es.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/netlogon/srv_netlog_nt.c -->
# sources/user-network-fs/samba/source3/rpc_server/netlogon/srv_netlog_nt.c

Purpose: implements Samba's server-side Netlogon RPC operations for the source3 RPC server. It covers logon control, trusted-domain enumeration, secure-channel challenge/authentication, machine-account password changes, SAM logon validation, DC discovery, capabilities, forest trust information, trust password retrieval, and many explicitly unsupported opnums.

Important APIs and functions: `_netr_LogonControl*()` normalize to `_netr_LogonControl2Ex()` for query/control responses and trust credential actions via winbind helpers. `_netr_NetrEnumerateTrustedDomains()` calls internal LSA RPC to enumerate trusted domains and returns a registry multi-SZ blob. `get_md4pw()` opens SAMR internally, validates machine/trust account type and status, and retrieves the NT hash. `_netr_ServerReqChallenge()` stores server/client challenges in per-connection iface state. `_netr_ServerAuthenticate3()` negotiates flags, enforces AES when weak crypto is disallowed, validates credentials, and saves schannel credential state. `_netr_ServerPasswordSet*()` decrypt and validate new machine passwords and update SAMR through `netr_set_machine_account_password()`. `_netr_LogonSamLogon*_base()` decrypts netlogon credentials, builds auth subsystem inputs, verifies NTLMv2 trust context, returns SamInfo2/3/6, and encrypts validation data. Forest/trust helpers build `lsa_ForestTrustInformation` and encrypt trust passwords from passdb trustAuth blobs.

Control flow: secure-channel setup starts with challenge, then authenticate, which saves schannel credential state. Subsequent credential-chained operations call `dcesrv_netr_creds_server_step_check()` under root to validate authenticators. Logon operations validate requested levels, decrypt protected logon material, authenticate via Samba auth3, reject guest domain logons, convert server info into requested validation structures, and seal the reply. Discovery/control methods use winbind first where appropriate, falling back to local `dsgetdcname()`.

State and persistence: challenge state is per DCE/RPC connection. Schannel credential state is persisted through Samba schannel utilities so it can survive disconnect/reconnect. Machine password updates persist through SAMR/passdb. Forest trust information is synthesized from passdb domain info, UPN suffixes, and trusted-domain records.

Dependencies: DCE/RPC core and generated netlogon glue, SAMR/LSA internal RPC clients, passdb, winbind client API, schannel credential utilities, auth subsystem, GnuTLS session encryption helpers, registry multi-SZ utilities, dsgetdcname, forest-trust conversion utilities, loadparm security settings, and root impersonation.

Risks: this file is security-critical. Negotiation flags, seal/privacy requirements, credential chaining, password decryption checks, and trust validation must match Windows behavior. PasswordSet2 includes explicit checks for unencrypted length/confounder/password buffers and empty/zero passwords. Many unsupported opnums set RPC fault state intentionally; compatibility changes must be tested against Windows clients. The bind hook logs warnings for dangerous `server schannel` and `server schannel require seal` misconfiguration related to CVE-2020-1472 and CVE-2022-38023.

Test signals: coverage should include schannel negotiation under weak-crypto policies, challenge/authenticate success/failure, machine password set variants, SamLogon levels 2/3/6 with privacy enforcement, trust enumeration, DC lookup fallbacks, forest trust info, and unsupported opnum fault behavior. Interop tests with Windows domain members/controllers are especially important.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/netlogon/srv_netlog_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/ntsvcs/srv_ntsvcs_nt.c -->
# sources/user-network-fs/samba/source3/rpc_server/ntsvcs/srv_ntsvcs_nt.c

Purpose: implements a small compatibility subset of the Windows NTSVCS/Plug and Play RPC interface. It mostly returns plausible responses for service-backed legacy device queries and marks the rest of the PNP surface unsupported.

Important APIs and functions: `get_device_path()` formats `ROOT\Legacy_<service>\0000`. `_PNP_GetVersion()` returns version `0x0400`. `_PNP_GetDeviceListSize()` and `_PNP_GetDeviceList()` validate service-filter pointers, construct a legacy device path, and return size or multi-SZ encoded list data. `_PNP_GetDeviceRegProp()` supports `DEV_REGPROP_DESC` by parsing the service name from the device path, looking up the display name through `svcctl_lookup_dispname()`, and returning it as `REG_SZ`. `_PNP_ValidateDeviceInstance()`, `_PNP_GetHwProfInfo()`, and `_PNP_HwProfFlags()` return simple compatibility responses. Most other `_PNP_*` calls set `DCERPC_FAULT_OP_RNG_ERROR` and return `WERR_NOT_SUPPORTED`.

Control flow: clients can ask for a device list size, then list, then description property. The implementation uses registry encoding helpers (`push_reg_multi_sz`, `push_reg_sz`) to produce Windows-compatible string buffers and returns buffer-small errors with needed sizes.

State and persistence: no persistent state is stored. Data is synthesized from incoming service/device names and live service-control display-name lookup.

Dependencies: generated NTSVCS NDR compatibility glue, DCE/RPC call state for session info, service control winreg glue, and registry utility string encoders.

Risks: `_PNP_GetDeviceRegProp()` mutates `r->in.devicepath` in place while parsing by writing NUL terminators; this assumes the generated stub provides mutable storage. Device-list functions only emulate legacy service devices and do not enumerate real hardware. The many unsupported opnums are compatibility decisions and may affect clients expecting fuller PNP behavior.

Test signals: RPC tests should cover buffer sizing, multi-SZ encoding, display-name lookup success/failure, invalid pointer handling under `CM_GETIDLIST_FILTER_SERVICE`, and expected faults for unsupported PNP calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/ntsvcs/srv_ntsvcs_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpc_config.c -->
# sources/user-network-fs/samba/source3/rpc_server/rpc_config.c

Purpose: provides lazy global initialization and teardown for the source3 DCE/RPC server context.

Important APIs and functions: `global_dcesrv_context()` initializes a singleton `struct dcesrv_context` using `global_event_context()`, an S3 loadparm context from `loadparm_init_s3()`, and `srv_callbacks`. `global_dcesrv_context_free()` frees the singleton. Callback wiring provides successful authorization logging, GENSEC preparation, root/unroot hooks, and association-group lookup.

Control flow: the first caller gets initialization; later callers reuse `global_dcesrv_ctx`. The loadparm context is stolen under the DCE/RPC context to align lifetimes. Fatal initialization failures call `smb_panic()` because the RPC server cannot run without this context.

State and persistence: `global_dcesrv_ctx` is static process state. It is intentionally allocated from a NULL context rather than the autofree context to avoid forked-child exit side effects.

Dependencies: RPC server helpers, DCE/RPC core, loadparm S3 helpers, global event context, and Samba privilege transition callbacks.

Risks: singleton lifecycle must be coordinated across forked processes and shutdown. Any callback behavior affects all RPC interfaces using the global context. Panics are appropriate for startup failure but make memory/config failures fatal.

Test signals: initialization tests should verify singleton reuse, callback availability, and clean `global_dcesrv_context_free()` behavior. Integration tests should ensure forked RPC workers do not inherit unsafe autofree ownership.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpc_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpc_config.h -->
# sources/user-network-fs/samba/source3/rpc_server/rpc_config.h

Purpose: declares the global DCE/RPC context accessor and free function for source3 RPC server code.

Important APIs: forward declares `struct dcesrv_context`, exports `global_dcesrv_context(void)`, and `global_dcesrv_context_free(void)`.

Control flow and integration: consumers include this header to obtain the lazily initialized server context without depending on the implementation details in `rpc_config.c`.

State and persistence: the state is the implementation singleton; the header exposes no mutable globals.

Dependencies: minimal by design, avoiding heavy DCE/RPC includes in consumers that only need an opaque pointer.

Risks: callers must not assume ownership of the returned context. Freeing the global context while active RPC users still exist would invalidate shared state.

Test signals: build coverage and integration tests around RPC startup/shutdown are the relevant checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpc_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpc_handles.c -->
# sources/user-network-fs/samba/source3/rpc_server/rpc_handles.c

Purpose: implements source3 policy-handle compatibility helpers on top of the DCE/RPC core handle API and provides a pipe access check for anonymous restrictions.

Important APIs and functions: `check_open_pipes()` and `num_pipe_handles()` expose a global handle count. `create_policy_hnd()` creates a `dcesrv_handle`, attaches a tiny destructor object that decrements `num_handles`, moves optional talloc-owned service data into the handle, writes the wire handle, and increments the count. `_find_policy_by_hnd()` wraps lookup and returns typed private data with NTSTATUS. `close_policy_hnd()` validates and frees the core handle. `pipe_access_check()` enforces `restrict anonymous > 0` by requiring completed auth and at least `SECURITY_USER`, except schannel-authenticated calls are accepted.

Control flow: server stubs create policy handles during open/connect operations, retrieve private state on later opnums, and close handles on close calls. Lookup intentionally avoids passing the requested handle type to `dcesrv_handle_lookup()` so type mismatch can return NULL without setting a fault in `pipes_struct`; empty or missing handles set context mismatch.

State and persistence: `num_handles` is static process state. Handle-private data is owned by the DCE/RPC handle via talloc and freed when the handle is freed. There is no disk persistence.

Dependencies: generated NDR policy handle helpers, DCE/RPC core, Samba auth/session/security levels, loadparm `restrict anonymous`, and tsocket/security headers used by the surrounding RPC stack.

Risks: `num_handles` is process-global and not synchronized; it assumes the server execution model does not need cross-thread atomicity. Moving `data_ptr` transfers ownership, so callers must not reuse it after successful creation. Anonymous restriction enforcement depends on `auth_finished` and session user level correctness.

Test signals: tests should cover empty handle lookup, invalid handle lookup, handle type mismatch, private-data lifetime on close, count increments/decrements, schannel bypass, and anonymous denial when `restrict anonymous` is enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/rpc_handles.c -->
