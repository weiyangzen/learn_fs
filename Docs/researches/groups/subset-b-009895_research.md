# subset-b-009895 Research

Grouped research for Samba winbindd cache, credential-cache, domain child, and domain controller connection-management sources. Each section is delimited for deterministic reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_cache.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_cache.c

## Purpose

`winbindd_cache.c` implements winbindd's persistent cache database for domain lookups, policy queries, offline logon credentials, trusted-domain metadata, and selected NDR-level winbind responses. It backs the higher-level `wb_cache_*` API used by winbind domain backends, while preserving enough state in `winbindd_cache.tdb` to keep name/SID lookups and cached logons working when a domain controller is unavailable.

The file also owns cache initialization, validation, version upgrade, and global offline-state persistence. It chooses the correct backend for a domain on first use, avoids caching local SAM and BUILTIN domains for normal entries, and coordinates cache expiry with domain sequence numbers and online/offline state.

## Important APIs, Types, and Functions

- `struct winbind_cache` wraps the global `TDB_CONTEXT *tdb`.
- `struct cache_entry` is the serialized centry format: `NTSTATUS status`, `uint32_t sequence_number`, `uint64_t timeout`, and a packed byte stream with an offset.
- `winbindd_use_cache()`, `winbindd_use_idmap_cache()`, `winbindd_set_use_cache()`, and `winbindd_flush_caches()` expose cache policy and flushing.
- `get_cache()` lazily initializes a global cache handle and initializes the domain backend.
- `centry_*` readers and writers encode and decode integers, `NTTIME`, `time_t`, strings, hashes, SIDs, and statuses.
- `wcache_fetch()`, `centry_start()`, and `centry_end()` are the generic centry read/write path.
- `refresh_sequence_number()`, `wcache_fetch_seqnum()`, and `wcache_store_seqnum()` keep per-domain sequence metadata in `SEQNUM/<domain>`.
- Lookup wrappers include `wb_cache_name_to_sid()`, `wb_cache_sid_to_name()`, `wb_cache_rids_to_names()`, `wb_cache_query_user_list()`, `wb_cache_enum_dom_groups()`, `wb_cache_enum_local_groups()`, `wb_cache_lookup_usergroups()`, `wb_cache_lookup_useraliases()`, `wb_cache_lookup_aliasmem()`, `wb_cache_lookup_groupmem()`, `wb_cache_lockout_policy()`, and `wb_cache_password_policy()`.
- Offline credential APIs include `wcache_cached_creds_exist()`, `wcache_get_creds()`, `wcache_save_creds()`, `wcache_count_cached_creds()`, and `wcache_remove_oldest_cached_creds()`.
- Global offline APIs are `set_global_winbindd_state_offline()`, `set_global_winbindd_state_online()`, and `get_global_winbindd_state_offline()`.
- Validation and migration APIs are `winbindd_validate_cache()`, `winbindd_validate_cache_nobackup()`, and `winbindd_cache_validate_and_initialize()`.
- Trusted-domain-cache APIs are `wcache_tdc_fetch_list()`, `wcache_tdc_add_domain()`, `wcache_tdc_fetch_domain()`, and `wcache_tdc_clear()`.
- NDR response caching is exposed through `wcache_fetch_ndr()` and `wcache_store_ndr()`.

## Control Flow

Normal cached calls begin by calling `get_cache(domain)`, which initializes the domain backend and opens `winbindd_cache.tdb` if needed. Lookup functions then try a cache-specific fetch path. A hit is accepted only if `wcache_fetch()` refreshes the domain sequence number and `centry_expired()` decides the centry remains valid. If there is no usable hit, the wrapper calls `domain->backend->...`, handles timeout or DC-not-found results by possibly calling `set_domain_offline()`, and saves successful responses with `centry_start()`/`centry_end()`.

Name/SID lookup uses the separate `namemap_cache` instead of the generic centry format. `wb_cache_name_to_sid()` first checks `namemap_cache_find_name()`, then calls the backend and stores name-to-SID and sometimes SID-to-name mappings. `wb_cache_sid_to_name()` similarly checks `namemap_cache_find_sid()` before backend lookup and reverse caching. `wb_cache_rids_to_names()` loops over individual SID entries and falls back to the backend if any RID is not cached.

User, group, alias, policy, and list queries use centry keys such as `UL/<domain>`, `GL/<domain>/domain`, `GL/<domain>/local`, `UG/<sid>`, `UA/<sid-list>`, `AM/<sid>`, `GM/<sid>`, `LOC_POL/<domain>`, and `PWD_POL/<domain>`. They decode typed fields in the exact order they encode them and return the cached `NTSTATUS`.

Validation traverses the TDB and dispatches each key to a per-prefix validator in `key_val[]`. Corrupt entries set flags in `tdb_validation_status`; unknown keys are rejected. Version 1 databases are upgraded to version 2 by adding the `timeout` field to each centry.

## State and Persistence Behavior

The persistent file is `state_path(..., "winbindd_cache.tdb")`. If offline logon is disabled, the TDB is opened with `TDB_CLEAR_IF_FIRST`, so restart can clear it. If offline logon is enabled, cache state persists across restart and is validated with backup support.

The TDB stores both centry and non-centry keys. Non-centry prefixes include `NDR/`, `SEQNUM/`, `TRUSTDOMCACHE/`, `WINBINDD_OFFLINE`, and `WINBINDD_CACHE_VERSION`; cleanup and validation treat them specially. Generic centries store status, sequence, timeout, then payload. Cached credential records store creation time, a salted MD5 of salt plus NT hash, and the salt; old unsalted records are tolerated on read.

Offline behavior is deliberate. If global offline logon is active or a specific domain is offline, `centry_expired()` keeps cached entries usable even past normal timeout. `lookup_cached_name()` temporarily marks the domain offline to avoid expiry during cached logon lookup. `WINBINDD_OFFLINE` is persisted in the same TDB as a four-byte timestamp marker.

The trusted-domain cache stores a packed list under `TRUSTDOMCACHE/<workgroup>`. NDR cache keys include `NDR/<domain>/<opnum>/<raw request bytes>` and store sequence number, timeout, and response bytes.

## Dependencies and Integration Points

This file sits between winbind callers and `struct winbindd_methods` backends, selected from passdb, built-in, RPC reconnect, or ADS reconnect methods. It integrates with `tdb`, `tdb_validate`, `namemap_cache`, `samlogon_cache`, NSS alias mapping, GnuTLS hashing, passdb machine SID helpers, ADS code, and winbind connection management via `init_dc_connection()`, `set_domain_offline()`, and domain online state.

It is consumed by credential-cache code (`winbindd_creds.c`), connection manager code (`winbindd_cm.c` for global offline state and trusted DC state), and lookup/auth paths throughout winbindd. The NDR cache depends on generated winbind opnum constants such as `NDR_WBINT_LOOKUPSID` and `NDR_WBINT_DSGETDCNAME`.

## Risks and Edge Cases

- The centry string format stores lengths in one byte and truncates strings longer than 254 bytes, which can affect unusual account names or descriptions.
- Many readers panic through `smb_panic_fn()` on malformed data; validation mode swaps in `validate_panic()` to turn those into validation failures.
- `wcache_remove_oldest_cached_creds()` reads a creation timestamp directly from TDB data offset zero, even though current centry records begin with status/sequence/timeout and then creation time. This should be verified against historical credential formats and tests because eviction order could be wrong if interpreted against the current layout.
- Offline mode intentionally returns stale data. That is required for offline logon but increases the importance of correct transition handling when domains return online.
- Name/SID reverse caching avoids some mappings, such as UPN reverse maps and SID history cases, to avoid poisoning later lookups.
- NDR cache validation currently does not parse or checksum response data, so corrupted NDR cache payloads may survive validation.
- Global `wcache` and mutable `domain` state assume winbindd's process model and locking discipline; careless reuse after fork is unsafe unless closed.

## Test Signals

High-value tests should cover centry round trips for every key prefix, cache expiry under online/offline/global-offline states, version 1 to version 2 upgrade, validation rejection for malformed lengths and unknown keys, negative mapping behavior, salted and old credential retrieval, maximum cached-login eviction, trusted-domain pack/unpack compatibility, and NDR cache sequence/timeout invalidation. Integration tests should simulate backend timeout/DC-not-found and verify fallback to cached data only when the domain transitions offline.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_ccache_access.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_ccache_access.c

## Purpose

`winbindd_ccache_access.c` implements parent-winbindd request handlers that let local clients save plaintext credentials in the in-memory winbind credential cache and later use those stored credentials to answer an NTLMSSP challenge. It is the access-control layer over `WINBINDD_MEMORY_CREDS`, binding credential access to the peer UID on the winbind socket.

## Important APIs, Types, and Functions

- `winbindd_ccache_save()` handles the save-password request and calls `winbindd_add_memory_creds()`.
- `winbindd_ccache_ntlm_auth()` handles NTLM authentication using a stored password.
- `check_client_uid()` uses `getpeereid()` to verify the request's claimed UID matches the socket peer or the initial/root UID.
- `client_can_access_ccache_entry()` permits access only to the credential owner UID or UID 0.
- `do_ntlm_auth_with_stored_pw()` drives a GENSEC NTLMSSP client using a stored plaintext password and returns the authenticate blob, 16-byte session key, and new-SPNEGO indicator.

## Control Flow

For `winbindd_ccache_save()`, the handler null-terminates fixed-size request strings, canonicalizes the requested account, checks that the referenced authentication domain exists, verifies the socket peer UID, and stores the password with `winbindd_add_memory_creds(user, uid, pass)`.

For `winbindd_ccache_ntlm_auth()`, the handler canonicalizes and validates the requested account, finds the auth domain, verifies the peer UID, validates that the initial and challenge blob lengths fit within `request->extra_len` without integer wrap, reparses the canonicalized name, and finds `WINBINDD_MEMORY_CREDS`. It then checks owner access. If both blobs are empty, it treats the request as an availability probe. Otherwise it builds `DATA_BLOB`s over the caller-provided negotiate and challenge data and calls `do_ntlm_auth_with_stored_pw()`. On success it copies the generated auth blob into response extra data and fills the session key.

`do_ntlm_auth_with_stored_pw()` prepares an `auth_generic_state`, sets username/domain/password, requests a session key for empty initial messages, starts mechanism `ntlmssp_resume_ccache`, injects the initial negotiate message to advance the state machine, processes the server challenge, extracts a 16-byte session key, and returns the generated authenticate message.

## State and Persistence Behavior

The file does not persist data itself. It relies on the process-local memory credential list managed in `winbindd_cred_cache.c`. Saved passwords can be mlocked and reference-counted there. Responses are stored only in the current winbind request/response buffers.

The access decision is stateful with respect to the Unix socket peer. A client-provided UID is not trusted until `getpeereid()` confirms it. Root/initial UID may act on behalf of other users.

## Dependencies and Integration Points

This file depends on winbind request structures, domain canonicalization helpers (`canonicalize_username()`, `parse_domain_user()`, `find_auth_domain()`), the in-memory credential cache (`find_memory_creds_by_name()`, `winbindd_add_memory_creds()`), and Samba GENSEC/auth-generic NTLMSSP client APIs.

It is a bridge between PAM/ntlm_auth-style clients that store credentials and later NTLMSSP challenge handling that needs the user's password, while avoiding a domain-child round trip for memory cache access.

## Risks and Edge Cases

- Plaintext passwords are used for NTLMSSP response generation; protection depends on the memory credential layer and process security.
- Access checks depend on `getpeereid()` availability and correctness. Failure to retrieve peer credentials denies access.
- The blob-length guard explicitly checks overflow and overrun; regressions here would expose request extra-data parsing bugs.
- The function returns boolean success rather than directly sending rich NT status to callers, so diagnostics rely on logs and response fields.
- An empty initial and challenge blob is a probe path and should not accidentally disclose session key material.

## Test Signals

Tests should cover UID mismatch denial, root/initial UID override, missing memory credentials, malformed blob lengths including wraparound, zero-length probe behavior, successful NTLMSSP challenge response generation, session-key length enforcement, canonical name rewriting, and save failure when the domain is unknown.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_ccache_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_change_machine_acct.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_change_machine_acct.c

## Purpose

`winbindd_change_machine_acct.c` implements the asynchronous parent-side handler for `WINBINDD_CHANGE_MACHINE_ACCT`. It locates the requested domain and forwards the machine-account password change operation to that domain's winbind child over the generated `wbint` DCERPC interface.

## Important APIs, Types, and Functions

- `struct winbindd_change_machine_acct_state` is an empty tevent state holder.
- `winbindd_change_machine_acct_send()` validates the target domain and starts `dcerpc_wbint_ChangeMachineAccount_send()`.
- `winbindd_change_machine_acct_done()` receives both transport status and operation result and completes the parent request.
- `winbindd_change_machine_acct_recv()` exposes `tevent_req_simple_recv_ntstatus()`.

## Control Flow

The send function creates a tevent request, optionally extracts `request->data.init_conn.dcname`, resolves `request->domain_name` via `find_domain_from_name()`, and returns `NT_STATUS_NO_SUCH_DOMAIN` if missing. Internal domains complete successfully without child RPC, because they are passdb-based and the code intentionally avoids changing an AD DC password without updating all required databases. External domains are forwarded to `dom_child_handle(domain)` with the optional DC name. The callback merges the wrapper status and child result with `any_nt_status_not_ok()`.

## State and Persistence Behavior

This file does not store state directly. Durable changes happen in the child-side machine-account-change implementation and secrets/passdb layers outside this file. Its local state is only the tevent request object.

## Dependencies and Integration Points

The file depends on winbind domain lookup, domain child handles, tevent, and generated `ndr_winbind_c.h` client stubs. It is part of winbind's async command dispatch path and expects the domain child to own the real account-change mechanics.

## Risks and Edge Cases

- Internal domains are treated as success; callers expecting an actual password rotation for an internal/AD-DC-local case must be aware of the intentional bypass.
- Optional DC affinity is passed through only when the request field is non-empty.
- Result handling must consider both RPC transport status and remote operation status; `any_nt_status_not_ok()` handles that merging.
- A missing child or broken child handle will surface as the generated RPC send/recv status.

## Test Signals

Tests should cover missing domain, internal-domain short-circuit, external-domain RPC forwarding with and without explicit DC name, child result failure propagation, and transport failure propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_change_machine_acct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_check_machine_acct.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_check_machine_acct.c

## Purpose

`winbindd_check_machine_acct.c` implements the asynchronous parent-side handler for `WINBINDD_CHECK_MACHINE_ACCT`. It checks whether a domain machine account is valid by resolving the domain and delegating the check to the appropriate domain child.

## Important APIs, Types, and Functions

- `struct winbindd_check_machine_acct_state` is an empty tevent state holder.
- `winbindd_check_machine_acct_send()` resolves the target domain and starts `dcerpc_wbint_CheckMachineAccount_send()`.
- `winbindd_check_machine_acct_done()` receives the child RPC result and completes or errors the request.
- `winbindd_check_machine_acct_recv()` returns the NT status and calls `set_auth_errors()` on the response.

## Control Flow

The send function creates a tevent request. If `request->domain_name` is empty, it preserves old behavior by using `find_our_domain()`. Otherwise it uses `find_domain_from_name()`. Missing domains return `NT_STATUS_NO_SUCH_DOMAIN`. Internal domains are immediately successful because they are passdb-based and always contactable. External domains are checked through `dom_child_handle(domain)`. The callback receives both transport and operation result and fails the request if either is not OK.

## State and Persistence Behavior

No persistent state is owned here. The file only participates in async request lifecycle state. `winbindd_check_machine_acct_recv()` writes authentication error information into the caller response via `set_auth_errors()`.

## Dependencies and Integration Points

The handler integrates with winbind request dispatch, domain lookup, domain child RPC, tevent, generated winbind RPC stubs, and response auth-error population. The actual machine-account validation work occurs in the domain child.

## Risks and Edge Cases

- Empty domain name falls back to the local joined domain; tests should preserve this compatibility behavior.
- Internal domains always pass, so this does not detect passdb corruption.
- Failure propagation depends on checking both generated RPC status and the child-returned result.

## Test Signals

Tests should cover empty-domain fallback, missing domain, internal-domain success, external-domain child success, child failure status, transport failure status, and response auth-error fields on receive.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_check_machine_acct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_cm.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_cm.c

## Purpose

`winbindd_cm.c` is winbindd's domain-controller connection manager. It centralizes domain online/offline transitions, DC discovery and affinity, SMB session setup, RPC pipe creation, schannel/Kerberos/NTLMSSP authentication selection, connection invalidation, and messaging hooks for network changes.

Its job is to hide connection policy from individual winbind operations: callers ask for SAMR, LSA, LSAT, or NETLOGON connections, and this file finds a suitable DC, authenticates or falls back according to configuration and trust state, caches the connection in `domain->conn`, and reinitializes state on failure.

## Important APIs, Types, and Functions

- `struct dc_name_ip` pairs a DC name string with a `sockaddr_storage`.
- Online/offline entry points include `set_domain_offline()`, `set_domain_online_request()`, message handlers `winbind_msg_domain_offline()` and `winbind_msg_domain_online()`, and private `set_domain_online()`.
- Negative connection helpers include `winbind_add_failed_connection_entry()` and `winbind_idmap_add_failed_connection_entry()`.
- Credential helpers include `cm_get_ipc_userpass()`, `cm_get_ipc_credentials()`, `cm_is_ipc_credentials()`, and `winbindd_get_trust_credentials()`.
- DC discovery and selection use `get_dcs()`, `dcip_check_name()`, optional ADS `dcip_check_name_ads()`, `connect_preferred_dc()`, and `find_dc()`.
- Connection setup and lifecycle use `cm_prepare_connection()`, `cm_open_connection()`, `invalidate_cm_connection()`, `close_conns_after_fork()`, `connection_ok()`, `init_dc_connection()`, and `init_dc_connection_rpc()`.
- Domain metadata detection uses `set_dc_type_and_flags_trustinfo()`, `set_dc_type_and_flags_connect()`, and `set_dc_type_and_flags()`.
- Pipe connection APIs are `cm_connect_sam()`, `cm_connect_lsa()`, `cm_connect_lsat()`, `cm_connect_netlogon()`, and `cm_connect_netlogon_secure()`.
- `wb_open_internal_pipe()` opens local RPC pipes for internal domains.
- Message handlers `winbind_msg_ip_dropped()` and `winbind_msg_disconnect_dc()` close affected connections.

## Control Flow

Connection initialization starts with `init_dc_connection()` or `init_dc_connection_rpc()`. Internal and BUILTIN domains avoid network work; external domains check `connection_ok()`, invalidate stale connection state, optionally learn trust flags via the primary domain, then call `cm_open_connection()`.

`cm_open_connection()` tries up to three DC connection attempts. Each attempt calls `find_dc()` to reuse server affinity or discover DCs through DNS/NetBIOS, then `cm_prepare_connection()` to create an SMB client, negotiate protocol, decide whether IPC authentication is needed, authenticate with trust credentials or configured IPC credentials, optionally fall back to anonymous, and tree-connect to `IPC$` unless an AD DC path does not require SMB. A successful connection moves the domain online, clears global offline state, updates KDC locator state, caches current DC info in gencache, and selects pipe auth level based on `winbind sealed pipes`.

DC discovery first tries the server-affinity cache or forced DC, skipping negative connection cache entries. If no preferred DC works, `get_dcs()` builds a sorted DC list from site-specific AD DNS, general AD DNS, NetBIOS queries, and fallback DNS. `find_dc()` attempts parallel/any connection with `smbsock_any_connect()`, resolves IP-only entries to DC names with CLDAP or NetBIOS status, and records failures in the negative connection cache.

Pipe connection functions build on the domain connection. `cm_connect_sam()` prefers SPNEGO-authenticated SAMR using trust or IPC credentials, falls back to schannel/Kerberos, and only falls back to anonymous if sealed pipes and strong key requirements allow it. `cm_connect_lsa()` follows similar logic and `cm_connect_lsat()` prefers LSA over TCP for AD domains when available. `cm_connect_netlogon()` prefers NETLOGON over TCP for AD if possible and otherwise uses named pipe transport. `cm_connect_netlogon_secure()` additionally requires a non-null secure channel and returns the netlogon credential context.

## State and Persistence Behavior

Most state is held in `struct winbindd_domain`: `online`, `startup`, `initialized`, `backend`, `dcname`, `dcaddr`, domain flags, AD capability flags, secure channel type, and `domain->conn` pipe/client handles. `invalidate_cm_connection()` clears sequence number state, closes SAMR/LSA/NETLOGON pipes, resets auth level, frees netlogon creds, and shuts down the SMB client.

Persistent or cross-process state is stored through other subsystems: server affinity via `saf_store()`/`saf_fetch()`, failed DC entries via negative connection cache helpers, current DC via gencache key `CURRENT_DCNAME/<domain>`, site/KDC locator files/env updates, and global offline state through `winbindd_cache.c`. Domain online/offline changes are broadcast through the Samba messaging system to parent and idmap child processes.

After fork, `close_conns_after_fork()` disconnects low-level SMB sockets and invalidates all domain connections, then closes client sockets in inherited winbind client state.

## Dependencies and Integration Points

This file integrates with libsmb transport/session code, RPC pipe clients, generated NETLOGON/SAMR/LSA/DSSETUP interfaces, ADS CLDAP and sitename helpers, name query and DC discovery helpers, secrets/passdb trust credentials, `cli_credentials`, GENSEC, netlogon credential contexts, Samba messaging, gencache, server affinity cache, negative connection cache, idmap child messaging, and winbind Kerberos ccache refresh (`ccache_regain_all_now()`).

It is a central dependency for winbind backends and cache code: cache refresh uses `init_dc_connection()`, lookup wrappers call `set_domain_offline()` on DC failure, and domain child operations depend on `domain->conn` pipe handles created here.

## Risks and Edge Cases

- Authentication fallback is security-sensitive. Anonymous fallback is blocked when sealed pipes or strong keys are required, but configuration changes can allow weaker behavior.
- Server affinity and negative connection caches can steer DC choice; stale or over-broad negative entries can delay recovery.
- AD DC handling intentionally permits paths where SMB setup is ignored because only TCP RPC will be used; regressions can break trusted-domain or firewall scenarios.
- `set_global_winbindd_state_offline()` is triggered when no DC is found, coupling connection failure to offline-logon behavior.
- The code mutates domain identity fields when a DC reports canonical NetBIOS/DNS/SID data; mismatch checks are critical to avoid accepting the wrong DC.
- Pipe reuse relies on `rpccli_is_connected()` and SMB session validity; expired SMB2 sessions trigger limited retry logic.
- Fork handling must be called in children to avoid inherited live sockets and pipe handles.

## Test Signals

Tests should cover forced DC and server-affinity selection, negative connection cache skipping, AD site-specific discovery, IP-to-DC-name resolution failure loops, online/offline messaging, global offline transition, connection invalidation, fork cleanup, trust credential and IPC fallback paths, anonymous fallback denial under sealed-pipe/strong-key settings, SAMR/LSA/NETLOGON retry after expired sessions, current-DC gencache store/fetch, and domain metadata mismatch rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_cm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_cred_cache.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_cred_cache.c

## Purpose

`winbindd_cred_cache.c` manages two process-local credential structures for winbindd: Kerberos credential-cache entries with refresh/regain timers, and mlocked in-memory password/hash credentials used by cached NTLM and Kerberos ticket renewal paths. It keeps tickets alive when possible and regains them after offline authentication when domains return online.

## Important APIs, Types, and Functions

- `MAX_CCACHES` limits live ccache entries to 100.
- `ccache_list` stores `WINBINDD_CCACHE_ENTRY` records.
- `memory_creds_list` stores `WINBINDD_MEMORY_CREDS` records.
- `krb5_event_refresh_time()` computes the midpoint refresh schedule before ticket expiry.
- `ccache_remove_all_after_fork()` clears inherited ccache timers and entries.
- `ccache_entry_exists()` and `ccache_entry_identical()` inspect ccache entries.
- `add_ccache_to_list()` creates or references a Kerberos ccache entry and schedules renew/regain events.
- `remove_ccache()` decrements references and destroys the Kerberos ccache with `ads_kdestroy()` when the last reference is gone.
- `ccache_regain_all_now()` immediately reschedules all ccache entries for refresh or regain.
- `find_memory_creds_by_name()`, `winbindd_add_memory_creds()`, `winbindd_delete_memory_creds()`, and `winbindd_replace_memory_creds()` expose in-memory credential management.
- Private `store_memory_creds()`, `delete_memory_creds()`, and replace/add helpers allocate, mlock, populate, zero, and munlock credential memory when supported.

## Control Flow

When a login creates a Kerberos ccache, `add_ccache_to_list()` validates identity fields, enforces `MAX_CCACHES`, reuses an identical existing entry by incrementing refcount, or allocates a new `WINBINDD_CCACHE_ENTRY`. If `winbind refresh tickets` is disabled or there is no renewal window, it just records the entry. Otherwise it schedules a refresh timer at half the remaining ticket lifetime, or a gain timer for postponed/offline requests. If a refresh timer exists, the user's password is also stored via `winbindd_add_memory_creds()` so rekinit can happen later.

`krb5_ticket_refresh_handler()` renews an existing ticket as the user UID. If the renewal window has expired, it attempts password-based rekinit using the linked memory credentials. KDC unreachable or realm-resolution failures schedule a later gain attempt rather than breaking the chain. Expired or missing tickets can jump to rekinit. If renewal will soon become impossible, the handler schedules a gain event shortly before expiry.

`krb5_ticket_gain_handler()` is used after offline authentication or destroyed tickets. It requires stored plaintext credentials, finds the domain by realm, waits if the domain is offline, then performs `kerberos_kinit_password_ext()` as the user UID. Success schedules the normal refresh handler; failure destroys any maybe-existing cache and retries later.

The memory credential path allocates one contiguous block for NT hash, LM hash, and optional plaintext password, locks it with `mlock()`, computes hashes from the password, reference-counts by username, and zeroes/unlocks memory on deletion. If the platform lacks `mlock`/`munlock`, these helpers return success but do not store usable credential buffers.

## State and Persistence Behavior

All state in this file is process-local. Kerberos tickets themselves live in external ccaches named by `entry->ccname`; this file destroys those ccaches on final removal. Timer state is attached to entries through `entry->event` in the global tevent context.

Memory credentials are intended to avoid paging via `mlock()`. They are reference-counted separately from ccache entries but can be linked through `entry->cred_ptr`. Deleting memory creds clears dangling ccache references. `ccache_remove_all_after_fork()` is required because timers and ccache entries should not be inherited by child processes.

## Dependencies and Integration Points

This file integrates with Samba Kerberos helpers (`kerberos_kinit_password_ext()`, `smb_krb5_renew_ticket()`, `ads_kdestroy()`), tevent global event context, winbind domain lookup and online state, effective UID switching, configuration (`winbind refresh tickets`, `winbind cache time`), and callers in PAM/auth paths and `winbindd_ccache_access.c`.

It also integrates with `winbindd_cm.c`: when a domain comes back online, `set_domain_online()` calls `ccache_regain_all_now()` to wake ticket regain/refresh work immediately.

## Risks and Edge Cases

- Plaintext passwords are intentionally retained when ticket refresh requires rekinit; failure of `mlock()` prevents storing them and returns an error on supported platforms.
- On platforms without `mlock`/`munlock`, memory credential functions are no-ops that report success, which can make callers believe credentials are stored when they are not.
- Reference counts must stay balanced across login/logout and ccache reuse; imbalances leak ccaches or destroy active tickets.
- Timer callbacks switch effective UID and must always regain root privilege on every path after Kerberos calls.
- KDC-unreachable retry loops intentionally persist; misconfigured realms can cause recurring timers and log noise.
- `ccache_entry_identical()` treats case-sensitive ccache name differences as invalid for the same username.

## Test Signals

Tests should cover ccache creation, identical reuse and refcounting, mismatch rejection, maximum ccache limit, removal and `ads_kdestroy()` behavior including missing ccache, fork cleanup, refresh timer scheduling, gain retry while domain offline, rekinit after expired renew window, memory credential add/replace/delete/refcount behavior, mlock failure handling, and dangling `cred_ptr` clearing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_cred_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_creds.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_creds.c

## Purpose

`winbindd_creds.c` is a small wrapper layer for offline cached logon credentials. It combines the persistent winbind credential cache in `winbindd_cache.c` with the Netlogon `SamInfo3` cache so winbind can retrieve enough information for cached authentication and store updated credentials after online authentication.

## Important APIs, Types, and Functions

- `MAX_CACHED_LOGINS` limits persistent cached credential records to 10.
- `winbindd_get_creds()` reads the cached NT password material and salt with `wcache_get_creds()` and retrieves matching `netr_SamInfo3` from `netsamlogon_cache_get()`.
- `winbindd_store_creds()` stores or updates cached credential data and optional SamInfo3.
- `winbindd_update_creds_by_info3()` and `winbindd_update_creds_by_name()` are simple wrappers around `winbindd_store_creds()`.

## Control Flow

`winbindd_get_creds()` first fetches password verifier material by SID from the TDB cache. If that succeeds, it fetches the user's `SamInfo3` from the net samlogon cache; both are required for success.

`winbindd_store_creds()` determines the credential SID either from supplied `info3` by composing domain SID plus RID, or by resolving the supplied username through `lookup_cached_name()`. With `info3`, it also marks `NETLOGON_CACHED_ACCOUNT` in `base.user_flags`. If a password is provided, it counts current cached credentials, evicts the oldest or existing record when the `MAX_CACHED_LOGINS` limit would be exceeded, computes the NT hash with `E_md4hash()`, and stores salted credential material via `wcache_save_creds()`. If both `info3` and `user` are provided, it stores the SamInfo3 record with `netsamlogon_cache_store()`.

## State and Persistence Behavior

Persistent password verifier state is stored in `winbindd_cache.tdb` through the `CRED/<sid>` records owned by `winbindd_cache.c`. SamInfo3 logon data is stored through the separate samlogon cache. This file does not keep process-local state.

The max cached login count is enforced before storing a new password record. Existing records for the same SID are deleted before eviction selection when possible.

## Dependencies and Integration Points

This file depends on `wcache_get_creds()`, `wcache_save_creds()`, `wcache_count_cached_creds()`, `wcache_remove_oldest_cached_creds()`, `lookup_cached_name()`, Netlogon SamInfo3 structures, `netsamlogon_cache_get()`/`netsamlogon_cache_store()`, and Samba password hash helpers.

It is part of winbind's offline logon path: online authentication updates this cache, and offline authentication retrieves from it.

## Risks and Edge Cases

- Both credential verifier and SamInfo3 must exist for `winbindd_get_creds()` to succeed; partial cache state causes cached logon failure.
- Username-only updates depend on an existing cached name-to-SID mapping. If that mapping is absent or expired, storage fails with no such user.
- The fixed `MAX_CACHED_LOGINS` eviction policy relies on `wcache_remove_oldest_cached_creds()` correctness.
- `info3->base.user_flags` is modified in place, which callers must tolerate.
- Passwordless calls can store SamInfo3 without updating the password verifier.

## Test Signals

Tests should cover storing with SamInfo3, storing by username through cached name lookup, missing SID/name failures, cache-limit eviction, existing SID replacement, successful retrieval requiring both CRED and SamInfo3, salted credential output, and failure when `netsamlogon_cache_store()` rejects the record.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_creds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_domain.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_domain.c

## Purpose

`winbindd_domain.c` contains the helper that initializes child processes for a single winbind domain. It is intentionally narrow: it iterates the domain's configured child slots and calls the generic child setup routine with a domain-specific log prefix.

## Important APIs, Types, and Functions

- `setup_domain_child(struct winbindd_domain *domain)` is the only function in the file.
- It uses `domain->children`, `talloc_array_length()`, and `setup_child(domain, &domain->children[i], "log.wb", domain->name)`.

## Control Flow

`setup_domain_child()` loops from zero to the talloc array length of `domain->children`. For each child record, it delegates initialization to `setup_child()`, passing the domain as owner/context, the child slot address, log prefix `"log.wb"`, and the domain name.

## State and Persistence Behavior

The file does not persist state itself. It mutates or initializes child records indirectly through `setup_child()`. Logging paths/names are derived from `"log.wb"` plus the domain name by the child setup layer.

## Dependencies and Integration Points

This helper depends on the `winbindd_domain` structure and the generic winbind child setup API declared in `winbindd.h`. It is part of winbind startup or domain-list initialization, ensuring each domain child has process metadata/logging configured before use.

## Risks and Edge Cases

- A null or malformed `domain->children` array would make the loop length depend on talloc metadata; callers are expected to provide a valid domain object.
- All children use the same log prefix and domain name; differentiation among multiple child slots must come from `setup_child()`.
- The function has no error reporting, so setup failures must be handled or logged inside `setup_child()`.

## Test Signals

Tests should verify that every child slot is passed to `setup_child()`, zero-child domains do nothing, the domain name and `"log.wb"` prefix are preserved, and setup failure behavior is visible through the lower-level child setup mechanism.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_domain.c -->
