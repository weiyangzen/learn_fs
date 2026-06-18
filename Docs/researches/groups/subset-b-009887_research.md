# subset-b-009887 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_rpc.c -->
# sources/user-network-fs/samba/source3/utils/net_rpc.c

## Purpose

`net_rpc.c` is the large RPC command implementation file for Samba's `net rpc` utility. It provides the top-level `net rpc` dispatcher and many of the concrete subcommands for managing Windows/Samba domains and servers over MSRPC/SMB. The file bridges command-line parsing in `utils/net.h` with Samba client subsystems such as SAMR, LSA, SRVSVC, NETLOGON, INITSHUTDOWN, WINREG, SPOOLSS, libnetapi, winbind, passdb, and secrets storage.

The command families implemented here include:

- generic RPC setup and domain SID discovery.
- domain join/test-join and trust password change.
- domain information and storing a remote domain SID.
- user and group management.
- share and file management, including share/file migration.
- share allowed-user analysis using local user SID lists and remote share/root security descriptors.
- remote shutdown and abort-shutdown.
- NT-style interdomain trust management.
- SAM database vampire dispatch.
- printer listing, publishing, and migration dispatch.
- the final `net_rpc()` command table that wires this file together with other `net rpc` modules such as rights, services, registry, shell, trust, conf, and audit.

The file is explicitly described as a stable, user-friendly subset of functionality that historically lived in `rpcclient`: callers should not need to know low-level RIDs/SIDs before performing common administrative operations.

## Important APIs, Types, and Functions

### Shared RPC setup

- `net_get_remote_domain_sid(struct cli_state *cli, TALLOC_CTX *mem_ctx, struct dom_sid **domain_sid, const char **domain_name)` opens an unauthenticated LSA pipe, opens policy with maximum allowed access, queries `LSA_POLICY_INFO_ACCOUNT_DOMAIN`, and returns the remote account-domain name and SID in the caller's talloc context. This is the common prelude for most `run_rpc_command()` operations.
- `run_rpc_command(struct net_context *c, struct cli_state *cli_arg, const struct ndr_interface_table *table, int conn_flags, rpc_command_fn fn, int argc, const char **argv)` is the central wrapper. It optionally creates an IPC connection, allocates a temporary talloc context, gets the domain SID/name, opens the requested RPC pipe unless `NET_FLAGS_NO_PIPE` is set, invokes the supplied callback, maps NTSTATUS success to shell status 0, and tears down pipe/connection/context.
- The wrapper handles special NETLOGON schannel setup when `lp_client_schannel()` is enabled and the requested table is NETLOGON. It also supports sealed NTLMSSP pipes via `NET_FLAGS_SEAL`, TCP transport via `NET_FLAGS_TCP`, and no-auth named-pipe opens for ordinary calls.

### Join, trust-password, info, SID storage

- `rpc_changetrustpw_internals()` calls `trust_pw_change()` with netlogon credentials to force a machine trust password change.
- `net_rpc_changetrustpw()` selects PDC connection flags and anonymous fallback when explicit credentials are not present, then dispatches through `run_rpc_command()` on NETLOGON.
- `net_rpc_oldjoin()` performs the legacy unsecure join path using `libnet_JoinCtx`, a machine password derived from the local NetBIOS name, `WKSSVC_JOIN_FLAGS_JOIN_UNSECURE`, and optional registry config modification.
- `net_rpc_join_newstyle()` performs the credentialed join path using `c->creds` and `WKSSVC_JOIN_FLAGS_ACCOUNT_CREATE | WKSSVC_JOIN_FLAGS_DOMAIN_JOIN_IF_JOINED`.
- `net_rpc_join()` validates role/name constraints, tries oldjoin under `NET_FLAGS_EXPECT_FALLBACK`, then falls back to the new join path.
- `net_rpc_testjoin()` locates a DC if one was not supplied, optionally translating a flat workgroup into a DNS realm search, then calls `libnet_join_ok()`.
- `rpc_info_internals()` connects to SAMR, opens the domain, queries domain info level 2, and prints domain name, SID, sequence number, and account counts.
- `rpc_getsid_internals()` persists the domain SID to `secrets.tdb` using `secrets_store_domain_sid()`.

### User management

The public command `net_rpc_user()` initializes libnetapi and dispatches:

- `rpc_user_add()`, `rpc_user_delete()`, `rpc_user_rename()`, `rpc_user_password()`, and `rpc_user_setprimarygroup()` use NetAPI calls such as `NetUserAdd`, `NetUserDel`, `NetUserSetInfo`, `NetGroupGetInfo`, and related USER/GROUP info levels.
- `rpc_user_list()` pages through `NetQueryDisplayInformation()` level 1 using `dcerpc_get_query_dispinfo_params()`.
- `rpc_user_info()` lists a user's domain groups through `NetUserGetGroups()`.
- `rpc_user_password()` either uses the supplied password or prompts via `samba_getpass()`, then writes USER_INFO_1003 with `NetUserSetInfo()`.

The file also exposes interactive shell command providers:

- `net_rpc_user_cmds()` defines shell subcommands for `list`, `info`, `show`, and `edit`.
- `net_rpc_user_edit_cmds()` defines editable string fields (`fullname`, `homedir`, `homedrive`, `logonscript`, `profilepath`, `description`) and account flags (`disabled`, `autolock`, `pwnotreq`, `pwnoexp`).
- `rpc_sh_handle_user()` is the shared shell helper that resolves a user name to a SID, validates that it is a domain user in the current domain, opens SAMR connect/domain/user handles, calls a supplied editor callback, and closes policy handles.
- `rpc_sh_user_str_edit_internals()` queries SAMR user info level 21, optionally prints the current selected field, and when a value is supplied zeroes the union, sets the chosen field and `fields_present`, then calls `dcerpc_samr_SetUserInfo()`.
- `rpc_sh_user_flag_edit_internals()` similarly queries level 21, computes new `ACB_*` flags, and writes `SAMR_FIELD_ACCT_FLAGS`.

### Group and alias management

`net_rpc_group()` initializes libnetapi and dispatches group operations:

- `rpc_group_add()` selects global group vs local alias creation based on `c->opt_localgroup`, using `NetGroupAdd()` or `NetLocalGroupAdd()`.
- `rpc_group_delete_internals()` uses SAMR to look up the object, delete aliases directly, or for domain groups first enumerate members, check whether the group is any user's primary group, remove members, and then call `dcerpc_samr_DeleteDomainGroup()`.
- `get_sid_from_name()` opens LSA, resolves names to SIDs/types, and falls back to parsing string SIDs beginning with `S-`.
- `rpc_add_groupmem()` and `rpc_del_groupmem()` manipulate domain group members by opening SAMR domain/group handles and calling `dcerpc_samr_AddGroupMember()` or `DeleteGroupMember()`.
- `rpc_add_aliasmem()` and `rpc_del_aliasmem()` manipulate local alias membership by resolving the member SID through LSA and calling SAMR alias member APIs.
- `rpc_group_addmem_internals()` and `rpc_group_delmem_internals()` route global group vs alias logic after resolving the target group SID/type.
- `rpc_group_list_internals()` lists global groups, local domain aliases, and builtin aliases. It supports long output by opening aliases and querying descriptions.
- `rpc_group_members_internals()` resolves a group/alias, falls back to the builtin domain if not found in the account domain, then calls `rpc_list_group_members()` or `rpc_list_alias_members()`.
- `rpc_group_rename_internals()` renames global groups via `NetGroupSetInfo()`.

### Share, file, and migration logic

`net_rpc_share()` initializes libnetapi and dispatches share operations:

- `rpc_share_add()` parses `share=path`, constructs `SHARE_INFO_2`, and calls `NetShareAdd()`.
- `rpc_share_delete()` calls `NetShareDel()`.
- `rpc_share_list()` calls `NetShareEnum()` level 1 and prints either plain or long share rows.
- `get_share_info()` is an SRVSVC helper that either enumerates all shares with `dcerpc_srvsvc_NetShareEnumAll()` or fetches one share with `dcerpc_srvsvc_NetShareGetInfo()`, then constructs a matching `srvsvc_NetShareInfoCtr` for levels 1, 2, or 502.
- `check_share_availability()` verifies that a share can be tree-connected as a disk share.
- `check_share_sanity()` rejects non-disk shares, builtin names such as `IPC$`, `ADMIN$`, and `global`, excluded shares, and inaccessible shares.

Share migration is coordinated by `rpc_share_migrate()` and the global `net_mode_share`:

- `rpc_share_migrate_shares_internals()` reads source share definitions at level 502, connects to destination SRVSVC via `connect_dst_pipe()`, and creates destination shares with `dcerpc_srvsvc_NetShareAdd()`. It intentionally logs that the definition migration excludes share ACLs.
- `rpc_share_migrate_files_internals()` reads share definitions, connects to each source and destination share using SMB tree connects, copies top-level attributes/ACLs/timestamps via `copy_top_level_perms()`, and recursively copies children through `sync_files()` and `copy_fn()`.
- `copy_fn()` is the recursive callback used by `cli_list()`. It skips `.` and `..`, handles directories by creating/copying directory metadata then descending, and handles files via `net_copy_file()`. It honors `c->opt_acls`, `c->opt_attrs`, and `c->opt_timestamps`.
- `rpc_share_migrate_security_internals()` uses level 502 security descriptors and applies them to destination shares with `dcerpc_srvsvc_NetShareSetInfo()`.
- `rpc_share_migrate_all()` runs the three phases in order: definitions, files, then security, deliberately delaying ACL application so the migration does not lock itself out before file copying.

File commands are exposed by `net_rpc_file()`:

- `rpc_file_user()` lists open files with `NetFileEnum()` level 3, optionally filtered by user.
- `rpc_file_close()` closes a remote open file via `NetFileClose()`.

### Share allowed-user analysis and user SID lists

The allowed-user feature is built from three data sources:

- Remote alias membership from SAMR.
- Local/user-supplied user tokens.
- Remote SRVSVC share security descriptors plus SMB root-directory security descriptors.

Important types and functions:

- `struct full_alias` stores an alias SID and member SID list. `server_aliases` and `num_server_aliases` are file-static process-global state.
- `rpc_aliaslist_internals()` opens SAMR and populates all builtin and domain aliases using `rpc_fetch_domain_aliases()`.
- `push_alias()` appends to the global alias array in chunks of 100.
- `rpc_aliaslist_dump()` optionally resolves aliases and members through LSA for debug output.
- `struct user_token` names a user and holds a `security_token`.
- `get_user_sids()` asks winbind for a user's SID and group GIDs, converts GIDs back to SIDs, and builds a token seeded with user, Everyone, Network, and Authenticated Users.
- `get_user_tokens()` enumerates users through winbind and calls `get_user_sids()` for each.
- `net_usersidlist()` prints local/winbind users and token SIDs in the format consumed by `net rpc share allowedusers`.
- `get_user_tokens_from_file()` parses that file format: a username line followed by SID lines prefixed with a space.
- `collect_alias_memberships()` scans the global alias list and augments each user token with aliases containing any current token SID.
- `show_userlist()` fetches a share security descriptor, tree-connects to the share, tries to open/query the root directory security descriptor, and runs `se_access_check()` against every token before printing user names.
- `rpc_share_allowedusers()` runs three RPC passes: populate alias list through SAMR, dump it through LSA, then evaluate shares through SRVSVC.

### Shutdown

- `rpc_shutdown()` first attempts INITSHUTDOWN `dcerpc_initshutdown_Init()` through `rpc_init_shutdown_internals()`, then falls back to WINREG `dcerpc_winreg_InitiateSystemShutdown()` through `rpc_reg_shutdown_internals()`.
- `rpc_shutdown_abort()` follows the same pattern for aborting a scheduled shutdown, first `dcerpc_initshutdown_Abort()` and then `dcerpc_winreg_AbortSystemShutdown()`.
- Both shutdown paths use `c->opt_comment`, `c->opt_timeout`, `c->opt_force`, and `c->opt_reboot`.

### Interdomain trust management

The `rpc_trustdom()` dispatcher owns legacy NT trust operations:

- `rpc_trustdom_add_internals()` creates an uppercased `<domain>$` SAMR account, obtains the SAM pipe session key, encrypts the supplied trust password with `init_samr_CryptPassword()`, and writes SAMR user info level 23 with `ACB_DOMTRUST`.
- `rpc_trustdom_del_internals()` resolves and opens the trust account, attempts `dcerpc_samr_RemoveMemberFromForeignDomain()`, then deletes the user.
- `rpc_trustdom_establish()` connects to a remote trusting domain using this domain's trust account, verifies the expected interdomain-trust logon result, reconnects anonymously, queries the remote account-domain SID through LSA, and persists the trust password/SID with `pdb_set_trusteddom_pw()`.
- `rpc_trustdom_revoke()` removes a trusted-domain password using `pdb_del_trusteddom_pw()`.
- `rpc_trustdom_list()` enumerates outgoing trusted domains through LSA `EnumTrustDom()` and incoming trust accounts through SAMR `EnumDomainUsers(ACB_DOMTRUST)`, attempting to query each remote domain SID.
- `rpc_trustdom_vampire()` enumerates LSA trusted domains and calls `vampire_trusted_domain()` to query/decrypt each trust password and persist it locally.
- `vampire_trusted_domain()` uses LSA trusted-domain password info, the RPC transport session key, `sess_decrypt_string()`, and `pdb_set_trusteddom_pw()`.

### Printer and SAM vampire dispatch

This file mostly dispatches printer operations to internals implemented elsewhere:

- `rpc_printer_migrate_all()` runs printer migration phases in required order: printers, drivers, forms, settings, security.
- `rpc_printer_migrate()` exposes `all`, `drivers`, `forms`, `printers`, `security`, and `settings`.
- `net_rpc_printer()` exposes `list`, `migrate`, `driver`, and `publish`.
- `rpc_printer_publish()` exposes `publish`, `update`, `unpublish`, and `list`.
- The called internals include `rpc_printer_migrate_*_internals`, `rpc_printer_list_internals`, `rpc_printer_driver_list_internals`, and `rpc_printer_publish_*_internals`, which are declared through included headers/other compilation units.
- `rpc_vampire()` dispatches `net rpc vampire` to `rpc_vampire_passdb()` by default, or `rpc_vampire_keytab()`.

### Final command table

`net_rpc()` initializes libnetapi and registers the top-level command table. Commands implemented in this file include `info`, `join`, `oldjoin`, `testjoin`, `user`, `password`, `group`, `share`, `file`, `printer`, `changetrustpw`, `trustdom`, `abortshutdown`, `shutdown`, `vampire`, and `getsid`. Commands delegated to other modules include `audit`, `rights`, `service`, `registry`, `shell`, `trust`, and `conf`.

## Control Flow

The dominant flow is:

1. A `net rpc ...` command enters `net_rpc()`.
2. `net_run_function()` selects a function from a local `struct functable`.
3. The selected function validates usage, initializes libnetapi if needed, and either performs a NetAPI call directly or calls `run_rpc_command()`.
4. `run_rpc_command()` creates/reuses `cli_state`, obtains the remote domain SID/name through LSA, opens the requested RPC interface, invokes the command callback, frees handles/pipe/context, and returns shell status.

There are notable exceptions:

- NetAPI-only user/group/share/file commands often bypass `run_rpc_command()` and rely on `libnetapi_net_init()` plus `c->opt_host`.
- Join and trust-establish flows use `libnet_Join`, `net_make_ipc_connection()`, `connect_to_ipc()`, or `connect_to_ipc_anonymous()` directly because they need custom credentials, DC discovery, or expected failure semantics.
- `rpc_share_allowedusers()` intentionally runs three separate `run_rpc_command()` invocations against SAMR, LSA, and SRVSVC to build process-global alias state and then consume it.
- Shutdown and abort-shutdown commands implement an interface fallback from INITSHUTDOWN to WINREG.
- Share/printer `migrate all` commands are ordered orchestration functions, not single RPC calls.

## State and Persistence Behavior

Persistent effects are central to this file:

- `net_rpc_join()` and join helpers can create or update machine accounts remotely and may update local Samba configuration when registry config backend is active.
- `rpc_changetrustpw_internals()` changes the machine trust account password.
- `rpc_getsid_internals()` writes the remote domain SID into local `secrets.tdb`.
- Trust management writes and deletes trusted-domain passwords in passdb/secrets through `pdb_set_trusteddom_pw()` and `pdb_del_trusteddom_pw()`.
- User, group, alias, share, open-file, printer, shutdown, and audit-related top-level dispatch can mutate remote server state.
- Share migration creates destination shares, copies file trees/metadata/security descriptors, and may overwrite or apply ACLs on destination objects.
- Printer migration creates queues/drivers/forms/settings and applies printer ACLs on a destination print server.
- `server_aliases` is process-global state allocated under the null talloc context and freed after `rpc_share_allowedusers_internals()`. It is populated in earlier RPC passes and consumed later.
- `net_mode_share` is file-static state set by `rpc_share_migrate()` and read by copy helpers.

Most transient memory is talloc-scoped to a `run_rpc_command()` context or local stackframe. Some functions allocate with `SMB_MALLOC_ARRAY`, `SMB_STRDUP`, `SAFE_FREE`, or winbind buffer allocation and must explicitly free. RPC policy handles are frequently closed, though several helpers close only parent handles on success/error and rely on pipe/context teardown for cleanup.

## Dependencies and Integration Points

This file is tightly integrated with Samba's source3 client/admin stack:

- `utils/net.h` provides `struct net_context`, functable dispatch, common options, usage helpers, connection helpers, and command callback types.
- `cli_state`, SMB tree connect/list/create/close/query functions, and SMB protocol negotiation come from source3 libsmb/client code.
- RPC interfaces come from generated NDR client headers: SAMR, LSA, NETLOGON, SRVSVC, SPOOLSS, INITSHUTDOWN, and WINREG.
- Authentication and credentials use `cli_credentials`, schannel/netlogon credentials, NTLMSSP sealing, passdb, secrets, and local loadparm state.
- User/group/share/file administrative shortcuts use libnetapi.
- Domain controller discovery uses `dsgetdcname()`, `net_find_server()`, `net_find_pdc()`, and legacy RAP/NetServerEnum support.
- User token construction uses winbind client APIs (`wbcListUsers`, `wbcLookupName`, `wbcGetGroups`, `wbcGidToSid`) and Samba security descriptor access checks.
- Printer and registry/service/right/shell/trust/conf subcommands are partially or wholly delegated to neighboring source files through shared symbols.
- Internationalized output is wrapped in `_()`/`N_()` and diagnostic output uses `d_printf`, `d_fprintf`, `DEBUG`, and `DBG_ERR`.

## Risks and Edge Cases

- `run_rpc_command()` assumes domain SID discovery through LSA is required even for commands whose actual pipe may not need it. If LSA policy query fails, downstream operations never run.
- The file mixes NTSTATUS, WERROR, NET_API_STATUS, and shell return codes. Some NetAPI helpers return raw nonzero status values while others normalize to `-1`, which can produce inconsistent CLI exit codes.
- Many operations request `MAXIMUM_ALLOWED_ACCESS` or `SEC_FLAG_MAXIMUM_ALLOWED`, expanding the privilege surface and making least-privilege behavior hard to reason about.
- `rpc_user_password()` checks `argv[1]` after only requiring `argc >= 1`; in the usual argv contract this works if the array is NULL-terminated, but the safer predicate would be `argc >= 2`.
- Several SAMR helpers close only the connect policy handle and rely on context/pipe teardown for subordinate handles. This is common in command-line code but complicates server-side resource lifetime during partial failure.
- `rpc_group_delete_internals()` must inspect every member to avoid deleting a primary group. Large groups can make the command expensive, and errors during member inspection abort deletion.
- `rpc_list_group_members()` advances the RID pointer by 512 even when `this_time` is smaller. Because the loop ends when the final partial batch is consumed, this does not overrun for current control flow, but it is brittle if reused.
- `rpc_share_migrate_files_internals()` has `got_src_share` and `got_dst_share` booleans outside the per-share loop; if multiple shares are processed, cleanup only closes the final stored `cli_share_*` pointers at function exit. This deserves attention in long migrations.
- `copy_fn()` uses static locals for per-callback state (`nt_status`, `local_state`, `filename`, `new_mask`). That is acceptable for single-threaded CLI recursion but unsuitable for concurrent reuse.
- `copy_fn()` builds paths in fixed-size `fstring` buffers and returns `NT_STATUS_NO_MEMORY` on `strlcpy`/`strlcat` truncation. Deep or long paths may fail migration.
- `show_userlist()` appears to call `cli_query_secdesc()` only when `cli_ntcreate()` is not OK, which is counterintuitive because a failed open should not yield a valid `fnum`. This may make root ACL checks ineffective or dependent on unusual failure behavior.
- The allowed-user analysis uses local/winbind token reconstruction rather than server-authenticated access tokens. Conditional ACEs are explicitly unsupported via `CLAIMS_EVALUATION_INVALID_STATE`, and group/alias expansion may differ from the remote server's real logon token construction.
- `server_aliases` is global and populated across separate command invocations in one process; this is simple but fragile if future code makes `net` concurrent or reentrant.
- Trust vampire/decrypt paths intentionally handle cleartext trust passwords and session keys. Debug builds with `DEBUG_PASSWORD` can log passwords.
- `rpc_trustdom_del_internals()` has suspicious error handling after `dcerpc_samr_DeleteUser()`: on non-OK `result`, it assigns `result = status` rather than `status = result`, which can mask the server result.
- Share/printer migration and shutdown commands are highly stateful and destructive; dry-run semantics are absent in this file.
- `net_rpc_check()` only verifies SMB negotiation to at least NT1; it does not verify specific RPC interfaces or permissions.

## Test Signals

Useful test coverage should include:

- Unit or integration tests for `run_rpc_command()` behavior under IPC connection failure, LSA SID-query failure, no-pipe mode, sealed pipe mode, schannel NETLOGON mode, callback success, and callback failure.
- CLI tests for command dispatch and usage output for `net rpc`, `user`, `group`, `share`, `file`, `printer`, `trustdom`, shutdown, and join/testjoin.
- Samba selftest environments with a test DC/member server validating `net rpc info`, `getsid`, `testjoin`, user/group add/list/rename/delete, group membership, share add/list/delete, and file enumeration.
- Negative tests for invalid name/SID lookup, nonexistent groups/users/shares, permission-denied SAMR/LSA/SRVSVC calls, and partial `STATUS_MORE_ENTRIES` pagination.
- Migration tests with disk shares, hidden/admin shares, excluded shares, long paths, ACL/attribute/timestamp combinations, existing destination shares, and destination ACL lockout scenarios.
- Tests for `net usersidlist` and `net rpc share allowedusers` using a controlled user/SID input file, builtin/domain aliases, unmapped SIDs, empty shares, and conditional ACE descriptors.
- Trust-domain tests in an isolated lab domain covering add/delete/establish/revoke/list/vampire, including password persistence and cleanup.
- Shutdown tests should use mocked RPC endpoints or isolated VMs because they intentionally mutate remote machine power state.
- Static analysis should pay attention to fixed-size string buffers, NULL argv assumptions, mixed status conversion, global state lifetime, and paths that handle secrets.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_rpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_rpc_audit.c -->
# sources/user-network-fs/samba/source3/utils/net_rpc_audit.c

## Purpose

`net_rpc_audit.c` implements the `net rpc audit` command family. It is a focused companion to `net_rpc.c` that lets the Samba `net` utility view and modify the target server's global LSA auditing configuration through MSRPC. The supported subcommands are:

- `net rpc audit list`
- `net rpc audit get <category>`
- `net rpc audit set <category> <policy>`
- `net rpc audit enable`
- `net rpc audit disable`

The file does not implement its own connection setup. Each public subcommand delegates to `run_rpc_command()` from `net_rpc.c` with the LSA RPC interface table (`ndr_table_lsarpc`), then performs policy operations through the provided `rpc_pipe_client`.

## Important APIs, Types, and Functions

- `net_help_audit()` prints command-specific help and the accepted category/policy names. It returns `-1` for usage/error paths.
- `print_auditing_category(const char *policy, const char *value)` formats one audit category row. It substitutes localized "Unknown" or "Invalid" labels when inputs are NULL.
- `rpc_audit_get_internal()` validates one category argument, converts it with `get_audit_category_from_param()`, opens LSA policy with `rpccli_lsa_open_policy()`, queries `LSA_POLICY_INFO_AUDIT_EVENTS`, and prints the selected category's current policy using `audit_policy_str()` and `audit_description_str()`.
- `rpc_audit_set_internal()` validates category and policy arguments, maps `Success`, `Failure`, `All`, or `None` to `LSA_AUDIT_POLICY_*` bits, queries the current audit-events policy, updates `settings[audit_category]`, writes it back with `dcerpc_lsa_SetInfoPolicy()`, re-queries, and prints the resulting category setting.
- `rpc_audit_enable_internal_ext()` is the shared enable/disable implementation. It queries `LSA_POLICY_INFO_AUDIT_EVENTS`, toggles `info->audit_events.auditing_mode`, and writes the policy back.
- `rpc_audit_enable_internal()` and `rpc_audit_disable_internal()` are thin wrappers around `rpc_audit_enable_internal_ext()` with `enable=true` or `false`.
- `rpc_audit_list_internal()` opens LSA policy, queries audit events, prints whether auditing is enabled, prints the category count, then prints every category/policy pair.
- `rpc_audit_get()`, `rpc_audit_set()`, `rpc_audit_enable()`, `rpc_audit_disable()`, and `rpc_audit_list()` are command-line wrappers that handle `c->display_usage` and call `run_rpc_command()`.
- `net_rpc_audit()` builds the functable for `get`, `set`, `enable`, `disable`, and `list`, then calls `net_run_function()`.

The key external data structures are `struct policy_handle`, `union lsa_PolicyInformation`, and the `audit_events` branch containing `auditing_mode`, `count`, and `settings[]`.

## Control Flow

The command path is intentionally uniform:

1. `net_rpc()` in `net_rpc.c` dispatches the `audit` subcommand to `net_rpc_audit()`.
2. `net_rpc_audit()` selects a subcommand through `net_run_function()`.
3. The selected wrapper checks `c->display_usage`; otherwise it calls `run_rpc_command(c, NULL, &ndr_table_lsarpc, 0, callback, argc, argv)`.
4. `run_rpc_command()` establishes IPC/RPC context and passes the LSA pipe to the callback.
5. The callback opens an LSA policy handle with maximum allowed access, queries or mutates `LSA_POLICY_INFO_AUDIT_EVENTS`, reports status, and returns NTSTATUS.

`get` and `set` are category-specific. `enable` and `disable` mutate only the global auditing mode. `list` reports both the global mode and every category setting.

## State and Persistence Behavior

The file mutates persistent remote LSA policy state:

- `set` changes one element of `info->audit_events.settings[]` and writes the full audit-events policy blob back with `dcerpc_lsa_SetInfoPolicy()`.
- `enable` and `disable` change `info->audit_events.auditing_mode` and write the full audit-events policy blob back.
- `get` and `list` are read-only.

No local persistent files are written. Memory is allocated under the `mem_ctx` supplied by `run_rpc_command()` and is reclaimed there. Policy handles are opened but not explicitly closed in this file; pipe/context teardown is relied upon for cleanup.

## Dependencies and Integration Points

- Includes `utils/net.h` for `struct net_context`, dispatch helpers, audit-string helpers, and `run_rpc_command()` declaration.
- Uses `rpc_client/rpc_client.h`, generated `ndr_lsa_c.h`, and `rpc_client/cli_lsarpc.h` for LSA policy and DCE/RPC calls.
- Integrates into the broader `net rpc` command table through `net_rpc_audit()`, which is referenced by `net_rpc.c`.
- Uses Samba localization wrappers `_()` and `N_()` for user-visible text.
- Uses `strequal()` for policy keyword comparisons. The accepted values in implementation are title-case (`Success`, `Failure`, `All`, `None`), while the help text displays uppercase names. Whether this is case-insensitive depends on `strequal()` semantics in the Samba string helpers.

## Risks and Edge Cases

- `rpc_audit_get_internal()` accepts `argc` values from 1 to 2 but uses only `argv[0]`; an extra argument is silently ignored.
- `rpc_audit_set_internal()` accepts `argc` values from 2 to 3 but uses only the first two arguments; an extra argument is silently ignored.
- The help text advertises uppercase `SUCCESS`, `FAILURE`, `ALL`, and `NONE`, while the implementation compares against `Success`, `Failure`, `All`, and `None`. If `strequal()` is not case-insensitive in the active build, documented input may fail.
- Category validation depends entirely on `get_audit_category_from_param()` and the returned index. The code trusts that the resulting `audit_category` is in range for `info->audit_events.settings[]`.
- `rpc_audit_set_internal()` queries the policy, modifies one entry, writes it, then re-queries and prints the result. Concurrent administrators changing other audit settings between query and set could lose updates because the entire policy info object is written back.
- All operations request `SEC_FLAG_MAXIMUM_ALLOWED`; this is broad and may hide the minimal access mask required for read-only vs mutating operations.
- Policy handles are not explicitly closed on success or failure. In a short-lived CLI command this is usually harmless, but explicit close would make server-side resource cleanup clearer.
- Error reporting folds both transport failures and server-side LSA result failures into one command-level message, which is user-friendly but can obscure where the failure occurred.

## Test Signals

Useful tests for this file include:

- Dispatch tests for `net rpc audit` with each subcommand and usage mode.
- Argument validation tests for missing category, invalid category, invalid policy, and extra arguments.
- Case-sensitivity tests comparing documented uppercase policies with title-case policy strings accepted by implementation.
- Mocked or integration LSA tests verifying `list` prints global mode, count, and all settings.
- Integration tests verifying `set` updates only the chosen category as observed by a subsequent `get`/`list`.
- Integration tests verifying `enable` and `disable` persist `auditing_mode` and preserve category settings.
- Permission-denied tests for read-only credentials and mutating operations.
- Static checks for array bounds around `audit_category` and for explicit LSA policy handle cleanup.

<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_rpc_audit.c -->
