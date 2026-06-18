# Research Group subset-b-009888

This grouped report covers the eight Samba `source3/utils` RPC utility files assigned to `subset-b-009888`. Each section is source-tree aligned and bounded for reconciliation into the corresponding per-file research artifact.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_rpc_conf.c -->
# sources/user-network-fs/samba/source3/utils/net_rpc_conf.c

## Purpose

`net_rpc_conf.c` implements `net rpc conf`, a remote management interface for Samba configuration stored in the registry backend. Its command surface reads, imports, creates, edits, and deletes share definitions under the fixed Winreg path `HKLM\Software\Samba\smbconf`, printing results in an smb.conf-like format. It is explicitly designed for local or remote RPC interaction with registry-backed configuration, not for editing the local text `smb.conf` directly.

## Important APIs, Types, and Functions

The file is built around Winreg RPC, `struct smbconf_service`, and Samba's `net_context` command framework. `rpc_conf_open_conf()` opens `HKLM` and the `Software\Samba\smbconf` key with a requested access mask. `rpc_conf_get_share()` enumerates values from a share subkey into `struct smbconf_service`, converting registry `includes` multi-string values back into repeated `include` parameters. `rpc_conf_set_share()` performs the inverse conversion, creating a share key and storing normal parameters with `dcerpc_winreg_set_sz()` while folding repeated `include` parameters into a single `includes` `REG_MULTI_SZ`. `rpc_conf_del_value()` opens a share subkey and deletes a named value, treating `WERR_FILE_NOT_FOUND` as non-fatal for delete operations.

The command internals are `rpc_conf_listshares_internal()`, `rpc_conf_list_internal()`, `rpc_conf_showshare_internal()`, `rpc_conf_addshare_internal()`, `rpc_conf_delshare_internal()`, `rpc_conf_drop_internal()`, `rpc_conf_import_internal()`, `rpc_conf_getparm_internal()`, `rpc_conf_setparm_internal()`, `rpc_conf_delparm_internal()`, and the `getincludes`/`setincludes`/`delincludes` variants. The exported `net_rpc_conf()` builds the `functable` used by `net_run_function()`, while each command wrapper calls `run_rpc_command()` with `ndr_table_winreg`.

## Control Flow

All mutating and read operations follow the same shape: validate `argc` and `c->display_usage`, open a Winreg pipe via `run_rpc_command()`, open the smbconf registry root, perform the specific key/value operation, translate `WERROR` to `NTSTATUS` on failure, and close policy handles before freeing the talloc stack frame. Listing first enumerates share subkeys, then optionally retrieves each share with `rpc_conf_get_share()` and prints it through `rpc_conf_print_shares()`. `addshare` parses a small positional grammar for `writeable=`, `guest_ok=`, and optional comment, creates a new key, rejects already existing shares, and stores `path`, `read only`, `guest ok`, and `comment`.

`import` reads a text file through `smbconf_init("file:<filename>")`, optionally limits to one service, prints the parsed services in test mode, otherwise drops the remote smbconf registry tree and rewrites it from the parsed `smbconf_service` records. `setparm` creates or opens a share key, deletes any existing value when opened, validates the value with `net_conf_param_valid()`, and writes a new `REG_SZ`.

## State and Persistence

Persistent state is entirely remote registry state below `HKLM\Software\Samba\smbconf`. `drop` deletes and recreates the whole root, `import` performs a destructive replace before setting shares, and the parameter/include commands mutate individual registry values. There is no local persistent state beyond the input file read by `import`. Talloc stack frames contain transient service arrays, registry value strings, and policy handles.

## Dependencies and Integration Points

This file depends on generated Winreg RPC stubs, `rpc_client/cli_winreg.h`, `lib/smbconf`, `net_conf_util`, `loadparm`, and the common `net` RPC runner. It integrates with Samba's command tree via `net_rpc_conf()` and with the registry smbconf backend used by Samba's configuration system.

## Risks

`rpc_conf_import_internal()` drops the full remote configuration before writing imported shares, so partial failures can leave the remote smbconf backend empty or incomplete. Several create calls request `REG_KEY_READ` while subsequently setting values through the returned handle, which depends on server-side behavior and may be fragile. The import test-mode branch prints `services[i]` even when importing a single `servicename`, where `services` remains `NULL`; that path is a concrete crash risk. Input parsing for `addshare` checks only the first value character after `writeable=` and `guest_ok=`, so extra trailing text is ignored. Delete operations intentionally suppress missing values, which is convenient but can hide typos.

## Test Signals

Useful tests are command-level RPC integration tests against a temporary registry backend: list empty/non-empty config, add/show/del share round trips, `setparm` validation failures, include multi-string round trips, and destructive `import --test` versus real import. Regression coverage should include single-service import in test mode, failure injection after `drop`, and case-insensitive share lookup in `rpc_conf_get_share()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_rpc_conf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_rpc_printer.c -->
# sources/user-network-fs/samba/source3/utils/net_rpc_printer.c

## Purpose

`net_rpc_printer.c` contains the implementation behind the `net rpc printer` subcommands registered from `net_rpc.c`: listing printers, listing drivers, publishing/unpublishing printer objects in Active Directory through spoolss, and migrating printer queues, drivers, forms, settings, and security descriptors from a remote print server to a destination server.

## Important APIs, Types, and Functions

The file mixes SMB file-copy helpers and Spoolss RPC wrappers. `net_copy_fileattr()` copies security descriptors, DOS attributes, and timestamps through `cli_ntcreate()`, `cli_query_secdesc()`, `cli_qfileinfo_basic()`, `cli_set_secdesc()`, and `cli_setfileinfo_ext()`. `net_copy_file()` copies file contents or creates directories over connected SMB shares, then delegates metadata preservation to `net_copy_fileattr()`. `net_copy_driverfile()`, `check_arch_dir()`, and `copy_print_driver_3()` handle print driver file layout under `print$\<architecture>\<version>\file`.

The `net_spoolss_*` wrappers normalize common spoolss calls: enumerate/open/get/set printers, set printer data, enumerate keys/data/forms/drivers, get driver info, and add drivers. Higher-level exported internals include `rpc_printer_list_internals()`, `rpc_printer_driver_list_internals()`, publish helpers, and the five migration functions: security, forms, drivers, printers, and settings.

## Control Flow

Listing and publishing use `get_printer_info()` to either enumerate all local/shared printers or open one named printer. Publishing opens each printer with `PRINTER_ALL_ACCESS`, fetches level 7 data, changes the action to publish/update/unpublish, and calls `SetPrinter`.

Migration functions first connect to the destination spoolss pipe via `connect_dst_pipe()`, enumerate source printers, and iterate over the selected printer set. Security migration opens matching source and destination printer handles, reads the source level 3 security descriptor, copies it into destination level 2 info, and calls `SetPrinter`. Forms migration enumerates source forms and adds only `SPOOLSS_FORM_PRINTER` forms on the destination. Driver migration opens source and destination `print$` shares, enumerates architecture table entries, fetches source driver level 3, copies each driver file to the destination architecture directory, calls `AddPrinterDriver`, and finally sets the destination printer's driver name. Printer migration creates missing destination queues from source `PRINTER_INFO_2` using `rpccli_spoolss_addprinterex()`. Settings migration copies devmode/selected level 2 attributes, republishes if needed, enumerates legacy printer data and subkey values, rewrites location-sensitive registry values such as port, UNC name, server name, and short server name, and writes them with `SetPrinterData` or `SetPrinterDataEx`.

## State and Persistence

Persistent state is remote print server state: printer queues, driver files under `print$`, forms, printer registry data, Active Directory publication state, and security descriptors. Local state is only transient talloc allocations, SMB file handles, and RPC policy handles. File copy operations can create destination files and directories and can partially populate `print$` before an RPC add-driver operation fails.

## Dependencies and Integration Points

The implementation depends on generated Spoolss RPC stubs, `rpc_client/cli_spoolss.h`, SMB client helpers from `libsmb`, `nt_printing.h`, registry value helpers, security descriptor utilities, `archi_table`, and command glue in `net_rpc.c`. It also uses `connect_dst_pipe()` and `connect_to_service()` from the broader net utility code to reach a destination server and its `print$` share.

## Risks

Migration is multi-step and not transactional; a failure can leave copied driver files, created forms, or queues without matching settings. Several paths abort the whole migration on one printer failure, while others continue on form add failures, so behavior is uneven. Driver file path parsing assumes `...\<short_arch>\<version>\<filename>` and does not robustly handle malformed dependent-file paths. `net_copy_fileattr()` closes handles explicitly and again in cleanup if `fnum_src` or `fnum_dst` remain nonzero. In settings migration, the inner `for (i=0; keylist && keylist[i] != NULL; i++)` reuses the outer printer loop variable, which can skip printers or terminate the outer loop incorrectly. The polling loop in `watch_service_state` equivalent does not exist here; spoolss operations generally rely on immediate RPC results.

## Test Signals

High-value tests are integration-style: enumerate printers/drivers against a known server, migrate a fixture printer queue to a disposable destination, verify copied `print$` files and driver registration, copy forms while ignoring built-ins, copy security descriptors, and compare printer data subkeys after settings migration. A focused regression test should exercise settings migration with more than one printer and at least one subkey to catch loop-index corruption.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_rpc_printer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_rpc_registry.c -->
# sources/user-network-fs/samba/source3/utils/net_rpc_registry.c

## Purpose

`net_rpc_registry.c` implements `net rpc registry`, a remote Winreg management command family plus local registry hive file utilities. It can enumerate, create, delete, get, set, save, export, import, dump, and copy registry data, bridging Samba's command framework, generated Winreg RPC bindings, `.reg` formatting/parsing, and local `regfio` hive files.

## Important APIs, Types, and Functions

`dcerpc_winreg_Connect()` maps hive IDs to the corresponding Winreg open call. `reg_hive_key()` parses strings such as `HKLM\Software\Samba` or `HKEY_LOCAL_MACHINE\...` into a hive constant and relative key path using `split_hive_key()`. `registry_openkey()` opens the hive and requested subkey. `registry_enumkeys()`, `registry_enumvalues()`, and `registry_enumvalues2()` query key metadata, allocate buffers sized from `QueryInfoKey`, and enumerate subkeys or values into either `struct registry_value` or `struct regval_blob` representations.

Command internals implement remote set/delete/get value, create/delete key, enumerate, save, get security descriptor, export, and import. Local file helpers `dump_values()`, `dump_registry_tree()`, and `write_registry_tree()` use `regfio` to inspect or clone registry hive files. `registry_export()` recursively writes remote registry data through `struct reg_format`. Import is callback-driven through `struct import_ctx` and `reg_parse_file()`, with callbacks creating/deleting keys and values through Winreg.

## Control Flow

Remote commands parse arguments in their wrapper or internal function, open a Winreg pipe with `run_rpc_command(..., &ndr_table_winreg, ...)`, open the target hive/key, perform the operation, print formatted results, close handles, and return an `NTSTATUS`. `getvalue` performs the standard two-step `QueryValue`: first ask for required buffer size, then allocate and query the actual data. `enumerate` prints subkeys followed by values. `save` asks the remote server to save a registry key to a server-side file. `export` recursively opens subkeys, formats values, and writes a local `.reg` style file. `import` parses a local `.reg` file and applies each create/delete/set operation remotely.

The local `dump` and `copy` commands do not use RPC: they open hive files through `regfio_open()`, traverse the in-file tree, print values, or write a new hive file with copied subkey and value containers.

## State and Persistence

Remote persistent state is the selected registry hive/key on the target server. Mutations include creating/deleting keys, setting/deleting values, importing `.reg` data, and server-side `SaveKey`. Local persistent state is created by `export` and local hive `copy`; `dump` is read-only. The import callback owns Winreg policy handles with talloc and closes them through the adapter.

## Dependencies and Integration Points

Dependencies include generated Winreg and security NDR, `net_registry_util` print helpers, `registry/regfio.h`, `registry/reg_format.h`, `registry/reg_import.h`, `util_reg`, `display_sec`, and Samba string conversion utilities. The file integrates with the top-level `net rpc registry` function table and with Samba's registry import/export infrastructure.

## Risks

`rpc_registry_setvalue_internal()` returns `NT_STATUS_OK` unconditionally after cleanup even when parsing or `registry_setvalue()` failed, which can hide errors from callers. The public usage advertises `multi_sz`, but setvalue implements only `dword` and `sz`. `import_delete_val()` checks `NT_STATUS` twice and never checks `WERROR` after `DeleteValue`, so remote delete failures can be missed. Some early returns skip closing already opened handles, for example after argument/type validation failure in setvalue. `registry_enumkeys()` and value enumeration set output counts to metadata counts even if enumeration stops early on `WERR_NO_MORE_ITEMS`. Local dump/copy traversals are recursive and can be expensive or fragile on malformed hive structures.

## Test Signals

Tests should cover hive parsing aliases, remote create/get/set/delete round trips for `REG_DWORD` and `REG_SZ`, raw versus formatted `getvalue`, recursive export/import of nested keys, security descriptor display, and local dump/copy with a fixture hive. Regression checks should assert non-OK return status on failed setvalue and deletevalue operations and verify advertised-but-unimplemented value types are reported consistently.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_rpc_registry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_rpc_rights.c -->
# sources/user-network-fs/samba/source3/utils/net_rpc_rights.c

## Purpose

`net_rpc_rights.c` implements user-rights management for `net rpc rights` and exposes the same operations inside `net rpc shell`. It lists available LSA privileges, lists privileges assigned to accounts, lists accounts with a specific privilege, and grants or revokes rights for a name or raw SID.

## Important APIs, Types, and Functions

The file is centered on LSA RPC. `sid_to_name()` opens an LSA policy and calls `rpccli_lsa_lookup_sids()` for display. `name_to_sid()` accepts raw SID strings via `dom_sid_parse()` or resolves names with `rpccli_lsa_lookup_names()`. `enum_privileges()` calls `dcerpc_lsa_EnumPrivs()` and `LookupPrivDisplayName` to show available rights with descriptions. `enum_privileges_for_user()` and `check_privilege_for_user()` call `EnumAccountRights`; `enum_accounts_for_privilege()` and `enum_privileges_for_accounts()` enumerate account SIDs and join them with right membership.

`rpc_rights_list_internal()`, `rpc_rights_grant_internal()`, and `rpc_rights_revoke_internal()` implement the command behavior. The shell adapters `rpc_sh_rights_list()`, `rpc_sh_rights_grant()`, and `rpc_sh_rights_revoke()` reuse the same internals with the active shell context. `net_rpc_rights_cmds()` returns the nested shell command table.

## Control Flow

The standalone wrappers validate display-usage mode and call `run_rpc_command()` with `ndr_table_lsarpc`. Listing opens a policy once, then dispatches based on the first argument: no arguments or `privileges` without names lists all available privileges; `privileges <right...>` lists accounts that have each right; `accounts` without names lists every privileged SID and its rights; `accounts <name|SID...>` lists rights for each account; a single legacy argument is treated as an account name. Grant and revoke resolve the target SID, open an LSA policy with fallback support and maximum access, build an `lsa_RightSet` from the remaining arguments, then call `AddAccountRights` or `RemoveAccountRights`.

## State and Persistence

The persistent state is the target domain/server LSA account-right assignment database. Grant and revoke mutate rights for the resolved SID. Listing commands are read-only. Transient state includes policy handles, SID/name arrays, `lsa_RightSet` arrays, and talloc-backed display strings.

## Dependencies and Integration Points

This file depends on generated LSA RPC stubs, `rpc_client/cli_lsarpc.h`, `init_lsa.h`, security SID utilities, and Samba's command and shell frameworks. It integrates both as a standalone `net rpc rights` command and as the `rights` subtree in `net_rpc_shell.c`.

## Risks

Most operations request `SEC_FLAG_MAXIMUM_ALLOWED`, so failures depend heavily on remote privilege and policy configuration. `enum_accounts_for_privilege()` enumerates all accounts and then calls `EnumAccountRights` for each, which can be expensive on large domains. List mode often continues after privilege lookup errors and returns the last status, which may not reflect partial failures clearly. Grant/revoke accept arbitrary right strings and rely on server-side validation. Some close calls run even when policy open failed, though invalid handles are usually tolerated by Samba helpers.

## Test Signals

Useful tests include raw SID parsing, name resolution failure mapping, listing all privileges on a known server, granting and revoking a test privilege to a disposable account, shell command reuse, and behavior when the caller lacks rights. A scale test for `rights list privileges <right>` should cover domains with many account SIDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_rpc_rights.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_rpc_samsync.c -->
# sources/user-network-fs/samba/source3/utils/net_rpc_samsync.c

## Purpose

`net_rpc_samsync.c` implements the `net rpc vampire` passdb and keytab paths that use Active Directory DRS replication to pull account data from a remote domain controller. The file is a thin command adapter around `libnet_dssync`, adding domain checks, option propagation, and command usage output.

## Important APIs, Types, and Functions

`rpc_vampire_usage()` prints the historical command usage. `rpc_vampire_ds_internals()` initializes a `struct dssync_context`, verifies the remote domain SID matches the local global SAM SID, sets `ctx->cli`, `ctx->domain_name`, and `ctx->ops = &libnet_dssync_passdb_ops`, and calls `libnet_dssync()`. `rpc_vampire_passdb()` creates an IPC connection, scans the DC, rejects non-AD DCs, rejects AD passdb import unless `--force` is set, and runs the DRSUAPI command with sealing and TCP. `rpc_vampire_keytab_ds_internals()` configures `libnet_dssync_keytab_ops`, output filename, optional object DN list, full-replication and cleanup options, and optional single-object replication. `rpc_vampire_keytab()` performs the same IPC/DC scan and runs DRSUAPI.

## Control Flow

Both exported commands first validate usage, open an IPC connection with `net_make_ipc_connection()`, and inspect the remote DC with `net_scan_dc()`. They require Active Directory because the actual synchronization path is DRSUAPI-based. The passdb path additionally enforces a safety gate: without `--force`, it prints guidance instead of importing from AD. Once the command reaches the RPC runner, the internal function initializes a dssync context, attaches the active pipe and chosen operation vtable, calls `libnet_dssync()`, prints any error or result messages, frees the context, and returns the dssync status.

## State and Persistence

Persistent effects are delegated to `libnet_dssync` operation tables. The passdb path writes account data to Samba's configured local passdb. The keytab path writes or updates the specified Kerberos keytab file, with options for full replication, cleaning old entries, and single-object replication. This file itself stores no persistent state.

## Dependencies and Integration Points

Dependencies include DRSUAPI and Netlogon NDR headers, `libnet/libnet_dssync.h`, machine SID accessors, and the common `net` connection/DC discovery helpers. It integrates with the broader `net rpc vampire` command family rather than registering a local function table in this file.

## Risks

This code intentionally performs sensitive credential/account replication. The passdb domain SID check prevents importing accounts from a mismatched remote domain, but the keytab path does not perform the same local SID compatibility check because it writes keys rather than passdb records. `rpc_vampire_passdb()` has early `return -1` paths after creating an IPC connection and scanning the DC without local cleanup in this file. Most correctness and security risk resides in the selected `libnet_dssync_*_ops` implementations and transport sealing. Operator misuse is a major risk, especially with `--force`, full replication, cleanup of old keytab entries, or single-object filters.

## Test Signals

Test signals include usage validation, non-AD rejection, AD passdb refusal without `--force`, domain SID mismatch handling, keytab filename requirement, propagation of `--force-full-repl`, `--clean-old-entries`, and single-object options, plus mocked `libnet_dssync` success/error/result message handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_rpc_samsync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_rpc_service.c -->
# sources/user-network-fs/samba/source3/utils/net_rpc_service.c

## Purpose

`net_rpc_service.c` implements `net rpc service`, a Service Control Manager client for listing, querying, starting, stopping, pausing, resuming, creating, and deleting remote Win32 services over SVCCTL RPC.

## Important APIs, Types, and Functions

`struct svc_state_msg` and `state_msg_table` map SVCCTL state constants to localized display strings. `svc_status_string()` returns a talloc-backed state string. `open_scm()` wraps `OpenSCManagerW`; `open_service()` wraps `OpenServiceW`. `query_service_state()`, `watch_service_state()`, and `control_service()` provide common state query/control/poll behavior. Command internals implement list, status, stop, pause, resume, start, delete, and create. The exported `net_rpc_service()` registers these commands with `net_run_function()`.

## Control Flow

Each wrapper handles display-usage mode and then calls `run_rpc_command()` with `ndr_table_svcctl`. `list` opens SCM with enumerate rights, calls `EnumServicesStatusW` first with a zero-size buffer, reallocates on `WERR_MORE_DATA`, unmarshals the returned array with `ndr_pull_ENUM_SERVICE_STATUSW_array()`, and prints service/display names. `status` opens SCM and a service handle, queries current status, then queries configuration, retrying with the returned buffer size on `WERR_INSUFFICIENT_BUFFER`.

`stop`, `pause`, and `resume` share `control_service()`, which opens the service, sends the control code, polls for the desired final state, and prints the resulting state. `start` opens the service with start access, calls `StartServiceW`, polls for `SVCCTL_RUNNING`, and reports success or failure. `delete` opens with `SERVICE_ALL_ACCESS` and calls `DeleteService`; `create` opens SCM with create-service rights and calls `CreateServiceW` with a demand-start own-process service using the provided binary path.

## State and Persistence

Persistent state is remote SCM/service state: service runtime state, service records, and service configuration created or deleted by commands. The code does not persist local state. It keeps transient policy handles and NDR buffers under the per-command talloc context.

## Dependencies and Integration Points

The file depends on generated SVCCTL NDR/client stubs, common `net` RPC runners, and Samba string wrappers. It integrates as the `service` subtree under `net rpc` and uses `pipe_hnd->srv_name_slash` as the remote SCM server name.

## Risks

Several operations open SCM with `SC_RIGHT_MGR_ENUMERATE_SERVICE` even when subsequent service operations require service-specific rights; this may work because service rights are requested later, but can fail on stricter servers. `watch_service_state()` sleeps only `usleep(100)` per iteration and caps at 30 polls, making the total wait extremely short for real service transitions. Usage errors often return `NT_STATUS_OK`, which can make invalid invocations look successful to scripts. `list` manually unmarshals a buffer returned by the RPC stub, so changes in stub behavior could break parsing. Create uses fixed service type, start type, and no credentials/dependencies, limiting functionality.

## Test Signals

Tests should cover service listing with `WERR_MORE_DATA`, status config retry on insufficient buffer, start/stop/pause/resume state polling, create/delete of a disposable service, permission-denied propagation, invalid argument returns, and slow service transitions that exceed the current poll window.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_rpc_service.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_rpc_sh_acct.c -->
# sources/user-network-fs/samba/source3/utils/net_rpc_sh_acct.c

## Purpose

`net_rpc_sh_acct.c` implements the `account` subtree for `net rpc shell`. It shows and modifies domain account policy settings such as password length/history/age and account lockout thresholds/windows through SAMR RPC.

## Important APIs, Types, and Functions

The central helper is `rpc_sh_acct_do()`, which opens a SAMR connect handle, opens the shell context's domain SID, queries domain information levels 1, 3, and 12, calls a supplied callback, and optionally writes back one modified info level with `samr_SetDomainInfo`. Callback functions include `account_show()`, `account_set_badpw()`, `account_set_lockduration()`, `account_set_resetduration()`, `account_set_minpwage()`, `account_set_maxpwage()`, `account_set_minpwlen()`, and `account_set_pwhistlen()`. Each RPC-facing wrapper passes the appropriate callback to `rpc_sh_acct_do()`. `net_rpc_acct_cmds()` returns the shell command table.

## Control Flow

Shell dispatch in `net_rpc_shell.c` opens the SAMR pipe and invokes one of these command handlers. `rpc_sh_acct_do()` always reads all three domain info levels before invoking the callback, so show and set operations have the same read prelude. A callback validates its argument count, prints usage or current/changed values, mutates one of the provided info structures, and returns `0` for no save, a positive SAMR info level to save, or a negative value for usage/no-save. The helper switches on that returned level and writes only level 1, 3, or 12.

## State and Persistence

Read-only `show` prints account policy state from SAMR. Set commands persist changes in the remote domain policy database: password policy fields are stored in level 1; lockout threshold, duration, and reset window are stored in level 12. Level 3 is read for display of force-logoff behavior but this file does not provide a setter for it.

## Dependencies and Integration Points

Dependencies include SAMR generated client stubs, Samba time conversion helpers, domain SID data from `struct rpc_sh_ctx`, and the interactive shell command model. The file is not a standalone `net rpc` command; it is installed as `account` by `net_rpc_shell.c`.

## Risks

Numeric parsing uses `atoi()` with no validation for non-numeric text, overflow, negative values, or policy range constraints. Time setters use absolute NT time conversion for durations, which deserves careful validation against SAMR's expected signed interval semantics. `rpc_sh_acct_do()` reads all levels even when a setter needs only one, increasing failure surface. Usage callback failures return negative values that the helper treats as "do not save" but still returns the prior SAMR read status, so command-line error reporting can be ambiguous. The display for "Disconnect users when logon hours expire" depends on interpreting zero force-logoff time and should be checked against domain semantics.

## Test Signals

Tests should cover shell usage errors, valid setters for each command, invalid numeric input behavior, no-write behavior for `show`, correct `SetDomainInfo` level selection, permissions failure, and round-trip display after setting lockout and password policy values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_rpc_sh_acct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_rpc_shell.c -->
# sources/user-network-fs/samba/source3/utils/net_rpc_shell.c

## Purpose

`net_rpc_shell.c` implements an interactive shell around selected `net rpc` subcommands. It maintains hierarchical command context, opens the needed RPC pipe for each leaf command, provides readline completion for top-level commands in the current context, and exposes `info`, `rights`, `share`, `user`, and `account` command trees.

## Important APIs, Types, and Functions

`rpc_sh_info()` delegates to `rpc_info_internals()` using the current shell context. The global `this_ctx` tracks the active context for prompt and completion. `completion_fn()` completes command names at the beginning of a line. `net_sh_run()` creates a per-command talloc context, opens an unauthenticated RPC pipe with `cli_rpc_pipe_open_noauth()` using the leaf command's NDR table, runs the leaf callback, then frees the pipe and memory. `net_sh_process()` implements command parsing, context descent, `..`, `help`, and `exit` behavior. `sh_cmds` defines the root shell commands. `net_rpc_shell()` creates the IPC connection, discovers the remote domain SID/name, then runs the readline loop.

## Control Flow

`net_rpc_shell()` rejects arguments, initializes libnetapi, creates an IPC connection, builds the root `rpc_sh_ctx`, calls `net_get_remote_domain_sid()`, sets `this_ctx`, and enters a prompt loop. Each line is parsed with `poptParseArgvString()`. `net_sh_process()` first handles empty input, context-up navigation, exit aliases, and help. It then matches the first token against the current context's command table. For subtree commands, it creates a child context with a longer `whoami`, obtains a subtree command table, and either descends interactively or recursively processes the remaining tokens. For leaf commands, it calls `net_sh_run()` and reports non-OK status.

## State and Persistence

Shell state is an in-memory tree of `rpc_sh_ctx` objects holding the active SMB connection, prompt path, current command name, parent pointer, domain SID/name, and command table. Persistent remote state changes are performed only by leaf commands in other files, such as rights, share, user, and account operations. The shell itself only maintains the IPC connection until exit.

## Dependencies and Integration Points

Dependencies include SMB readline, popt argument parsing, libnetapi initialization, SMB client connection helpers, RPC pipe helpers, SAMR/LSA command subtrees, SID formatting, and the command providers `net_rpc_rights_cmds()`, `net_rpc_share_cmds()`, `net_rpc_user_cmds()`, and `net_rpc_acct_cmds()`.

## Risks

`this_ctx` is global mutable state, so the shell is inherently single-session and not reentrant. `net_sh_run()` leaks its `mem_ctx` if `cli_rpc_pipe_open_noauth()` fails because it returns before freeing it. The shell opens RPC pipes with `cli_rpc_pipe_open_noauth()`, relying on the existing IPC session's authentication context; this is intentional but worth validating for security assumptions. `poptParseArgvString()` allocations for `argv` are not explicitly freed in the loop. Returning `false` from parse errors maps to `0`/`false` from a function declared `int`, which is harmless but inconsistent. Completion only covers first-token command names and not nested arguments.

## Test Signals

Tests should cover interactive and one-line subtree dispatch, `help`, `..`, exit aliases, unknown command recovery, command status reporting, prompt updates, domain SID discovery failure, RPC pipe open failure cleanup, and command completion for unique and multiple prefixes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_rpc_shell.c -->
