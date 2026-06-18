# subset-b-009898 Research

Grouped research for the listed Samba winbindd sources. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_reconnect_ads.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_reconnect_ads.c

## Purpose
This file wraps the ADS winbind backend with a narrow retry layer. It exposes `reconnect_ads_methods`, a `struct winbindd_methods` table whose entries call the matching `ads_methods` implementation and then retry once when the returned status looks like a transient LDAP/RPC transport problem. It exists only under `HAVE_ADS`, so non-ADS builds omit it.

## Important APIs, Types, And Functions
The central helper is `ldap_reconnect_need_retry()`, which refuses retries for successful statuses, informational/non-error statuses, expected lookup misses such as `NONE_MAPPED`, `NO_SUCH_USER`, `NO_SUCH_GROUP`, `NO_SUCH_ALIAS`, `NO_SUCH_MEMBER`, `NO_SUCH_DOMAIN`, `NO_SUCH_PRIVILEGE`, and `NO_MEMORY`, and returns true for other errors. The wrapper functions mirror the winbind backend vtable: `query_user_list`, `enum_dom_groups`, `enum_local_groups`, `name_to_sid`, `sid_to_name`, `rids_to_names`, `lookup_usergroups`, `lookup_useraliases`, `lookup_groupmem`, `lookup_aliasmem`, `lockout_policy`, `password_policy`, and `trusted_domains`.

## Control Flow
Every method calls the corresponding `ads_methods.*` function first. If the status matches the retry predicate, the same method is invoked a second time with the same arguments and its result is returned. Some name and policy paths use the generic `reconnect_need_retry()` instead of the LDAP-specific predicate, while list and membership LDAP-heavy paths use `ldap_reconnect_need_retry()`.

## State And Persistence Behavior
The file keeps no private persistent state. It relies on ADS connection state owned by the wrapped backend and on retry side effects in lower layers. Output pointers are those supplied by callers and may be overwritten by either the first successful call or the second retry.

## Dependencies And Integration Points
It depends on `winbindd.h`, `ads_methods` from `winbindd_ads.c`, the generic reconnect predicate from the non-ADS reconnect layer, NTSTATUS helpers, and the `winbindd_methods` backend dispatch contract. Integration is through domain backend selection for ADS domains that need reconnect behavior without duplicating ADS lookup code.

## Risks And Test Signals
The retry policy must not retry semantic "not found" answers, otherwise callers can experience duplicate LDAP traffic and misleading logs. Since retries reuse the same output pointers, callees must tolerate partial output from a failed first attempt or clean it internally. Good signals are ADS lookup tests with dropped LDAP connections, expected miss cases that return immediately, and build coverage with and without `HAVE_ADS`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_reconnect_ads.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_rpc.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_rpc.c

## Purpose
This file provides low-level synchronous SAMR and LSA RPC helper functions used by winbind domain backends. It enumerates users and groups, resolves group and alias membership, enumerates trusted domains, and translates SID arrays through LSA lookup calls.

## Important APIs, Types, And Functions
User and group enumeration is handled by `rpc_query_user_list()`, `rpc_enum_dom_groups()`, and `rpc_enum_local_groups()`. Membership helpers include `rpc_lookup_usergroups()`, `rpc_lookup_useraliases()`, `rpc_lookup_groupmem()`, and `rpc_lookup_aliasmem()`. Trust discovery is in `rpc_trusted_domains()`. SID lookup uses `rpc_lookup_sids()` with an NCACN-IP-TCP fast path through `rpc_try_lookup_sids3()`.

## Control Flow
Enumeration functions loop on `STATUS_MORE_ENTRIES`, reallocating result arrays and appending returned entries. Membership functions open SAMR user, group, or alias handles, call the relevant query RPC, close temporary handles, and compose returned RIDs into full domain SIDs or formatted names. `rpc_trusted_domains()` first tries `EnumTrustedDomainsEx`, falls back to older `EnumTrustDom`, and builds `netr_DomainTrust` entries. `rpc_lookup_sids()` connects to LSAT and uses `LookupSids3` over TCP transport or `LookupSids` for other transports, then validates translated-name/domain indexes.

## State And Persistence Behavior
There is no durable state. Result arrays are talloc-owned by the caller context, while temporary RPC arrays, policy handles, and stack frames are freed before return. Remote state is read-only except for opening and closing RPC policy handles.

## Dependencies And Integration Points
The file depends on generated SAMR/LSA client stubs, Samba RPC pipe clients, `cli_samr`, `cli_lsarpc`, SID helpers, and winbind name formatting utilities. It is consumed by `winbindd_samr.c` and other RPC-backed winbind code that already holds connected SAMR/LSA pipes and policy handles.

## Risks And Test Signals
Important risks are off-by-one and overflow handling while appending paged RPC results, stale policy handles, invalid server responses where returned counts do not match request counts, and trust enumeration fallback behavior. `rpc_trusted_domains()` has a particularly sensitive mixed `dom_list_ex`/`dom_list` path; tests should cover both modern and legacy LSA servers. Good signals are SAMR enumeration tests, alias membership tests with more than 1024 SIDs, LSAT lookup tests over named pipe and TCP, and leak/error-path checks for handle closes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_rpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_rpc.h -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_rpc.h

## Purpose
This header declares the low-level RPC helper interface implemented by `winbindd_rpc.c`. It is the contract between SAMR/LSA pipe management code and the reusable query/membership/trust routines.

## Important APIs, Types, And Functions
The declarations cover `rpc_query_user_list`, group enumeration, user group and alias lookup, group and alias member expansion, and trusted-domain enumeration. The API surface uses `TALLOC_CTX`, `rpc_pipe_client`, `policy_handle`, `dom_sid`, `wb_acct_info`, `netr_DomainTrust`, and NTSTATUS.

## Control Flow
The header has no runtime control flow. Its declarations imply callers must establish and pass valid SAMR or LSA pipe clients plus domain or policy handles before calling the helpers.

## State And Persistence Behavior
No state is defined here. Ownership is expressed by talloc output pointers: result arrays are allocated under the provided memory context and returned through out parameters.

## Dependencies And Integration Points
It is included by `winbindd_rpc.c` and `winbindd_samr.c`. The header depends on types declared by broader Samba winbind/RPC headers included before or alongside it.

## Risks And Test Signals
The main risk is API drift between this header and `winbindd_rpc.c` or callers. Compile coverage of winbindd with SAMR support is the primary signal, supplemented by tests that exercise every declared helper through `sam_passdb_methods`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_rpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_samr.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_samr.c

## Purpose
This file implements the passdb/SAMR-backed winbind backend method tables for local SAM, BUILTIN, and internal RPC access. It bridges high-level `winbindd_methods` operations to cached internal SAMR/LSA pipes and the reusable helpers in `winbindd_rpc.c`.

## Important APIs, Types, And Functions
Connection setup is handled by `open_internal_samr_conn()`, `open_internal_lsa_conn()`, and `open_cached_internal_pipe_conn()`, with cached state in `struct winbind_internal_pipes`. Backend operations include `sam_enum_dom_groups`, `sam_query_user_list`, `sam_trusted_domains`, `sam_enum_local_groups`, `sam_name_to_sid`, `sam_sid_to_name`, `sam_rids_to_names`, `sam_lockout_policy`, `sam_password_policy`, `sam_lookup_usergroups`, `sam_lookup_useraliases`, `sam_lookup_groupmem`, and `sam_lookup_aliasmem`. The exported method tables are `builtin_passdb_methods` and `sam_passdb_methods`.

## Control Flow
The cached pipe opener lazily creates internal SAMR and LSA pipes, opens domain/policy handles, and installs a five-second idle timer that frees the cached pipe bundle. Most SAM operations call `open_cached_internal_pipe_conn()`, invoke a `rpc_*` helper or generated SAMR call, and retry once if `reset_connection_on_error()` sees a timeout, device error, or disconnected binding handle. Name/SID conversion has special local handling for Unix users/groups, well-known SIDs, the domain SID itself, and optional name normalization before falling back to SAMR `LookupNames` or `LookupRids`.

## State And Persistence Behavior
State is cached in `domain->backend_data.samr_pipes` and expires through a tevent timer. Domain method tables themselves are static. The code reads passdb, Unix passwd/group databases, machine SID state, and SAMR/LSA policies, but does not persist new records. Name normalization may consult alias caches and mark domains offline when alias lookup reports DC unavailability.

## Dependencies And Integration Points
It depends on internal RPC pipe support, generated SAMR/LSA stubs, passdb and Unix SID helpers, global event contexts, and `winbindd_rpc.h`. It integrates into winbind backend dispatch for the local SAM and BUILTIN domains and is used by higher-level NSS, SID/name lookup, group membership, and policy calls.

## Risks And Test Signals
Risks include cached policy handles becoming stale, retry logic hiding transport failures but not semantic errors, subtle output-pointer ownership through temporary talloc frames, and compatibility expectations for Unix pseudo-domains and well-known SIDs. Build-sensitive risk exists around exact function signatures and generated SAMR calls. Strong test signals are local SAM SID/name round trips, BUILTIN alias expansion, password and lockout policy queries, group membership lookups, and forced pipe disconnect tests that verify one retry and cache invalidation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_samr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_setgrent.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_setgrent.c

## Purpose
This file implements the asynchronous `WINBINDD_SETGRENT` command, which resets per-client group enumeration state before `GETGRENT` calls.

## Important APIs, Types, And Functions
The public entry points are `winbindd_setgrent_send()` and `winbindd_setgrent_recv()`. The state struct is only a dummy tevent state because the command completes immediately after setting `cli->grent_state`.

## Control Flow
`send()` creates a tevent request, frees any previous `cli->grent_state`, logs the client and `winbind enum groups` setting, and either completes immediately when group enumeration is disabled or allocates a fresh `struct getgrent_state` under the client. It posts the completed request to the event loop. `recv()` logs command completion and returns OK.

## State And Persistence Behavior
The only state mutation is per-client in-memory `cli->grent_state`. No persistent storage is touched. Disabling enumeration leaves the state cleared, causing later enumeration to produce no entries.

## Dependencies And Integration Points
It depends on tevent, talloc, `winbindd_cli_state`, `getgrent_state`, and the `lp_winbind_enum_groups()` configuration. It is used by traditional NSS clients and by varlink group/membership enumeration code that synthesizes internal winbind requests.

## Risks And Test Signals
Risks are low but include stale enumeration state if callers skip `ENDGRENT`, and behavior changes when `winbind enum groups` is disabled. Test signals are set/get/end group enumeration sequences and varlink enumeration behavior with enumeration enabled and disabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_setgrent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_setpwent.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_setpwent.c

## Purpose
This file implements the asynchronous `WINBINDD_SETPWENT` command, resetting per-client passwd enumeration state before `GETPWENT` calls.

## Important APIs, Types, And Functions
The public entry points are `winbindd_setpwent_send()` and `winbindd_setpwent_recv()`. The private state contains only a dummy byte because the command is immediately posted as complete.

## Control Flow
`send()` creates a tevent request, frees prior `cli->pwent_state`, logs client metadata and `winbind enum users`, and either completes without allocation when enumeration is disabled or allocates a new `struct getpwent_state` under the client. `recv()` always returns OK after logging.

## State And Persistence Behavior
Only `cli->pwent_state` is changed, and it is per-client memory. There is no persistent storage or cross-client state.

## Dependencies And Integration Points
It depends on tevent/talloc, `winbindd.h`, and the `lp_winbind_enum_users()` configuration. It feeds user enumeration through NSS and the varlink `GetUserRecord` enumeration path.

## Risks And Test Signals
The main risk is surprising "success with no enumeration state" when user enumeration is disabled. Tests should cover `SETPWENT` followed by `GETPWENT`, disabled enumeration, and cleanup through `ENDPWENT`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_setpwent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_sids_to_xids.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_sids_to_xids.c

## Purpose
This file implements the asynchronous external `WINBINDD_SIDS_TO_XIDS` command. It maps a newline-separated list of SID strings to Unix IDs and formats a line-aligned response for clients.

## Important APIs, Types, And Functions
The command is implemented by `winbindd_sids_to_xids_send()`, callback `winbindd_sids_to_xids_done()`, and `winbindd_sids_to_xids_recv()`. It uses `parse_sidlist()` from `winbindd_util.c`, `wb_sids2xids_send/recv()`, `struct dom_sid`, and `struct unixid`.

## Control Flow
`send()` validates that extra data is either empty or null-terminated, parses the SID list, and dispatches `wb_sids2xids_send()`. The callback allocates an output `unixid` array sized to the input SID count and receives mapping results. `recv()` turns each mapped ID into `U<id>`, `G<id>`, or `B<id>` lines and emits a blank line for unmapped or invalid entries.

## State And Persistence Behavior
State is request-local: parsed SIDs, count, and mapped XIDs. Persistence is delegated to the idmap layer, which may read or allocate mappings according to its backend policy.

## Dependencies And Integration Points
It depends on winbind request framing, tevent, SID parsing, idmap conversion helpers, and `response->extra_data`. It integrates with clients that batch SID-to-UID/GID conversions and expect line order to match input order.

## Risks And Test Signals
Risks include malformed non-null-terminated client payloads, very large SID lists, `UINT32_MAX` being treated as unmapped, and exact response length accounting through `talloc_get_size()`. Test signals are batch mappings containing UID, GID, BOTH, unmapped, empty input, and invalid SID syntax.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_sids_to_xids.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_traceid.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_traceid.c

## Purpose
This file wires Samba debug trace IDs into tevent callbacks so asynchronous winbind event handling preserves request correlation in logs.

## Important APIs, Types, And Functions
`winbind_debug_traceid_setup()` registers trace callbacks for tevent loop, fd, signal, timer, immediate, and queue events. Each event-specific callback stores `debug_traceid_get()` as an event tag on attach and restores that tag with `debug_traceid_set()` before handler execution.

## Control Flow
On setup, all tevent trace callbacks are installed and trace ID is initialized to 1, representing out-of-request execution. When events are attached, the current trace ID is copied into the event tag. Before a handler runs, the tag is copied back into the active debug trace ID. After a loop iteration, `debug_traceid_trace_loop()` resets the active ID to 1.

## State And Persistence Behavior
State is held in tevent event tags and the process-local debug trace ID. There is no persistent storage. The reset-to-1 behavior prevents one request handler's trace ID from bleeding into unrelated loop work.

## Dependencies And Integration Points
It depends on `lib/util/debug.h`, tevent trace APIs, and the header `winbindd_traceid.h`. It integrates during winbind event loop initialization.

## Risks And Test Signals
Risks are trace callback ordering changes in tevent, missing coverage for a new event type, or accidental reset while nested callbacks still need request context. Good signals are debug-log correlation tests across timers, fd events, queue entries, and idle loop boundaries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_traceid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_traceid.h -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_traceid.h

## Purpose
This header declares the winbind trace ID setup hook for tevent contexts.

## Important APIs, Types, And Functions
The only API is `winbind_debug_traceid_setup(struct tevent_context *ev)`. It includes `<tevent.h>` and uses a conventional include guard.

## Control Flow
There is no runtime control flow in the header. Callers use the declaration to install trace propagation on a tevent context.

## State And Persistence Behavior
No state is defined here. Runtime state lives in tevent event tags and debug trace internals in `winbindd_traceid.c`.

## Dependencies And Integration Points
It is included by setup code and the implementation file. Its public surface is intentionally small.

## Risks And Test Signals
Risks are limited to declaration drift or include-order issues. Compile coverage and log-correlation tests in the implementation are the relevant signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_traceid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_util.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_util.c

## Purpose
This is a core utility file for winbind domain and client management. It owns the trusted-domain list, domain references, trust rescans, domain lookup/routing helpers, username parsing/canonicalization, client list bookkeeping, cached group lookup, name normalization, KDC locator environment setup, auth error formatting, online/offline checks, and SID/XID list parsers.

## Important APIs, Types, And Functions
Domain-list APIs include `domain_list()`, `wb_next_domain()`, `_winbindd_domain_ref_set/get()`, `add_trusted_domain_from_auth()`, `domain_is_forest_root()`, `rescan_trusted_domains()`, `update_trusted_domains_dc()`, `init_domain_list()`, and the `find_*domain*` helpers. Client APIs include `winbindd_client_list()`, `winbindd_add_client()`, `winbindd_remove_client()`, `winbindd_promote_client()`, and `winbindd_num_clients()`. Identity helpers include `parse_domain_user()`, `canonicalize_username()`, `fill_domain_username_talloc()`, `lookup_usergroups_cached()`, `normalize_name_map()`, `normalize_name_unmap()`, `parse_sidlist()`, `parse_xidlist()`, and `find_dns_domain_name()`.

## Control Flow
`domain_list()` lazily initializes global domain state through `init_domain_list()`. `add_trusted_domain()` validates uniqueness of SID and DNS names, creates `winbindd_domain` objects, initializes child connection structures and routing metadata, adds entries to the global list, bumps `domain_list_generation`, and updates the trusted-domain cache. Trust rescans call child `ListTrustedDomains` requests asynchronously, add newly discovered trusts, and follow forest root and forest-transitive trust paths. Lookup helpers route SIDs and names differently for member servers versus DCs, handling local SAM, BUILTIN, Unix pseudo-domains, well-known domains, and default route domains.

## State And Persistence Behavior
The file owns `_domain_list`, `domain_list_generation`, `_client_list`, and `_num_clients`. It reads and updates the winbind trusted-domain cache, migrates secrets database formats, sends process messages for new trusted domains, starts/stops domain children, and may set/unset environment variables used by the Kerberos locator plugin. Per-domain state includes online/offline flags, routing domain pointers, child arrays, queues, trust flags, and cached sequence/connection metadata.

## Dependencies And Integration Points
It depends on Samba configuration, secrets, passdb, machine SID, LSA trust structures, DRS blobs, messaging, global event contexts, samlogon cache, SID utilities, string parsing, idmap types, and winbind child RPC interfaces. It is integrated almost everywhere in winbindd: backend selection, NSS request parsing, trust discovery, client lifecycle, offline/online behavior, and batch ID mapping command parsing.

## Risks And Test Signals
This file has high blast radius. Risks include stale domain pointers after rescans, trust-cache drift when removed domains remain until restart, duplicate SID/DNS validation errors, member/DC routing differences, username parsing around separators and UPNs, normalization alias lookup marking domains offline, and parser strictness for newline/null-terminated SID/XID lists. The checked-out source also contains duplicate-looking lines in a few places, making full compile coverage important. Strong signals are domain initialization on standalone/member/DC roles, trust rescans including forest trusts, auth-driven on-the-fly domain addition, SID/name routing tests, default-domain username parsing, client list accounting, and invalid list parser tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_varlink.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_varlink.c

## Purpose
This file exposes winbindd through systemd's `io.systemd.UserDatabase` varlink interface. It sets up the service socket, validates the requested service name, dispatches user/group/membership calls to async helper files, and prevents recursive varlink calls back into itself.

## Important APIs, Types, And Functions
The public setup entry point is `winbind_setup_varlink()`. `wb_vl_fake_cli_state()` builds a minimal `winbindd_cli_state` from varlink peer credentials. The method handlers are `io_systemd_getuserrecord()`, `io_systemd_getgrouprecord()`, and `io_systemd_getmemberships()`. `vl_active` is a global recursion guard.

## Control Flow
Setup creates `/run/systemd/userdb` or configured socket directory, builds a `unix:` URI using the configured service name, creates a varlink service, registers the interface and handlers, obtains the service fd, and adds it to tevent. Method handlers parse `service` plus optional name/id parameters, reject wrong services with `BadService`, reject recursive calls when `vl_active` is set, set `vl_active`, and dispatch to the relevant `wb_vl_*` async function. The tevent fd handler calls `varlink_service_process_events()`.

## State And Persistence Behavior
Persistent process state is the `wb_vl_state` talloc object holding the varlink service, event context, fd event, and fd. The global `vl_active` flag is reset by per-call state destructors. Filesystem persistence is limited to creating the socket directory and varlink socket managed by the varlink service.

## Dependencies And Integration Points
It depends on libvarlink, tevent, talloc, Samba config parameters under `winbind varlink`, peer credential retrieval through `SO_PEERCRED`, and the helper functions declared in `winbindd_varlink.h`. It integrates with systemd-userdb clients and internal winbind request handlers by synthesizing fake client state.

## Risks And Test Signals
Risks include global `vl_active` serializing or rejecting overlapping varlink requests, Linux-specific peer credential behavior, service-name mismatches, socket lifecycle errors, and incorrect error mapping where dispatch failures become `ServiceNotAvailable`. Test signals are varlink socket creation, `BadService` handling, recursion prevention, peer credential capture, and all dispatch quadrants for user/group/membership calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_varlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_varlink.h -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_varlink.h

## Purpose
This header defines the varlink integration surface for winbindd's systemd userdb service.

## Important APIs, Types, And Functions
It declares `vl_active`, service/error string constants, the `WB_VL_ERR_CHECK_GOTO` error-handling macro, `wb_vl_fake_cli_state()`, user record functions, group record functions, membership functions, and `winbind_setup_varlink()`.

## Control Flow
The header has no runtime flow. Its macro standardizes local varlink error checks by logging `varlink_error_string(rc)` and jumping to a caller-supplied cleanup label.

## State And Persistence Behavior
It exposes the global recursion guard `vl_active`; all other state is owned by implementation files. No storage is persisted by the header itself.

## Dependencies And Integration Points
It includes talloc, tevent, and varlink headers, and is shared by `winbindd_varlink.c` plus the three method implementation files. It binds those files to the systemd userdb error namespace.

## Risks And Test Signals
Risks are ABI/API drift among the varlink files and the broad effect of the global `vl_active`. Compile coverage with and without `with_systemd_userdb` is the key signal, along with tests for every declared handler.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_varlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_varlink_getgrouprecord.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_varlink_getgrouprecord.c

## Purpose
This file implements varlink `GetGroupRecord` operations: enumerate groups, lookup by gid, lookup by name, and lookup by both name and gid with conflict detection.

## Important APIs, Types, And Functions
`group_record_reply()` converts a `winbindd_gr` plus comma-separated member data into a varlink record object. Public handlers are `wb_vl_group_enumerate()`, `wb_vl_group_by_gid()`, `wb_vl_group_by_name()`, and `wb_vl_group_by_name_and_gid()`. Each operation has a state struct, destructor that unrefs the varlink call and clears `vl_active`, async callbacks, and a connection-closed cleanup callback.

## Control Flow
Enumeration requires `lp_winbind_enum_groups()` and `VARLINK_CALL_MORE`, then runs `SETGRENT`, repeated `GETGRENT` chunks of 500, and `ENDGRENT`. It delays the final record from each chunk so the last reply can be sent without the `continues` flag. Single lookup paths synthesize `GETGRGID` or `GETGRNAM` requests and translate `NONE_MAPPED` to `NoRecordFound`. The name+gid path tries name first, falls back to gid if name is missing, and returns `ConflictingRecordFound` if the resolved record does not match both requested fields.

## State And Persistence Behavior
State is per varlink call: fake winbind request/client structures, a referenced `VarlinkCall`, last delayed group record, and copied member string where needed. It mutates `vl_active` and per-fake-client enumeration state but no persistent database.

## Dependencies And Integration Points
It depends on varlink object/array APIs, winbind getgr* async handlers, `winbindd_setgrent/endgrent`, Samba string wrappers, and `lp_winbind_enum_groups()`. It integrates with systemd userdb group record consumers.

## Risks And Test Signals
Risks include parsing member strings destructively with `strtok_r`, correct `continues` flag handling across chunk boundaries, gid/name integer range behavior, and fake-client state parity with real NSS clients. Tests should cover empty enumeration, disabled enumeration, multi-chunk enumeration, groups with and without members, lookup misses, and name/gid conflicts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_varlink_getgrouprecord.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_varlink_getmemberships.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_varlink_getmemberships.c

## Purpose
This file implements varlink `GetMemberships`: enumerate all user/group membership pairs, list groups for one user, list members of one group, and check a specific user/group membership.

## Important APIs, Types, And Functions
Reply helpers are `membership_reply()` and `member_list_reply()`. Public handlers are `wb_vl_memberships_enumerate()`, `wb_vl_memberships_by_user()`, `wb_vl_memberships_by_group()`, and `wb_vl_membership_check()`. The implementation uses async winbind `SETGRENT`, `GETGRENT`, `ENDGRENT`, `GETGROUPS`, `GETGRGID`, and `GETGRNAM` calls.

## Control Flow
Enumeration requires group enumeration, group expansion, and the varlink `more` flag. It walks group chunks, skips groups without members, keeps one member-bearing group delayed so the final reply can omit `continues`, and emits one varlink record per member. The by-user path calls `GETGROUPS`, then resolves each returned gid through `GETGRGID` to emit group names. The by-group path gets the group record and emits each member. The check path gets the group and scans its comma-separated member list for the requested username.

## State And Persistence Behavior
All operational state is per call and talloc-scoped: fake client/request objects, copied usernames/groupnames, gid arrays, delayed group/member data, and a referenced call object. `vl_active` is cleared in destructors. No persistent winbind data is modified.

## Dependencies And Integration Points
It depends on varlink, winbind group expansion behavior, `lp_winbind_expand_groups()`, group enumeration support, and internal async NSS handlers. It is the membership side of the systemd userdb integration.

## Risks And Test Signals
This file is sensitive to compile and control-flow correctness. The checked-out source has suspicious constructs including an undefined-looking `struct memberships_enum_state` in the enumeration connection-closed callback and historical-looking duplicate declarations/error arguments in nearby code, so build coverage with `with_systemd_userdb` is essential. Behavioral risks include `strtok_r` mutating member buffers, `GETGROUPS` gid ordering being reversed while emitted, no-record behavior for groups with zero members, and exact `continues` handling. Tests should cover all four modes, disabled expansion, missing `more`, users with one and many groups, empty groups, and positive/negative membership checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_varlink_getmemberships.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_varlink_getuserrecord.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_varlink_getuserrecord.c

## Purpose
This file implements varlink `GetUserRecord` operations: enumerate users, lookup by uid, lookup by name, and lookup by both name and uid with conflict detection.

## Important APIs, Types, And Functions
`user_record_reply()` builds systemd userdb record objects from `struct winbindd_pw`. Public handlers are `wb_vl_user_enumerate()`, `wb_vl_user_by_uid()`, `wb_vl_user_by_name()`, and `wb_vl_user_by_name_and_uid()`. Each path uses a per-call state object, fake winbind request/client objects, callbacks, and connection-closed cleanup.

## Control Flow
Enumeration requires `lp_winbind_enum_users()` and `VARLINK_CALL_MORE`, runs `SETPWENT`, repeated `GETPWENT` chunks of 500, and `ENDPWENT`, delaying the last record so the final reply lacks `continues`. UID and name lookups synthesize `GETPWUID` or `GETPWNAM` requests and translate `NONE_MAPPED` to `NoRecordFound`. Name lookup overwrites the returned username with the requested string so systemd's multiplexer accepts UPN lookups. Name+uid first tries name, falls back to uid on miss, and returns `ConflictingRecordFound` if both fields do not match.

## State And Persistence Behavior
The file uses only per-call memory plus `vl_active`. It relies on normal winbind caches and NSS state below the async handlers but does not persist records itself.

## Dependencies And Integration Points
It depends on varlink, winbind getpw* async commands, `winbindd_setpwent/endpwent`, `lp_winbind_enum_users()`, and string wrappers. It integrates with systemd userdb clients through `winbindd_varlink.c`.

## Risks And Test Signals
Risks include chunk-boundary `continues` handling, fake-client parity, integer range conversion from varlink `int64_t` to uid fields, name rewriting for UPNs, and conflict semantics when name and uid identify different records. Tests should cover disabled enumeration, missing `more`, multi-chunk enumeration, uid/name misses, UPN lookups, and name+uid conflicts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_varlink_getuserrecord.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_wins_byip.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_wins_byip.c

## Purpose
This file implements the asynchronous `WINBINDD_WINS_BYIP` command. It performs a NetBIOS node status query for a numeric IP address and returns matching workstation/server names.

## Important APIs, Types, And Functions
The entry points are `winbindd_wins_byip_send()`, `winbindd_wins_byip_done()`, and `winbindd_wins_byip_recv()`. State includes the wildcard NetBIOS name, parsed socket address, and fixed-size response buffer.

## Control Flow
`send()` null-terminates the client request string, initializes the response as `<ip>\t`, creates a wildcard `*` NetBIOS name, parses the IP with `interpret_string_addr(..., AI_NUMERICHOST)`, and dispatches `node_status_query_send()`. The callback receives node status names, filters out group names and non-0x20 entries, appends names separated by spaces, replaces the trailing space/tab with newline, and completes the request.

## State And Persistence Behavior
All state is request-local. The command sends network queries but does not persist data.

## Dependencies And Integration Points
It depends on Samba namequery/nmblib helpers, tevent, fixed `fstring` response handling, and winbind request/response structures. It serves legacy WINS lookup clients.

## Risks And Test Signals
Risks include response buffer overflow, invalid numeric address handling, no matching 0x20 names causing the tab to become a newline, and IPv4/IPv6 formatting compatibility. Tests should cover invalid input, single and multiple names, group-name filtering, and oversized response handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_wins_byip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_wins_byname.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_wins_byname.c

## Purpose
This file implements the asynchronous `WINBINDD_WINS_BYNAME` command. It resolves a NetBIOS name to IP addresses through WINS first and broadcast fallback second.

## Important APIs, Types, And Functions
The command uses `winbindd_wins_byname_send()`, `winbindd_wins_byname_wins_done()`, `winbindd_wins_byname_bcast_done()`, and `winbindd_wins_byname_recv()`. State tracks the event context, original request, returned socket-address array, and count.

## Control Flow
`send()` null-terminates the name and calls `resolve_wins_send()` for type 0x20. If WINS succeeds, the request completes. If it fails, the callback starts `name_resolve_bcast_send()`. `recv()` formats returned addresses separated by spaces followed by a tab, original name, and newline, then copies the result into the fixed winbind response buffer after checking size.

## State And Persistence Behavior
State is request-local and network-derived. No persistent storage is updated.

## Dependencies And Integration Points
It depends on namequery, nmblib, socket address formatting, tevent, and winbind response structures. It integrates with legacy WINS-by-name winbind clients.

## Risks And Test Signals
Risks are fallback timing, address-list formatting, response marshalling overflow, and behavior when WINS fails but broadcast succeeds. Tests should cover WINS success, broadcast fallback, total failure, multiple addresses, and oversized responses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_wins_byname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_xids_to_sids.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_xids_to_sids.c

## Purpose
This file implements the asynchronous external `WINBINDD_XIDS_TO_SIDS` command. It maps newline-separated Unix ID requests to SID strings.

## Important APIs, Types, And Functions
The command is implemented by `winbindd_xids_to_sids_send()`, `winbindd_xids_to_sids_done()`, and `winbindd_xids_to_sids_recv()`. It uses `parse_xidlist()` from `winbindd_util.c`, `wb_xids2sids_send/recv()`, `struct unixid`, and `struct dom_sid`.

## Control Flow
`send()` validates null-terminated extra data, parses `U<id>` and `G<id>` lines, and starts the idmap conversion request. The callback receives an array of SIDs. `recv()` writes one line per input XID, using the SID string when mapped and `-` when the result is the null SID.

## State And Persistence Behavior
State is request-local: parsed XIDs, count, and result SIDs. Persistence is delegated to idmap backends, which may read or allocate mappings.

## Dependencies And Integration Points
It depends on winbind request framing, tevent, ID parsing utilities, idmap conversion helpers, and SID formatting. It integrates with clients that batch UID/GID-to-SID conversion.

## Risks And Test Signals
Risks include strict parser rejection, unsigned ID overflow, null SID handling, and response size accounting. Tests should cover UID and GID inputs, invalid type prefixes, empty input, unmapped IDs, and large batches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_xids_to_sids.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wscript_build -->
# sources/user-network-fs/samba/source3/winbindd/wscript_build

## Purpose
This Waf build script defines the Samba3 winbindd/idmap/nss_info build graph. It declares idmap libraries/modules, nss_info modules, optional varlink support, the core `winbindd-lib` subsystem, and the `winbindd` binary.

## Important APIs, Types, And Functions
The file uses Waf helpers such as `bld.SAMBA3_LIBRARY`, `bld.SAMBA3_SUBSYSTEM`, `bld.SAMBA3_MODULE`, and `bld.SAMBA3_BINARY`. The important targets in this subset are `VARLINK`, `winbindd-lib`, and `winbindd`, plus idmap and nss_info module targets.

## Control Flow
Build declarations are evaluated by Waf. Module enablement is conditional on configured static/enabled module state, LDAP availability, `with_systemd_userdb`, and `build_winbind`. `VARLINK` compiles the four varlink sources only when systemd userdb support is enabled. `winbindd-lib` aggregates the core winbindd C sources and depends on `VARLINK`, RPC, idmap, passdb, ADS, messaging, and related subsystems. `winbindd` links `winbindd.c` against `winbindd-lib`.

## State And Persistence Behavior
There is no runtime state. Build state is generated artifacts, enabled module selections, and install output under `${SBINDIR}` for the binary.

## Dependencies And Integration Points
It integrates winbindd with Samba's broader build system, idmap plugin loading model, nss_info plugin model, optional varlink/systemd support, and the Samba3 binary installation path.

## Risks And Test Signals
Risks include missing source/dependency entries when files are added, optional varlink code not compiling unless `with_systemd_userdb` is exercised, LDAP-gated modules silently dropping from builds, and broad `winbindd-lib` dependency churn. Test signals are configuration/build matrix coverage for static and shared modules, LDAP on/off, systemd userdb on/off, and `build_winbind` enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/wscript_build -->
