# Research: subset-b-009896

Grouped research for selected Samba `source3/winbindd` request handlers, child-process plumbing, internal winbind RPC server code, idmap setup, IRPC forwarding, and group/user enumeration helpers. Each section preserves the source path and is bounded by reconciliation markers for source-tree-aligned extraction.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_domain_info.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_domain_info.c

## Purpose
Implements the async `WINBINDD_DOMAIN_INFO` external command. It resolves a requested domain name without forcing full initialization, ensures the domain is initialized when necessary, and returns the domain's canonical name, alternate DNS name, SID, AD/native flags, and primary-domain flag.

## Important APIs, Types, And Control Flow
`struct winbindd_domain_info_state` holds a `winbindd_domain_ref` plus ping input/output fields. `winbindd_domain_info_send()` finds the domain with `find_domain_from_name_noinit()`, stores a stable domain ref, and completes immediately for already initialized domains. For uninitialized domains it sends `dcerpc_wbint_Ping_send()` through `dom_child_handle(domain)`; the callback `winbindd_domain_info_done()` checks both transport status and wbint result, revalidates the domain ref, and verifies that the ping caused initialization. `winbindd_domain_info_recv()` copies fields into `response->data.domain_info`.

## State And Persistence
State is temporary tevent/talloc request state. The only persistent mutation is indirect: pinging the domain child can initialize `struct winbindd_domain` fields and child/DC connection state. No file or database output is written here.

## Dependencies And Integration Points
Depends on `winbindd.h`, `string_wrappers.h`, global event context helpers, generated `ndr_winbind_c.h`, domain refs, `dom_child_handle()`, and the in-child `_wbint_Ping` implementation.

## Risks And Test Signals
Risks include stale domain refs while an async ping is outstanding, child ping success that still leaves `domain->initialized` false, and truncated fixed-size response strings. Test by querying initialized and uninitialized domains, unknown domains, killed domain children during ping, and verifying returned SID/alt-name/AD/primary fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_domain_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_dsgetdcname.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_dsgetdcname.c

## Purpose
Implements async `WINBINDD_DSGETDCNAME`, exposing Windows-style DC locator behavior to winbind clients. It translates libwbclient lookup flags, optionally parses a domain GUID, calls the locator child, and returns a `netr_DsRGetDCNameInfo` projection in the winbind response.

## Important APIs, Types, And Control Flow
`struct winbindd_dsgetdcname_state` stores an optional parsed GUID and returned `dc_info`. `winbindd_dsgetdcname_send()` null-terminates request strings, maps `WBC_LOOKUP_DC_*` flags through `get_dsgetdc_flags()`, parses `domain_guid` with `GUID_from_string()`, and calls `dcerpc_wbint_DsGetDcName_send()` on `locator_child_handle()`. `winbindd_dsgetdcname_done()` combines call status and server result with `any_nt_status_not_ok()`. `winbindd_dsgetdcname_recv()` copies DC UNC/address/type, domain GUID, domain/forest names, flags, and site names into fixed response fields.

## State And Persistence
Only async request-local state is kept. DC locator caching or network discovery state lives below `dsgetdcname()` and the locator child, not in this wrapper.

## Dependencies And Integration Points
Uses generated wbint client stubs, GUID utilities, debug macros, string wrappers, and `_wbint_DsGetDcName()` in `winbindd_dual_srv.c`, which calls Samba's `dsgetdcname()` helper.

## Risks And Test Signals
Flag translation completeness is the main compatibility risk. Invalid GUIDs are silently treated as absent unless they parse to a nonzero GUID. Test every `WBC_LOOKUP_DC_*` flag mapping, empty and malformed GUIDs, forced rediscovery, site-specific lookup, locator child failure, and response truncation for long DNS names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_dsgetdcname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_dual.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_dual.c

## Purpose
Provides winbind's parent/child process infrastructure. The parent forks per-domain, idmap, and locator children to isolate blocking network/domain work, multiplexes async requests through queues, relays process-control messages, and manages child reinitialization, online/offline state, trust password rotation, signal handling, and cache flushing.

## Important APIs, Types, And Control Flow
`wb_child_request_send/recv()` serializes one request to one child over a socketpair using `wb_simple_trans_send()`, preserving the request when callers abandon an in-flight transaction. `wb_domain_request_send/recv()` queues requests per domain, picks the child with the shortest queue, initializes uninitialized domains via `wbint_InitConnection`, optionally obtains a DC with `wb_dsgetdcname_send()`, then delegates to `wb_child_request_send()`. `setup_child()` initializes a `winbindd_child` queue, log path, socket sentinel, domain pointer, and internal wbint binding handle. `fork_domain_child()` creates the socketpair, forks, reinitializes messaging/logging/db state in the child, registers child message handlers, starts domain online/setup timers, and enters the tevent loop with `child_handler()`. Message handlers relay debug, reload, disconnect, online/offline, IP-dropped, dump-domain, and status requests across parent and children.

## State And Persistence
Maintains child PIDs, sockets, monitor fds, per-child queues, per-domain queues, log file names, domain initialized/online/startup fields, lockout-policy timers, machine-password-change timers, and inherited messaging registrations. It unlinks the winbindd socket and PID file only on parent termination. Machine-password changes update secrets through lower-level trust code.

## Dependencies And Integration Points
Integrates with tevent queues/signals/fds, Samba messaging, domain list management, idmap and locator children, generated wbint binding handles, winbind cache, connection manager, passdb/secrets, netlogon credential code, and OS socket/fork primitives.

## Risks And Test Signals
High-risk areas are orphaned requests, child death while queued, socket closure detection, domain queue starvation, stale domain pointers after reload, fork reinitialization leakage, timer races in clustered password changes, and online/offline propagation. Test with slow DC calls, child kill/restart, SIGHUP/reload, SIGTERM cleanup, multiple domain children, abandoned client requests, offline logon transitions, machine password expiry, and debug traceid propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_dual.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_dual_ndr.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_dual_ndr.c

## Purpose
Implements the internal parent-to-child wbint transport using Samba's NDR/DCERPC infrastructure without full network DCERPC fragmentation. It lets parent code call generated `dcerpc_wbint_*` stubs while actually sending a compact `WINBINDD_DUAL_NDRCMD` request over the winbind child socket.

## Important APIs, Types, And Control Flow
`wbint_binding_handle()` builds a `dcerpc_binding_handle` with custom `wbint_bh_ops`. `wbint_bh_raw_call_send()` checks connection state, serves cache hits with `wcache_fetch_ndr()`, wraps opnum and marshalled input in `struct winbindd_request`, and dispatches either to `wb_child_request_send()` for special children or `wb_domain_request_send()` for domain children. Completion callbacks copy response extra data into `out_data`; domain calls also store successful replies with `wcache_store_ndr()`. `winbindd_dual_ndrcmd()` runs in a child: it creates an internal NCACN connection and dcesrv connection, sets socket-derived local/remote addresses, dispatches the generated server call via `dcesrv_call_dispatch_local()`, and moves the reply blob into `state->response`.

## State And Persistence
Binding state holds either a domain or child pointer plus the synthetic binding. Domain calls may persist NDR responses in winbind cache. Child-side dispatch uses stackframe/talloc lifetime and does not itself write files.

## Dependencies And Integration Points
Depends on generated `ndr_winbind`, DCERPC server core, RPC server config, `wb_domain_request`, `wb_child_request`, winbind cache NDR helpers, tsocket address conversion, and global dcesrv context callbacks.

## Risks And Test Signals
`set_timeout()` is a stub, so higher-level timeout expectations may not apply. Opnum bounds rely on generated table callers. Risks include cache coherency for NDR replies, invalid response lengths, stale domain refs, and local dcesrv endpoint discovery failure. Test cache hit/miss behavior, idmap/locator/domain binding paths, child socket peer address failures, generated wbint call round-trips, and malformed/oversized NDR payloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_dual_ndr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_dual_srv.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_dual_srv.c

## Purpose
Implements the in-child server side of the wbint/winbind internal RPC interfaces. It exposes SID/name lookup, idmap translation/allocation, NSS info, token/group queries, DC locator, trust account operations, netlogon/LSA forwarding helpers, forest trust maintenance, trusted-domain listing, and name normalization to the parent and IRPC frontends.

## Important APIs, Types, And Control Flow
Simple wbint calls include `_wbint_Ping`, `_wbint_InitConnection`, `_wbint_LookupSid`, `_wbint_LookupName`, `_wbint_LookupSids`, group/alias/member queries, sequence number, `DsGetDcName`, and normalization map/unmap. Idmap calls translate between domain RID batches and Unix IDs via idmap domain methods, allocate UIDs/GIDs, and enforce configured id ranges. Trust/netlogon calls include `_wbint_CheckMachineAccount`, `_wbint_ChangeMachineAccount`, `_wbint_PingDc`, `_winbind_DsrUpdateReadOnlyServerDnsRecords`, `_winbind_SamLogon`, `_winbind_LogonControl`, `_winbind_GetForestTrustInformation`, and `_winbind_SendToSam`. Many network operations call `reset_cm_connection_on_error()` and retry once after invalidating connection state.

## State And Persistence
Mutates the child domain's `dcname`, `force_dc`, initialized flags, connection manager state, and netlogon reauth flags. Trust password changes and forest trust updates persist via passdb/secrets or local LSA RPCs. Cache-backed lookup calls read/write through `wb_cache_*` layers outside this file.

## Dependencies And Integration Points
Integrates with `wb_child_domain()`, idmap backend APIs, winbind cache, netlogon credential client, connection manager, passdb, local LSA, DSDB forest trust helpers, generated NDR scompat server code, and Samba RPC client/server infrastructure.

## Risks And Test Signals
Risks include inconsistent NTSTATUS/WERROR layering, partial idmap mappings, trust-password races, forest-trust update side effects, retry loops that hide connection churn, and operations that require the child to have a valid domain. Test with remote and internal domains, unmapped IDs, out-of-range idmap results, DC disconnect/reconnect, expired trust passwords, RODC DNS update, SamLogon validation levels 3/6, LogonControl modes, forest-trust update flags, and name normalization round-trips.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_dual_srv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_endgrent.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_endgrent.c

## Purpose
Implements async `WINBINDD_ENDGRENT`, the end-of-enumeration command for group database iteration. It releases per-client group enumeration state held on the winbind client object.

## Important APIs, Types, And Control Flow
`winbindd_endgrent_send()` creates a trivial tevent request, logs the client command, frees `cli->grent_state` with `TALLOC_FREE()`, marks the request done, and posts it. `winbindd_endgrent_recv()` only logs completion and returns `NT_STATUS_OK`.

## State And Persistence
The only state change is freeing `winbindd_cli_state.grent_state`. This can affect any outstanding `GETGRENT` request using the same client state; `winbindd_getgrent.c` explicitly detects that race and reports `NT_STATUS_INVALID_PARAMETER`.

## Dependencies And Integration Points
Depends on `winbindd.h`, tevent request conventions, and the enumeration state allocated by setgrent/getgrent code elsewhere.

## Risks And Test Signals
The handler always returns success after request creation, even if no enumeration was active. Test normal `setgrent/getgrent/endgrent`, repeated `endgrent`, `endgrent` before enumeration, and an interleaved end while a batch `GETGRENT` is outstanding.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_endgrent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_endpwent.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_endpwent.c

## Purpose
Implements async `WINBINDD_ENDPWENT`, the end-of-enumeration command for passwd/user iteration. It releases per-client passwd enumeration state.

## Important APIs, Types, And Control Flow
`winbindd_endpwent_send()` allocates a dummy tevent state, logs the command, frees `cli->pwent_state`, completes the request, and posts it to the caller's event context. `winbindd_endpwent_recv()` logs completion and returns `NT_STATUS_OK`.

## State And Persistence
Only `winbindd_cli_state.pwent_state` is cleared. No global cache or persistent database is modified.

## Dependencies And Integration Points
Depends on `winbindd.h` and the user-enumeration state consumed by `wb_next_pwent_send()` in `winbindd_getpwent.c`.

## Risks And Test Signals
Behavior is intentionally idempotent from the client perspective, but interleaving with in-flight `GETPWENT` can invalidate the running enumeration. Test repeated end calls, end without set, end after partial enumeration, and end during a large domain enumeration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_endpwent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_getdcname.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_getdcname.c

## Purpose
Implements legacy async `WINBINDD_GETDCNAME`. It asks the DC locator for a domain controller and returns only the stripped hostname in `response->data.dc_name`.

## Important APIs, Types, And Control Flow
`struct winbindd_getdcname_state` holds returned `netr_DsRGetDCNameInfo`. `winbindd_getdcname_send()` null-terminates `request->domain_name`, logs, and calls `wb_dsgetdcname_send()` with no GUID/site/flags. `winbindd_getdcname_done()` receives `dcinfo`. `winbindd_getdcname_recv()` handles errors and copies `strip_hostname(dcinfo->dc_unc)` into the fixed response field.

## State And Persistence
No local persistent state. DC locator state and cache are delegated to `wb_dsgetdcname_*`.

## Dependencies And Integration Points
Uses winbind request/response structures, `wb_dsgetdcname_send/recv`, generated netlogon types, and string wrapper helpers.

## Risks And Test Signals
Risks are primarily legacy semantics: only the hostname is returned, and no locator flags are exposed. Test unknown domains, locator failure, returned UNC with leading backslashes, very long hostnames, and parity with `DSGETDCNAME` for default lookup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_getdcname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_getgrent.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_getgrent.c

## Purpose
Implements async batched `WINBINDD_GETGRENT` for enumerating group records from a client-specific enumeration cursor.

## Important APIs, Types, And Control Flow
`winbindd_getgrent_send()` requires `cli->grent_state`, caps the requested batch at 500 groups, allocates arrays for `struct winbindd_gr` and member databases, and starts `wb_next_grent_send()`. `winbindd_getgrent_done()` loops until no more entries, the batch is full, an error occurs, or `endgrent` freed the cursor. `winbindd_getgrent_recv()` converts each group's member db via `winbindd_print_groupmembers()`, lays out group structs followed by comma-separated member strings in one extra-data blob, and updates offsets and response length.

## State And Persistence
Consumes and may free `cli->grent_state`. Temporary per-group member db contexts are freed after serialization. No persistent database is modified.

## Dependencies And Integration Points
Depends on enumeration helpers `wb_next_grent_*`, `lp_winbind_expand_groups()`, and `winbindd_print_groupmembers()` from `winbindd_group.c`.

## Risks And Test Signals
The packed extra-data layout is sensitive to offset/length mistakes. An empty member database allocates zero bytes and leaves an empty string assumption to consumers. Test zero requested entries, no active cursor, exact batch limit, large member lists, no-more-entries cleanup, and `endgrent` interleaving.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_getgrent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_getgrgid.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_getgrgid.c

## Purpose
Implements async `WINBINDD_GETGRGID`, resolving a Unix GID to a winbind group record with members.

## Important APIs, Types, And Control Flow
The send path builds a single `struct unixid` with `ID_TYPE_GID` and calls `wb_xids2sids_send()`. `winbindd_getgrgid_gid2sid_done()` rejects a null SID, then calls `wb_getgrsid_send()` to obtain domain/name/gid/member db. `winbindd_getgrgid_done()` normalizes the domain/name through `dcerpc_wbint_NormalizeNameMap_send()` on the idmap child. `winbindd_getgrgid_normalize_done()` chooses mapped, renamed, or original full group name. The recv path fills `response->data.gr`, serializes members with `winbindd_print_groupmembers()`, and appends member data to `extra_data`.

## State And Persistence
Reads idmap and group/member data through helper layers. It depends on parent idmap setup already being valid when calling `idmap_child_handle()`.

## Dependencies And Integration Points
Uses idmap xids-to-sids, `wb_getgrsid`, wbint name normalization, `fill_domain_username_talloc()`, and group member printing.

## Risks And Test Signals
The send function logs `request->data.gid` but initializes from `request->data.uid`, which deserves regression coverage against the request union layout. Risks also include null-SID handling, normalization fallbacks, and member serialization. Test mapped/unmapped GIDs, ID_TYPE_BOTH cases, renamed normalized names, empty member lists, and idmap child setup failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_getgrgid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_getgrnam.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_getgrnam.c

## Purpose
Implements async `WINBINDD_GETGRNAM`, resolving a group name to a POSIX group structure and member list.

## Important APIs, Types, And Control Flow
`winbindd_getgrnam_send()` copies and null-terminates the requested group, then runs `wb_parent_idmap_setup_send()` before talking to the idmap child. The initialized callback calls `NormalizeNameUnmap`; the unmap callback parses namespace/domain/group with `parse_domain_user()`, defaults empty/local domains to `get_global_sam_name()`, and calls `wb_lookupname_send()`. `lookupname_done()` accepts group, alias, well-known group, user, and computer SID types to allow ID_TYPE_BOTH-backed group records, then calls `wb_getgrsid_send()`. After `NormalizeNameMap`, recv fills `struct winbindd_gr` and serializes members.

## State And Persistence
Maintains only request-local strings, SID, gid, and member db. Parent idmap setup can initialize the global idmap child/config cache.

## Dependencies And Integration Points
Uses parent idmap setup, wbint normalization on the idmap child, name parsing, `wb_lookupname`, `wb_getgrsid`, `lp_winbind_expand_groups()`, and `winbindd_print_groupmembers()`.

## Risks And Test Signals
Risks include name mapping/unmapping mismatches, default-domain behavior for local aliases, accepting user/computer SID types, and output name formatting differences when normalization returns `NT_STATUS_FILE_RENAMED`. Test domain-qualified and unqualified names, local SAM aliases, normalized names, users mapped as both, unsupported SID types, and huge member lists.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_getgrnam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_getgroups.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_getgroups.c

## Purpose
Implements async `WINBINDD_GETGROUPS`, returning the Unix GID list for a named user's token.

## Important APIs, Types, And Control Flow
The send path runs parent idmap setup, unmaps normalized names, parses namespace/domain/user, and looks up the user SID with `LOOKUP_NAME_NO_NSS`. `winbindd_getgroups_lookupname_done()` calls `wb_gettoken_send(..., true)` to include the user SID and groups. `winbindd_getgroups_gettoken_done()` maps the complete SID token with `wb_sids2xids_send()`. The mapping callback converts acceptable `ID_TYPE_GID` and `ID_TYPE_BOTH` entries to GIDs, permits the user SID only if not an inappropriate UID, logs skipped entries, shrinks the gid array, and completes. Recv returns the gid array in extra data.

## State And Persistence
No persistent writes. It depends on idmap setup cache and token/cache state below helper calls.

## Dependencies And Integration Points
Uses idmap setup, wbint normalization, `parse_domain_user`, `wb_lookupname`, `wb_gettoken`, `wb_sids2xids`, and `passdb/lookup_sid.h` for `LOOKUP_NAME_NO_NSS`.

## Risks And Test Signals
Security-sensitive risk is skipped IDs from DENY ACE-related groups; the code logs warnings when idmap types are unusable. Test unmapped groups, UID-only mappings in group positions, ID_TYPE_BOTH, no groups, large tokens, normalized UPN/domain names, and `STATUS_SOME_UNMAPPED` conversion to success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_getgroups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_getpwent.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_getpwent.c

## Purpose
Implements async batched `WINBINDD_GETPWENT`, returning up to 500 passwd entries from a client-specific user enumeration cursor.

## Important APIs, Types, And Control Flow
`winbindd_getpwent_send()` checks `cli->pwent_state`, caps requested entries at 500, allocates a `struct winbindd_pw` array, and starts `wb_next_pwent_send()`. `winbindd_getpwent_done()` loops until no more users, batch full, error, or `endpwent` removes the cursor. `winbindd_getpwent_recv()` frees the cursor on errors, returns `NO_MORE_ENTRIES` for empty batches, logs entries, moves the user array into response extra data, and updates `response->data.num_entries` and length.

## State And Persistence
Consumes and may free `cli->pwent_state`. It does not persist anything itself.

## Dependencies And Integration Points
Depends on `wb_next_pwent_send/recv()` and the surrounding setpwent/endpwent command lifecycle.

## Risks And Test Signals
Packed output is a raw array of `struct winbindd_pw`, so ABI expectations matter between daemon and client library. Test zero requested entries, inactive cursor, large domains with multiple batches, no-more cleanup, NSS enumeration-disabled behavior through setup path, and `endpwent` interleaving.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_getpwent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_getpwnam.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_getpwnam.c

## Purpose
Implements async `WINBINDD_GETPWNAM`, resolving a username to a `struct winbindd_pw` passwd response.

## Important APIs, Types, And Control Flow
The send path copies the username, runs `wb_parent_idmap_setup_send()`, unmaps normalized names through `NormalizeNameUnmap`, parses namespace/domain/user, and performs `wb_lookupname_send()` with `LOOKUP_NAME_NO_NSS`. The lookup callback treats `SID_NAME_UNKNOWN` as unmapped and calls `wb_getpwsid_send()` for the resolved SID. `winbindd_getpwnam_done()` receives the passwd record, and recv copies `state->pw` into `response->data.pw`.

## State And Persistence
Only request-local state plus indirect idmap setup initialization. No database writes.

## Dependencies And Integration Points
Uses parent idmap setup, idmap child normalization, `parse_domain_user`, `wb_lookupname`, `wb_getpwsid`, generated wbint normalization stubs, and lookup flags from passdb.

## Risks And Test Signals
Risks include NSS recursion if flags change, normalization/unmap mismatches, malformed domain-user syntax, and no explicit SID type filtering before `wb_getpwsid`. Test domain-qualified, UPN, normalized, unmapped, computer/user names, malformed strings, idmap child failures, and long passwd fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_getpwnam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_getpwsid.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_getpwsid.c

## Purpose
Implements async `WINBINDD_GETPWSID`, resolving a textual SID directly to a passwd record.

## Important APIs, Types, And Control Flow
`winbindd_getpwsid_send()` null-terminates `request->data.sid`, parses it with `string_to_sid()`, rejects invalid strings with `NT_STATUS_INVALID_PARAMETER`, and starts `wb_getpwsid_send()`. `winbindd_getpwsid_done()` receives the helper result. `winbindd_getpwsid_recv()` copies the passwd record to `response->data.pw`.

## State And Persistence
No persistent state. SID-to-passwd mapping and any NSS/idmap cache effects are handled in `wb_getpwsid`.

## Dependencies And Integration Points
Uses `security.h` SID parsing, winbind async passwd helper, and standard tevent request response conventions.

## Risks And Test Signals
Test invalid SID syntax, unknown SIDs, user vs non-user SID behavior, SID mapped as ID_TYPE_BOTH, and long generated passwd names/gecos/dirs. The main wrapper risk is returning useful diagnostics without leaking malformed input into downstream helpers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_getpwsid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_getpwuid.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_getpwuid.c

## Purpose
Implements async `WINBINDD_GETPWUID`, resolving a Unix UID to a passwd record through idmap and SID lookup.

## Important APIs, Types, And Control Flow
`winbindd_getpwuid_send()` builds a single `struct unixid` with `ID_TYPE_UID` and calls `wb_xids2sids_send()`. `uid2sid_done()` receives a SID pointer, rejects null SID as `NT_STATUS_NO_SUCH_USER`, then calls `wb_getpwsid_send()` to populate `state->pw`. `winbindd_getpwuid_done()` validates the helper result. Recv copies the passwd record into the winbind response.

## State And Persistence
Only request-local state. Reads idmap and account data through helpers and caches outside this file.

## Dependencies And Integration Points
Uses `wb_xids2sids`, `wb_getpwsid`, `dom_sid` helpers, and winbind response structures.

## Risks And Test Signals
Test unmapped UIDs, null SID returns, ID_TYPE_BOTH mappings, idmap backend failures, user records with missing NSS attributes, and request union correctness for UID fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_getpwuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_getsidaliases.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_getsidaliases.c

## Purpose
Implements async `WINBINDD_GETSIDALIASES`, returning local/domain alias SIDs for an input domain SID and optional SID list.

## Important APIs, Types, And Control Flow
The send path parses `request->data.sid`, finds the owning domain with `find_domain_from_sid_noinit()`, optionally validates and parses newline/comma SID list extra data via `parse_sidlist()`, then calls `wb_lookupuseraliases_send(domain, num_sids, sids)`. The callback stores alias RID results. Recv composes full alias SIDs from the base domain SID and each returned RID with `sid_compose()`, appends textual SIDs to a newline-separated extra-data string, and sets `num_entries`.

## State And Persistence
No persistent local state. Alias lookup reads cache/domain state in lower layers.

## Dependencies And Integration Points
Uses SID parsing, domain lookup by SID, `wb_lookupuseraliases`, and response extra-data string conventions.

## Risks And Test Signals
Risks include malformed or non-null-terminated extra SID lists, unknown base domain SIDs, memory growth while appending large alias lists, and base-SID/RID composition assumptions. Test invalid SIDs, empty SID lists, no aliases, many aliases, trusted-domain aliases, and extra data lacking a final NUL.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_getsidaliases.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_getuserdomgroups.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_getuserdomgroups.c

## Purpose
Implements async `WINBINDD_GETUSERDOMGROUPS`, returning the domain group SID token for a user SID without aliases.

## Important APIs, Types, And Control Flow
`winbindd_getuserdomgroups_send()` parses the textual SID and calls `wb_gettoken_send(state, ev, &sid, false)`. The callback receives `num_sids` and `sids`. Recv formats each SID into a newline-separated string in response extra data and sets `num_entries`.

## State And Persistence
No local persistent state. Token generation and caching occur in `wb_gettoken`.

## Dependencies And Integration Points
Uses SID parsing, `wb_gettoken`, `dom_sid_str_buf`, and winbind extra-data string response conventions.

## Risks And Test Signals
Test invalid SID syntax, unknown users, users with no domain groups, nested groups, large tokens, and ensure `include_aliases=false` differs from `GETUSERSIDS`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_getuserdomgroups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_getusersids.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_getusersids.c

## Purpose
Implements async `WINBINDD_GETUSERSIDS`, returning the complete SID token for a user SID, including aliases.

## Important APIs, Types, And Control Flow
`winbindd_getusersids_send()` null-terminates and parses `request->data.sid`, then calls `wb_gettoken_send(..., true)`. The callback stores the returned SID array. Recv builds a newline-separated SID string in response extra data and updates `num_entries`.

## State And Persistence
No persistent local state. Token expansion and domain/cache access are delegated to `wb_gettoken`.

## Dependencies And Integration Points
Uses security SID helpers, token helper APIs, and winbind textual extra-data output format.

## Risks And Test Signals
Test malformed SIDs, unknown users, alias inclusion, nested memberships, very large tokens, and memory failure during string accumulation. Compare with `GETUSERDOMGROUPS` to verify alias behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_getusersids.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_gpupdate.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_gpupdate.c

## Purpose
Schedules and runs Group Policy update commands from winbindd for machine policy and one-shot user policy application.

## Important APIs, Types, And Control Flow
`gpupdate_interval()` returns 90 minutes plus up to 30 minutes of random jitter. `gpupdate_init()` loads an S3 loadparm context, checks `lpcfg_apply_group_policies()`, and schedules an immediate timer. `gpupdate_callback()` invokes the configured `gpo update command` through `samba_runcmd_send()` with `--target=Computer` and `--machine-pass`, then schedules the next jittered timer. `gpupdate_user_init(user)` checks the same config and runs a user-targeted command immediately with `-U user`. `gpupdate_cmd_done()` logs nonzero command exit status.

## State And Persistence
Holds a talloc context and loadparm context for recurring machine timers. Actual policy persistence is performed by the external gpupdate command, not this file.

## Dependencies And Integration Points
Depends on global event context, loadparm, `samba_runcmd`, configured `gpo update command`, smb.conf path discovery, and winbind login/session paths that call user init.

## Risks And Test Signals
Risks include leaked contexts on early returns, missing NULL checks after `loadparm_init_s3()` in user path, external command failure visibility, and no recurring user timer despite the TODO. Test policy disabled, command missing/failing, custom smb.conf path, random interval bounds, machine timer rescheduling, and user invocation quoting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_gpupdate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_group.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_group.c

## Purpose
Provides shared serialization of group-member databases into the comma-separated member string used by winbind group responses.

## Important APIs, Types, And Control Flow
`winbindd_print_groupmembers()` traverses a `db_context` twice. `getgr_calc_memberlen()` counts records and sums stored value sizes while detecting overflow by checking wrapped length. It then allocates a buffer of the summed size. `getgr_unparse_members()` copies each stored value except its trailing NUL, appends a comma, and advances an offset. After traversal, the final comma is replaced by NUL when the computed length is nonzero. It returns the member count and allocated result buffer.

## State And Persistence
Reads a transient dbwrap database of member names. Does not modify the database or persist output beyond caller-owned talloc memory.

## Dependencies And Integration Points
Used by `GETGRENT`, `GETGRGID`, and `GETGRNAM` response paths. Depends on dbwrap traversal/value APIs and talloc allocation.

## Risks And Test Signals
If there are zero members, it allocates a zero-length buffer and does not explicitly store a NUL; consumers must tolerate that. Risks also include malformed record values without trailing NUL and overflow handling that returns traversal success. Test empty groups, one member, many members, long names, non-NUL values, traversal failure, and allocation failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_group.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_idmap.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_idmap.c

## Purpose
Owns parent-side setup for the dedicated idmap child and builds a cached map from idmap configuration ranges to domain names/SIDs. This lets parent code split SID/Unix-ID mapping work by idmap domain before using the idmap child binding.

## Important APIs, Types, And Control Flow
`init_idmap_child()` allocates `static_idmap_child` and starts `wb_parent_idmap_setup_send()` as an optimization. `idmap_child()`, `is_idmap_child()`, `idmap_child_pid()`, and `idmap_child_handle()` expose the singleton child; the handle asserts setup produced at least one domain. `wb_parent_idmap_setup_send/recv()` serializes setup through `static_parent_idmap_config.queue`. The first waiter creates a default passdb domain entry for `get_global_sam_name()`, scans `idmap config DOMAIN : range` values with `lp_scan_idmap_domains()`, then resolves each non-wildcard domain name to a domain SID via `wb_lookupname_send()`. On completion it calls `setup_child(NULL, static_idmap_child, "log.winbindd", "idmap")` and marks the config initialized.

## State And Persistence
Maintains process-global `static_idmap_child` and `static_parent_idmap_config` with domain ranges, names, SIDs, queue, and initialized flag. No disk persistence; values derive from smb.conf and name lookups.

## Dependencies And Integration Points
Integrates with idmap config parsing, domain name lookup, child setup in `winbindd_dual.c`, global event context, passdb lookup flags, and callers that require `idmap_child_handle()`.

## Risks And Test Signals
Risks include stale config after smb.conf reload, ignored malformed ranges, wildcard domain SID omission, setup failure cleanup, and queue lifetime subtleties where the queue subrequest is held until recv. Test multiple concurrent setup callers, invalid ranges, low>high ranges, duplicate domains, wildcard config, lookup failures, reload behavior, and idmap child startup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_idmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_irpc.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_irpc.c

## Purpose
Registers and implements winbind's IRPC entry points, bridging source4-style internal messaging callers to winbind child/domain RPC operations and local async lookup helpers.

## Important APIs, Types, And Control Flow
`winbind_imessaging_context()` lazily creates an imessaging context using the global messaging server id and a loadparm context allocated on NULL to survive fork cleanup. `wb_irpc_forward_rpc_call()` forwards a generated RPC request to a domain child binding, sets the child binding timeout, marks `msg->defer_reply`, and replies in `wb_irpc_forward_callback()`. Forwarded operations include RODC DNS update, SamLogon, LogonControl, forest trust information, and SendToSam after domain routing/validation. LSA IRPC calls are implemented locally: `LookupSids3` calls `wb_lookupsids`; `LookupNames4` parses qualified names, runs parallel `wb_lookupname` calls, resolves domain SIDs, and builds LSA translated SID arrays. `wb_irpc_GetDCName()` wraps `wb_dsgetdcname`.

## State And Persistence
Keeps a static imessaging context. Individual IRPC calls allocate state under the message and send async replies. Forest trust or netlogon persistence occurs only in forwarded child server implementations.

## Dependencies And Integration Points
Uses IRPC registration macros, generated winbind/LSA/netlogon NDR types, global messaging/event contexts, domain routing helpers, wb lookup helpers, and child binding handles.

## Risks And Test Signals
Risks include missing async replies on early errors after partial subrequests, timeout mismatch, accepting only fully qualified LookupNames4 inputs, domain routing subtleties on DCs, and multiple pending name lookups racing to reply on failure. Test all registered IRPC opnums, unknown domains with authoritative flags, UPN and DOMAIN\\name parsing, partial LSA mappings, DC member vs AD DC roles, and child failure during deferred reply.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_irpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_list_groups.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_list_groups.c

## Purpose
Implements async `WINBINDD_LIST_GROUPS`, returning comma-separated fully qualified group names across all domains or one requested domain.

## Important APIs, Types, And Control Flow
`winbindd_list_groups_send()` respects `WBFLAG_FROM_NSS` plus `lp_winbind_enum_groups()` by returning an empty success when NSS enumeration is disabled. It selects either the requested domain or all domains from `domain_list()`, stores each as a `winbindd_domain_ref`, and fires parallel `dcerpc_wbint_QueryGroupList_send()` calls through each domain child handle. `winbindd_list_groups_done()` receives each domain result, validates the domain ref, logs and suppresses per-domain failures by zeroing that domain's group count, and completes after all subrequests return. Recv first computes output length using `fill_domain_username_talloc()`, then builds a comma-separated string and sets `num_entries`.

## State And Persistence
Only request-local arrays of domain refs and returned `wbint_Principals`. It may initialize/contact domain children indirectly through wbint calls but writes no persistent data.

## Dependencies And Integration Points
Uses domain list/ref APIs, generated wbint QueryGroupList, `dom_child_handle()`, winbind enum group configuration, and the internal `_wbint_QueryGroupList()` server.

## Risks And Test Signals
If zero groups are returned, `result[len-1] = '\0'` underflows because `len` is zero; empty-domain and enumeration-disabled paths need attention. Other risks include partial-domain failure being hidden, stale domain refs, and large output memory use. Test no domains, one empty domain, NSS enum disabled, requested unknown domain, mixed success/failure domains, and very large group lists.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_list_groups.c -->
