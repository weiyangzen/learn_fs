# subset-b-009816 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/ldap.c -->
# sources/user-network-fs/samba/source3/libads/ldap.c

## Purpose

`ldap.c` is Samba source3's central ADS LDAP client implementation. It discovers an AD domain controller, opens LDAP/LDAPS/StartTLS sessions, performs SASL or anonymous binds, exposes search helpers, constructs LDAP add/modify/delete operations, and provides higher-level AD object helpers for machine accounts, SPNs, OUs, domain metadata, sites, SIDs, and token groups.

## Important APIs, Types, and Functions

Connection entry points are `ldap_open_with_timeout`, `ads_connect_cldap_only`, `ads_connect_creds`, `ads_connect_simple_anon`, `ads_connect_machine`, `ads_disconnect`, and `ads_zero_ldap`. DC discovery flows through `ads_find_dc`, `resolve_and_ping_dns`, `resolve_and_ping_netbios`, `cldap_ping_list`, `ads_try_connect`, and `ads_fill_cldap_reply`. Search APIs include `ads_do_search`, `ads_do_search_all`, `ads_do_search_all_args`, `ads_do_search_all_sd_flags`, `ads_do_search_all_fn`, `ads_search`, `ads_search_dn`, `ads_msgfree`, `ads_first_entry`, `ads_next_entry`, `ads_first_message`, and `ads_next_message`. Result extraction helpers include `ads_get_dn`, `ads_parent_dn`, `ads_pull_string`, `ads_pull_strings`, `ads_pull_strings_range`, `ads_pull_uint32`, `ads_pull_guid`, `ads_pull_sid`, `ads_pull_sids`, `ads_pull_sd`, and `ads_pull_username`.

Modification helpers use `ADS_MODLIST`, `LDAPMod`, and `berval`: `ads_init_mods`, `ads_mod_str`, `ads_mod_strlist`, `ads_add_strlist`, `ads_gen_mod`, `ads_gen_add`, and `ads_del_dn`. AD object helpers include `ads_find_machine_acct`, `ads_create_machine_acct`, `ads_move_machine_acct`, `ads_leave_realm`, `ads_clear_service_principal_names`, `ads_get_service_principal_names`, `ads_add_service_principal_names`, `ads_find_samaccount`, `ads_get_tokensids`, `ads_domain_sid`, `ads_domain_func_level`, `ads_current_time`, `ads_site_dn`, `ads_site_dn_for_machine`, `ads_upn_suffixes`, `ads_get_joinable_ous`, `ads_config_path`, `ads_get_extended_right_name_by_guid`, `ads_get_sid_from_extended_dn`, `ads_get_upn`, and `ads_check_ou_dn`.

## Control Flow

Connect begins by preserving any previously discovered socket address, resetting LDAP/TLS/wrap state, then resolving either a caller-specified LDAP server or a DC discovered from DNS SRV, site-aware SRV, NetBIOS fallback, or generated krb5 configuration paths. CLDAP/NetLogon replies populate `ads->config` with server name, realm, bind DN, site names, server flags, LDAP port, and socket address. For real LDAP binds, the code opens TCP, optionally sends StartTLS, installs TLS wrapping for LDAPS/StartTLS, stores closest-DC affinity, fetches `currentTime` for time offset, then binds anonymously or via `ads_sasl_bind`.

Searches convert local charset base/filter strings to UTF-8, disable referrals, and call OpenLDAP with Samba timeouts. Paged searches attach no-referrals and paged-results controls, optionally extended-DN or security-descriptor controls, collect cookies, and concatenate pages when OpenLDAP supports `ldap_add_result_entry`. `ads_do_search_all_fn` streams pages through `ads_process_results`, which determines string versus binary handling by asking the callback once per attribute.

Modification paths build talloc-owned `LDAPMod` arrays, UTF-8 encode DNs and string values, normalize list termination, optionally use the permissive modify control, then call OpenLDAP add/modify/delete APIs. Machine-account creation escapes the RDN, encodes quoted unicode password bytes, creates default HOST and RestrictedKrbHost SPNs, and adds a `computer` object. If the machine already exists, it changes `unicodePwd`, toggles `UF_ACCOUNTDISABLE`, and re-reads the object. Realm leave first tries tree-delete control, then falls back to deleting immediate children before deleting the machine object.

## State and Persistence Behavior

Primary runtime state lives in `ADS_STRUCT`: `ads->ldap.ld`, `ads->ldap.ss`, port, last attempt time, TLS wrap data, SASL wrap data, auth flags, KDC server, time offset, page size, realm/workgroup/bind path/server/site fields, and server flags. Discovery writes persistent-ish Samba caches through `sitename_store`, `saf_store`, `namecache_delete`, and negative connection cache helpers. Machine and SPN helpers persist changes in AD itself. Password and TLS/SASL buffers are talloc-owned and freed by `ads_disconnect` or stack frames.

## Dependencies and Integration Points

This file depends on OpenLDAP, Samba CLDAP/NetLogon ping code, tsocket, DNS/namequery DC sorting, gencache-backed sitename storage, passdb credentials, SASL/TLS wrappers, security descriptor and SID parsing, iconv charset helpers, and loadparm settings such as LDAP timeouts and page size. It is integrated by domain join/leave, winbind/idmap queries, `net ads`, printer publishing, schema lookup, SPN tools, and any source3 ADS LDAP consumer.

## Risks and Test Signals

Risks include process-global `SIGALRM` timeout handling, stale or incorrect site/DC caches, negative-cache propagation by IP/name, charset conversion failures, LDAP page-cookie/resource leaks, referral/paged-results interaction, race-prone ranged retrieval when `usnChanged` moves, incorrect RDN escaping, destructive SPN replacement, machine-account password handling, and subtree deletion fallback behavior. Test signals should cover DC discovery with site hit/miss/fallback, CLDAP flag filtering, LDAPS and StartTLS success/failure, SASL sign/seal/strong-auth retry, paged and unpaged searches, extended-DN and SD controls, reconnect after server-down/timeouts, ranged multi-value retrieval with USN restart, machine create/change/move/leave, SPN add/clear, SID/GUID/SD extraction, domain metadata queries, and OU DN validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/ldap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/ldap_printer.c -->
# sources/user-network-fs/samba/source3/libads/ldap_printer.c

## Purpose

`ldap_printer.c` publishes and locates AD `printQueue` objects for Samba printers. It bridges spoolss RPC printer metadata and ADS LDAP add/modify operations.

## Important APIs, Types, and Functions

Public functions are `ads_find_printer_on_server`, `ads_find_printers`, `ads_mod_printer_entry`, `ads_add_printer_entry`, and `get_remote_printer_publishing_data`. Mapping helpers `map_sz`, `map_dword`, `map_bool`, `map_multi_sz`, and `map_regval_to_ads` translate `struct registry_value` data into an `ADS_MODLIST`. The static `valmap_to_ads` table maps many `SPOOL_REG_*` registry names to AD attribute updates.

## Control Flow

`ads_find_printer_on_server` first locates the server machine account, extracts its DN/CN, then searches for a printer named `servercn-printer` with full attributes and `nTSecurityDescriptor`. `ads_find_printers` searches visible `printQueue` entries with UNC names. Add/modify wrappers delegate to `ads_gen_add` and `ads_gen_mod`, adding `objectClass=printQueue` for creates.

`get_remote_printer_publishing_data` opens the remote printer over spoolss, enumerates `DsDriver` and `DsSpooler` printer data keys, maps each returned registry value into LDAP modifications, adds the printer name, closes the policy handle, and returns the last spoolss status.

## State and Persistence Behavior

This file owns no durable local state. It reads remote spooler registry state and writes AD printer object attributes through LDAP modifications. Temporary printer names, mod lists, and enum results are caller/talloc owned.

## Dependencies and Integration Points

Dependencies include `ads.h`, OpenLDAP result helpers, spoolss RPC client helpers, registry value parsers, and spooler registry constants. It integrates with printer publishing workflows in `net ads`/Samba print serving and relies on `ldap.c` for search and modify operations.

## Risks and Test Signals

Risks include malformed server DNs, printer names requiring LDAP escaping, partial publication when one spoolss key fails but another succeeds, type mismatches in registry values, boolean values encoded as one-byte `REG_BINARY`, and silently ignored unmapped attributes. Tests should cover locating printers by server CN, publishing a representative mix of REG_SZ/REG_DWORD/REG_BINARY/REG_MULTI_SZ values, failed spoolss open/enum paths, AD add versus modify, and cleanup of LDAP/RPC resources.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/ldap_printer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/ldap_schema.c -->
# sources/user-network-fs/samba/source3/libads/ldap_schema.c

## Purpose

`ldap_schema.c` resolves AD schema metadata needed by Samba, especially POSIX attribute names for SFU, SFU 2.0, and RFC2307 mappings, plus lookup helpers for schema GUIDs and schema naming context.

## Important APIs, Types, and Functions

`ads_schema_path` reads `schemaNamingContext` from RootDSE. `ads_get_attrname_by_guid` encodes a schema GUID as LDAP NDR and searches `schemaIDGUID`. `ads_check_posix_schema_mapping` fills a `struct posix_schema` for a selected `enum wb_posix_mapping`. The internal `ads_get_attrnames_by_oids` searches for `attributeId` values and returns matching `lDAPDisplayName` names with OID/name arrays.

## Control Flow

For POSIX schema mapping, template/unixinfo modes return success without LDAP schema lookups. SFU, SFU20, and RFC2307 modes choose the corresponding OID arrays from `ldap_schema_oids.h`, fetch the schema DN, search for all requested OIDs under the schema container, and map each returned OID to the correct `posix_schema` field. The helper reports `STATUS_SOME_UNMAPPED` if fewer schema objects are returned than requested.

## State and Persistence Behavior

No global state is kept. Returned schema names are allocated under the caller-provided memory context through a `struct posix_schema`; temporary OID/name arrays live under an internal talloc context. The source of truth is AD schema state.

## Dependencies and Integration Points

It depends on ADS search/retry helpers, schema OID constants, LDAP NDR GUID encoding, and `ldap_schema.h` declarations. It integrates with winbind NSS/idmap code that must know the actual AD display names for Unix attributes instead of assuming one schema flavor.

## Risks and Test Signals

Risks include schema searches returning unordered results, missing optional `posix_uid_attr` not being validated while other fields are required, OID arrays not being NULL-terminated even though the helper checks only `num_OIDs`, and treating allocation failures and missing required mappings similarly. Tests should mock or exercise SFU/SFU20/RFC2307 schemas, partial OID matches, unknown map type, RootDSE schema DN failures, GUID lookup with zero/multiple hits, and memory ownership of returned schema strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/ldap_schema.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/ldap_schema.h -->
# sources/user-network-fs/samba/source3/libads/ldap_schema.h

## Purpose

`ldap_schema.h` declares Samba's ADS schema lookup surface for POSIX attribute mapping and schema GUID resolution.

## Important APIs, Types, and Functions

`struct posix_schema` stores AD display names for POSIX home directory, shell, uidNumber, gidNumber, gecos, and uid attributes. `enum wb_posix_mapping` names supported mapping modes: unknown, template, SFU, SFU20, RFC2307, and unixinfo. Function declarations expose `ads_get_attrname_by_guid`, `ads_schema_path`, and `ads_check_posix_schema_mapping`.

## Control Flow

The header has no runtime flow. Callers choose a mapping enum, call `ads_check_posix_schema_mapping`, and then use the returned attribute names in subsequent LDAP searches. GUID consumers call `ads_get_attrname_by_guid` after obtaining the schema DN.

## State and Persistence Behavior

The header defines only caller-owned data contracts. `struct posix_schema` instances are talloc-allocated by the implementation and reflect current AD schema metadata.

## Dependencies and Integration Points

It depends on ADS types, `TALLOC_CTX`, `ADS_STATUS`, and `struct GUID` declarations provided by broader Samba includes. It integrates with `ldap_schema.c`, winbind POSIX mapping, idmap backends, and ACL/security display code that resolves schema GUIDs to readable names.

## Risks and Test Signals

Risks are ABI drift if fields or enum values are changed without updating users, lack of explicit ownership comments for returned `struct posix_schema`, and compile-time dependency on `ADS_STRUCT` being declared before inclusion. Tests should include compile coverage for all consumers and runtime schema mapping for every enum branch.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/ldap_schema.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/ldap_schema_oids.h -->
# sources/user-network-fs/samba/source3/libads/ldap_schema_oids.h

## Purpose

`ldap_schema_oids.h` centralizes string constants for AD/SFU/RFC2307 LDAP attribute OIDs used to discover POSIX attribute display names dynamically.

## Important APIs, Types, and Functions

The file defines six OIDs each for Services for Unix 3.x, Services for Unix 2.0, and RFC2307: uidNumber, gidNumber, homeDirectory, loginShell, gecos, and uid.

## Control Flow

There is no executable flow. `ldap_schema.c` selects one OID set based on `enum wb_posix_mapping` and searches the schema for matching `attributeId` objects.

## State and Persistence Behavior

No state is kept. The constants are compile-time schema identifiers.

## Dependencies and Integration Points

The header has only include guards and macro definitions. It integrates with POSIX schema detection and indirectly with winbind NSS/idmap behavior.

## Risks and Test Signals

Risks are typo-sensitive OID constants and divergence from Microsoft/RFC schema definitions. Tests should verify that every OID constant maps to an expected attribute in representative AD schema fixtures and that adding new schema modes updates both this header and `ldap_schema.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/ldap_schema_oids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/ldap_user.c -->
# sources/user-network-fs/samba/source3/libads/ldap_user.c

## Purpose

`ldap_user.c` contains simple ADS LDAP helpers for finding and creating AD user and group accounts.

## Important APIs, Types, and Functions

`ads_find_user_acct` searches by escaped `sAMAccountName`. `ads_add_user_acct` creates a disabled normal user with `top/person/organizationalPerson/user` object classes, UPN, display name, and `sAMAccountName`. `ads_add_group_acct` creates a `top/group` object with optional description.

## Control Flow

The find path escapes the LDAP filter value, builds `(sAMAccountName=value)`, and delegates to `ads_search`. User creation picks `fullname` or `user` as CN/display name, escapes the RDN, builds `cn=<name>,<container>,<bind_path>`, sets `UF_NORMAL_ACCOUNT|UF_ACCOUNTDISABLE`, builds a mod list, and calls `ads_gen_add`. Group creation follows the same DN and mod-list pattern with group object classes and optional description.

## State and Persistence Behavior

The file owns no local state. Successful add operations persist new AD objects. Temporary DNs, escaped names, UPN strings, and mod lists are talloc/heap owned and freed before return.

## Dependencies and Integration Points

It depends on ADS search/add/mod helpers, AD account-control flags, LDAP and RDN escaping utilities, and `ads->config.realm`/`bind_path`. It integrates with administrative account creation paths in Samba tools.

## Risks and Test Signals

Risks include insufficient escaping if `container` is caller-provided malformed DN text, creating disabled users without password setup, duplicate `sAMAccountName`, and unclear behavior when ADS config lacks realm or bind path. Tests should cover special-character usernames/full names, duplicate and missing container failures, optional group comments, disabled-account flags, and LDAP filter escaping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/ldap_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/ldap_utils.c -->
# sources/user-network-fs/samba/source3/libads/ldap_utils.c

## Purpose

`ldap_utils.c` provides resilient ADS LDAP search wrappers: reconnect-on-error, page-size backoff on timeouts, SID/DN convenience searches, security-descriptor and extended-DN controls, and ranged multi-value retrieval.

## Important APIs, Types, and Functions

`ads_set_reconnect_fn` installs a callback for obtaining credentials during reconnect. Search APIs are `ads_do_search_retry`, `ads_search_retry`, `ads_search_retry_dn`, `ads_search_retry_dn_sd_flags`, `ads_search_retry_extended_dn_ranged`, `ads_search_retry_sid`, and `ads_ranged_search`. Internal helpers are `adjust_ldap_page_size`, `ads_do_search_retry_internal`, `ads_do_search_retry_args`, and `ads_ranged_search_internal`.

## Control Flow

`ads_do_search_retry_internal` first avoids immediate reconnect churn if the LDAP handle is absent and the last attempt is recent. It performs anonymous unpaged search for anonymous binds and paged search for authenticated binds. On failure, it optionally halves LDAP page size for meaningful IO timeouts, frees partial results, disconnects, asks the registered reconnect callback for credentials, reconnects with `ads_connect_creds`, and retries up to three attempts.

Ranged search builds an attribute list containing the ranged attribute and `usnChanged`, then loops while AD reports more values. It records the first `usnChanged`, appends returned range chunks via `ads_pull_strings_range`, and restarts up to five times if `usnChanged` changes between range reads.

## State and Persistence Behavior

State is stored in `ads->auth.reconnect_state`, `ads->ldap.ld`, `ads->ldap.last_attempt`, and `ads->config.ldap_page_size`. Ranged-search accumulated strings are talloc-owned by the caller. No durable state is written, but reconnect mutates the live ADS connection.

## Dependencies and Integration Points

It depends on `ldap.c` search/connect/result helpers, `cli_credentials`, loadparm LDAP page-size settings, SID hex encoding, security descriptor control OIDs, and extended-DN control OIDs. It is the safer search layer for callers that need long-running winbind/domain queries to survive dropped LDAP connections.

## Risks and Test Signals

Risks include retrying non-transient LDAP errors, losing the original error after reconnect failure, page-size reduction affecting later callers on the same `ADS_STRUCT`, range retrieval aborting on concurrent object modifications, and a bug-like assignment to local `strings = NULL` instead of `*strings = NULL` on ranged-search failure. Tests should simulate server-down, timeout, reconnect callback failure, strong success after reconnect, anonymous versus authenticated search paths, SD/extended-DN controls, SID special DN searches, ranged values with final `*`, malformed range names, and USN restart exhaustion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/ldap_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/net_ads_setspn.c -->
# sources/user-network-fs/samba/source3/libads/net_ads_setspn.c

## Purpose

`net_ads_setspn.c` implements `net ads setspn` operations for listing, adding, and deleting service principal names on a machine account.

## Important APIs, Types, and Functions

Public functions are `ads_setspn_list`, `ads_setspn_add`, and `ads_setspn_delete`. Internal `find_spn_in_spnlist` performs case-insensitive duplicate detection. The file uses `parse_spn`, `ads_get_service_principal_names`, `ads_add_service_principal_names`, `ads_find_machine_acct`, `ads_mod_strlist`, `ads_get_dn`, and `ads_gen_mod`.

## Control Flow

List fetches SPNs and prints each value. Add parses the requested SPN for basic syntax, reads existing SPNs, rejects case-insensitive duplicates, then appends the new SPN through `ads_add_service_principal_names`. Delete lowercases the target, loads the machine object and current SPN list, builds a new NULL-terminated list excluding case-insensitive matches, then replaces the whole `servicePrincipalName` attribute on the object DN.

## State and Persistence Behavior

The only persistent state is AD's `servicePrincipalName` attribute. Temporary arrays and lowercase strings live in a stack talloc frame. Delete persists a full attribute replacement, not a single-value LDAP delete.

## Dependencies and Integration Points

It depends on ADS LDAP object helpers and `parse_spn` from `util.c`. It integrates with the `net ads setspn` command surface and with machine account/SPN management used by Kerberos service discovery.

## Risks and Test Signals

Risks include full-list replacement racing with other SPN updates, no success/failure distinction when deleting a non-existent SPN, syntax validation limited to parsing rather than checking service class semantics, and case-folding allocation failures. Tests should cover list formatting, duplicate add rejection with case variants, invalid SPN parse failures, add success, delete exact and case-variant matches, delete no-op behavior, and concurrent modification handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/net_ads_setspn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/netlogon_ping.c -->
# sources/user-network-fs/samba/source3/libads/netlogon_ping.c

## Purpose

`netlogon_ping.c` sends NetLogon discovery pings over CLDAP, LDAP, LDAPS, or LDAP StartTLS and returns parsed `netlogon_samlogon_response` objects. It is the async engine used by ADS DC discovery to find usable domain controllers.

## Important APIs, Types, and Functions

`check_cldap_reply_required_flags` validates DC capability flags. Public APIs are `netlogon_pings_send`, `netlogon_pings_recv`, and synchronous `netlogon_pings`. Internal request families include `ldap_netlogon_send/recv` for LDAP-family transports, `cldap_netlogon_ping_send/recv` for CLDAP, `netlogon_ping_send/recv` for one server, and `netlogon_pings_next/done` for staggered multi-server orchestration. State structs include `ldap_netlogon_state`, `cldap_netlogon_ping_state`, `netlogon_ping_state`, and `netlogon_pings_state`.

## Control Flow

The multi-ping sender builds an LDAP filter from `netlogon_ping_filter` fields (`NtVer`, domain, account control, domain SID/GUID, host, user), starts requests to the first `wanted_servers`, then schedules additional sends every 100 ms until all candidates are in flight. CLDAP uses `cldap_search_send` against UDP/389 for the `NetLogon` attribute. LDAP-family pings TCP-connect to 389 or 636, optionally perform StartTLS or direct TLS setup without peer verification in this discovery path, run a base search for `netlogon`, then parse the returned blob.

Each completed response is parsed and filtered: paused responses are rejected, `required_flags` must be present, and successful responses are stored at the server's original index. The aggregate request completes once enough good responses arrive, once all responses arrive with one good response, or fails with `NT_STATUS_NOT_FOUND` if no acceptable server responds.

## State and Persistence Behavior

State is per-tevent request and talloc-owned. No durable cache is written here; callers decide whether to store site or negative-connection information. Network state includes transient TCP, TLS, tldap, and CLDAP sockets.

## Dependencies and Integration Points

It depends on tevent, tsocket, tstream, tldap, CLDAP, TLS helpers, LDAP NDR encoders, NetLogon response parsers, loadparm client netlogon ping protocol selection, and Samba NTSTATUS utilities. `ldap.c` calls `netlogon_pings` from DC discovery.

## Risks and Test Signals

Risks include the `timeout` argument being stored but not visibly applied to individual ping sends, StartTLS/LDAPS discovery using `TLS_VERIFY_PEER_NO_CHECK`, filter values not being escaped as regular LDAP strings because they are mostly NDR-encoded or caller-provided names, off-by-one assumptions around `wanted_servers <= num_servers`, and accepting one good answer even when more were requested after all replies. Tests should cover every protocol enum, invalid proto, filter construction, required flag combinations, paused responses, malformed netlogon blobs, no-result searches, staggered send ordering, wanted-server thresholds, and timeout/cancellation behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/netlogon_ping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/netlogon_ping.h -->
# sources/user-network-fs/samba/source3/libads/netlogon_ping.h

## Purpose

`netlogon_ping.h` declares the ADS NetLogon ping API and filter structure used to discover domain controllers over CLDAP/LDAP-family transports.

## Important APIs, Types, and Functions

`struct netlogon_ping_filter` contains `ntversion`, domain, domain SID, domain GUID, hostname, user, account-control filter, and required DC flags. The header declares `check_cldap_reply_required_flags`, async `netlogon_pings_send`, `netlogon_pings_recv`, and synchronous `netlogon_pings`.

## Control Flow

Callers provide a protocol, server address array, filter, wanted response count, and timeout. Async callers drive the returned `tevent_req`; synchronous callers use `netlogon_pings`, which creates an event context and polls the request to completion.

## State and Persistence Behavior

The header defines request contracts only. Returned `netlogon_samlogon_response` arrays are talloc-moved to the caller and contain per-server response slots.

## Dependencies and Integration Points

It depends on tsocket address types, generated NBT/NetLogon declarations, NTSTATUS, and loadparm's `client_netlogon_ping_protocol` enum. It integrates directly with ADS DC discovery in `ldap.c`.

## Risks and Test Signals

Risks include callers passing mismatched signed `int` counts to size_t implementations, unclear ownership of the server array versus returned response array, and timeout semantics needing validation against implementation. Tests should compile async and sync callers, verify filter defaults such as `acct_ctrl = -1`, and assert response ownership on success/failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/netlogon_ping.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/sasl.c -->
# sources/user-network-fs/samba/source3/libads/sasl.c

## Purpose

`sasl.c` performs ADS LDAP SASL/SPNEGO binds using Samba GENSEC credentials, chooses LDAP signing/sealing behavior, applies TLS channel bindings, and provides a helper for building simple `cli_credentials`.

## Important APIs, Types, and Functions

`ads_simple_creds` constructs credentials from domain, account name, and password. `ads_sasl_bind` is the public bind entry point. Internal functions include `ads_sasl_spnego_bind`, `ads_sasl_spnego_gensec_bind`, `ads_guess_target`, `ads_generate_service_principal`, and GENSEC wrap hooks `ads_sasl_gensec_wrap`, `ads_sasl_gensec_unwrap`, and `ads_sasl_gensec_disconnect`. `struct ads_service_principal` tracks generated LDAP service, host, and principal strings.

## Control Flow

`ads_sasl_bind` maps auth flags to wrap type: LDAPS/StartTLS use plain SASL over TLS, seal requests signing and sealing, sign requests signing, and the default is plain. TLS modes require channel bindings from `ads_tls_channel_bindings`. The SPNEGO path guesses `ldap/<server>@<realm>`, configures target service/hostname, sets GENSEC channel bindings when available, requests GENSEC features for sign/seal modes, starts the client by SASL name `GSS-SPNEGO`, then loops `gensec_update` tokens through `ldap_sasl_bind_s` until both LDAP and GENSEC complete.

After bind, it verifies requested sign/seal features, records credential expiry, computes wrapping sizes, and installs the SASL sockbuf wrapper when wrap type is sign or seal. If a plain non-TLS bind receives `LDAP_STRONG_AUTH_REQUIRED`, it retries with signing enabled.

## State and Persistence Behavior

State mutates `ads->ldap_wrap_data` wrap type, ops, private GENSEC pointer, buffer sizing, and `ads->auth.expire_time`. GENSEC state is retained past bind only when socket wrapping is installed. `ads_simple_creds` returns caller-owned `cli_credentials`.

## Dependencies and Integration Points

Dependencies include `cli_credentials`, loadparm context initialization, GENSEC/auth_generic, OpenLDAP SASL bind APIs, Kerberos support for target principal generation, TLS channel binding data from `tls_wrapping.c`, and SASL wrapping from `sasl_wrapping.c`. It integrates with `ads_connect_internal`.

## Risks and Test Signals

Risks include target-name guesses for short/non-FQDN server names, channel-binding absence under TLS, feature negotiation mismatches, token-loop termination errors, fallback from plain to sign changing security expectations, and retained GENSEC lifetime management. Tests should cover simple creds, Kerberos and NTLMSSP SPNEGO, LDAPS/StartTLS with channel bindings, sign/seal feature verification, strong-auth retry, generated service principal cases, expiry propagation, and installed wrapper encrypt/decrypt round trips.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/sasl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/sasl_wrapping.c -->
# sources/user-network-fs/samba/source3/libads/sasl_wrapping.c

## Purpose

`sasl_wrapping.c` installs an OpenLDAP sockbuf transport layer that frames, signs, seals, unwraps, and streams LDAP bytes after SASL negotiation.

## Important APIs, Types, and Functions

`ndr_print_ads_saslwrap_struct` prints wrapper state for diagnostics. `ads_setup_sasl_wrapping` installs the `Sockbuf_IO` layer and records mechanism-specific `ads_saslwrap_ops`. Internal helpers manage setup/remove, input buffer prepare/grow/shrink, output buffer prepare/shrink, `ads_saslwrap_read`, `ads_saslwrap_write`, `ads_saslwrap_ctrl`, and close.

## Control Flow

Reads first collect a four-byte big-endian wrapped length, validate it against min/max wrapped bounds, grow the buffer, read the complete wrapped payload, call the configured `unwrap` hook once, then satisfy caller reads from the unwrapped bytes. Writes split input to `out.max_unwrapped`, allocate room for length plus signature/payload, call the configured `wrap` hook, write the length header, then drain the wrapped buffer to the next sockbuf layer.

## State and Persistence Behavior

All state is inside `struct ads_saslwrap`: current sockbuf descriptor, talloc memory context, wrap type, ops/private data, input offset/needed/left/bounds/buffer, and output offset/left/bounds/buffer. It is live for the LDAP connection lifetime and freed through `ads_disconnect`.

## Dependencies and Integration Points

It depends on OpenLDAP `Sockbuf_IO`, Samba ADS wrapper structures, `ads_saslwrap_ops` provided by `sasl.c`, and NDR printing utilities. It integrates directly into OpenLDAP's socket stack after a successful sign/seal SASL bind.

## Risks and Test Signals

Risks include partial-read/write `EAGAIN` semantics, corrupted length headers, min-wrapped truncation assumptions, buffer lifetime leaks on wrap/unwrap failure, and incorrect `DATA_READY` behavior when unwrapped bytes remain. Tests should drive partial header/payload reads, oversized and undersized wrapped frames, fragmented writes, sign-only and seal wrapping, unwrap failures mapping to `EACCES`, and disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/sasl_wrapping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/sitename_cache.c -->
# sources/user-network-fs/samba/source3/libads/sitename_cache.c

## Purpose

`sitename_cache.c` stores and retrieves the AD client site name associated with a realm/domain so future DC discovery can start with site-aware DNS SRV lookups.

## Important APIs, Types, and Functions

`sitename_store` writes or deletes a site name. `sitename_fetch` reads a cached site name, defaulting an empty realm to `lp_realm()`. `stored_sitename_changed` compares a candidate site name with the cached value. Internal `sitename_key` builds uppercase gencache keys using `AD_SITENAME/DOMAIN/%s`.

## Control Flow

Store rejects empty realms, deletes the cache key for empty site names, and otherwise writes the value with `get_time_t_max()` expiration. Fetch normalizes the query realm, reads gencache into the caller's talloc context, and logs hit or miss. Change detection fetches the current value and compares NULL/non-NULL and string mismatch cases.

## State and Persistence Behavior

State persists in Samba's generic cache (`gencache`) with effectively indefinite expiration. CLDAP discovery in `ldap.c` rewrites the cached site whenever a new reply reports client site data.

## Dependencies and Integration Points

It depends on `lib/gencache.h`, loadparm realm settings, talloc, and Samba string helpers. It integrates with ADS DC discovery and site-fallback logic in `ads_find_dc`.

## Risks and Test Signals

Risks include indefinite stale site names after AD subnet changes, realm/workgroup aliases producing separate cache keys, deletion on empty CLDAP site replies, and uppercase normalization expectations. Tests should cover store/fetch/delete, empty realm fallback, case-insensitive realm key behavior, changed detection for NULL and string cases, and discovery fallback when a cached site has no live DC.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/sitename_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/sitename_cache.h -->
# sources/user-network-fs/samba/source3/libads/sitename_cache.h

## Purpose

`sitename_cache.h` declares the small ADS client site-name cache API used by DC discovery.

## Important APIs, Types, and Functions

The header exports `sitename_store`, `sitename_fetch`, and `stored_sitename_changed`.

## Control Flow

Callers store site names after CLDAP replies, fetch them before site-specific DNS lookup, and compare candidate values when deciding whether cached site state changed.

## State and Persistence Behavior

The header itself has no state; the implementation stores values in Samba gencache. `sitename_fetch` returns a caller-owned talloc string.

## Dependencies and Integration Points

It relies on declarations from the common Samba include environment for `bool` and `TALLOC_CTX`. It is included by `ldap.c` and implemented by `sitename_cache.c`.

## Risks and Test Signals

Risks are ownership misunderstandings for fetched strings and broad inclusion without explicit includes. Compile tests should include the header from normal ADS callers, and runtime tests should validate store/fetch/change behavior through the implementation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/sitename_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/tls_wrapping.c -->
# sources/user-network-fs/samba/source3/libads/tls_wrapping.c

## Purpose

`tls_wrapping.c` installs a synchronous TLS layer into OpenLDAP's sockbuf stack for ADS LDAPS and StartTLS connections, and exposes channel bindings for SASL.

## Important APIs, Types, and Functions

`ndr_print_ads_tlswrap_struct` prints TLS wrapper state. `ads_setup_tls_wrapping` is the main setup API. `ads_tls_channel_bindings` returns TLS channel binding data. Internal OpenLDAP sockbuf callbacks include setup/remove, read/write, ctrl, close, and GnuTLS transport send/recv shims.

## Control Flow

Setup obtains the LDAP sockbuf, initializes a Samba loadparm context, builds client TLS parameters for the server name, adds the TLS sockbuf layer, sets an endtime from LDAP connection timeout, performs synchronous TLS setup using callbacks that read/write the underlying sockbuf, clears the endtime, and removes the IO layer if the handshake fails. After setup, LDAP reads/writes pass through `tstream_tls_sync_read/write`, while `DATA_READY` checks pending decrypted TLS bytes before delegating.

## State and Persistence Behavior

State is held in `struct ads_tlswrap`: memory context, sockbuf descriptor, TLS params, sync TLS context, and temporary handshake deadline. It lasts for the LDAP connection and is freed on sockbuf close or `ads_disconnect`. Channel binding data is derived from the live TLS context.

## Dependencies and Integration Points

It depends on OpenLDAP sockbuf APIs, Samba source4 TLS helpers, GnuTLS transport callbacks, loadparm TLS configuration, and ADS connection code. `sasl.c` uses `ads_tls_channel_bindings` to bind SASL authentication to the TLS channel.

## Risks and Test Signals

Risks include handshake timeout mapping to `ECONNRESET`, TLS parameter/config errors, IO layer cleanup on partial failure, channel bindings unavailable before setup, and sync TLS calls inside OpenLDAP's blocking expectations. Tests should cover LDAPS and StartTLS handshakes, certificate policy failures, timeout behavior, pending-data `DATA_READY`, channel binding availability, and cleanup after handshake failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/tls_wrapping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/trusts_util.c -->
# sources/user-network-fs/samba/source3/libads/trusts_util.c

## Purpose

`trusts_util.c` manages trust account password changes over NETLOGON, including password generation, local secrets staging/recovery, remote verification with current/old passwords, Kerberos-authenticated secure-channel cases, and final local/remote commit handling.

## Important APIs, Types, and Functions

`trust_pw_new_value` generates a random machine/trust password sized by secure channel type and security mode. `trust_pw_change` performs the full password rotation. Internal helpers include `trust_pw_change_state_destructor` for g_lock cleanup, `netlogon_creds_cli_lck_auth` to authenticate under an exclusive NETLOGON creds lock, and `extract_nt_hash_and_pwd` to convert stored UTF-16MUNGED secrets into UTF-8 cleartext plus NT hash pointers.

## Control Flow

`trust_pw_change` takes an exclusive g_lock per domain, loads trust credentials, determines secure-channel type, password age, old kvno, and whether a change is needed. For workstation/BDC channels it calls `secrets_prepare_password_change`, handles any previous unfinished change, and builds a list of candidate current/old/older passwords. For domain trust channels it uses passdb trusted-domain state and increments the trust version.

Before changing anything remotely, it authenticates to the DC using all candidate hashes, or performs Kerberos kinit against an explicit KDC if the NETLOGON credential state is Kerberos-authenticated. If a previous staged password is already accepted remotely, it finishes recovery. If only an older password works, it defers the change. Otherwise it writes the new password locally, calls `netlogon_creds_cli_ServerPasswordSet`, records failed/deferred state depending on connection status, finishes local secrets on success, updates in-memory credentials, and verifies the new password remotely.

## State and Persistence Behavior

Persistent state includes secrets database password-change records, trusted-domain passdb passwords, keytab sync side effects via `sync_pw2keytabs`, NETLOGON credential state, and optional Kerberos memory ccache used only during verification. The g_lock protects concurrent local rotations for the same domain.

## Dependencies and Integration Points

It depends on NETLOGON creds client APIs, RPC binding handles, passdb/secrets, generated secrets and netlogon NDR types, Kerberos wrappers, messaging/g_lock, loadparm machine password timeout/security role, and keytab sync when ADS is enabled. It is part of machine/trust account maintenance.

## Risks and Test Signals

Risks include incorrect recovery after interrupted local/remote commits, password length constraints for RODC/RWDC forwarding, lock acquisition failures, Kerberos path requiring an IP-address host binding, local password committed before remote rejection, deferred state persistence errors, and secret data lifetime/logging. Tests should cover timeout/force decisions, every supported secure-channel type, previous-change recovery, older-password defer, NETLOGON auth failure, Kerberos verification, disconnected versus connected remote set failure, secrets finish/fail/defer calls, keytab sync, and final new-password verification.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/trusts_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/util.c -->
# sources/user-network-fs/samba/source3/libads/util.c

## Purpose

`util.c` contains two ADS utility areas: Kerberos-based machine trust password change for domain members, and parsing of Windows-style SPN strings.

## Important APIs, Types, and Functions

Under `HAVE_KRB5`, `ads_change_trust_account_password` rotates the machine account password via Kerberos set-password. `parse_spn` parses `service/host[:port][/servicename]` into `struct spn_struct` fields: service class, host, optional port, and optional service name.

## Control Flow

The password-change path verifies the server role is `ROLE_DOMAIN_MEMBER`, generates a workstation trust password, stages the change in secrets with keytab sync support, rejects recovery if a previous change already exists, converts current and next stored UTF-16MUNGED passwords to Unix strings, calls `kerberos_set_password`, records failure with `secrets_failed_password_change` on conversion or remote errors, and finalizes with `secrets_finish_password_change` on success.

`parse_spn` allocates a result, duplicates the input as mutable serviceclass storage, splits at the first slash, then optional colon and second slash. It rejects missing or empty host, empty service name, empty port, out-of-range ports, and conversion range errors. Pointers for host and service name point inside the duplicated serviceclass buffer.

## State and Persistence Behavior

Password change persists staged and completed machine password state in Samba secrets and can update keytabs. SPN parsing has no persistent state; parsed fields are talloc-owned by the caller.

## Dependencies and Integration Points

The password path depends on Kerberos set-password, secrets password-change helpers, ADS/KDC connection state, loadparm role/workgroup, trust password generation from `trusts_util.c`, and optional keytab sync. `parse_spn` is used by `net_ads_setspn.c` and any command path validating SPN syntax.

## Risks and Test Signals

Risks include partial secrets state after Kerberos failures, role restrictions, previous-change recovery being rejected rather than repaired here, secret cleartext conversion failures, `parse_spn` storing subfield pointers inside a single mutable buffer, and `errno` handling around `strtol`. Tests should cover domain-member role enforcement, successful and failed Kerberos set-password, secrets prepare/finish/fail paths, SPNs with port and service name, malformed missing-host/no-slash/empty-port/empty-service cases, port bounds, and lifetime of parsed subfields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/util.c -->
