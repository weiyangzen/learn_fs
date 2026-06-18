# subset-b-009848 research

Grouped research report for selected Samba `source3` RPC client/server files. Each section preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/wsp_cli.c -->
# sources/user-network-fs/samba/source3/rpc_client/wsp_cli.c

Purpose: Windows Search Protocol client helpers for building WSP request messages, connecting to the `MsFteWds` named pipe over SMB2+, sending raw DCERPC transport calls, and decoding row buffers returned by search queries.

Important APIs/types/functions: `init_connectin_request`, `create_querysearch_request`, `create_setbindings_request`, `create_seekat_getrows_request`, `extract_rowsarray`, `wsp_server_connect`, `wsp_request_response`, and `get_wsp_pipe`. The file relies heavily on generated `ndr_wsp` structures, `wsp_request`/`wsp_response`, AQS parser output `t_select_stmt`/`t_query`, and the local `struct wsp_client_ctx` containing a `dcerpc_binding_handle`.

Control flow: connect initialization builds fixed property sets for catalog, machine, locale, query options, scope, and search root, serializes them into opaque connect blobs, and tags the request as `CPMCONNECT`. Query creation walks the parsed where-tree into WSP restrictions, maps selected columns to property specs, and defines a default sort set. Binding creation computes per-row value/status/length offsets and row width for later `CPMGETROWS`. `wsp_request_response` serializes the selected message body at offset 16, back-patches protocol size fields, computes the WSP checksum for selected messages, inserts the header, performs a raw call, and parses the response.

State/persistence behavior: no durable local state is stored. Runtime state is talloc-owned request/response blobs, row binding layouts, decoded variants, and the persistent server-side WSP cursor referenced by handles returned in responses.

Dependencies/integration: integrates Samba client state, SMB2 pipe wait, DCERPC named-pipe transport, tstream binding handles, generated WSP NDR, WSP property metadata helpers, AQS parsing, and low-level endian/buffer utilities.

Risks/test signals: row-buffer decoding is pointer/offset-sensitive, especially 32-bit versus 64-bit address handling, variable strings, vectors, and length fields. Unsupported fixed-size vectors and arrays return validation errors. Tests should cover connect/create-query/set-bindings/getrows round trips, malformed row buffers, property names including `System.Search.RowID`, checksum/header bytes, and SMB1 rejection in `wsp_server_connect`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/wsp_cli.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/wsp_cli.h -->
# sources/user-network-fs/samba/source3/rpc_client/wsp_cli.h

Purpose: public header for the source3 Windows Search Protocol client helpers implemented in `wsp_cli.c`.

Important APIs/types/functions: declares `enum search_kind`, `get_kind`, request builders for connect/query/bindings/getrows, `extract_rowsarray`, `wsp_server_connect`, `wsp_request_response`, and `get_wsp_pipe`. It forward-declares generated WSP request structures and `struct wsp_client_ctx` so consumers do not need the private client context layout.

Control flow: the header defines the expected call sequence for WSP consumers: connect to the server with `wsp_server_connect`, initialize a `wsp_request`, send it with `wsp_request_response`, create a query, bind selected columns, fetch rows, and decode row data with the same bindings.

State/persistence behavior: it exposes only opaque runtime state. `struct wsp_client_ctx` ownership remains private to the implementation and is talloc-managed by the caller-provided memory context.

Dependencies/integration: includes `libcli/wsp/wsp_aqs.h` for query parser types and depends on Samba core types such as `TALLOC_CTX`, `DATA_BLOB`, `NTSTATUS`, and generated WSP structures from translation units that include this header.

Risks/test signals: API users must pass consistent `wsp_cpmsetbindingsin` data to `extract_rowsarray` and preserve request lifetimes long enough for response parsing. Compile tests should catch generated type drift; integration tests should cover the public sequence against Windows Search or a WSP-compatible server.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/wsp_cli.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/dfs/srv_dfs_nt.c -->
# sources/user-network-fs/samba/source3/rpc_server/dfs/srv_dfs_nt.c

Purpose: source3 implementation of the DFS RPC pipe, including add/remove/enumerate/get-info operations for MSDFS links stored through Samba shares and VFS DFS path hooks.

Important APIs/types/functions: `create_junction`, `junction_to_local_path_tos`, `create_msdfs_link`, `remove_msdfs_link`, `count_dfs_links`, `form_junctions`, `enum_msdfs_links`, `_dfs_Add`, `_dfs_Remove`, `_dfs_Enum`, and `_dfs_GetInfo`. Reply helpers populate `dfs_Info1`, `dfs_Info2`, `dfs_Info3`, and `dfs_Info100`.

Control flow: mutation calls require the caller's Unix UID to match `sec_initial_uid`. `_dfs_Add` parses the DFS path, resolves any existing referral via `get_referred_path`, appends a referral built from server/share input, then creates or replaces the DFS link through `SMB_VFS_CREATE_DFS_PATHAT`. `_dfs_Remove` resolves the path, either deletes the link entirely or clears a matching referral and rewrites the DFS path. Enumeration loads registry and usershare shares, counts DFS roots and links, creates synthetic root referrals, and enumerates link referrals under each DFS root.

State/persistence behavior: DFS state is persisted as filesystem DFS link objects under MSDFS root shares, not in process memory. Enumeration also depends on current share definitions, usershare registry loading, and optional `msdfs proxy` configuration.

Dependencies/integration: integrates loadparm share configuration, global messaging, fake connection creation, smbd VFS directory APIs, `msdfs.h` referral parsing, auth session information, and generated DFS RPC boilerplate.

Risks/test signals: path parsing deliberately rejects non-DFS roots and invalid non-POSIX syntax. Create uses unlink-and-retry on name collision, so tests should cover replacement and read-only shares. Enumeration count overflow handling, proxy roots, hidden path forms with leading separators, and unsupported DFS calls that set `DCERPC_FAULT_OP_RNG_ERROR` are important compatibility signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/dfs/srv_dfs_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/dssetup/srv_dssetup_nt.c -->
# sources/user-network-fs/samba/source3/rpc_server/dssetup/srv_dssetup_nt.c

Purpose: implements the DSSETUP RPC server surface needed to report primary domain role information, with the rest of the domain-controller promotion/demotion operations explicitly unsupported.

Important APIs/types/functions: `fill_dsrole_dominfo_basic` and `_dssetup_DsRoleGetPrimaryDomainInformation` are the implemented path. All other `_dssetup_DsRole*` entry points set `p->fault_state = DCERPC_FAULT_OP_RNG_ERROR` and return `WERR_NOT_SUPPORTED`.

Control flow: `fill_dsrole_dominfo_basic` allocates a `dssetup_DsRolePrimaryDomInfoBasic`, maps `lp_server_role()` to standalone/member/backup-DC/primary-DC role values, fills the NetBIOS domain name from Samba global state, optionally adds the stored domain GUID, and, for ADS security, lowercases `lp_realm()` into DNS domain and forest fields. `_dssetup_DsRoleGetPrimaryDomainInformation` dispatches level `DS_ROLE_BASIC_INFORMATION` to that helper and rejects unknown levels with `WERR_INVALID_LEVEL`.

State/persistence behavior: no state is modified. It reads live Samba configuration, secrets.tdb domain GUID data via `secrets_fetch_domain_guid`, and realm/workgroup/server-role settings.

Dependencies/integration: tied to loadparm role/security configuration, Samba secrets, generated `ndr_dssetup` server compatibility code, and standard RPC pipe memory contexts.

Risks/test signals: role mapping must stay aligned with Samba server-role semantics, especially IPA DC being reported as primary DC. ADS DNS fields depend on lowercase conversion. Tests should cover each server role, ADS versus domain security, missing domain GUID, invalid info levels, and unsupported calls generating the expected DCERPC fault.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/dssetup/srv_dssetup_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/echo/srv_echo_nt.c -->
# sources/user-network-fs/samba/source3/rpc_server/echo/srv_echo_nt.c

Purpose: simple RPC echo pipe implementation used for DCERPC plumbing tests and basic server behavior validation.

Important APIs/types/functions: `_echo_AddOne`, `_echo_EchoData`, `_echo_SinkData`, `_echo_SourceData`, `_echo_TestSleep`, and several unsupported test calls that set `DCERPC_FAULT_OP_RNG_ERROR`.

Control flow: `_echo_AddOne` increments a scalar. `_echo_EchoData` allocates output data in `p->mem_ctx` and copies input bytes unless length is zero. `_echo_SinkData` discards input. `_echo_SourceData` returns a deterministic byte sequence `i & 0xff` of requested length. `_echo_TestSleep` sleeps synchronously for the requested seconds and returns zero. Other methods are deliberately fault stubs.

State/persistence behavior: stateless except for synchronous sleep and per-call talloc allocations. It does not persist data or maintain handles.

Dependencies/integration: depends on generated `ndr_echo` structures, RPC pipe memory context handling, Samba debug logging, and `smb_msleep`.

Risks/test signals: useful for testing NDR array marshalling, zero-length pointer behavior, RPC fault mapping, server blocking behavior during sleep, and memory allocation for arbitrary requested lengths. It is intentionally small but can reveal transport, generated boilerplate, and pipe dispatch regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/echo/srv_echo_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/epmapper/srv_epmapper.c -->
# sources/user-network-fs/samba/source3/rpc_server/epmapper/srv_epmapper.c

Purpose: endpoint mapper RPC server for resolving registered Samba RPC interfaces into endpoint towers through the local `epmdb.tdb` database.

Important APIs/types/functions: `_epm_Lookup`, `_epm_Map`, `_epm_LookupHandleFree`, `build_ep_list`, `build_ep_list_fn`, `build_ep_list_fill_iface`, `epm_map_get_towers`, and `epmapper_init_server`. Internal types include `dcesrv_ep_iface`, `rpc_eps`, and a lookup policy-handle state.

Control flow: initialization opens `lock_path("epmdb.tdb")` read-only. Lookup traverses every TDB record, validates null-terminated syntax-id keys and string-vector endpoint values, parses bindings, substitutes the local IPv4 address for wildcard/non-IP TCP hosts, builds endpoint towers, and stores cursor state in a policy handle. Each call returns up to `max_ents`, advances the in-memory cursor by pointer arithmetic, and closes the handle at exhaustion. Map validates the input tower transfer syntax, infers requested transport, fetches matching bindings for the requested interface, and returns towers similarly.

State/persistence behavior: persistent endpoint data lives in `epmdb.tdb`; per-client lookup/map progress is transient policy-handle state containing a talloc array of towers.

Dependencies/integration: uses TDB/db utilities, DCERPC binding parser/build-tower helpers, tsocket local address detection, generated epmapper NDR, and source3 policy-handle helpers.

Risks/test signals: malformed TDB records are ignored, but version filtering has permissive assignments in exact and major-only branches that may over-match. Tests should cover null-terminated record validation, TCP host substitution, paged lookup handles, map tower validation, unsupported insert/delete/mgmt calls, and empty/exhausted cursor behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/epmapper/srv_epmapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/eventlog/srv_eventlog_nt.c -->
# sources/user-network-fs/samba/source3/rpc_server/eventlog/srv_eventlog_nt.c

Purpose: Event Log RPC server implementation for opening, reading, clearing, querying, and writing records to Samba eventlog TDB files, plus server initialization that ensures backing registry keys exist.

Important APIs/types/functions: `EVENTLOG_INFO`, `elog_open`, `elog_close`, `elog_check_access`, `get_num_records_hook`, `sync_eventlog_params`, `_eventlog_OpenEventLogW`, `_eventlog_ReadEventLogW`, `_eventlog_ClearEventLogW`, `_eventlog_GetOldestRecord`, `_eventlog_GetNumRecords`, `_eventlog_GetLogInformation`, `evlog_report_to_record`, `_eventlog_ReportEventW`, and `eventlog_init_server`.

Control flow: open validates the requested log against `lp_eventlog_list`, opens the TDB as root, falls back to Application in some missing-file cases, checks file ACL access using a synthetic connection and `se_access_check`, creates a policy handle, syncs MaxSize/Retention from HKLM eventlog registry values, and prunes records. Read validates seek/sequential and direction flags, pulls records from the current or requested record number, NDR-encodes each `EVENTLOGRECORD`, respects caller buffer size, and advances `current_record`.

State/persistence behavior: policy handles own `EVENTLOG_INFO` and close TDBs through a destructor. Records and counters live in eventlog TDBs; retention/max-size settings are copied from registry into TDB keys. Clear reopens the TDB with truncate semantics when write access is granted.

Dependencies/integration: integrates eventlog library helpers, winreg internal RPC client calls, security descriptors, VFS ACL access, generated eventlog NDR, global messaging context, and `eventlog_init_winreg`.

Risks/test signals: access checks depend on filesystem ACLs plus a SYSTEM ACE, and root maps to the system token. Read buffer sizing and record pointer updates are protocol-sensitive. Many ANSI/backup/cluster methods are unimplemented fault stubs. Tests should cover open fallback, ACL denial, registry sync failure, zero-byte read size probing, forward/backward reads, clear permissions, record reporting, and server init key creation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/eventlog/srv_eventlog_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/eventlog/srv_eventlog_reg.c -->
# sources/user-network-fs/samba/source3/rpc_server/eventlog/srv_eventlog_reg.c

Purpose: initializes Windows-compatible eventlog registry keys used by the Event Log RPC server.

Important APIs/types/functions: `eventlog_init_winreg` opens `HKLM\SYSTEM\CurrentControlSet\Services\Eventlog`, enumerates existing subkeys, creates missing configured eventlog keys, and writes default values.

Control flow: the function opens the top-level Eventlog key through the internal winreg RPC client using the system session. It enumerates existing log subkeys, then for every configured log name from `lp_eventlog_list`, skips existing keys and creates missing keys. It writes `MaxSize`, `Retention`, `PrimaryModule`, `File`, and `Sources`, then creates a nested source-specific subkey with `CategoryCount` and `CategoryMessageFile`.

State/persistence behavior: persistent state is the Samba registry backend. Default values are 512 KiB max size and one week retention. The `File` value points at `%SystemRoot%\system32\config\<log>.tdb`.

Dependencies/integration: depends on generated winreg client stubs, `cli_winreg_int` helpers, Samba auth system session, messaging context, loadparm eventlog list, and registry policy handles.

Risks/test signals: status from several set-value calls is overwritten by later calls before being checked, so write failures can be masked unless the final call fails. The nested subkey name is formed by appending the log name again to the current key path. Tests should verify idempotent startup, exact registry values, missing top-level key behavior, configured logs with existing subkeys, and cleanup of opened handles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/eventlog/srv_eventlog_reg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/eventlog/srv_eventlog_reg.h -->
# sources/user-network-fs/samba/source3/rpc_server/eventlog/srv_eventlog_reg.h

Purpose: small public header for eventlog registry initialization.

Important APIs/types/functions: declares `bool eventlog_init_winreg(struct messaging_context *msg_ctx);` and guards it with `SRV_EVENTLOG_REG_H`.

Control flow: consumers include this header when they need to initialize the registry backing for eventlog RPC service startup. The main consumer in this subset is `srv_eventlog_nt.c`, which calls the function before invoking generated server initialization.

State/persistence behavior: the header does not own state, but its API implies writes to Samba's registry backend through the implementation.

Dependencies/integration: exposes only `struct messaging_context` by pointer and avoids pulling winreg implementation details into callers.

Risks/test signals: compile coverage should ensure the declaration matches `srv_eventlog_reg.c`. Startup tests for eventlog should indirectly validate the header-level contract.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/eventlog/srv_eventlog_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/fss/srv_fss_agent.c -->
# sources/user-network-fs/samba/source3/rpc_server/fss/srv_fss_agent.c

Purpose: File Server Remote VSS Protocol server implementation that coordinates shadow copy set lifecycle, snapshot creation/deletion through VFS hooks, exposed snapshot shares, state persistence, access checks, and sequence timers.

Important APIs/types/functions: `fss_global`, `fss_ntstatus_map`, `fss_unc_parse`, `fss_prune_stale`, `srv_fssa_start`, `fss_permitted`, `fss_seq_tout_set`, `_fss_SetContext`, `_fss_StartShadowCopySet`, `_fss_AddToShadowCopySet`, `_fss_PrepareShadowCopySet`, `_fss_CommitShadowCopySet`, `_fss_ExposeShadowCopySet`, `_fss_RecoveryCompleteShadowCopySet`, `_fss_AbortShadowCopySet`, `_fss_IsPathSupported`, `_fss_GetShareMapping`, `_fss_DeleteShareMapping`, and `sc_smap_unexpose`.

Control flow: clients must set a context, start a set, add one or more shares, optionally prepare, commit snapshots through `SMB_VFS_SNAP_CREATE`, expose committed snapshots by cloning share definitions into registry smbconf, query mappings, complete recovery, and later delete mappings. A single in-progress set is enforced. Timers clear unfinished state after message-sequence timeouts; successful operations restart timers with protocol-specific intervals.

State/persistence behavior: active state lives in `fss_global` and nested `fss_sc_set`/`fss_sc`/`fss_sc_smap` lists. Committed/exposed/recovered state is stored in `srv_fss.tdb` through `fss_state_store`. Exposed shares are persistent registry smbconf entries; snapshot paths are owned by the underlying VFS module. Optional startup pruning removes state and shares for missing snapshot paths.

Dependencies/integration: integrates Samba authorization tokens, Backup Operators/Administrators checks, VFS snapshot hooks, smbconf registry/file backends, share security cloning, global messaging for config updates and forced tree disconnects, generated FSRVP NDR, and private state helpers.

Risks/test signals: error mapping must match FSRVP/HRESULT expectations. Share parsing accepts UNC paths and truncates trailing path components. Registry transactions guard expose/unexpose, but share security cloning is outside that transaction. Tests should cover permission gates, illegal state transitions, timer cleanup, duplicate volume handling, snapshot VFS failures, expose rollback, persisted restart recovery, stale pruning, and delete behavior when multiple share mappings refer to one snapshot.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/fss/srv_fss_agent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/fss/srv_fss_private.h -->
# sources/user-network-fs/samba/source3/rpc_server/fss/srv_fss_private.h

Purpose: private data model and persistence API for the File Server Remote VSS Protocol server.

Important APIs/types/functions: defines `FSS_DB_NAME`, `struct fss_sc_smap`, `struct fss_sc`, `enum fss_sc_state`, `struct fss_sc_set`, `struct fss_global`, `fss_state_store`, and `fss_state_retrieve`.

Control flow: the structures encode the parent-child hierarchy used by `srv_fss_agent.c`: a global context owns shadow copy sets; each set owns shadow copies; each shadow copy owns share mappings. The state enum models the protocol lifecycle from started to recovered.

State/persistence behavior: `FSS_DB_NAME` is `srv_fss.tdb`. Stored state includes set IDs/state/context/counts, snapshot IDs/base volumes/snapshot paths/timestamps, and mapping names/comments/exposure flags. `fss_global` also tracks the current requested context and the sequence timer, which are runtime-only.

Dependencies/integration: depends on Samba GUID, talloc, tevent timer, NTSTATUS, and list-link conventions used by `DLIST_*` macros in the implementation.

Risks/test signals: count fields must remain synchronized with linked lists because retrieval validates expected child counts. The misspelled `FSS_SC_COMMITED` enumerator is part of the local API and must remain consistent across generated state serialization and agent logic. Tests should cover ABI/compile compatibility and persistence round trips for all state values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/fss/srv_fss_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/fss/srv_fss_state.c -->
# sources/user-network-fs/samba/source3/rpc_server/fss/srv_fss_state.c

Purpose: persistent storage layer for FSRVP server state, serializing and reconstructing the shadow copy set hierarchy in `srv_fss.tdb`.

Important APIs/types/functions: `fss_state_store`, `fss_state_retrieve`, `fss_state_sc_set_store`, `fss_state_sc_store`, `fss_state_smap_store`, matching retrieve helpers, `fss_state_retrieve_traverse`, and hierarchy rebuild helpers for sets, copies, and share maps.

Control flow: store opens/creates the TDB read-write, wipes existing contents, stores the version and set count, starts a transaction, and writes each set, child snapshot, and share map under path-like keys such as `sc_set/<set>/sc/<copy>/smap/<share>`. Retrieve opens read-only, validates the database version, traverses every record into flat lists based on key prefixes, then reconstructs parent-child ownership by matching key-path substrings and trimming keys down to GUID/share-name components.

State/persistence behavior: all persisted payloads are generated `fsrvp_state_*` NDR blobs. Empty optional fields such as uncommitted `sc_path` or missing comments are stored as empty strings and restored as `NULL`. The database is all-or-rewritten on every store.

Dependencies/integration: uses dbwrap/TDB, generated `ndr_fsrvp_state`, talloc ownership moves, GUID parsing, NTSTATUS mapping, and private FSS structures.

Risks/test signals: hierarchy reconstruction uses substring membership tests on stored key paths, so malformed keys can create false parent matches unless counts catch it. The traverse prefix checks are order-sensitive because `smap` keys also contain `sc`. Tests should cover missing DB as success-empty, unsupported version, corrupt NDR payloads, orphan records, inconsistent child counts, all state enum values, and atomic transaction failure paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/fss/srv_fss_state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/initshutdown/srv_initshutdown_nt.c -->
# sources/user-network-fs/samba/source3/rpc_server/initshutdown/srv_initshutdown_nt.c

Purpose: thin initshutdown RPC compatibility layer that delegates shutdown and abort requests to the winreg shutdown implementation.

Important APIs/types/functions: `_initshutdown_Init`, `_initshutdown_InitEx`, and `_initshutdown_Abort` translate initshutdown request structures into `winreg_InitiateSystemShutdownEx` or `winreg_AbortSystemShutdown`.

Control flow: `Init` copies hostname, message, timeout, force-apps, and reboot flags into a winreg shutdown-ex request with reason zero. `InitEx` does the same but preserves the caller-provided reason. `Abort` copies the server field into a winreg abort request. Each function immediately returns the delegated winreg result.

State/persistence behavior: this file holds no independent state. Any shutdown scheduling, cancellation, authorization, and side effects are owned by the winreg server routines it calls.

Dependencies/integration: includes generated initshutdown and winreg NDR headers plus winreg server compatibility declarations. It shares the active `pipes_struct` with delegated calls so auth, fault, and memory behavior come from the winreg implementation.

Risks/test signals: correctness depends on field-for-field thunking and preserving the reason only for `InitEx`. Tests should compare initshutdown and equivalent winreg behavior, including access denial, abort behavior, timeout/reboot flags, and generated boilerplate dispatch.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_server/initshutdown/srv_initshutdown_nt.c -->
