# Research: subset-b-009885

This grouped report covers Samba `source3/utils` `net` command modules for ADS, DNS, AFS, cache, configuration, remote domain, eventlog, file, g_lock, group, groupmap, and help behavior. Each section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_ads.c -->
# sources/user-network-fs/samba/source3/utils/net_ads.c

Purpose: implements the `net ads` command tree for Active Directory operations when Samba is built with `HAVE_ADS`, plus no-ADS stubs when it is not. It provides discovery (`info`, `lookup`, `workgroup`), membership (`join`, `leave`, `testjoin`, `changetrustpw`), directory object management (`user`, `group`, `printer`, `search`, `dn`, `sid`), DNS registration, Kerberos/keytab/PAC helpers, SPN management, GPO dispatch, and encryption-type attribute management.

Important APIs and functions: `ads_startup()` and `ads_startup_nobind()` wrap `ads_startup_int()` and are the shared connection setup path. `net_ads()` dispatches the top-level functable. Major exported sub-dispatchers include `net_ads_user()`, `net_ads_group()`, `net_ads_keytab()`, `net_ads_kerberos()`, `net_ads_setspn()`, `net_ads_changetrustpw()`, `net_ads_join()`, and `net_ads_check()`. Internal helpers include `assume_own_realm()`, JSON emitters under `HAVE_JANSSON`, `net_ads_cldap_netlogon()`, `usergrp_display()`, `net_ads_enctype_lookup_account()`, and `net_ads_enctype_dump_enctypes()`.

Control flow: most commands allocate a `talloc_stackframe()`, validate usage, call `ads_startup()` or `ads_startup_nobind()`, then perform one LDAP/Kerberos/libnet operation and free ADS LDAP messages before freeing the frame. `ads_startup_int()` initializes an `ADS_STRUCT`, optionally performs CLDAP-only discovery, otherwise binds with `ads_connect_creds()`, and retries after clearing namecache if the closest DC heuristic says a better DC should be used. `net_ads_join()` parses key/value options, initializes `libnet_JoinCtx`, calls `libnet_Join()`, falls back from DNS to NetBIOS domain name when DC lookup fails for the configured realm, reports the join, then triggers DNS updates unless disabled. `net_ads()` itself is a static functable routed through `net_run_function()`.

State and persistence: this file mutates AD LDAP state for users, groups, machine accounts, printers, SPNs, and `msDS-SupportedEncryptionTypes`. It reads and updates local trust secrets through `secrets_init()`, machine credentials, trust password changes, and keytab synchronization. Join and leave can modify Samba registry-backed configuration when `lp_config_backend_is_registry()` is true through libnet join/unjoin contexts. DNS subcommands call into dynamic DNS update code. PAC save writes a raw PAC blob to a user-specified file. JSON output is transient.

Dependencies and integration points: depends heavily on `ads.h`, libads CLDAP/LDAP helpers, libnet join/unjoin, `smb_krb5`, secrets/passdb, `utils/net_dns.h`, winbind client SID lookup, spoolss RPC for printer publishing, Jansson/audit JSON helpers when available, and the common `net_context` command/credential/options model. `net_group.c` delegates ADS-capable group operations to `net_ads_group()`, `net_ads_gpo.c` provides the GPO subcommand called from this file, and `net_ads_join_dns.c` provides post-join DNS updates.

Risks: the file accepts raw LDAP filters and DNs for diagnostic commands, so correctness depends on caller escaping except where explicitly escaped, such as `ads_user_info()`. `net_ads_enctype_lookup_account()` builds an LDAP filter from `account` without escaping. Several destructive commands delete or modify directory objects. The printer remove "not found" message indexes `argv[1]` even when only `argv[0]` may exist. Password handling zeros some buffers but stores command-line passwords if provided. Many operations require valid ADS/Kerberos build options and network/DC availability, making error paths important.

Test signals: exercise no-ADS builds for stub behavior; CLDAP-only `net ads lookup/info/workgroup`; join/testjoin/leave with and without registry backend; user/group add/delete/list against a test AD; DNS register/unregister including clustered refusal; keytab create/list; Kerberos kinit/renew/PAC dump/save; SPN add/list/delete; enctype list/set/delete; JSON output with and without Jansson; and malformed LDAP/account inputs for escaping and error handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_ads.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_ads_gpo.c -->
# sources/user-network-fs/samba/source3/utils/net_ads_gpo.c

Purpose: implements `net ads gpo` subcommands for listing, resolving, and linking Active Directory Group Policy Objects. It is compiled only under `HAVE_ADS`.

Important APIs and functions: `net_ads_gpo()` dispatches `getgpo`, `linkadd`, `linkget`, `list`, and `listall`. `net_ads_gpo_list_all()` searches all `groupPolicyContainer` objects with security descriptor flags. `net_ads_gpo_list()` resolves a SAM account, derives user or machine token context, and computes applicable GPOs. `net_ads_gpo_link_get()` reads `gPLink`; `net_ads_gpo_link_add()` writes a new link; a `linkdelete` implementation is present but disabled with `#if 0`.

Control flow: each command validates arguments, creates a named talloc context, calls `ads_startup()`, performs one libgpo/libads operation, dumps the resulting GPO or link structure, then frees the context. Account listing switches to `GPO_LIST_FLAG_MACHINE` and `gp_get_machine_token()` when the target has `UF_WORKSTATION_TRUST_ACCOUNT`; otherwise it uses `ads_get_sid_token()`.

State and persistence: `list`, `listall`, `getgpo`, and `linkget` are read-only LDAP/GPO queries. `linkadd` mutates the target container's GPO link attribute via `ads_add_gpo_link()`. There is no local persistence except command output.

Dependencies and integration points: depends on `ads_startup()` from `net_ads.c`, `../libgpo/gpo.h`, `libgpo/gpo_proto.h`, and AD user-account-control flags. It is reachable through the top-level `net ads gpo` dispatch in `net_ads.c`.

Risks: the commands accept raw DNs and GPO names; the usage text warns DNs must be RFC 4514 escaped. Several functions return `0` even after failures reached through `goto out`, so shell status may not reflect failure. `net_ads_gpo_list_all()` requests DACL data and depends on directory permissions. The disabled `linkdelete` suggests incomplete mutation coverage.

Test signals: list all GPOs in a test domain; list applicable GPOs for both user and machine accounts; get a GPO by DN and by display/name lookup; add and read back a GPO link; verify insufficient permissions and malformed DN paths; verify command exit codes on lookup failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_ads_gpo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_ads_join_dns.c -->
# sources/user-network-fs/samba/source3/utils/net_ads_join_dns.c

Purpose: provides internal DNS update support used by `net ads join` and explicit DNS registration paths. It decides which nameserver/domain to update, obtains machine trust credentials after joins, and calls the dynamic DNS engine in `net_dns.c`.

Important APIs and functions: `net_update_dns_ext()` is the exported update wrapper under `HAVE_KRB5`; `net_update_dns_internal()` discovers nameservers and calls `DoDNSUpdate()`. `net_ads_join_dns_updates()` is called by `net_ads_join()` after successful AD joins.

Control flow: `net_update_dns_ext()` lowercases the requested hostname or uses `lp_dns_hostname()`, gathers non-loopback local IPs via `get_my_ip_address()` when registering with no explicit IP list, and delegates to `net_update_dns_internal()`. The internal function extracts the DNS domain from the machine name, honors `--dns-ttl`, uses `c->opt_host` as a direct nameserver when set, otherwise looks up NS records. If child-domain NS lookup fails, it queries rootDSE for `rootDomainNamingContext`, builds the forest root domain, and retries. It then iterates nameservers, trying probe, unsigned, and signed update flags with force/removal adjustments.

State and persistence: successful registration/removal changes DNS records on AD-integrated DNS servers. Post-join updates read newly stored trust credentials via `pdb_get_trust_credentials()` and do not alter local config directly. Automatic post-join updates are skipped for clustered setups and non-AD domains.

Dependencies and integration points: depends on libads DNS lookup/search, passdb trust credentials, `utils/net_dns.h`, `DoDNSUpdate()`, and `struct libnet_JoinCtx` output from `libnet_Join()`. It is invoked from `net_ads.c` after joins and from explicit `net ads dns register/unregister` through `net_update_dns_ext()`.

Risks: child-domain fallback requires an LDAP connection if CLDAP-only state lacks `ads->ldap.ld`. Hostname without a dot is rejected because no DNS domain can be derived. Automatic interface discovery excludes loopback and link-local addresses but may still include undesired local addresses outside clustered mode. With `--force`, probe/unsigned sufficient flags are disabled, increasing signed update attempts. DNS deletion deliberately ignores probe-sufficient success so removal proceeds.

Test signals: join against AD with DNS updates enabled/disabled; clustered configuration skip; explicit hostname/IP registration and removal; hostnames lacking domain; TTL clamping; nameserver failover; forest-root NS fallback; machine trust credential failure; and forced update behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_ads_join_dns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_afs.c -->
# sources/user-network-fs/samba/source3/utils/net_afs.c

Purpose: implements optional `net afs` commands for fake KASERVER/OpenAFS integration when built with `WITH_FAKE_KASERVER`.

Important APIs and functions: `net_afs()` dispatches `key` and `impersonate`; `net_afs_key()` imports an OpenAFS `KeyFile` into Samba secrets; `net_afs_impersonate()` creates and installs an AFS token; `net_afs_usage()` prints command help.

Control flow: `net_afs_key()` requires keyfile path and cell, initializes `secrets.tdb`, reads a fixed-size `struct afs_keyfile` from disk, stores it with `secrets_store_afs_keyfile()`, and zeroes the local key buffer. `net_afs_impersonate()` calls `afs_createtoken_str()` and `afs_settoken_str()`, then prints success.

State and persistence: `key` persists secret AFS key material into `secrets.tdb`. `impersonate` installs a token into the kernel AFS token state. Both are local operations.

Dependencies and integration points: depends on `utils/net_afs.h`, `secrets.h`, `system/filesys.h`, `lib/afs/afs_funcs.h`, and `lib/afs/afs_settoken.h`. It plugs into the generic `net_run_function()` command model.

Risks: compiled out entirely unless `WITH_FAKE_KASERVER` is enabled. `net_afs_impersonate()` calls `exit(1)` on usage/token errors instead of returning through the dispatcher. Keyfile import assumes exact structure size and no endian/version negotiation. Secret key material is handled in memory and must remain zeroed on all error paths.

Test signals: build with and without `WITH_FAKE_KASERVER`; import valid/truncated/missing keyfiles; verify secrets entry by cell; token creation/set failure paths; and dispatcher help output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_afs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_afs.h -->
# sources/user-network-fs/samba/source3/utils/net_afs.h

Purpose: declares the optional AFS command entry points used by `net_afs.c` and command registration code.

Important APIs and types: declares `net_afs_usage()`, `net_afs_key()`, `net_afs_impersonate()`, and `net_afs()`, all taking `struct net_context *`, `argc`, and `argv`.

Control flow: this header has no runtime logic; it exposes the command functions to other compilation units.

State and persistence: none directly. The declared functions can modify `secrets.tdb` and kernel AFS token state when implemented.

Dependencies and integration points: relies on `struct net_context` being visible to includers through prior includes. Guarded by `_NET_AFS_H_`.

Risks: declarations are unconditional while implementation bodies are under `WITH_FAKE_KASERVER`, so build integration must ensure missing symbols are not referenced when the feature is disabled.

Test signals: compile both feature-enabled and feature-disabled configurations; include-order checks for `struct net_context` visibility; and command registration linkage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_afs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_cache.c -->
# sources/user-network-fs/samba/source3/utils/net_cache.c

Purpose: implements `net cache`, a local CLI around Samba generic cache (`gencache`) and samlogon cache data, primarily for inspection, testing, and cleanup.

Important APIs and functions: `net_cache()` dispatches `add`, `del`, `get`, `search`, `list`, `flush`, and nested `samlogon`. Helpers include `print_cache_entry()`, `delete_cache_entry()`, `parse_timeout()`, `net_cache_samlogon_list()`, `show()`, `ndrdump()`, and `delete()`.

Control flow: simple cache commands parse arguments, call `gencache_set()`, `gencache_del()`, `gencache_get_data_blob()`, or `gencache_iterate*_blobs()`, and print human-readable entries. `print_cache_entry()` formats expiry times, decodes known `NAME2SID/` and `SID2NAME/` string-vector values, prints printable NUL-terminated blobs directly, and labels other data as binary. Samlogon commands parse SIDs, retrieve `netr_SamInfo3` entries, derive SID arrays, or NDR-print the structure.

State and persistence: mutates local gencache entries and samlogon cache entries; `flush` deletes all gencache keys matching `*`; `samlogon delete` removes one cached user. Other commands are read-only.

Dependencies and integration points: depends on `libsmb/samlogon_cache.h`, generated Netlogon NDR types, SID helpers, `lib/gencache.h`, `strv`, and the common `net_run_function()` framework.

Risks: `parse_timeout()` has weak validation: nonnumeric strings become zero-ish values through `atoi()`, and empty strings can underflow `timeout_str[len - 1]`. `flush` is broad and destructive. Cache values may be binary and are intentionally not fully printed. Samlogon display depends on valid NDR/cache layout.

Test signals: add/get/delete/list/search with relative and expired timeouts; binary versus printable value formatting; `NAME2SID` and `SID2NAME` decoding; flush on test cache; samlogon list/show/ndrdump/delete with valid and invalid SIDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_conf.c -->
# sources/user-network-fs/samba/source3/utils/net_conf.c

Purpose: implements `net conf`, a local management interface for Samba configuration stored through libsmbconf, currently registry-backed for command execution and file-backed for imports.

Important APIs and functions: `net_conf()` dispatches a private `conf_functable` through `net_conf_run_function()`. `net_conf_wrap_function()` opens `registry:` via `smbconf_init()`, calls the selected handler, and shuts down. Handlers include `list`, `import`, `listshares`, `drop`, `showshare`, `addshare`, `delshare`, `setparm`, `getparm`, `delparm`, `getincludes`, `setincludes`, and `delincludes`.

Control flow: each handler validates argc/usage and works against an opened `struct smbconf_ctx`. Import opens `file:<filename>`, optionally limits to one service, optionally test-prints, and otherwise wraps changes in transactions; full imports drop current config then commit in batches of 100 services to cap talloc growth. Share creation validates names and absolute paths, creates the share, sets `path`, optional `comment`, `guest ok`, and `writeable`, then commits. Parameter setting lowercases the parameter, validates via `net_conf_param_valid()`, creates the service if missing, and sets the parameter transactionally.

State and persistence: mutates registry-backed Samba configuration. `drop` deletes the complete config. `delshare` also deletes share security with `delete_share_security()`. Include operations mutate include lists. Test mode for import avoids writes and prints intended config.

Dependencies and integration points: depends on `lib/smbconf/smbconf*`, registry smbconf backend, `lib/param/loadparm.h`, `net_conf_util.h`, and common `net_context` options such as `opt_testmode`. It is a local transport command and deliberately wraps each function with config open/close.

Risks: destructive commands (`drop`, full `import`, `delshare`) can remove production config or ACLs. Full import appears to commit when `sidx % 100 == 0`, which includes the first item, so batching behavior should be checked. `setparm` can create a service for a typo. Validation relies on `net_conf_param_valid()` and registry backend restrictions. Some commands do not use explicit transactions for include mutations.

Test signals: list/show/listshares against known registry config; import full and single-service files with and without `--test`; transaction rollback on invalid service; addshare validation for invalid name/path and homes empty path; set/get/del parameter validation; include get/set/delete; delshare ACL cleanup error handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_conf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_conf_util.c -->
# sources/user-network-fs/samba/source3/utils/net_conf_util.c

Purpose: provides shared validation for `net conf` and `net rpc conf` parameter writes.

Important APIs and functions: `net_conf_param_valid(const char *service, const char *param, const char *valstr)` validates a parameter name/value and whether it can be stored in the registry backend.

Control flow: validation checks `lp_parameter_is_valid()`, then `smbconf_reg_parameter_is_valid()`, then rejects global parameters in non-global service definitions, then calls `lp_canonicalize_parameter_with_value()` to ensure the value parses.

State and persistence: no persistence; it is a guard before smbconf writes.

Dependencies and integration points: depends on loadparm parameter metadata, registry smbconf validation, and `GLOBAL_NAME`. Called by `net_conf_setparm()` before transaction and write.

Risks: `strequal(service, GLOBAL_NAME)` assumes `service` handling is safe for possible NULL values used by libsmbconf dangling/global semantics. It intentionally discards canonicalized names/values and only uses canonicalization as validation, so stored spelling remains caller-provided lowercased parameter plus original value.

Test signals: invalid parameter names; registry-disallowed parameters; global-only parameters in shares; invalid values for valid parameters; global section and empty-service behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_conf_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_conf_util.h -->
# sources/user-network-fs/samba/source3/utils/net_conf_util.h

Purpose: declares utility functions shared by configuration command modules.

Important APIs and types: exports `bool net_conf_param_valid(const char *service, const char *param, const char *valstr);`.

Control flow: no runtime control flow; include guard `__NET_CONF_UTIL_H__` prevents duplicate declarations.

State and persistence: none directly; declared validation protects later registry configuration writes.

Dependencies and integration points: consumers must have `bool` and Samba config symbols available through normal includes. Used by `net_conf.c` and intended for `net rpc conf`.

Risks: API accepts nullable-looking C strings but the contract is not documented in the header; callers must align with implementation assumptions.

Test signals: compile include users; validate declaration matches implementation; static analysis for nullable service usage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_conf_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_dns.c -->
# sources/user-network-fs/samba/source3/utils/net_dns.c

Purpose: implements the dynamic DNS update engine used by `net ads dns` and post-join DNS registration when Kerberos support is available.

Important APIs and functions: `DoDNSUpdate()` builds and sends DNS update transactions; `DoDNSUpdateNegotiateGensec()` negotiates a Kerberos/GENSEC signing context for secure DNS updates; `get_my_ip_address()` discovers local non-loopback, non-link-local interface addresses.

Control flow: `DoDNSUpdate()` validates requested modes and address inputs, opens a TCP DNS connection, optionally sends a probe request, optionally sends an unsigned update, then optionally negotiates signed GSS-TSIG and sends a signed update. Sufficient flags allow early success after probe or unsigned update. Signed negotiation first tries normal server type and retries with a Windows 2000 DNS server type workaround. `get_my_ip_address()` loads configured interfaces and copies usable addresses into a malloced array.

State and persistence: updates remote DNS records. It does not persist local state, but callers may use discovered IPs. `get_my_ip_address()` allocates memory that callers must free with `SAFE_FREE()`.

Dependencies and integration points: depends on `../lib/addns/dns.h`, GENSEC/auth generic client setup, `utils/net_dns.h` flag definitions, interface loading helpers, and `struct cli_credentials`. Called by `net_ads_join_dns.c`.

Risks: DNS update mode is flag-driven; wrong combinations can silently skip desired phases or return invalid parameter. Unsigned update attempts can be sufficient unless caller clears the sufficient flag, so security expectations depend on flags. The removal path still passes address arguments through update request creation, so caller semantics for remove must match addns behavior. Interface discovery may return zero usable addresses even with network connectivity.

Test signals: invalid flag combinations; probe-sufficient success; unsigned-only and signed fallback paths; GENSEC negotiation failure and Windows 2000 retry; no-address validation; IPv4/IPv6 interface discovery excluding loopback/link-local; DNS response-code failure handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_dns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_dns.h -->
# sources/user-network-fs/samba/source3/utils/net_dns.h

Purpose: defines dynamic DNS update flags and declares the Kerberos-enabled DNS update API.

Important APIs and types: flags include `DNS_UPDATE_SIGNED`, `DNS_UPDATE_SIGNED_SUFFICIENT`, `DNS_UPDATE_UNSIGNED`, `DNS_UPDATE_UNSIGNED_SUFFICIENT`, `DNS_UPDATE_PROBE`, and `DNS_UPDATE_PROBE_SUFFICIENT`. Under `HAVE_KRB5`, declares `DoDNSUpdate()` with nameserver, domain, hostname, credentials, address list, flags, TTL, and removal mode.

Control flow: no runtime control flow; compile-time guard exposes declarations only when Kerberos headers are available.

State and persistence: none directly; the declared function mutates remote DNS.

Dependencies and integration points: includes addns DNS types and forward-declares `struct cli_credentials`. Used by `net_dns.c`, `net_ads_join_dns.c`, and `net_ads.c`.

Risks: callers must combine flags carefully because the header exposes low-level sequencing policy. The function takes mutable `char *pszServerName` even though it is treated as a server name input, which can encourage unnecessary mutable buffers.

Test signals: compile with and without `HAVE_KRB5`; API compatibility across callers; flag behavior coverage in `DoDNSUpdate()` tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_dns.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_dom.c -->
# sources/user-network-fs/samba/source3/utils/net_dom.c

Purpose: implements `net dom` commands for remote machine domain join, unjoin, and rename through the NetAPI layer, optionally followed by remote reboot.

Important APIs and functions: `net_dom()` initializes `libnetapi` and dispatches `join`, `unjoin`, and `renamecomputer`. Handlers call `NetJoinDomain()`, `NetUnjoinDomain()`, and `NetRenameMachineInDomain()`. Reboot paths use `net_make_ipc_connection_ex()` and `run_rpc_command()` against initshutdown or winreg RPC tables.

Control flow: each command parses `key=value` arguments (`domain`, `ou`, `account`, `password`, `newname`) and a `reboot` token, derives `server_name` from `c->opt_host`, performs the NetAPI operation, and if requested sets `c->opt_comment`, `c->opt_reboot`, and `c->opt_timeout` before trying shutdown RPC via initshutdown then winreg fallback.

State and persistence: mutates the remote machine/domain membership or machine name through NetAPI. Optional reboot changes remote system state. No local persistent state is written by this file.

Dependencies and integration points: depends on generated initshutdown/winreg NDR tables, `lib/netapi`, SMB IPC connection helpers, and shared `net_context` credentials/options. It is local transport from the CLI perspective but targets remote hosts.

Risks: passwords can be provided on the command line. `argc < 1` is the only basic requirement, so missing required key/value fields may reach NetAPI and fail less clearly. Remote reboot is disruptive and uses the same original arguments when invoking shutdown internals. Join with `--force` adds `NETSETUP_DOMAIN_JOIN_IF_JOINED`.

Test signals: remote join/unjoin/rename success and error strings; missing account/password/domain/newname values; `--force` rejoin behavior; reboot path with initshutdown success and winreg fallback; host selection through `-S`; NetAPI init failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_dom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_eventlog.c -->
# sources/user-network-fs/samba/source3/utils/net_eventlog.c

Purpose: implements local `net eventlog` import/export/dump utilities for Windows `.evt` files and Samba eventlog TDB storage.

Important APIs and functions: `net_eventlog()` dispatches `dump`, `import`, and `export`. `net_eventlog_dump()` loads an `.evt` file and NDR-prints `EVENTLOG_EVT_FILE`. `net_eventlog_import()` converts `.evt` records to `eventlog_Record_tdb` entries and pushes them into an eventlog TDB. `net_eventlog_export()` converts a TDB eventlog to `.evt` blob and saves it.

Control flow: dump/import load files with `file_load()`, parse headers/structures with NDR pull helpers, and handle parse errors. Import rejects wrapped eventlog files, opens the destination eventlog TDB, calculates record count from header numbers, converts records in a loop, and writes them. Export opens an eventlog TDB read-only/export mode, converts to a blob, then `file_save()`s the output.

State and persistence: import writes to eventlog TDB storage. Export writes a user-specified `.evt` file. Dump is read-only.

Dependencies and integration points: depends on `lib/eventlog/eventlog.h`, NDR generated eventlog parsers/printers, and util file helpers. Registered as a local transport command through `net_run_function()`.

Risks: import refuses wrapped logs, so some real `.evt` files cannot be imported. Record count arithmetic assumes header values and array content are consistent. Import may partially write records before a later conversion/write failure. File paths are caller controlled.

Test signals: dump valid/invalid `.evt`; import non-wrapped and wrapped files; verify record counts and TDB contents; export an eventlog TDB and re-dump it; file permission and missing-file errors; partial-write failure behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_eventlog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_file.c -->
# sources/user-network-fs/samba/source3/utils/net_file.c

Purpose: implements the generic `net file` command front end for listing, inspecting, and closing open files on a server, delegating protocol-specific work to RPC or RAP implementations.

Important APIs and functions: `net_file_usage()` prints syntax and common method/flag help. `net_file()` handles help/usage and selects `net_rpc_file()` or `net_rap_file()`.

Control flow: if no subcommand is supplied, usage is printed. `HELP` prints usage and succeeds. Otherwise `net_rpc_check(c, 0)` decides whether RPC is available; true dispatches to `net_rpc_file()`, false falls back to RAP.

State and persistence: this file itself has no persistence. Delegated close operations can close remote open files.

Dependencies and integration points: depends on common `net_context`, common help functions, and external RPC/RAP file command implementations.

Risks: protocol selection is implicit and depends on `net_rpc_check()` behavior and target capabilities. The local file has no validation beyond basic argc/help; delegated functions own command semantics.

Test signals: no-arg and HELP usage; RPC-capable target dispatch; RAP fallback target dispatch; close/info/list subcommands through both backends.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_g_lock.c -->
# sources/user-network-fs/samba/source3/utils/net_g_lock.c

Purpose: exposes Samba's `g_lock` distributed/local lock facility through `net g_lock` diagnostics and a command execution wrapper.

Important APIs and functions: `net_g_lock()` dispatches `do`, `locks`, `dump`, and `dumpall`. `net_g_lock_init()` creates tevent, messaging, and `g_lock_ctx`. `net_g_lock_do()` acquires a write lock and runs a shell command. Dump helpers print owners and lock data using `g_lock_dump()` and `g_lock_locks_read()`.

Control flow: diagnostic commands initialize independent event/messaging/lock contexts, read lock names or entries, print TDB keys and server IDs, and free contexts. `do` parses lock name, timeout, and command, initializes a lock context from `c->msg_ctx`, calls `g_lock_lock()` with write mode and timeout, runs `system(cmd)`, unlocks, and returns the command result.

State and persistence: `do` creates transient lock state in the g_lock backend and can mutate arbitrary system state through the shell command. `locks`, `dump`, and `dumpall` read lock tables.

Dependencies and integration points: depends on `g_lock.h`, `messages.h`, tevent, server ID formatting, util TDB dumping, and common `net_run_function()`.

Risks: `net_g_lock_do()` runs a caller-supplied shell command through `system()`, so quoting and injection are caller responsibility. It returns raw `system()` status, not normalized exit code. Timeout is parsed with `atoi()` and split as milliseconds into seconds/milliseconds. Unlock is called after `system()` but cannot run if the process is killed.

Test signals: acquire/release behavior with competing processes; timeout parse boundaries; command return status mapping; dump locks with read and write holders; unavailable messaging or g_lock context; shell quoting behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_g_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_group.c -->
# sources/user-network-fs/samba/source3/utils/net_group.c

Purpose: implements generic `net group` front-end behavior and usage text, selecting ADS group handling when available and RAP otherwise.

Important APIs and functions: `net_group_usage()` prints group subcommand syntax and common flags. `net_group()` handles no-arg/HELP and dispatches to `net_ads_group()` or `net_rap_group()`.

Control flow: no arguments produce usage. `HELP` prints usage and returns success. Otherwise `net_ads_check(c) == 0` means ADS is reachable, so it calls `net_ads_group()`; if not, it falls back to RAP. Unlike file dispatch, this front end does not choose RPC here.

State and persistence: no direct persistence; delegated ADS/RAP group commands can create, delete, or modify remote groups.

Dependencies and integration points: depends on `net_ads_check()` and `net_ads_group()` from `net_ads.c`, `net_rap_group()`, common help printers, and `net_context` options such as comments/container/local group flags.

Risks: transport auto-detection can route to ADS based on CLDAP reachability, which may surprise users expecting RAP. Usage advertises RPC operations even this dispatcher falls back to RAP when ADS is unavailable; other command routing may handle explicit methods.

Test signals: no-arg/HELP usage; ADS-reachable dispatch; ADS-unreachable RAP fallback; add/delete/list/member commands through selected backend; option text coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_group.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_groupmap.c -->
# sources/user-network-fs/samba/source3/utils/net_groupmap.c

Purpose: implements `net groupmap`, a local passdb-backed tool for mapping Windows/NT group SIDs to Unix groups and managing alias membership records.

Important APIs and functions: `net_groupmap()` dispatches `add`, `modify`, `delete`, `set`, `cleanup`, `addmem`, `delmem`, `listmem`, `memberships`, and `list`. Helpers include `get_sid_from_input()` and `print_map_entry()`. It uses passdb functions such as `pdb_getgrnam()`, `pdb_getgrsid()`, `pdb_enum_group_mapping()`, `pdb_add/update/delete_group_mapping_entry()`, `pdb_add_aliasmem()`, `pdb_enum_aliasmem()`, and `pdb_enum_alias_memberships()`.

Control flow: list parses `verbose`, `ntgroup=`, and `sid=` filters, resolves names/SIDs, and either prints one mapping or enumerates all. Add parses RID/SID, Unix group, NT group, comment, and type; validates Unix group, allocates or derives RID, composes SID if needed, fills default comment/name, and calls `add_initial_entry()`. Modify resolves an existing mapping by SID or NT group, applies type/comment/name/gid changes, and updates passdb. Delete resolves then removes. Set is a higher-level add-or-update command using global options (`-L`, `-D`, RID, comment, new NT name). Alias membership commands parse SIDs and add/delete/list memberships.

State and persistence: mutates local passdb group mapping database and alias membership records. `cleanup` deletes mappings outside the local SAM and BUILTIN SID namespaces and reports unmapped gids. List and memberships are read-only.

Dependencies and integration points: depends on Unix group lookup (`getgrnam()`, `nametogid()`, `gidtoname()`), passdb, domain SID helpers (`get_global_sam_sid()`, `sid_compose()`), SID parsing/formatting, and `net_context` option fields.

Risks: mapping operations are destructive and local-auth critical. `modify` rejects omitted `type=` because `sid_type` remains `SID_NAME_UNKNOWN`, even though usage suggests type is optional. RID allocation falls back to algorithmic gid-to-rid if backend cannot store RIDs. Cleanup can delete foreign mappings by design. Some functions allocate with NULL talloc contexts and rely on explicit frees.

Test signals: add with explicit RID and explicit SID; add with automatic RID on backends with/without `PDB_CAP_STORE_RIDS`; list single/all verbose; modify comment/name/gid/type including no-type case; delete by name and SID; set add/update with `-L`/`-D`; cleanup with foreign/local/builtin mappings; alias add/delete/list/memberships across SAM and BUILTIN domains.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_groupmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_help.c -->
# sources/user-network-fs/samba/source3/utils/net_help.c

Purpose: implements generic `net help` behavior for the top-level command table stored in `c->private_data`.

Important APIs and functions: `net_help()` is the public entry; `net_usage()` prints either command summaries or full usage text; `net_help_usage()` toggles full usage mode and delegates to `net_usage()`.

Control flow: `net_help()` with no args prints normal usage. If first arg is `help`, it sets `display_usage` and prints full usage for all commands. Otherwise it sets `display_usage` and invokes `net_run_function()` so the named command prints its detailed usage. `net_usage()` iterates a `struct functable` from `c->private_data` and prints descriptions or usage strings.

State and persistence: no persistence; mutates `c->display_usage` for the current command path and reads `c->private_data`.

Dependencies and integration points: depends on the global `net` dispatcher populating `net_context.private_data` with a valid functable. Uses `net_common_flags_usage()` from `net_help_common.c`.

Risks: assumes `c->private_data` is a valid, NULL-terminated `struct functable`. Full usage path returns `-1` from `net_usage()`, so help status semantics may not always be success except the special `help` subpath through `net_help_usage()` still returns that value.

Test signals: `net help`, `net help help`, `net help <command>`; invalid command; missing or malformed private functable in tests; translated usage strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_help.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_help_common.c -->
# sources/user-network-fs/samba/source3/utils/net_help_common.c

Purpose: centralizes common help text for transport methods, target selection, miscellaneous options, connection options, and credentials.

Important APIs and functions: `net_common_methods_usage()` prints ADS/RPC/RAP methods. `net_common_flags_usage()` prints common targets and options including server/IP/workgroup, debug/config/logging, name resolution/protocol/netbios/realm, and credential/Kerberos/client-protection options.

Control flow: both functions only emit translated text with `d_printf()`. Methods returns `0`; flags returns `-1`, matching historical usage helper behavior.

State and persistence: none.

Dependencies and integration points: called by command-specific usage functions such as `net_group_usage()`, `net_file_usage()`, search/DN/SID ADS usage, and top-level help.

Risks: because flags helper returns `-1`, callers that directly return it report usage as failure. Help text can drift from actual option parser behavior. The methods helper says methods are auto-detected, but individual commands differ in fallback order.

Test signals: help output includes all expected options; return-code expectations for callers; localization extraction; consistency with actual option parser.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_help_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_help_common.h -->
# sources/user-network-fs/samba/source3/utils/net_help_common.h

Purpose: declares shared common-help functions for `net` command modules.

Important APIs and types: declares `net_common_methods_usage()` and `net_common_flags_usage()`, both accepting `struct net_context *`, `argc`, and `argv`.

Control flow: no runtime logic; include guard `_NET_HELP_COMMON_H_` prevents duplicate declarations.

State and persistence: none.

Dependencies and integration points: used by command modules that print common help. Header comments document intent, parameters, and return values.

Risks: comments say nonzero on failure, but implementation intentionally returns `-1` from the flags helper after printing normal usage; callers should not treat that as an internal failure without context.

Test signals: compile include users; verify declarations match implementation; help callers include this header or receive declarations through common includes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_help_common.h -->
