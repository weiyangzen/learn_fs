# subset-b-009894 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_lookupsids.c -->
# sources/user-network-fs/samba/source3/winbindd/wb_lookupsids.c

Purpose: implements the async bulk SID-to-name lookup helper used by winbindd request handlers and idmap helper paths. It takes an ordered SID array and returns an `lsa_RefDomainList` plus an `lsa_TransNameArray` whose name indexes match the input SID indexes.

Important APIs and types: `wb_lookupsids_send/recv` are the public tevent API. `struct wb_lookupsids_state` owns input SIDs, per-domain bulk queues, single-SID fallback indexes, temporary `LookupRids`/`LookupSids` outputs, and final LSA result arrays. `struct wb_lookupsids_domain` groups SIDs by `winbindd_domain_ref`, stores `lsa_SidArray`, and tracks original indexes. Helpers include `wb_lookupsids_bulk`, `wb_lookupsids_get_domain`, `wb_lookupsids_find_dom_idx`, and `wb_lookupsids_move_name`.

Control flow: `wb_lookupsids_send` preallocates result arrays sized to `num_sids`, classifies each SID into a bulk domain bucket or the `single_sids` fallback list, then calls `wb_lookupsids_next`. Bulk local SAM SIDs use `dcerpc_wbint_LookupRids_send`; other accepted domain SIDs use `dcerpc_wbint_LookupSids_send`; fallback SIDs use `wb_lookupsid_send` one at a time. Completion callbacks splice temporary names into the final result arrays with preserved input indexes and advance to the next domain or single SID. `recv` validates that the output name count equals the input SID count before moving results to the caller.

State and persistence: runtime state is talloc-scoped to the request. The file does not persist directly, but it consults domain lists, server role flags, local SAM SID/name state, and domain references that can become stale. Domain identity in final `lsa_RefDomainList` is deduplicated by SID.

Dependencies and integration points: depends on `winbindd.h`, generated `ndr_winbind_c.h`, SID utility helpers, machine SID/passdb state, LSA structures, and child RPC handles from `dom_child_handle`. It integrates with `wb_sids2xids.c` when type hints are needed and with winbindd LOOKUPSIDS command handlers elsewhere.

Risks: preserving original indexes is critical; a mismatch returns `NT_STATUS_INTERNAL_ERROR` only at `recv`, so callback logic must keep counts aligned. `wb_lookupsids_get_domain` has a suspicious allocation check using `domains->sids.sids` immediately after assigning `domain->sids.sids`, which deserves review because it can reference the first element rather than the new bucket. Bulk eligibility changes can leak special local/well-known SIDs to a DC or miss batching opportunities. Stale domain refs are silently skipped in domain mode, potentially producing fewer names and tripping final count validation.

Test signals: exercise zero SID input, all local SAM SIDs, trusted-domain SIDs, builtin/well-known/unix SIDs that should take fallback, mixed mapped/unmapped results, stale domain refs, and lookup result arrays whose counts do not match requested SIDs. Regression tests should assert output ordering against input ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_lookupsids.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_lookupuseraliases.c -->
# sources/user-network-fs/samba/source3/winbindd/wb_lookupuseraliases.c

Purpose: provides an async wrapper for looking up domain-local alias RIDs that contain a set of user/group SIDs.

Important APIs and types: `wb_lookupuseraliases_send/recv`; `struct wb_lookupuseraliases_state` containing the input `wbint_SidArray` and output `wbint_RidArray`.

Control flow: `send` logs the target domain and SIDs, builds a `wbint_SidArray` by borrowing the caller's SID memory via `discard_const_p`, then calls `dcerpc_wbint_LookupUserAliases_send` on the domain child handle. The callback receives both transport and operation result status with `any_nt_status_not_ok`. `recv` exposes `num_aliases` and moves `state->rids.rids` to the caller.

State and persistence: no persistent state; all output is talloc-owned by the request. The input SID array is borrowed, so the caller's SID memory must outlive the async request.

Dependencies and integration points: generated winbind RPC client stubs, `dom_child_handle(domain)`, SID formatting helpers, and the backend method contract represented in `struct winbindd_methods.lookup_useraliases`.

Risks: input lifetime is important because the state stores a non-owning pointer to caller-provided SIDs. Errors collapse transport and result status into one `NTSTATUS`, so tests should cover both. Large SID arrays rely on child RPC limits rather than local chunking.

Test signals: successful alias lookup with multiple SIDs, empty SID list behavior if callers permit it, child transport failure, operation failure, and validation that returned RIDs are moved under the caller's memory context.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_lookupuseraliases.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_lookupusergroups.c -->
# sources/user-network-fs/samba/source3/winbindd/wb_lookupusergroups.c

Purpose: implements async user group SID lookup for a single user SID, with a cache-first path before dispatching to the relevant domain child.

Important APIs and types: `wb_lookupusergroups_send/recv`; `struct wb_lookupusergroups_state` stores the copied user SID and returned `wbint_SidArray`.

Control flow: `send` copies the input SID, checks `lookup_usergroups_cached`, and completes immediately on a cache hit. On cache miss it finds the domain with `find_domain_from_sid_noinit`, fails with `NT_STATUS_NO_SUCH_DOMAIN` if absent, then calls `dcerpc_wbint_LookupUserGroups_send`. The callback merges RPC transport/result errors and completes. `recv` moves returned group SIDs to the caller and logs them at info level.

State and persistence: group membership can be satisfied from winbind cache. The async request itself owns only transient talloc state and a copied SID.

Dependencies and integration points: depends on security/SID helpers, cache lookup, domain discovery, and generated `wbint_LookupUserGroups` child RPC. Used by higher-level `GETUSERDOMGROUPS`/group membership request paths and by ADS/MSRPC backend method implementations.

Risks: domain discovery uses the copied user SID; unknown domains fail before backend fallback. Cache correctness directly affects returned memberships. A cache hit avoids domain contact and returns request-posted completion, so callers must handle both synchronous-posted and asynchronous completions.

Test signals: cache hit, cache miss success, unknown-domain failure, RPC failure, and ownership of moved SID arrays. Membership tests should include primary group and nested/alias behavior at higher layers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_lookupusergroups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_next_grent.c -->
# sources/user-network-fs/samba/source3/winbindd/wb_next_grent.c

Purpose: drives one step of `getgrent` enumeration across winbind domains, returning the next group entry and its member database.

Important APIs and types: `wb_next_grent_send/recv`; `struct wb_next_grent_state`; shared `struct getgrent_state` from `winbindd.h`. It uses `wb_query_group_list_send`, `wb_getgrsid_send`, and `dcerpc_wbint_NormalizeNameMap_send`.

Control flow: `wb_next_grent_send_do` obtains the current domain from a `winbindd_domain_ref`. If current group's list is exhausted, it frees the old list, advances to `wb_next_domain`, and fetches a new group list. If a group is available, it calls `wb_getgrsid_send` for the group's SID. Lookup returning `NT_STATUS_NONE_MAPPED` is skipped and enumeration continues. A successful group lookup is passed through `NormalizeNameMap`; the callback chooses the mapped full name, renamed name, or original domain/name pair, fills `winbindd_gr`, increments `next_group`, and completes.

State and persistence: enumeration cursor state is external in `getgrent_state`: current domain ref, group array, count, and next index. The request owns temporary lookup results and moves the member `db_context` to the caller on receive.

Dependencies and integration points: integrated with NSS `getgrent` handlers, group query wrapper, SID-to-group lookup, idmap child name normalization, and domain iteration. Uses passdb/machine SID context indirectly through included winbind domain logic.

Risks: errors fetching a domain group list are logged and treated as an empty domain, so backend outages can look like end-of-domain rather than hard failures. Name normalization result handling has three status paths that affect visible group names. Member database ownership must be moved exactly once. Stale domain refs terminate with no-more-entries.

Test signals: enumerate across multiple domains, empty/erroring domains, unmapped group SIDs that should be skipped, `NormalizeNameMap` OK/FILE_RENAMED/fallback statuses, member DB transfer, and end-of-enumeration `NT_STATUS_NO_MORE_ENTRIES`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_next_grent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_next_pwent.c -->
# sources/user-network-fs/samba/source3/winbindd/wb_next_pwent.c

Purpose: drives one step of `getpwent` enumeration across winbind domains, filling the next passwd entry for a domain user.

Important APIs and types: `wb_next_pwent_send/recv`; `struct wb_next_pwent_state`; shared `struct getpwent_state` containing current domain ref, RID list, and next index.

Control flow: `wb_next_pwent_send_do` resolves the current domain ref. When the current RID list is exhausted it frees it, advances to the next domain, and calls `dcerpc_wbint_QueryUserRidList_send`. Otherwise it composes a user SID from the domain SID plus current RID and calls `wb_getpwsid_send`. The RID-list callback ignores per-domain query errors, resets `next_user`, and recurses. The fill callback skips `NT_STATUS_NO_SUCH_USER` entries, otherwise propagates errors or completes after incrementing the cursor.

State and persistence: cursor state lives in the caller-owned `getpwent_state`. The request owns only the composed SID and pointer to caller-provided `winbindd_pw`.

Dependencies and integration points: child `QueryUserRidList`, `wb_getpwsid`, domain iteration, `winbindd_domain_ref`, and NSS enumeration request handlers.

Risks: per-domain RID-list errors are swallowed to allow enumeration to continue, which can hide partial outages. `wb_getpwsid` failures other than `NO_SUCH_USER` abort enumeration. The caller-provided `winbindd_pw` is mutated in place.

Test signals: RID list fetch success/failure, users without UID mapping skipped as `NO_SUCH_USER`, transition between domains, stale domain ref, and final `NO_MORE_ENTRIES`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_next_pwent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_query_group_list.c -->
# sources/user-network-fs/samba/source3/winbindd/wb_query_group_list.c

Purpose: async wrapper around child `QueryGroupList` RPC for retrieving group principals in one domain.

Important APIs and types: `wb_query_group_list_send/recv`; `struct wb_query_group_list_state` with a `wbint_Principals` result.

Control flow: `send` dispatches `dcerpc_wbint_QueryGroupList_send` to the domain child handle. The callback receives RPC status/result and completes. `recv` moves `groups.principals` to the caller and returns `num_groups`.

State and persistence: transient request-local talloc state only.

Dependencies and integration points: generated winbind RPC stubs, `dom_child_handle`, and group enumeration in `wb_next_grent.c`.

Risks: no local retry or fallback; backend/child errors propagate to the enumeration layer, where they may be treated as empty-domain progress. Caller receives only principals, so memory ownership is important.

Test signals: success with zero and nonzero groups, RPC transport failure, operation result failure, and talloc ownership of moved principal arrays.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_query_group_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_query_user_list.c -->
# sources/user-network-fs/samba/source3/winbindd/wb_query_user_list.c

Purpose: async wrapper that returns a null-separated/list string of fully qualified users for a domain by first querying RIDs and then resolving them to names.

Important APIs and types: `wb_query_user_list_send/recv`; `struct wb_query_user_list_state`; `wbint_RidArray`, `wbint_Principals`, and `winbindd_domain_ref`.

Control flow: `send` stores a domain ref and calls `dcerpc_wbint_QueryUserRidList_send`. The first callback validates status, gets the live domain from the ref, then calls `dcerpc_wbint_LookupRids_send` with the domain SID. The final callback converts each principal name into a domain-qualified username with `fill_domain_username_talloc` and appends it via `strv_add`. `recv` moves the constructed `users` string vector.

State and persistence: request-local state plus a domain ref that detects stale domain objects. No persistent writes.

Dependencies and integration points: child `QueryUserRidList`/`LookupRids`, `winbindd_domain_ref`, string vector helpers, and list-users command handling.

Risks: user list generation requires two child RPCs; stale domain between them fails the request. `strv_add` return values are mapped from Unix errors. The code assumes `LookupRids` returns principal entries corresponding to requested RIDs.

Test signals: empty domain, normal list, stale domain ref after RID fetch, RID lookup failure, names requiring domain qualification/escaping behavior, and allocation failure paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_query_user_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_queryuser.c -->
# sources/user-network-fs/samba/source3/winbindd/wb_queryuser.c

Purpose: resolves a user SID into complete `wbint_userinfo`, including UID mapping, default or cached account fields, NSS info enrichment, primary GID mapping, and optional primary group name.

Important APIs and types: public `wb_queryuser_send/recv`; `struct wb_queryuser_state` tracks the event context, `wbint_userinfo`, parent idmap config, and DC rediscovery flag. Async callbacks are `wb_queryuser_idmap_setup_done`, `wb_queryuser_got_uid`, `wb_queryuser_got_domain`, `wb_queryuser_done`, `wb_queryuser_got_dc`, `wb_queryuser_got_gid`, and `wb_queryuser_got_group_name`.

Control flow: `send` initializes `wbint_userinfo`, sets `primary_gid` to `(gid_t)-1`, copies the user SID, and starts parent idmap setup. The next step maps the user SID with `wb_sids2xids_send` and requires `ID_TYPE_UID` or `ID_TYPE_BOTH`. It defaults the group SID to Domain Users or Guests based on the user RID, fills template homedir/shell, and overlays account/domain/full-name fields from `netsamlogon_cache_get` when present. If the domain name is still unknown it calls `wb_lookupsid_send`; group-type SIDs are accepted when they map to `ID_TYPE_BOTH`, otherwise unknown types fail as no-such-user. The idmap child `dcerpc_wbint_GetNssInfo_send` enriches NSS fields. Host-unreachable/domain-controller-not-found triggers a single `wb_dsgetdcname_send` plus gencache update and retry. If `primary_gid` is still unset, the group SID is mapped through `wb_sids2xids_send`. Primary group name lookup is only done when template homedir or shell contains `%g`/`%G` and the name is missing.

State and persistence: no direct persistent writes, but it reads netsamlogon cache, idmap configuration/cache through `wb_sids2xids`, and writes DC discovery data via `wb_dsgetdcname_gencache_set` after rediscovery. Template homedir/shell values come from runtime configuration.

Dependencies and integration points: `wb_parent_idmap_setup`, `wb_sids2xids`, `wb_lookupsid`, `dcerpc_wbint_GetNssInfo`, netsamlogon cache, DC locator/gencache helpers, template configuration, and higher-level passwd/user lookup handlers. It bridges SID identity mapping with NSS account materialization.

Risks: UID and primary GID type checks are security-sensitive; accepting wrong `unixid.type` would expose bad POSIX identities. The default Domain Users/Guests group SID is a fallback until cache or `GetNssInfo` supplies better data. `GetNssInfo` result failures are intentionally ignored after transport succeeds, so later fallback filling must be correct. DC rediscovery is single-shot. The warning in the GID type failure says UID/BOTH although the code checks GID/BOTH, a diagnostic inconsistency worth preserving in tests.

Test signals: mapped UID success, invalid UID type, netsamlogon cache overlay, unknown domain resolved by `wb_lookupsid`, group-type SID accepted for `ID_TYPE_BOTH`, `GetNssInfo` host-unreachable/DC rediscovery retry, primary GID mapping success/failure, template `%g`/`%G` group-name lookup, and receive-time talloc move of `wbint_userinfo`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_queryuser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_sids2xids.c -->
# sources/user-network-fs/samba/source3/winbindd/wb_sids2xids.c

Purpose: maps an ordered list of SIDs to Unix IDs, using idmap cache first, idmap backend calls by domain next, and SID name lookup to obtain type hints when the backend requests them.

Important APIs and types: `wb_sids2xids_send/recv`; `struct wb_sids2xids_state`; `wbint_TransIDArray`; `wb_parent_idmap_config`; helper `wb_sids2xids_in_cache`; callback sequence `idmap_setup_done`, `next_sids2unix`, `done`, `lookupsids_done`, and `gotdc`; `lsa_SidType_to_id_type`.

Control flow: `send` copies SIDs, initializes invalid `all_ids` entries, splits RIDs, and fills cache hits with `idmap_cache_find_sid2unixid`. If unresolved entries remain it loads parent idmap config. The setup callback builds `idmap_doms` for unresolved SIDs, using configured domains, known domains, predefined SID type hints, and default hints. `next_sids2unix` batches unresolved IDs by domain and calls `dcerpc_wbint_Sids2UnixIDs_send` on the idmap child. If the backend returns `ID_TYPE_WB_REQUIRE_TYPE`, the code batches remaining SIDs through `wb_lookupsids_send`, derives type hints, and restarts idmap mapping. Domain-controller-not-found/host-unreachable can trigger `wb_dsgetdcname_send` and a retry. `recv` copies final `unixid` values into the caller's output array.

State and persistence: reads and writes idmap cache entries with `idmap_cache_set_sid2unixid`, including negative/not-specified results. Uses gencache for DC discovery via `wb_dsgetdcname_gencache_set` and failed-connection tracking via `winbind_idmap_add_failed_connection_entry`.

Dependencies and integration points: idmap child RPC, parent idmap config, domain list, predefined SID lookup, `wb_lookupsids.c`, netlogon DC discovery, LSA domain lists, and higher-level `SIDS_TO_XIDS` winbind commands.

Risks: negative cache insertion affects later calls; expired cache is ignored only when the own domain is online. Correct `tmp_idx` maintenance is essential for preserving input order after per-domain batches. Backend responses with mismatched counts are fatal. Type-hint retry loops must avoid exposing `ID_TYPE_WB_REQUIRE_TYPE` outside winbindd. DC rediscovery is single-shot per domain.

Test signals: all-cache-hit path, expired cache online/offline behavior, configured-domain match, unknown-domain fallback, predefined SID type hint, backend requiring type hints, none-mapped negative cache, count mismatch, host-unreachable/DC rediscovery retry, and output order preservation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_sids2xids.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_xids2sids.c -->
# sources/user-network-fs/samba/source3/winbindd/wb_xids2sids.c

Purpose: maps an ordered list of Unix IDs to SIDs by consulting idmap cache and then iterating configured idmap domains.

Important APIs and types: `wb_xids2sids_send/recv`; top-level `struct wb_xids2sids_state`; per-domain `struct wb_xids2sids_dom_state`; helper `wb_xids2sids_dom_send/recv`; callbacks `wb_xids2sids_idmap_setup_done`, `wb_xids2sids_done`, `wb_xids2sids_dom_done`, and `wb_xids2sids_dom_gotdc`.

Control flow: `send` copies input XIDs, initializes null SIDs and cached flags, and pre-fills nonexpired cache hits via `idmap_cache_find_xid2sid`. It loads idmap config, then dispatches `wb_xids2sids_dom_send` for each configured domain in order. Each domain filters XIDs by configured range, cache status, and already-filled SID, then calls `dcerpc_wbint_UnixIDs2Sids_send`. Domain-controller-not-found/host-unreachable can trigger DC rediscovery and retry. After all domains, uncached results are written back to the SID-to-Unix cache with backend-returned XID type values. `recv` moves the SID array to the caller.

State and persistence: request-local state plus idmap cache reads/writes, failed connection markers, and DC discovery gencache updates.

Dependencies and integration points: idmap child RPC, parent idmap config/ranges, cache helpers, DC discovery, netlogon types, and public `XIDS_TO_SIDS` winbind command handling.

Risks: configured domain ordering determines which range match wins. Null SIDs represent unresolved entries and are still cached at the end unless guarded by idmap cache semantics. Backend may adjust XID type; cache priming intentionally uses returned type rather than requested type. Count alignment in per-domain responses relies on iterating the same filtered XID set in the callback.

Test signals: cache hit, expired/missing cache, XIDs outside every domain range, overlapping ranges, backend returns none mapped, host-unreachable/DC retry, returned type changes, and preservation of input ordering with mixed cached and uncached IDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wb_xids2sids.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd.c

Purpose: main winbindd daemon entry point and client event loop. It initializes Samba/winbind services, opens public and privileged sockets, dispatches client protocol commands to sync or async handlers, manages client lifecycle, registers messaging/signal handlers, and runs the tevent loop.

Important APIs and types: `main`; `winbindd_setup_stdin_handler`; dispatch tables `bool_dispatch_table`, `async_nonpriv_table`, and `async_priv_table`; `process_request_send/recv` and callbacks; client callbacks `new_connection`, `winbind_client_request_read`, `winbind_client_activity`, `winbind_client_processed`; lifecycle helpers `remove_client`, `client_is_idle`, `remove_idle_client`, `remove_timed_out_clients`; listener setup; message handlers for shutdown and cache validation; address-change watcher.

Control flow: startup parses command-line options, disables recursive winbind calls, validates ADS configuration and socket path lengths, initializes messaging, passdb, secrets, idmap/locator children, domain list, DCE/RPC endpoints, address-change monitoring, and listener sockets. Accepted clients get a `winbindd_cli_state`, an output queue, and an async request read. Each request allocates per-request memory and response, selects an async handler from nonprivileged or privileged tables, or a bool handler, then writes the response and returns to read another request. Concurrent unexpected client input while a request is active removes the client. A scrub timer periodically removes idle or timed-out clients. The main loop repeatedly calls `tevent_loop_once`.

State and persistence: maintains in-memory client list, per-client enumeration cursors, request memory contexts, child process state, messaging registrations, domain/cache/idmap initialization, pid file, Unix sockets, and daemon status. It touches persistent/runtime state through lock/pid directories, sockets, logs, secrets, gencache/cache initialization, and child processes.

Dependencies and integration points: core Samba command-line, messaging, DCE/RPC endpoint server, idmap, locator, domain list/cache, netlogon creds, passdb, nscd flushing, varlink optional support, address-change API, generated winbind request protocol, and all command-specific `winbindd_*_send/recv` handlers including the files in this subset.

Risks: dispatch table permissions are the command security boundary; privileged commands must stay only in `async_priv_table`. Client removal intentionally frees pending I/O before closing sockets to avoid epoll/fork descriptor races. Long-running request profiling is only logged after completion; timed-out active requests are forcibly removed by scrubber. Startup has many fatal configuration gates. Socket path length and permissions directly affect NSS/PAM integration.

Test signals: startup with valid/invalid ADS config, public vs privileged command access, max-client idle eviction, active request timeout, client sends extra data during processing, SIGUSR2 status, SIGCHLD child cleanup, cache-validation message fork path, address-drop message path, and listener socket permission checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd.h -->
# sources/user-network-fs/samba/source3/winbindd/winbindd.h

Purpose: central winbindd header defining daemon/client/domain state, backend method tables, idmap config structures, enumeration cursors, cached credential structures, constants, and generated prototypes.

Important APIs and types: `struct winbindd_cli_state`; `struct winbindd_domain_ref` and `_winbindd_domain_ref_set/get` macros; `struct getpwent_state`; `struct getgrent_state`; `struct winbindd_cm_conn`; `struct winbindd_child`; `struct winbindd_domain`; `struct wb_parent_idmap_config(_dom)`; `struct wb_acct_info`; `struct winbindd_methods`; `struct winbindd_idmap_methods`; trusted-domain and credential cache structs; constants `WB_REPLACE_CHAR`, `WINBINDD_ESTABLISH_LOOP`, `WINBINDD_RESCAN_FREQ`, `DOM_SEQUENCE_NONE`.

Control flow role: the header itself has no runtime flow, but its structures define the state machines used by async request handlers, domain iteration, child RPC, ADS/MSRPC backend selection, idmap setup, and NSS enumeration.

State and persistence: declares in-memory state for client sockets, per-request memory, output queues, domain trust metadata, connection handles, children, caches, ccache entries, and memory credentials. Some structs mirror persistent or semi-persistent stores such as trusted-domain cache, idmap configuration, Kerberos ccaches, and domain sequence numbers.

Dependencies and integration points: includes nsswitch protocol structs, libwbclient, generated RPC headers, tevent NTSTATUS helpers, optional nscd and mmap headers, and generated `winbindd_proto.h`. It is included by most source3/winbindd files and anchors backend polymorphism via `winbindd_methods`.

Risks: structure changes are ABI-sensitive inside the daemon and can affect many files. Domain refs are designed to detect stale domain pointers; bypassing them risks use-after-free. Method-table contracts must be respected by ADS/MSRPC/cache layers. Client state owns per-request memory and enumeration cursors, so lifetime mistakes can leak or corrupt NSS enumeration.

Test signals: compile coverage is essential after any struct or method signature change. Runtime tests should cover stale domain ref detection, backend method substitution, getpwent/getgrent cursor lifetime across client requests, and privileged/nonprivileged client state handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_ads.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_ads.c

Purpose: implements the Active Directory LDAP-backed `winbindd_methods` backend, with ADS connection caching, user/group enumeration, group membership lookup, selected RPC fallbacks, and trusted-domain discovery.

Important APIs and types: exported `struct winbindd_methods ads_methods`; `ads_idmap_cached_connection`; static connection helpers `ads_cached_connection_reuse`, `ads_cached_connection_reconnect_creds`, `ads_cached_connection_connect`, `ads_cached_connection`; backend methods `query_user_list`, `enum_dom_groups`, `enum_local_groups`, `name_to_sid`, `sid_to_name`, `rids_to_names`, `lookup_usergroups`, `lookup_useraliases`, `lookup_groupmem`, `lookup_aliasmem`, `lockout_policy`, `password_policy`, and `trusted_domains`.

Control flow: connection helpers reuse nonexpired Kerberos-backed `ADS_STRUCT` objects or reconnect with trust credentials. User enumeration searches LDAP for users and extracts RIDs from `objectSid`. Domain group enumeration searches security-enabled groups and optionally includes domain-local groups in the primary domain. Name/SID conversions and several policy operations delegate to MSRPC methods. User group lookup tries cache, then LDAP `tokenGroups` plus primary group; if unavailable it falls back to `memberOf` ranged extended-DN lookup and then `member=` search. Group member lookup searches LDAP group `member` values with extended DN, adds primary-group members, resolves cached SIDs locally, and falls back to LSA SID lookup for uncached entries. Trusted-domain lookup uses Netlogon `DsrEnumerateDomainTrusts` and updates the trusted domain cache with inherited trust flags where needed.

State and persistence: caches ADS connections in `domain->backend_data.ads_conn` and frees expired ones. Updates trusted-domain cache with `wcache_tdc_add_domain`, reads idmap config option `all_groupmem`, uses samlogon/lookup caches, and relies on Kerberos ticket expiry. It marks `domain->last_status` on connection failures.

Dependencies and integration points: AD LDAP libraries, ADS SASL/seal connections, trust credentials, generated netlogon RPC, SID/security helpers, passdb, idmap config, MSRPC backend methods, winbind domain list/cache, SAF server affinity, and group membership/name lookup helpers.

Risks: LDAP filters and ranged attributes are security-sensitive and must handle escaping and large membership sets. `ads_cached_connection_reuse` depends on ticket expiry and realm presence. Some functions return success with zero entries when trust/contact is unavailable, while others return synchronization/server-disabled statuses; callers must understand caching implications. Builtin SIDs are filtered out of ADS group results. Trusted-domain inheritance logic is complex and depends on query perspective.

Test signals: expired/nonexpired ADS connection reuse, connection fallback to MSRPC on refused LDAP, user RID enumeration with non-user objects, domain group filters, tokenGroups success, tokenGroups unavailable with memberOf/member fallbacks, large ranged group membership, primary group members with `all_groupmem`, cached vs uncached group member SID resolution, trusted-domain cache updates for primary/forest/external trusts, and AD DC mode rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_ads.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_ads.h -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_ads.h

Purpose: declares the ADS backend method table and the idmap ADS cached connection helper.

Important APIs and types: include guard `__WINBINDD_ADS_H__`, `#include "ads.h"`, external `struct winbindd_methods ads_methods`, and `ADS_STATUS ads_idmap_cached_connection(const char *dom_name, TALLOC_CTX *mem_ctx, ADS_STRUCT **adsp)`.

Control flow role: no implementation flow; it exposes ADS backend integration points to other winbindd/idmap code.

State and persistence: no direct state. The declared helper returns or creates cached `ADS_STRUCT` objects whose lifetime is controlled by the caller's talloc context and implementation in `winbindd_ads.c`.

Dependencies and integration points: depends on ADS types and `winbindd_methods` from `winbindd.h` users. Integrated by backend selection code and idmap AD paths that need a cached LDAP connection by domain name.

Risks: declarations are only valid when ADS support is built consistently with implementation guards. Signature changes ripple into idmap and backend registration code.

Test signals: build with and without ADS support, link-time availability of `ads_methods`, and callers correctly managing returned `ADS_STRUCT` lifetime.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_ads.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_allocate_gid.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_allocate_gid.c

Purpose: async implementation of privileged `WINBINDD_ALLOCATE_GID`, allocating a new Unix GID through the idmap child.

Important APIs and types: `winbindd_allocate_gid_send/recv`; `struct winbindd_allocate_gid_state` with event context and `uint64_t gid`.

Control flow: `send` creates state, logs the request, and starts `wb_parent_idmap_setup_send`. The setup callback validates idmap config and fails with `NT_STATUS_UNSUCCESSFUL` if no idmap domains are configured, matching idmap_tdb range-full behavior. It then calls `dcerpc_wbint_AllocateGid_send` on `idmap_child_handle`. The final callback merges transport/result status and completes. `recv` writes `response->data.gid`.

State and persistence: allocation persistence is owned by the idmap backend/child, not this wrapper. This file only holds the allocated value in request state.

Dependencies and integration points: parent idmap setup, idmap child RPC, privileged command dispatch in `winbindd.c`, and `winbindd_response` protocol fields.

Risks: no local validation of caller privilege; depends on dispatch table placement. No configured idmap domain and exhausted range both surface as unsuccessful. Returned `uint64_t` is assigned to protocol response field, so type/range compatibility matters.

Test signals: privileged command success, no idmap config, range exhaustion/backend failure, idmap child transport failure, and response field correctness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_allocate_gid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_allocate_uid.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_allocate_uid.c

Purpose: async implementation of privileged `WINBINDD_ALLOCATE_UID`, allocating a new Unix UID through the idmap child.

Important APIs and types: `winbindd_allocate_uid_send/recv`; `struct winbindd_allocate_uid_state` with event context and `uint64_t uid`.

Control flow: `send` creates state, logs the request, and starts `wb_parent_idmap_setup_send`. The setup callback validates idmap config and fails with `NT_STATUS_UNSUCCESSFUL` when no domains are configured. It calls `dcerpc_wbint_AllocateUid_send` on `idmap_child_handle`. The final callback merges RPC transport/result status and completes. `recv` writes `response->data.uid`.

State and persistence: actual UID allocation is persisted by the idmap backend behind the child RPC. The wrapper stores only transient request state.

Dependencies and integration points: parent idmap config, idmap child RPC, privileged async dispatch in `winbindd.c`, and winbind client response protocol.

Risks: privilege depends on command dispatch, not this file. No-domain and exhausted-range failures intentionally share status. Returned value width must match response consumers. Allocation semantics depend entirely on idmap backend atomicity.

Test signals: successful privileged allocation, missing idmap config, backend/range exhaustion, child RPC failure, response field population, and denial when invoked over the nonprivileged socket.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_allocate_uid.c -->
