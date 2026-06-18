# subset-b-009897 Research

Grouped research for Samba winbindd files under `sources/user-network-fs/samba/source3/winbindd`. Each section preserves the source path for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_list_users.c -->
## sources/user-network-fs/samba/source3/winbindd/winbindd_list_users.c

`winbindd_list_users.c` implements the asynchronous external `WINBINDD_LIST_USERS` command. Its purpose is to collect user lists from one named domain or from every domain in `domain_list()` and return the result as comma-separated extra data for the winbind client. The important state types are `winbindd_list_users_state`, which tracks the number of queried domains, callbacks received, and a domain-state array, and `winbindd_list_users_domstate`, which keeps a `winbindd_domain_ref`, the outstanding child request, and the returned NUL-separated user string.

The control flow begins in `winbindd_list_users_send()`: it logs client metadata, honors the NSS enumeration guard (`WBFLAG_FROM_NSS` plus `lp_winbind_enum_users()`), ensures `request->domain_name` is terminated, resolves either a single domain with `find_domain_from_name_noinit()` or snapshots all current domains, and starts `wb_query_user_list_send()` for each domain. Requests are reparented so tevent call-depth tracking and talloc cleanup both work. `winbindd_list_users_done()` matches the callback to the domain slot, receives the string with `wb_query_user_list_recv()`, suppresses per-domain errors by leaving that domain's users `NULL`, and completes after all domains have answered. `winbindd_list_users_recv()` concatenates successful domain vectors with `strv_append()`, steals the buffer into `response->extra_data.data`, updates `response->length`, converts embedded NUL separators to commas, and counts entries.

There is no persistent state here beyond use of global domain lists and cache-backed lower layers. Dependencies include tevent, talloc, `winbindd_domain_ref_*`, `wb_query_user_list_*`, loadparm enumeration settings, and `lib/util/strv.h`. Integration points are the winbind client command dispatch, NSS enumeration policy, domain child query APIs, and response `extra_data` formatting.

Primary risks are large enumeration responses, silent partial success when a domain query fails, correctness of NUL/comma conversion, and races between domain list changes and outstanding requests mitigated by domain refs. Test signals include NSS calls with enumeration disabled, explicit domain and all-domain listing, missing-domain failures, one child failing while another succeeds, empty domains, and response length/entry count validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_list_users.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_locator.c -->
## sources/user-network-fs/samba/source3/winbindd/winbindd_locator.c

`winbindd_locator.c` owns the singleton locator child used by winbindd for DC locator work. The file is intentionally small: it keeps a file-static `struct winbindd_child *static_locator_child`, exposes it through `locator_child()`, tests identity with `is_locator_child()`, returns its wbint binding handle through `locator_child_handle()`, and allocates it in `init_locator_child()`.

The control flow is a one-time initialization path. `init_locator_child()` refuses double allocation with `NT_STATUS_INTERNAL_ERROR`, allocates a zeroed child under the supplied talloc context, and delegates setup to `setup_child(NULL, static_locator_child, "log.winbindd", "locator")`. Passing `NULL` as the domain marks this as a special-purpose child rather than a domain child. After setup, callers use `locator_child_handle()` to send internal RPC requests to the locator process.

State is process-local and persistent for the lifetime of the parent process or the memory context that owns the child. There is no on-disk state. Dependencies are `winbindd.h`, talloc, the generic child setup code, and the child binding handle initialized elsewhere. Integration points include winbindd startup, child classification, logging with the `locator` suffix, and any command that routes locator work through the locator child.

The main risks are lifecycle assumptions: `locator_child_handle()` dereferences without a NULL check, so callers must only use it after successful initialization; double initialization is treated as an internal error; and cleanup depends on the owner context. Test signals are startup initialization, duplicate init failure, `is_locator_child()` discrimination from domain/idmap children, and successful wbint binding use through the locator child.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_locator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_lookupname.c -->
## sources/user-network-fs/samba/source3/winbindd/winbindd_lookupname.c

`winbindd_lookupname.c` implements the asynchronous external `WINBINDD_LOOKUPNAME` command, converting a domain/name or qualified username into a SID and LSA SID type. Its state object stores the event context, returned `dom_sid`, and `lsa_SidType`.

`winbindd_lookupname_send()` validates string termination for `request->data.name.dom_name` and `.name`, parses the request into `namespace`, `domname`, and `name`, and supports three input styles: an explicit domain field, a fully qualified name split by `lp_winbind_separator()`, and a UPN-like value containing `@`. If no domain or UPN realm is present, namespace is empty and lookup falls through normal routing. It then starts `wb_lookupname_send(state, ev, namespace, domname, name, 0)`. `winbindd_lookupname_done()` receives the SID/type with `wb_lookupname_recv()` and propagates errors through tevent. `winbindd_lookupname_recv()` fills `response->data.sid.sid` using `sid_to_fstring()` and `response->data.sid.type`.

No durable state is stored. The command depends on parse-time mutation of the request buffer when splitting `DOMAIN\user`; this is safe inside request handling but worth noting for callers expecting the original string. Dependencies include tevent, `dom_sid`, loadparm separator configuration, `wb_lookupname_*`, and winbind domain routing/caches in lower layers. Integration points are NSS/PAM/client SID lookup calls and the shared async command dispatch pattern.

Risks are ambiguous names when a separator or `@` appears in unexpected positions, separator changes, and failure logging that says "Could not convert SID" although the operation is name-to-SID. Test signals include explicit domain lookups, separator-qualified names, UPN names, default-domain names, unknown names, and response type preservation for users/groups/aliases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_lookupname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_lookuprids.c -->
## sources/user-network-fs/samba/source3/winbindd/winbindd_lookuprids.c

`winbindd_lookuprids.c` implements `WINBINDD_LOOKUPRIDS`, which maps a domain SID plus a newline-separated RID list to principal names and SID types. It is a parent-side async wrapper around the domain child `wbint_LookupRids` call. The state stores the parsed domain SID, returned domain name, `wbint_RidArray`, and returned `wbint_Principals`.

`winbindd_lookuprids_send()` terminates and parses `request->data.sid` with `string_to_sid()`, resolves the target with `find_lookup_domain_from_sid()`, validates that `request->extra_data.data` is NUL-terminated, parses RIDs via `parse_ridlist()`, and sends `dcerpc_wbint_LookupRids_send()` to `dom_child_handle(domain)`. The callback receives both transport and operation status using `dcerpc_wbint_LookupRids_recv()` and `any_nt_status_not_ok()`. The recv path formats each returned principal as `"<type> <name>\n"` in `response->extra_data.data`, sets `response->data.domain_name`, and updates response length.

`parse_ridlist()` counts newline delimiters, allocates a `uint32_t` array, and uses `smb_strtoul(..., SMB_STR_STANDARD)` to reject malformed or non-newline-terminated tokens. An empty list is valid and returns zero RIDs. There is no persistent state; results depend on domain child SAM/LSA lookups and associated caches.

Dependencies include generated `ndr_winbind_c`, SID helpers, `smb_strtox`, domain routing, tevent, and talloc. Risks include rejecting a final RID without a trailing newline, response growth for large RID lists, partial mapping semantics delegated to the child, and domain SID routing failures. Test signals include valid multi-RID input, empty input, malformed RID text, non-terminated `extra_data`, unknown domain SID, unmapped RIDs, and response domain/name/type formatting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_lookuprids.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_lookupsid.c -->
## sources/user-network-fs/samba/source3/winbindd/winbindd_lookupsid.c

`winbindd_lookupsid.c` implements the asynchronous external `WINBINDD_LOOKUPSID` command, converting one textual SID into a domain name, account name, and LSA SID type. The state carries the parsed SID and the returned domain/name/type pointers.

`winbindd_lookupsid_send()` ensures the SID request field is terminated, parses it with `string_to_sid()`, and starts `wb_lookupsid_send()`. Invalid SID syntax is returned immediately as `NT_STATUS_INVALID_PARAMETER`. `winbindd_lookupsid_done()` receives results with `wb_lookupsid_recv()`, tallocs returned strings under the state, and propagates any NTSTATUS error. `winbindd_lookupsid_recv()` writes `response->data.name.dom_name`, `response->data.name.name`, and `response->data.name.type`.

The file has no durable state and relies on lower-level lookup code for cache use, domain routing, and fallback behavior. Dependencies include tevent, SID parsing/formatting, `wb_lookupsid_*`, and fixed-size response string helpers (`fstrcpy`). Integration points are winbind NSS SID-to-name calls, `wbinfo --sid-to-name` style clients, and the shared async command dispatch.

Risks are mostly input and truncation related: malformed SID strings must be rejected, response names can be truncated to fixed fields by `fstrcpy`, and the command returns a single status rather than carrying partial data. Test signals include malformed SID text, well-known/internal/domain SIDs, unmapped SIDs, alias/group/user SID types, and long returned names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_lookupsid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_lookupsids.c -->
## sources/user-network-fs/samba/source3/winbindd/winbindd_lookupsids.c

`winbindd_lookupsids.c` implements `WINBINDD_LOOKUPSIDS`, a batch SID-to-name command. Its state stores a parsed SID array and the returned `lsa_RefDomainList` plus `lsa_TransNameArray`. It exists to amortize lookup overhead and return enough domain-reference metadata for clients to interpret translated names.

`winbindd_lookupsids_send()` requires non-empty `extra_data`, validates NUL termination, parses the SID list with shared `parse_sidlist()`, and calls `wb_lookupsids_send(state, ev, state->sids, state->num_sids)`. The callback receives domain and name arrays via `wb_lookupsids_recv()`. `winbindd_lookupsids_recv()` serializes the result into `extra_data`: first the domain count, then lines of `<sid> <domain-name>`, then the translated-name count, then lines of `<sid_index> <sid_type> <name>`.

There is no local persistence. Lower layers decide cache usage, domain fan-out, and partial translation behavior. Dependencies include tevent, talloc formatting, `parse_sidlist`, LSA generated structures, and SID string helpers. Integration points are high-volume consumers that need many SID translations, including group/token expansion and winbind client tools.

Risks include strict NUL-terminated input requirements, large response allocation, line-oriented output ambiguity if names contain unexpected whitespace, and robustness when lower layers return inconsistent count arrays. Test signals include zero-length rejection, malformed SID list rejection, multiple domains in one response, unknown SID translations, ordering preservation, and response parsing by existing winbind clients.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_lookupsids.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_misc.c -->
## sources/user-network-fs/samba/source3/winbindd/winbindd_misc.c

`winbindd_misc.c` implements miscellaneous synchronous winbind commands and daemon helpers. Public command handlers include `winbindd_list_trusted_domains()`, `winbindd_dc_info()`, `winbindd_ping()`, `winbindd_info()`, `winbindd_interface_version()`, `winbindd_domain_name()`, `winbindd_netbios_name()`, and `winbindd_priv_pipe_dir()`. Helper code formats trust metadata, reloads configuration, sizes file descriptor limits, and hooks tevent call-flow debugging.

Trusted-domain listing fetches the trusted-domain cache with `wcache_tdc_fetch_list()`, resolves each runtime `winbindd_domain`, derives a human-readable trust type from secure-channel type and trust attributes, computes inbound/outbound/transitive flags, and emits backslash-separated lines with domain name, DNS name, SID, trust type, transitivity, direction flags, and online state. DC info reads the current DC from gencache. The info/version/name handlers expose loadparm and compile-time state. `get_winbind_priv_pipe_dir()` returns the privileged socket directory under `state_path()`.

State and persistence are mostly indirect: trusted-domain and current-DC data come from winbind caches/gencache; reload changes global loadparm state, logs, interfaces, and process fd limits; call-flow debug stores a pointer to caller-owned depth storage in a file-static variable. Dependencies include loadparm, gencache, trusted-domain cache, SID formatting, interface loading, log reopening, `set_maxfiles()`, and tevent call-depth instrumentation.

Risks include line-format compatibility for `LIST_TRUSTED_DOMAINS`, stale cache data, missing routing domains when classifying routed trusts, NULL `extra_data` in `winbindd_priv_pipe_dir()` if allocation failed, and global effects of config reload in child vs parent contexts. Test signals include trusted-domain output across local/external/forest/routed trusts, offline-domain display, DC cache misses, config reload changing logfile/interface state, fd limit sizing under high client/domain counts, and tevent flow debug output at high debug levels.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_msrpc.c -->
## sources/user-network-fs/samba/source3/winbindd/winbindd_msrpc.c

`winbindd_msrpc.c` is the MSRPC backend implementation for `struct winbindd_methods`. It backs domain operations with SAMR, LSA, and NETLOGON-adjacent RPC clients: user/group enumeration, name/SID translation, RID translation, group and alias membership lookup, trusted-domain enumeration, and password/lockout policy retrieval. The exported method table is `msrpc_methods`.

Most methods follow a common pattern: check whether the domain can be contacted (`winbindd_can_contact_domain()`), open the needed pipe with `cm_connect_sam()`, `cm_connect_lsa()`, or `cm_connect_lsat()`, call a lower RPC helper, move returned talloc data to the caller, and free a stackframe. `msrpc_name_to_sid()` applies name normalization unmapping before `winbindd_lookup_names()`, while `msrpc_sid_to_name()` and `msrpc_rids_to_names()` apply name mapping on returned names. User-group lookup first checks cached SamLogon data with `lookup_usergroups_cached()` before using SAMR. Group membership opens the group, queries member RIDs with an extended timeout, then resolves RIDs in chunks below `MAX_LOOKUP_RIDS` to avoid old server issues.

The LSA translation helpers select lookup levels with `winbindd_lookup_level()` based on internal domains, DNS-domain secure channels, forest attributes, external trusts, and RODC state. `winbindd_lookup_sids()` and the internal `winbindd_lookup_names()` use LSAT over the connection manager, prefer LookupSids3/LookupNames4 on TCP transports, temporarily raise binding timeouts, reset broken connections on schannel/transport errors, and retry once before mapping to access denied. `winbindd_lookup_names()` normalizes `NONE_MAPPED` and `SOME_NOT_MAPPED` into successful arrays with `SID_NAME_UNKNOWN` where appropriate.

State is connection-manager and cache state rather than file-local persistence: policy handles, SAMR/LSA pipes, gencache and SamLogon cache all influence results. Dependencies include generated SAMR/LSA NDR clients, `cli_samr`, `cli_lsarpc`, security SID helpers, connection manager APIs, and talloc. Risks include trust/contact gating returning empty success vs synchronization-required status, stale cached group data, long-running RPCs, array-count mismatches from servers, retry side effects, and nuanced LSA lookup levels for forest/external trust resolution. Test signals include NT4/AD behavior, TCP vs named-pipe LSAT, some-unmapped lookups, broken schannel retry, no-inbound-trust domains, large group membership, policy retrieval, and trusted-domain enumeration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_msrpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_ndr.c -->
## sources/user-network-fs/samba/source3/winbindd/winbindd_ndr.c

`winbindd_ndr.c` provides debug/NDR printers for core winbindd runtime structures. It does not implement protocol behavior; it makes `winbindd_child`, `winbindd_cm_conn`, `winbindd_methods`, and `winbindd_domain` inspectable through Samba's NDR print framework.

`ndr_print_winbindd_child()` prints process id, domain pointer, logfile, and lockout policy event pointer. `ndr_print_winbindd_cm_conn()` prints RPC client pointers and policy handles for SAMR, LSA, and Netlogon connections. `ndr_print_winbindd_methods()` compares a method-table pointer against known global method tables (`msrpc_methods`, optionally ADS methods, passdb methods, reconnect wrappers) and prints a symbolic backend name or `UNKNOWN`. `ndr_print_winbindd_domain()` prints domain identity, trust flags/type/attributes, booleans such as `initialized`, `active_directory`, `primary`, `internal`, and `online`, timing and sequence state, backend identity, connection state, child array entries, and online-check event pointers.

The file has no persistent state and no ownership changes. It depends on generated NDR printers for Netlogon, security, and LSA structures, the `libndr` print API, and external method-table symbols. Integration points are debug dumps, messaging handlers that print domain lists, diagnostics, and developer troubleshooting.

Risks are diagnostic rather than behavioral: stale method-table comparisons can report `UNKNOWN` for new backends; pointer printing avoids recursive domain printing for child domains; and sensitive topology/connection information may appear at high debug levels. Test signals include compiling with and without `HAVE_ADS`, dumping domains with multiple children, reconnect method identification, and ensuring debug dumps do not dereference NULL domains.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_ndr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_pam.c -->
## sources/user-network-fs/samba/source3/winbindd/winbindd_pam.c

`winbindd_pam.c` is the domain-child implementation for winbind PAM authentication, NTLM challenge/response authentication, password changes, logoff cleanup, cached offline logons, Kerberos ccache handling, PAC verification, and auth event logging. It is the security-sensitive core behind parent wrappers such as `winbindd_pam_auth.c`, `winbindd_pam_auth_crap.c`, and password-change wrappers.

Important helpers format returned auth data (`append_auth_data()`, `append_info3_as_txt()`, `append_info3_as_ndr()`, `append_unix_username()`, `append_afs_token()`), parse required group SID lists (`extra_data_to_sid_array()`), enforce required membership by building a token from Info3 (`check_info3_in_group()`), choose an authentication domain (`find_auth_domain()`), and retrieve password/lockout policy from cache. Kerberos support builds credential-cache names (`generate_krb5_ccache()`), performs raw Kerberos login (`winbindd_raw_kerberos_login()`), extracts PAC logon data, stores renewable ccaches in winbind's ccache list, and removes failed transient caches. Cached auth verifies stored salted or legacy NT hashes, enforces account flags/expiry/lockout, updates cached credentials, and may synthesize ccache tracking while offline.

`_wbint_PamAuth()` handles plaintext PAM auth. It validates pid/uid ranges, normalizes names, optionally brings a startup-offline domain online, tries Kerberos first when requested, falls back to SamLogon or cached logon depending on flags/status, stores SamLogon/name caches on success, enforces required groups and allowed-domain policy, optionally stores offline credentials, returns validation and krb5ccname, logs auth events, and triggers `gpupdate_user_init()`. `winbind_dual_SamLogon()` and `_wbint_PamAuthCrap()` handle NTLM responses through passdb for local SAM or Netlogon for remote domains, including authoritative handling, trust-transitive logon info classes, retry/failover for broken DCs, and cache priming. `_wbint_PamAuthChangePassword()` tries strong `samr_chgpasswd_user4`, falls back to older change-password calls when policy permits, returns password policy/reject reason, and updates cached credentials. `_wbint_PamLogOff()` removes matching Kerberos ccaches and memory creds. `_wbint_PamAuthCrapChangePassword()` supports encrypted-hash password change but refuses it when offline logons are enabled. `winbindd_pam_auth_pac_verify()` decodes and optionally verifies PAC signatures using local keytab entries, maps PAC data to validation, enforces allowed domains, and only primes caches when signatures verified.

State and persistence span many subsystems: winbind credential caches, memory creds, ccache renewal list, netsamlogon cache, name-to-SID cache, domain online/offline flags, connection negative cache, gencache-backed policies, and auth event messaging. Dependencies include Netlogon/SAMR/LSA RPC clients, Kerberos/GENSEC/PAC utilities, GnuTLS hashing, passdb auth contexts, tsocket addresses, loadparm, messaging, AFS token helpers, and global contexts.

Major risks are authentication fallback semantics, authoritative vs non-authoritative failures, offline cached credential lockout behavior, ccache path/uid handling, PAC trust distinction, password-change downgrade policy, sensitive data in debug dumps, and NULL handling in failure paths. Test signals should cover Kerberos success/failure/fallback, SamLogon retry and DC failover, local passdb auth, cached offline login with salted hashes and lockout, required group enforcement, allowed-domain firewalling, password expiry/change policy, PAC verified and unverified paths, logoff ccache removal, and auth event content.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_pam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_pam_auth.c -->
## sources/user-network-fs/samba/source3/winbindd/winbindd_pam_auth.c

`winbindd_pam_auth.c` is the parent-process asynchronous wrapper for `WINBINDD_PAM_AUTH`, the plaintext PAM authentication command. It validates client request flags, canonicalizes the username, chooses the authentication domain, marshals a `wbint_PamAuth` request, sends it to the domain child, and formats the response for the winbind client.

`winbindd_pam_auth_send()` first rejects incompatible extra-data flags via `check_request_flags()`. It normalizes mapped names with `normalize_name_unmap()`, canonicalizes into namespace/domain/user using `canonicalize_username()`, and resolves the child domain with `find_auth_domain(request->flags, namespace)`. It builds `wbint_AuthUserInfo` fields for client name, pid, flags, Kerberos ccache type, password, username, uid, and required membership SIDs parsed by `extra_data_to_sid_array()`. It then calls `dcerpc_wbint_PamAuth_r_send()` against `dom_child_handle(domain)`.

The callback receives the wrapped RPC and child result. `winbindd_pam_auth_recv()` maps child validation into the legacy winbind response with `append_auth_data()`, copies `krb5ccname`, optionally adds trusted-domain data from Info3 text, stores memory credentials for cached-login single sign-on, and fakes password policy data for legacy `WBFLAG_PAM_GET_PWD_POLICY` callers by deriving min/max ages from validation timestamps.

The file itself has no durable state, but it can trigger memory credential storage and trusted-domain discovery through helpers. Dependencies include generated winbind RPC client stubs, global event context, username normalization, domain routing, auth-data append helpers in `winbindd_pam.c`, and fixed response auth fields. Risks include cleartext password lifetime in allocated RPC structures, correct rejection of incompatible output flags, canonicalization mismatches, and preserving child NTSTATUS in `set_auth_errors()`. Test signals include plaintext auth success/failure, Kerberos ccache response, required group SID parsing, memory-creds storage, legacy password policy output, and mapped username handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_pam_auth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_pam_auth_crap.c -->
## sources/user-network-fs/samba/source3/winbindd/winbindd_pam_auth_crap.c

`winbindd_pam_auth_crap.c` is the parent asynchronous wrapper for `WINBINDD_PAM_AUTH_CRAP`, Samba's NTLM challenge/response authentication command. It also supports PAC-auth verification when `WBFLAG_PAM_AUTH_PAC` is set. State tracks authoritative status, flags, PAC trust, domain/user strings, child validation, and the child result.

The send path handles two modes. PAC mode calls `winbindd_pam_auth_pac_verify()` locally in the parent, stores validation and trusted status, and completes without a domain child. NTLM mode terminates request strings, validates request flags with `check_request_flags()`, resolves the auth domain (defaulting blank domain to `lp_workgroup()`), checks LM/NT response lengths including the `WBFLAG_BIG_NTLMV2_BLOB` extra-data path, parses required membership SIDs, copies LM/NT responses and the 8-byte challenge into DATA_BLOBs, then calls `dcerpc_wbint_PamAuthCrap_send()` on the domain child.

`winbindd_pam_auth_crap_recv()` propagates transport and child errors via `set_auth_errors()`, appends requested keys/Info3/AFS data with `append_auth_data()`, conditionally suppresses trusted-domain addition for untrusted PACs, adds trusted-domain data for Info3 text, sets `response->data.auth.authoritative`, marks the response pending, and returns the encoded auth NTSTATUS.

There is no file-local persistence. Effects include cache priming in PAC verification when trusted and child-side SamLogon/cache updates. Dependencies include Netlogon utility types, generated wbint stubs, global event context, `extra_data_to_sid_array()`, `append_auth_data()`, and domain routing. Risks include length validation for large NTLMv2 blobs, authoritative semantics for unknown domains, PAC data being accepted but not cache-primed when untrusted, and NULL validation assumptions after child failures. Test signals include NTLMv1/NTLMv2/big-blob inputs, unknown-domain non-authoritative response, required group rejection, PAC verified/unverified behavior, and response auth flags.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_pam_auth_crap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_pam_chauthtok.c -->
## sources/user-network-fs/samba/source3/winbindd/winbindd_pam_chauthtok.c

`winbindd_pam_chauthtok.c` is the parent asynchronous wrapper for plaintext PAM password changes (`WINBINDD_PAM_CHAUTHTOK`). It canonicalizes the target user, sends old and new passwords to the correct domain child, and maps child password-policy/reject details into the legacy response.

`winbindd_pam_chauthtok_send()` terminates the username, applies `normalize_name_unmap()`, canonicalizes the user with `canonicalize_username()`, resolves the target with `find_domain_from_name(namespace)`, and fills `wbint_PamAuthChangePassword` with client pid, flags, client name, canonical user, old password, and new password. It sends `dcerpc_wbint_PamAuthChangePassword_r_send()` to the domain child. The callback only receives the wrapped RPC result and completes the parent tevent request.

`winbindd_pam_chauthtok_recv()` calls `set_auth_errors()` with the child result, copies password policy fields from returned `samr_DomInfo1` via `fill_in_password_policy()`, stores the reject reason, and, for cached-login requests, updates in-memory single sign-on credentials with `winbindd_replace_memory_creds()`, ignoring missing memory creds as a common expired-password login case.

No durable state is directly stored here, but child-side password changes can update domain credentials and cached credentials, while this wrapper updates memory creds. Dependencies include generated wbint stubs, global event context, username canonicalization, domain routing, SAMR policy structures, and auth-error mapping. Risks include cleartext password lifetime, canonicalization selecting the wrong domain, missing domain returning `NO_SUCH_USER`, memory-cred update failure after a successful password change, and policy/reject information only being available when the child could retrieve it. Test signals include successful change, wrong old password, password restriction with reject reason, unsupported domain, cached-login memory cred replacement, and mapped username input.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_pam_chauthtok.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_pam_chng_pswd_auth_crap.c -->
## sources/user-network-fs/samba/source3/winbindd/winbindd_pam_chng_pswd_auth_crap.c

`winbindd_pam_chng_pswd_auth_crap.c` is the parent wrapper for `WINBINDD_PAM_CHNG_PSWD_AUTH_CRAP`, a password-change command that sends pre-encrypted NT/LM password blobs rather than plaintext old/new passwords. It marshals the legacy request into `wbint_PamAuthCrapChangePassword` and delegates the real SAMR work to the domain child.

`winbindd_pam_chng_pswd_auth_crap_send()` terminates user and domain fields, derives the target domain from the explicit request domain or `lp_workgroup()` when `winbind use default domain` is enabled, resolves it with `find_domain_from_name()`, and rejects missing domains as `NO_SUCH_USER`. It fills client pid/name, domain, user, new NT password blob, encrypted old NT hash blob, and optional LM blobs. Empty LM length produces `data_blob_null` for both LM fields. It sends `dcerpc_wbint_PamAuthCrapChangePassword_r_send()` to the domain child and completes on callback.

`winbindd_pam_chng_pswd_auth_crap_recv()` maps transport errors immediately, otherwise sets auth errors from `state->r.out.result`, marks the response pending, and returns the encoded auth NTSTATUS. There is no file-local persistence; child-side behavior may change the password on the DC but refuses this mode when offline logons are enabled to avoid inconsistent cached credentials.

Dependencies include generated wbint stubs, global event context, talloc DATA_BLOB creation, domain routing, loadparm default-domain behavior, and `set_auth_errors()`. Risks include insufficient explicit length validation for blob fields beyond fixed request buffers, domain derivation ambiguity when no domain is supplied, legacy LM data handling, and limited policy feedback compared with plaintext chauthtok. Test signals include explicit and default-domain requests, NT-only and NT+LM blob changes, unknown domain, child failure mapping, and offline-logon refusal in the child implementation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_pam_chng_pswd_auth_crap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_pam_logoff.c -->
## sources/user-network-fs/samba/source3/winbindd/winbindd_pam_logoff.c

`winbindd_pam_logoff.c` is the parent asynchronous wrapper for `WINBINDD_PAM_LOGOFF`. Its purpose is to authorize a logoff request, delegate Kerberos ccache cleanup to the domain child, and remove winbind memory credentials on success.

`winbindd_pam_logoff_send()` terminates username and krb5 ccache fields, rejects invalid uid, canonicalizes the username, resolves the auth domain with `find_auth_domain()`, and checks the peer process credentials via `getpeereid(cli->sock, &caller_uid, &caller_gid)`. Root may log off any user; non-root callers must match `request->data.logoff.uid`. It then fills `wbint_PamLogOff` with client name/pid, flags, canonical user, uid, and ccache name, and sends `dcerpc_wbint_PamLogOff_r_send()` to the child.

`winbindd_pam_logoff_recv()` maps errors through `set_auth_errors()`, marks the response pending, and, when the child result is OK, deletes memory credentials for the user in the parent with `winbindd_delete_memory_creds()`. The child-side `_wbint_PamLogOff()` checks Kerberos flags and ccache identity before removing ccache and memory creds in the child.

Persistent effects are ccache-list removal and memory-credential deletion; no on-disk state is managed here directly. Dependencies include peer credential APIs, username canonicalization, domain routing, generated wbint stubs, global event context, and memory credential helpers. Risks include platform behavior of `getpeereid()`, uid truncation/invalid uid handling, canonicalization mismatches, and ensuring a caller cannot remove another user's ccache. Test signals include root and same-uid logoff, different-uid rejection, missing/blank ccache success, Kerberos and non-Kerberos flags, memory credential deletion, and unknown user/domain handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_pam_logoff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_ping_dc.c -->
## sources/user-network-fs/samba/source3/winbindd/winbindd_ping_dc.c

`winbindd_ping_dc.c` implements asynchronous `WINBINDD_PING_DC`, returning whether a domain controller can be contacted and, when available, the contacted DC name. State stores `dcname` and the child operation result.

`winbindd_ping_dc_send()` selects the target domain: blank domain preserves old behavior by using `find_our_domain()`, otherwise it uses `find_trust_from_name_noinit()`. Unknown domains return `NO_SUCH_DOMAIN`. Internal passdb-based domains are considered always contactable and synthesize the DC name from `lp_netbios_name()` plus `lp_dnsdomain()` when present, lowercasing the host component. Non-internal domains send `dcerpc_wbint_PingDc_send()` to the domain child.

The callback receives both transport and child operation status with `dcerpc_wbint_PingDc_recv()` and stores `state->result`; transport/operation errors are propagated via tevent. `winbindd_ping_dc_recv()` sets auth error fields if `state->result` is non-OK, copies `dcname` into `extra_data`, updates response length, and returns OK for successfully completed command processing.

There is no local persistence, but the child may initialize or test domain connections and current DC state. Dependencies include generated wbint stubs, domain lookup helpers, loadparm NetBIOS/DNS settings, talloc string helpers, and `set_auth_errors()`. Risks include inconsistent semantics where command transport success can return OK while auth fields contain a DC ping result, NULL `lp_dnsdomain()` handling, synthesized internal DC names, and stale domain online state. Test signals include blank-domain ping, trusted-domain ping, unknown domain, internal domain with/without DNS domain, child failure setting auth errors, and returned cstring length.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_ping_dc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_proto.h -->
## sources/user-network-fs/samba/source3/winbindd/winbindd_proto.h

`winbindd_proto.h` is the hand-maintained/generated-style prototype hub for the source3 winbind daemon. It declares cross-file APIs for daemon lifecycle, cache access, connection management, child processes, idmap/locator children, command handlers, PAM/auth helpers, domain discovery, client management, name parsing, lookup async APIs, and many NSS/idmap request entry points.

The header's important exported surfaces include cache functions (`wb_cache_*`, `wcache_*`, cache invalidation and TDC helpers), connection manager APIs (`cm_connect_sam/lsa/lsat/netlogon`, `invalidate_cm_connection`, trust credentials, current DC gencache), credential/ccache/memory-cred functions, child request/binding helpers, messaging handlers, idmap and locator child accessors, miscellaneous command handlers, NDR debug printers, PAM helpers (`check_request_flags`, `append_auth_data`, `extra_data_to_sid_array`, `_wbint_PamAuth*`, `winbind_dual_SamLogon`, PAC verify), domain list/routing APIs, username normalization/canonicalization, and tevent async send/recv pairs for lookups, UID/GID allocation, passwd/group queries, aliases, tokens, and group membership.

There is no runtime state in the header, but it defines integration contracts among many stateful modules. Its dependencies are broad: Samba NTSTATUS, talloc, tevent, generated NDR types, `dom_sid`, auth/PAM structures, idmap types, messaging, and winbind internal structures. Including it incorrectly can expand rebuild coupling, but it centralizes declarations so C files can share internal APIs without local externs.

Risks include prototype drift from implementation signatures, duplicate declarations visible in this snapshot for locator KDC env helpers, conditional type availability, and the large blast radius of changing shared structs or helper signatures. Test signals are build coverage across feature combinations (`HAVE_ADS`, Kerberos, LDAP), warnings-as-errors for mismatched prototypes, link coverage for all declared functions, and ABI-sensitive command behavior for public winbind request handlers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_reconnect.c -->
## sources/user-network-fs/samba/source3/winbindd/winbindd_reconnect.c

`winbindd_reconnect.c` wraps `msrpc_methods` with one-shot reconnect retry behavior and exposes the wrapper as `reconnect_methods`. Its purpose is to centralize the decision about which NTSTATUS failures indicate a broken connection rather than a real lookup/authz result.

`reconnect_need_retry()` returns false for success, warning/non-error statuses, and expected semantic failures such as `NONE_MAPPED`, `NO_SUCH_USER`, `NO_SUCH_GROUP`, `NO_SUCH_ALIAS`, `NO_SUCH_MEMBER`, `NO_SUCH_DOMAIN`, `NO_SUCH_PRIVILEGE`, and `NO_MEMORY`. For other NTSTATUS errors it calls `reset_cm_connection_on_error(domain, NULL, status)` and returns true. Each wrapper method calls the corresponding `msrpc_methods` function once, retries once if `reconnect_need_retry()` says to, and returns the second result if retried.

The wrapped APIs cover user listing, domain/local group enumeration, name-to-SID, SID-to-name, RIDs-to-names, user groups, user aliases, alias members, group members, lockout policy, password policy, and trusted domains. There is no file-local persistence, but retry behavior mutates connection-manager state by resetting bad connections and may force a fresh RPC bind on the second call.

Dependencies include `msrpc_methods`, `struct winbindd_methods`, NTSTATUS helpers, and connection manager reset behavior. Integration points are domain backend selection: domains can use `reconnect_methods` instead of raw `msrpc_methods` to improve resilience to stale/broken pipes. Risks include retrying non-idempotent operations if new methods are added without care, masking the first failure, not retrying some transport-like statuses listed as semantic failures, and added latency on hard failures. Test signals include simulated broken SAMR/LSA pipes, expected no-retry semantic lookup failures, one retry success after connection reset, policy/trusted-domain retry, and method-table completeness compared with `msrpc_methods`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_reconnect.c -->
