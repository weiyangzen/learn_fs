# subset-b-009858 research

Grouped research for Samba source3 `rpcclient` command modules covering LSARPC, NETLOGON, NTSVCS, SAMR, and the disabled shutdown command table. Each section preserves the source path and uses reconciliation markers for per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_lsarpc.c -->
# sources/user-network-fs/samba/source3/rpcclient/cmd_lsarpc.c

## Purpose
`cmd_lsarpc.c` implements the `rpcclient` LSARPC command set. It exposes interactive commands for querying policy information, translating SIDs and names, enumerating trusts and privileges, managing LSA accounts/account rights, reading security descriptors, managing trusted-domain records, and creating/querying/storing LSA secrets and private data. It is diagnostic and administrative glue around generated `lsa` DCE/RPC client stubs.

## Important APIs, types, and functions
- `name_to_sid()` accepts either a raw SID string or an account name and resolves it with `rpccli_lsa_lookup_names()` after `rpccli_lsa_open_policy()`.
- `display_query_info_*()` and `display_lsa_query_info()` format selected `union lsa_PolicyInformation` levels, including audit, account-domain, and DNS-domain information.
- Name/SID translation commands include `cmd_lsa_lookup_names`, `cmd_lsa_lookup_names_level`, `cmd_lsa_lookup_names4`, `cmd_lsa_lookup_sids`, `cmd_lsa_lookup_sids_level`, and `cmd_lsa_lookup_sids3`.
- Enumeration/query commands cover trusted domains, privileges, privilege display names, LSA accounts, account rights, privilege values, policy security descriptors, current username, and trusted-domain information by SID/name/handle.
- Mutating commands include account creation, adding/removing account rights, adding/removing privileges, setting trusted-domain encryption types, creating/deleting/updating secrets, storing private data, creating trusted domains through legacy/Ex2/Ex3 variants, and deleting trusted domains.
- Secret and trust-password paths use `dcerpc_binding_handle_transport_session_key()`, `sess_encrypt_string()`, `sess_decrypt_string()`, `rpc_lsa_encrypt_trustdom_info()`, and `rpc_lsa_encrypt_trustdom_info_aes()`.
- The exported `lsarpc_commands[]` table maps user command names to handlers with `RPC_RTYPE_NTSTATUS`, `&ndr_table_lsarpc`, descriptions, and a terminating null entry.

## Control flow
Most handlers parse `argv`, open an LSA policy handle with either `rpccli_lsa_open_policy()` or `dcerpc_lsa_open_policy_fallback()`, call one generated RPC operation on `cli->binding_handle`, validate both transport `status` and server `result`, print formatted results, and close policy handles. Translation commands intentionally accept `STATUS_SOME_UNMAPPED` as displayable partial success. Enumeration commands loop while the server returns `STATUS_MORE_ENTRIES`, carrying the resume context supplied by the RPC.

Trusted-domain commands open policy handles with maximum access, then either query directly by SID/name or open a trusted-domain handle before querying or setting information. Password-bearing trust info is decrypted for display with the negotiated transport session key. Secret and private-data commands open the policy/secret object, encrypt or decrypt payloads with the transport session key, and invoke `lsa_CreateSecret`, `OpenSecret`, `QuerySecret`, `SetSecret`, `RetrievePrivateData`, or `StorePrivateData`.

## State and persistence behavior
This file has no local persistent storage. It mutates remote LSA state through RPC: account rights and privileges, secret objects, private data values, and trusted-domain records are persisted by the target server. Local allocations are talloc-scoped to the command context. Policy and object handles are remote state and must be closed; most paths close them, often guarded by `is_valid_policy_hnd()`.

## Dependencies and integration points
The module depends on `rpcclient.h`, generated `ndr_lsa` structures/stubs, `rpc_client/cli_lsarpc.h`, `rpc_client/init_lsa.h`, SID/security helpers, session encryption helpers from `libcli_auth`, and `struct cmd_set` registration used by the rpcclient command dispatcher. It integrates with the active DCE/RPC binding and the authentication/session protection already established by rpcclient.

## Risks and edge cases
- Several commands print decrypted secrets or trust passwords to stdout, so captured terminal output can expose sensitive material.
- Many mutating commands request `SEC_FLAG_MAXIMUM_ALLOWED`, which is useful for diagnostics but high impact when run with privileged credentials.
- `cmd_lsa_enum_trust_dom()` checks `argc == 2` but reads `argv[2]`, an out-of-bounds argument access when a single optional resume context is provided.
- `cmd_lsa_create_secret()` opens policy into `sec_handle` but passes the uninitialized `handle` to `dcerpc_lsa_CreateSecret()`, suggesting a handle mix-up.
- Some handles are not closed on every error path, and some commands close only parent handles while child handles may remain open until connection teardown.
- Raw `atoi()`/`sscanf()` parsing gives little validation for info classes, access masks, trust directions, encryption types, and sizes.
- `CreateTrustedDomainEx2/Ex3` require enough arguments for both incoming and outgoing passwords, but the usage guard is `argc < 7` even though `argv[7]` is read.

## Test signals
Useful tests include rpcclient integration runs against a Samba test DC for `lsaquery`, `lookupnames`, `lookupsids`, partial unmapped translation, privilege enumeration, account-right add/remove round trips, and trust enumeration pagination. Negative tests should cover malformed SIDs, unsupported info classes, missing arguments for `enumtrust` and trust creation, unavailable session keys for secret/trust password display, and server-side access-denied responses. Secret/private-data tests should verify encrypted storage round trips without leaking values into logs unless explicitly requested by the command.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_lsarpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_netlogon.c -->
# sources/user-network-fs/samba/source3/rpcclient/cmd_netlogon.c

## Purpose
`cmd_netlogon.c` implements the `rpcclient` NETLOGON command set. It provides commands for domain controller discovery, logon-control operations, secure-channel logon/password operations, trust enumeration, DNS deregistration, forest trust queries, site coverage, capabilities probing, and `LogonGetDomainInfo`.

## Important APIs, types, and functions
- DC discovery commands wrap `netr_GetAnyDCName`, `netr_GetDcName`, `netr_DsRGetDCName`, `netr_DsRGetDCNameEx`, and `netr_DsRGetDCNameEx2`.
- Logon-control commands use `dcerpc_netr_LogonControl()` and `dcerpc_netr_LogonControl2()` with `union netr_CONTROL_*` request/response structures.
- Secure-channel commands include `cmd_netlogon_sam_logon()`, `cmd_netlogon_change_trust_pw()`, `cmd_netlogon_capabilities()`, and `cmd_netlogon_logongetdomaininfo()`.
- Trust/site commands call `LogonGetTrustRid`, `DsrEnumerateDomainTrusts`, `DsrDeregisterDNSHostRecords`, `DsRGetForestTrustInformation`, `NetrEnumerateTrustedDomains`, `NetrEnumerateTrustedDomainsEx`, and `DsrGetDcSiteCoverageW`.
- Secure-channel state is supplied through globals declared elsewhere: `rpcclient_netlogon_creds` and `rpcclient_msg_ctx`.
- The exported `netlogon_commands[]` table marks commands that require secure-channel credentials with `.use_netlogon_creds = true`.

## Control flow
Most commands parse optional server/domain/site/GUID/flag parameters, call one generated NETLOGON RPC through `cli->binding_handle`, translate transport `NTSTATUS` into `WERROR` for WERROR commands, then print the useful output. The older `getanydcname` and `getdcname` commands temporarily raise the RPC timeout to at least thirty seconds so the target DC has time to answer. DS discovery commands print the NDR-rendered `netr_DsRGetDCNameInfo` structure on success.

Secure-channel commands use higher-level helpers. `samlogon` requires `rpcclient_netlogon_creds`, generates a random logon ID, calls `rpccli_netlogon_password_logon()`, and maps the returned validation union to `netr_SamInfo3`. `change_trust_pw` forces a trust-password update with `trust_pw_change()`. `capabilities` takes an exclusive netlogon credentials lock, checks the secure channel, and prints server capabilities. `logongetdomaininfo` sends an empty `netr_WorkstationInformation` query through `netlogon_creds_cli_LogonGetDomainInfo()`.

## State and persistence behavior
Most commands are read-only discovery/control calls and persist no local state. `change_trust_pw` mutates the machine/trust account password on the remote domain controller and local secrets through the helper stack. `deregisterdnsrecords` mutates remote DNS registration state. Secure-channel commands consume and may update netlogon credential state maintained outside this file. Temporary timeout changes are restored before the command returns.

## Dependencies and integration points
The module depends on generated `ndr_netlogon` stubs, `rpc_client/cli_netlogon.h`, `rpc_client/util_netlogon.h`, `netlogon_creds_cli`, `secrets.h`, loadparm (`lp_workgroup()`), GUID parsing, NDR pretty-printing, and rpcclient command registration. It integrates with rpcclient's secure-channel setup through the `.use_netlogon_creds` flag and global credential handles.

## Risks and edge cases
- `samlogon` takes a plaintext password argument, so command history and process listings can expose credentials.
- `change_trust_pw` is a destructive administrative operation because it forcibly rotates trust credentials.
- `cmd_netlogon_capabilities()` returns early on `netlogon_creds_cli_check()` failure without freeing the acquired lock explicitly.
- Many commands accept numeric flags via `atoi()` or `%x` without validating semantic combinations.
- `DsrGetForestTrustInformation` and several enumeration commands print only `success`, leaving useful returned structures uninspected.
- Error handling is split between `WERROR` and `NTSTATUS`; callers must verify the command table return type when testing behavior.

## Test signals
Integration tests should exercise DC discovery with DNS and NetBIOS names, GUID parsing failures, logon-control success/failure, trust enumeration, site coverage, and secure-channel-required commands both with and without established `rpcclient_netlogon_creds`. Tests for `getanydcname` and `getdcname` should verify timeout restoration. Password and trust-password tests should run only in isolated domains where credential rotation is expected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_netlogon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_ntsvcs.c -->
# sources/user-network-fs/samba/source3/rpcclient/cmd_ntsvcs.c

## Purpose
`cmd_ntsvcs.c` implements the `rpcclient` NTSVCS command set for a small set of Windows Plug and Play service RPCs. It is primarily a diagnostic wrapper around generated `PNP_*` stubs for version, device instance validation, hardware profile information, device registry properties, and device list sizing/listing.

## Important APIs, types, and functions
- `cmd_ntsvcs_get_version()` calls `dcerpc_PNP_GetVersion()` and prints the returned 16-bit version.
- `cmd_ntsvcs_validate_dev_inst()` validates a device instance path with optional flags via `PNP_ValidateDeviceInstance`.
- `cmd_ntsvcs_hw_prof_flags()` calls `PNP_HwProfFlags` with a device path and fixed/default profile fields.
- `cmd_ntsvcs_get_hw_prof_info()` calls `PNP_GetHwProfInfo` for index zero into a `struct PNP_HwProfInfo`.
- `cmd_ntsvcs_get_dev_reg_prop()` queries `DEV_REGPROP_DESC` with caller-supplied buffer size.
- `cmd_ntsvcs_get_dev_list_size()` and `cmd_ntsvcs_get_dev_list()` wrap `PNP_GetDeviceListSize` and `PNP_GetDeviceList`.
- The exported `ntsvcs_commands[]` table maps all handlers as `RPC_RTYPE_WERROR` on `&ndr_table_ntsvcs`.

## Control flow
Each command parses a small argument list, fills default fields, invokes one generated NTSVCS RPC using `cli->binding_handle`, converts transport failures with `ntstatus_to_werror()`, and returns the server `WERROR`. Only `getversion`, `getdevlistsize`, and `getdevlist` print selected output; the others mainly expose success or failure status to rpcclient.

## State and persistence behavior
This file has no local persistent state. The commands are mostly read-only or validation-oriented against the remote Plug and Play service. The exact server-side side effects of `PNP_HwProfFlags` depend on flags and server implementation, but this wrapper passes fixed zeros apart from the device path. Buffers are talloc-scoped to the command memory context.

## Dependencies and integration points
The module depends on `rpcclient.h` and generated `ndr_ntsvcs_c.h`. It integrates only through the rpcclient command dispatcher and the active DCE/RPC binding to the NTSVCS endpoint.

## Risks and edge cases
- `cmd_ntsvcs_get_dev_reg_prop()` allocates `buffer_size` bytes and uses `W_ERROR_HAVE_NO_MEMORY(buffer)`; a zero buffer size may be treated as allocation failure depending on talloc behavior.
- `cmd_ntsvcs_get_dev_list()` allocates only one `uint16_t` regardless of requested `length`, then passes `&length` to the RPC. If the generated stub writes more than one element into the supplied buffer, this wrapper is unsafe.
- Device paths, flags, and buffer sizes are parsed with minimal validation and no range checks.
- Several commands return success/failure without printing returned structures or needed buffer sizes, reducing diagnostic value.

## Test signals
Tests should cover usage validation, transport-error mapping, zero and nonzero buffer-size behavior for device registry properties, and `GetDeviceList` with length values larger than one to detect buffer sizing problems. A Windows or Samba test endpoint with NTSVCS support can validate successful `getversion`, `getdevlistsize`, and expected error codes for invalid device instance paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_ntsvcs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_samr.c -->
# sources/user-network-fs/samba/source3/rpcclient/cmd_samr.c

## Purpose
`cmd_samr.c` implements the `rpcclient` SAMR command set. It exposes administrative and diagnostic operations for users, groups, aliases, domain information, display enumeration, SID/RID/name lookup, security descriptors, password policy, password changes, account creation/deletion, and setting user password information through multiple SAMR info levels.

## Important APIs, types, and functions
- `static struct dom_sid domain_sid` caches the first non-builtin domain SID discovered by `rpccli_try_samr_connects()`.
- `rpccli_try_samr_connects()` opens a SAMR connect handle using `dcerpc_try_samr_connects()`, enumerates domains, skips `builtin`, looks up the selected domain SID, and caches it globally.
- `get_domain_handle()` opens either the cached domain SID or `global_sid_Builtin` based on a `domain|builtin` argument.
- Display helpers format `samr_UserInfo*`, `samr_DomainInfo*`, `samr_DispEntry*`, password property flags, and group/alias information.
- Query/enumeration commands include `queryuser`, `querygroup`, `queryusergroups`, `queryuseraliases`, `querygroupmem`, `enumdomusers`, `enumdomgroups`, `enumalsgroups`, `enumdomains`, `querydispinfo*`, `querydominfo`, `queryaliasmem`, `queryaliasinfo`, `samquerysecobj`, `getdompwinfo`, `getusrdompwinfo`, `lookupdomain`, and `getdispinfoidx`.
- Mutating commands include `createdomuser`, `createdomgroup`, `createdomalias`, `deletedomgroup`, `deletedomuser`, `deletealias`, `chgpasswd*`, `setuserinfo`, and `setuserinfo2`.
- Password-setting support uses `nt_lm_owf_gen()`, `sess_crypt_blob()`, `init_samr_CryptPassword()`, `init_samr_CryptPasswordEx()`, and `init_samr_CryptPasswordAES()` for info levels 18, 21, 23, 24, 25, 26, and 31.
- The exported `samr_commands[]` table maps the SAMR user command names to `RPC_RTYPE_NTSTATUS` handlers with `&ndr_table_samr`.

## Control flow
Almost every command first calls `rpccli_try_samr_connects()` to establish a SAMR connect handle and initialize `domain_sid`. Commands then open a domain handle, optionally open a user/group/alias handle, call the relevant generated SAMR RPC, print formatted output, and close handles. Lookup commands validate returned counts to guard against malformed server responses. Enumeration commands use resume indexes and loop while the server returns `STATUS_MORE_ENTRIES`.

User and alias commands often accept either numeric RIDs or names. Some paths attempt a numeric open first, then fall back to `samr_LookupNames()` when opening RID zero fails or when the parsed RID is zero. Password change wrappers call higher-level `rpccli_samr_chgpasswd_user*()` helpers, while `chgpasswd4` directly calls the generated `dcerpc_samr_chgpasswd_user4()` server-name form. `setuserinfo` and `setuserinfo2` build the requested `union samr_UserInfo` variant, encrypt password material with the session key, resolve the target user, and invoke either `samr_SetUserInfo` or `samr_SetUserInfo2`.

## State and persistence behavior
The global `domain_sid` persists for the rpcclient process after first discovery and influences all later domain-scoped commands. The file otherwise stores no local persistent data. Remote SAM state is changed by create/delete commands, password changes, and set-user-info commands. Query commands can reveal account metadata, logon counters, password policy, security descriptors, and membership. Talloc frames own temporary encrypted password buffers in `setuserinfo`.

## Dependencies and integration points
The module depends on generated `ndr_samr` stubs, `rpc_client/cli_samr.h`, `rpc_client/init_samr.h`, `rpc_client/init_lsa.h`, SID/security helpers, string-to-integer helpers, session-key encryption, and rpcclient's command dispatcher. It uses common Samba constants for account flags, password properties, security descriptor selectors, and builtin/domain SIDs.

## Risks and edge cases
- The cached `domain_sid` assumes the first non-builtin domain is the desired target for the life of the process; multi-domain or retargeted sessions can surprise later commands.
- `cmd_samr_chgpasswd()` and `cmd_samr_chgpasswd2()` check `argc < 3` but then read `argv[3]`; they should require at least four arguments.
- `cmd_samr_query_aliasinfo()` allows at most four arguments but reads `argv[4]` when `argc > 3`, an out-of-bounds access for the documented optional access mask.
- `cmd_samr_get_dom_pwinfo()` allows `argc < 1` but unconditionally reads `argv[1]`; invoking without a domain can read past arguments.
- Passwords are supplied on the command line for `chgpasswd*` and `setuserinfo*`, exposing them through shell history and process inspection.
- Some close calls are skipped on early `goto done` paths unless guarded later, so remote handles may remain until connection teardown.
- `setuserinfo` includes low-level password hash/encryption handling; mistakes in level selection, session-key availability, salt, or buffer sizes can corrupt password updates or fail with policy errors.
- Commands that delete users, groups, and aliases perform permanent remote mutations with minimal confirmation.

## Test signals
Tests should cover domain SID discovery, builtin versus domain handle selection, name/RID lookup round trips, enumeration pagination, display info variants, query user by RID and by name fallback, security descriptor queries, and password policy display. Negative tests should call malformed argument combinations for `chgpasswd`, `chgpasswd2`, `queryaliasinfo`, and `getdompwinfo` under sanitizers. Mutation tests should run in an isolated SAM database and verify create/delete user/group/alias, password-change failure reporting, and `setuserinfo` levels 23/24/25/26/31 against known expected server behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_samr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_shutdown.c -->
# sources/user-network-fs/samba/source3/rpcclient/cmd_shutdown.c

## Purpose
`cmd_shutdown.c` is the placeholder for rpcclient remote shutdown commands. The historical `shutdowninit` and `shutdownabort` handlers remain in the file, but they are disabled behind `#if 0` with a note directing users to `net rpc shutdown` unless the getopt-based code is reworked.

## Important APIs, types, and functions
- Disabled `cmd_shutdown_init()` would parse `-m`, `-t`, `-r`, and `-f` options and call `cli_shutdown_init()` with message, timeout, reboot, and force flags.
- Disabled `cmd_shutdown_abort()` would call `cli_shutdown_abort()`.
- `shutdown_commands[]` currently exports only the `SHUTDOWN` category header and terminating null command because both command entries are inside the disabled block.

## Control flow
In compiled code, rpcclient sees an empty shutdown command group. The disabled init path would reset global `optind`, iterate `getopt()`, fill local flags, and send an init-shutdown request. The disabled abort path would send a shutdown-abort request and log success or failure at debug level 5.

## State and persistence behavior
The active file has no state or remote side effects. If re-enabled, `shutdowninit` would schedule or force a remote shutdown/reboot on the target host, and `shutdownabort` would attempt to cancel one. The disabled option parsing mutates process-global `optind`, which is the reason noted by the surrounding comment.

## Dependencies and integration points
The active file depends only on `includes.h`, `rpcclient.h`, and `struct cmd_set` registration. The disabled code depends on legacy client shutdown helpers rather than generated DCE/RPC stubs, and its command-table entries reference the initshutdown RPC table and remote shutdown pipe.

## Risks and edge cases
- Re-enabling the block without addressing `getopt()` global state could interfere with rpcclient's own command parsing or other commands in the same process.
- The disabled usage string mentions `-h`, but the option string is `m:t:rf` and no `-h` case exists.
- Remote shutdown is high impact and would need explicit authorization checks, clear test isolation, and probably confirmation if exposed interactively.

## Test signals
Current tests should assert that no `shutdowninit` or `shutdownabort` command is registered. If the block is re-enabled, tests need argument parsing coverage, `optind` isolation across repeated calls, scheduled shutdown and abort behavior against a controlled test server, and verification that `net rpc shutdown` remains the preferred supported path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_shutdown.c -->
