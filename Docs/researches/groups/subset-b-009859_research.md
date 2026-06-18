# subset-b-009859 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_spoolss.c -->
# sources/user-network-fs/samba/source3/rpcclient/cmd_spoolss.c

Purpose: this is the large SPOOLSS command module for `rpcclient`. It registers printer, driver, form, job, notification, print-processor, monitor, printer-data, and per-machine-connection commands in `spoolss_commands[]`.

Important APIs, types, and functions: handlers use `struct rpc_pipe_client`, `struct dcerpc_binding_handle`, `struct policy_handle`, `WERROR`, `NTSTATUS`, generated `dcerpc_spoolss_*` calls, and higher-level `rpccli_spoolss_*` helpers. Key helpers are `RPCCLIENT_PRINTERNAME`, `cmd_spoolss_get_short_archi`, printer/driver/form/job display functions, `display_printer_data`, `display_reg_value`, `init_drv_info_3_members`, and `parse_setjob_command`. Exported command handlers include `enumprinters`, `openprinter`, `getprinter`, `setprinter`, `adddriver`, `enumdrivers`, `getdriver`, `addprinter`, `setdriver`, `deldriver`, `deldriverex`, `getdata`, `getdataex`, `setprinterdata`, `enumdata`, `enumdataex`, `enumkey`, `enumjobs`, `getjob`, `setjob`, `addform`, `setform`, `getform`, `deleteform`, `enumforms`, `rffpcnex`, `printercmp`, `enumprocs`, `enumprocdatatypes`, `enummonitors`, `createprinteric`, `playgdiscriptonprinteric`, `getcoreprinterdrivers`, and per-machine connection commands.

Control flow: almost every mutating or query command validates `argc`, composes a server-qualified printer path, opens a printer handle, performs one or more SPOOLSS RPCs, prints decoded output, and closes the handle in a shared cleanup path. Enumeration calls allocate level-specific unions and dispatch display logic by info level. Two-call "probe then fetch" flows handle insufficient-buffer APIs such as driver directories, forms, printer data, and per-machine connections. Driver commands iterate Samba's architecture table to try supported environments.

State and persistence: the file does not persist local state. It mutates remote spooler state: printer comments/names/drivers, driver installation/removal, forms, job control state, printer data registry values, notifications, and per-machine connections. Remote handles are short-lived except while a handler is executing.

Dependencies and integration: the module depends on generated SPOOLSS NDR stubs, `cli_spoolss`, printer initialization helpers, registry encoding helpers, security descriptor display/equality helpers, cmdline credentials, and SMB client connection APIs for `printercmp`. It is integrated by `rpcclient.c` through `extern struct cmd_set spoolss_commands[]` and by `wscript_build` through the `rpcclient` binary source and dependencies.

Risks: broad admin-capable operations can alter or remove remote printer configuration. Many numeric arguments use `atoi` or `sscanf` with limited validation. Some handlers assume argument presence after loose argc checks, and some output-only commands return success without detailed printing. Printer data parsing must match the advertised registry type; malformed blobs can reduce diagnostic value. `printercmp` opens a second SMB/RPC connection and only partially compares properties.

Test signals: run `rpcclient -c "help SPOOLSS"` and command-specific usage paths; test against a disposable Samba print server with success and permission-denied cases; verify handle cleanup with repeated commands; cover info levels 0,1,2,3,4,5,6,7,8 where accepted; verify two-call buffer paths and job/form mutation flows; regression-check that `setprinterdata` changes `change_id`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_spoolss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_spotlight.c -->
# sources/user-network-fs/samba/source3/rpcclient/cmd_spotlight.c

Purpose: this module adds MDSSVC Spotlight test commands to `rpcclient`: `fetch_properties` and `fetch_attributes`.

Important APIs, types, and functions: it uses generated `dcerpc_mdssvc_open`, `dcerpc_mdssvc_unknown1`, and `dcerpc_mdssvc_cmd`, plus Samba Spotlight helpers `dalloc_new`, `dalloc_add`, `dalloc_stradd`, `sl_pack_alloc`, `sl_unpack`, and `dalloc_dump`. It constructs `struct mdssvc_blob`, `policy_handle`, `sl_array_t`, and `sl_cnids_t`.

Control flow: both commands validate positional arguments, open an MDSSVC share context, call `unknown1` with local uid/gid, allocate a DALLOC request tree, pack it into a Spotlight blob, send `mdssvc_cmd`, unpack the response, and dump decoded content. `fetch_attributes` parses a CNID with `smb_strtoull`, requests `kMDItemPath`, and rejects empty responses.

State and persistence: local allocations are talloc/DALLOC scoped to the command. Remote state is a short-lived MDSSVC context handle; no persistent local state is written.

Dependencies and integration: depends on generated MDSSVC NDR, server-side mdssvc marshalling/dalloc headers, and `smb_strtox`. Registered in `spotlight_commands[]` and compiled into `rpcclient` by `wscript_build`.

Risks: several protocol constants are hard-coded and partly labeled unknown. The command is mostly diagnostic, so server behavior changes can break it without obvious compile failures. Large or malformed Spotlight blobs stress marshalling and dump output.

Test signals: validate usage messages, CNID parse failures, empty response handling, successful decode against an MDSSVC-enabled share, and memory-failure paths through allocation checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_spotlight.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_srvsvc.c -->
# sources/user-network-fs/samba/source3/rpcclient/cmd_srvsvc.c

Purpose: this module implements SRVSVC commands for server metadata, share management, sessions, files, disks, connections, name validation, and file security.

Important APIs, types, and functions: exported handlers call generated `dcerpc_srvsvc_*` functions for `NetSrvGetInfo`, `NetShareEnum`, `NetShareEnumAll`, `NetShareGetInfo`, `NetShareSetInfo`, `NetRemoteTOD`, `NetFileEnum`, `NetNameValidate`, `NetGetFileSecurity`, `NetSessDel`, `NetSessEnum`, `NetDiskEnum`, `NetConnEnum`, `NetShareAdd`, and `NetShareDel`. Display helpers decode server type flags and share info levels 1, 2, 502, and 1005.

Control flow: handlers parse optional info levels and resume handles, initialize the correct level-specific container, call the SRVSVC RPC, convert transport `NTSTATUS` to `WERROR`, then print selected results. Share set operations read existing info, mutate selected fields, write it back, and re-read for display.

State and persistence: most commands are read-only. `netsharesetinfo`, `netsharesetdfsflags`, `netshareadd`, `netsharedel`, and `netsessdel` mutate remote server state. No local persistence is maintained.

Dependencies and integration: depends on SRVSVC NDR, security descriptor display, string wrappers, and `rpcclient` command dispatch. The command table is `srvsvc_commands[]`.

Risks: a few usage checks are permissive enough that missing required arguments can still be dereferenced. Many info levels are accepted but not displayed. Share add/set/delete can disrupt live service if used against production.

Test signals: exercise share enumeration at levels 1, 2, 502, and 1005; validate resume-handle behavior; test add/set/delete on disposable shares; verify file security printing; check invalid info levels and missing arguments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_srvsvc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_unixinfo.c -->
# sources/user-network-fs/samba/source3/rpcclient/cmd_unixinfo.c

Purpose: this module exposes UNIXINFO RPC helpers in `rpcclient`: UID-to-SID conversion and passwd-style lookup by UID.

Important APIs, types, and functions: `cmd_unixinfo_uidtosid` calls `dcerpc_unixinfo_UidToSid` and formats `struct dom_sid` with `dom_sid_str_buf`; `cmd_unixinfo_getpwuid` calls `dcerpc_unixinfo_GetPWUid` and prints returned status, home directory, and shell. Results are `NTSTATUS`.

Control flow: each command requires exactly one UID argument, parses it with `atoi`, calls the generated RPC, separately checks transport status and server result, prints on success, and returns the meaningful status.

State and persistence: no local or remote mutation is performed. The server resolves identities from its configured Unix identity backend.

Dependencies and integration: depends on generated UNIXINFO NDR stubs, SID helpers, and `rpcclient.h`. Exported through `unixinfo_commands[]`.

Risks: `atoi` silently maps malformed or overflowing input to weak values. `cmd_unixinfo_getpwuid` contains a duplicated `if (!NT_STATUS_IS_OK(status))` check, making one branch unreachable in practice.

Test signals: test valid UID, nonexistent UID, malformed UID, permission failures, and output formatting for NULL or empty home/shell values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_unixinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_winreg.c -->
# sources/user-network-fs/samba/source3/rpcclient/cmd_winreg.c

Purpose: this module adds basic WINREG inspection commands for HKLM keys and values.

Important APIs, types, and functions: handlers use `dcerpc_winreg_OpenHKLM`, `OpenKey`, `EnumKey`, `EnumValue_r`, `QueryMultipleValues`, `QueryMultipleValues2`, and `CloseKey`. `pull_winreg_Data` decodes NDR union data, and `display_winreg_data` prints `REG_DWORD`, `REG_SZ`, `REG_BINARY`, and `REG_MULTI_SZ`.

Control flow: commands open HKLM, optionally open a subkey, perform one-shot or iterative queries, handle `WERR_MORE_DATA` by retrying with larger buffers, display decoded values, and close handles when applicable.

State and persistence: all exported commands are read-only. Remote registry handles are transient and local state is talloc-scoped.

Dependencies and integration: depends on WINREG NDR stubs and misc NDR definitions, and is registered via `winreg_commands[]`.

Risks: `winreg_enumkey` only calls index 0 and uses the supplied string as the output buffer name, so it is not a complete recursive enumerator. Buffer pointer arithmetic in query-multiple display relies on server-provided offsets and lengths being valid after NDR unmarshalling.

Test signals: enumerate root and subkey values, query multiple value types, trigger `WERR_MORE_DATA`, check close-handle paths, and verify malformed key/value names return clean errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_winreg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_witness.c -->
# sources/user-network-fs/samba/source3/rpcclient/cmd_witness.c

Purpose: this module provides Witness protocol commands for interface discovery, registration, unregistration, and asynchronous notifications.

Important APIs, types, and functions: handlers call `dcerpc_witness_GetInterfaceList`, `Register`, `RegisterEx`, `UnRegister`, and `AsyncNotify`. It uses `popt` for option parsing, `struct policy_handle` for context handles, `GUID_from_string`, and Witness notify unions. `use_only_one_rpc_pipe_hack` intentionally reuses one pipe for every Witness subcommand.

Control flow: list prints interface flags/state/address/version. Register commands parse version/net/ip/share/client/flags/timeout options and print a `handle_type:guid` token. Unregister and notify parse that token back into a policy handle. Async notify temporarily sets the binding timeout to `UINT32_MAX`, waits for response, then restores the old timeout.

State and persistence: server registration context is stateful and only meaningful on the same RPC connection. The module mutates command-table `rpc_pipe` pointers so all Witness commands share the current pipe.

Dependencies and integration: depends on generated Witness NDR and popt. Registered as `witness_commands[]` and compiled with `RPC_NDR_WITNESS`.

Risks: the pipe reuse hack is global to the command table and can surprise generic rpcclient cache logic. Notify can block indefinitely. The IP address info printer appears to test `WITNESS_IPADDR_ONLINE` for both Online and Offline labels, which may misreport offline state.

Test signals: list interfaces, register V1/V2 and RegisterEx, pass printed handles to notify/unregister in the same session, interrupt long notify waits, and test malformed handle strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_witness.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_wkssvc.c -->
# sources/user-network-fs/samba/source3/rpcclient/cmd_wkssvc.c

Purpose: this module exposes WKSSVC workstation commands for workstation info, join info, message sending, computer-name enumeration, and logged-on user enumeration.

Important APIs, types, and functions: handlers call generated `dcerpc_wkssvc_NetWkstaGetInfo`, `NetrGetJoinInformation`, `NetrMessageBufferSend`, `NetrEnumerateComputerNames`, and `NetWkstaEnumUsers`. It converts outbound message strings with `push_ucs2_talloc`.

Control flow: command handlers use `cli->desthost` as server name, parse optional levels/name type/message, call the RPC, and print selected returned fields. User enumeration prints level 0 names or level 1 domain-qualified names.

State and persistence: queries are read-only except `wkssvc_messagebuffersend`, which sends a remote message. No local persistence.

Dependencies and integration: depends on WKSSVC NDR and `rpcclient.h`, registered by `wkssvc_commands[]`.

Risks: several commands accept optional numeric arguments via `atoi`. `wkssvc_wkstagetinfo` does not print returned workstation info, so success is mostly visible through status. Computer-name enumeration appears to print `ctr->computer_name->string` in each loop instead of indexing a per-entry array.

Test signals: test info levels, join info output, message conversion, name type enumeration, user levels 0 and 1, and invalid/unsupported level returns.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/cmd_wkssvc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/rpcclient.c -->
# sources/user-network-fs/samba/source3/rpcclient/rpcclient.c

Purpose: this is the `rpcclient` program entry point and dispatcher. It parses command-line options, connects to SMB/RPC transports, registers all command modules, implements built-in commands, opens RPC pipes lazily, and invokes command handlers.

Important APIs, types, and functions: central types are `struct cmd_set`, internal `cmd_list`, `struct dcerpc_binding`, `struct cli_state`, and `struct cli_credentials`. Important functions include `completion_fn`, `next_command`, `binding_get_auth_info`, `cmd_help`, `cmd_listcommands`, auth commands (`sign`, `seal`, `packet`, `none`, `schannel`, `schannelsign`), `cmd_choose_transport`, `rpccli_ncalrpc_connect`, `do_cmd`, `process_cmd`, and `main`.

Control flow: `main` initializes Samba cmdline state, parses a binding or host, normalizes transport, opens an IPC$ SMB connection for NCACN_NP, builds the command-list from all module arrays, then either executes semicolon-separated `-c` commands or enters a readline loop. `process_cmd` tokenizes input with popt, finds a matching `cmd_set`, and calls `do_cmd`. `do_cmd` lazily opens the module pipe using noauth, SPNEGO/NTLM/KRB5, SCHANNEL, or NCALRPC as requested, sets timeout, dispatches by return type, prints errors, and frees per-command memory.

State and persistence: global state includes command list, timeout, messaging context, cached netlogon creds, default netlogon domain, and cached per-command RPC pipes. Auth and transport changes invalidate incompatible cached pipes.

Dependencies and integration: includes every command table by `extern`, relies on Samba cmdline, credentials, messaging, SMB client, DCERPC binding, readline, passdb, and netlogon credential helpers. Built into the `rpcclient` binary by `wscript_build`.

Risks: cached pipes make stateful behavior efficient but sensitive to auth/transport changes. SCHANNEL and `use_netlogon_creds` paths depend on local trust credentials. `completion_fn` has a cleanup bug that frees `matches[count]` inside a loop instead of `matches[i]` on allocation failure. `-c` result only reflects whether each command ended in an NT error, and later commands overwrite earlier result state.

Test signals: parse binding strings and plain hosts, run `-c` multi-command sequences, switch auth and transport mid-session, exercise NCACN_NP and NCALRPC, validate readline completion, check pipe reuse/invalidation, and run commands requiring netlogon credentials.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/rpcclient.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/rpcclient.h -->
# sources/user-network-fs/samba/source3/rpcclient/rpcclient.h

Purpose: this header defines the command handler contract shared by `rpcclient.c` and all command modules.

Important APIs, types, and functions: it includes `rpc_client/cli_pipe.h`, defines `RPC_RETURN_TYPE` with `RPC_RTYPE_NTSTATUS`, `RPC_RTYPE_WERROR`, and `RPC_RTYPE_BINDING`, and defines `struct cmd_set`. The structure holds command name, dispatch function pointers, NDR interface table, cached pipe pointer, help text, usage, and a `use_netlogon_creds` flag. It also exports `rpcclient_msg_ctx` and `rpcclient_netlogon_creds`.

Control flow: no executable control flow exists in the header, but `returntype` determines which function pointer `do_cmd` calls and whether a command needs a bound pipe or can mutate the binding itself.

State and persistence: the `rpc_pipe` field is mutable process-local cache state for each command entry. External globals expose shared messaging and netlogon credential contexts.

Dependencies and integration: every command module includes this file and populates arrays of `struct cmd_set`. `rpcclient.c` consumes those arrays to build its command list.

Risks: the structure has no compile-time guard ensuring the correct function pointer is set for the declared return type; invalid entries are caught at runtime. Shared mutable `rpc_pipe` fields can carry state across commands.

Test signals: build all command modules, run `help`, ensure invalid command entries are rejected, and verify binding-only commands work with `cli == NULL` pipe pointers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/rpcclient.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/wscript_build -->
# sources/user-network-fs/samba/source3/rpcclient/wscript_build

Purpose: this Waf build fragment defines the Samba3 `rpcclient` binary.

Important APIs, types, and functions: it calls `bld.SAMBA3_BINARY('rpcclient', source=..., deps=...)`. The source list contains `rpcclient.c` and every command module, including SPOOLSS, SRVSVC, WKSSVC, WINREG, WITNESS, Spotlight, and UNIXINFO.

Control flow: build-time only. Waf evaluates the script and compiles the listed C files into one binary with the listed dependency libraries.

State and persistence: no runtime state. It affects generated build outputs and link dependency closure.

Dependencies and integration: dependencies include command-line support, pdb, libsmb, smbconf, NDR libraries, RPC client libraries, SMBREADLINE, ADS, schannel, DCUTIL, interface-specific RPC NDR libs, mdssvc, and UNIXINFO.

Risks: adding a command source without its matching dependency can create link failures. Removing a source from this list silently removes commands from the binary even if the source still builds elsewhere.

Test signals: run the configured Waf build, inspect `rpcclient -c help`, and verify all command groups from the source list appear.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpcclient/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/count_80_col.pl -->
# sources/user-network-fs/samba/source3/script/count_80_col.pl

Purpose: tiny Perl style helper that counts lines longer than 80 characters in one file, ignoring `#define` lines.

Important APIs, types, and functions: uses Perl file IO, `length`, regex matching, and `$ARGV[0]`.

Control flow: open input, increment a counter for long non-define lines, close input, print a summary only when count is nonzero, and exit zero.

State and persistence: read-only; no files are written.

Dependencies and integration: requires Perl. It is likely used manually or by style checks.

Risks: no argument validation; a missing file dies. Perl `length` includes the newline, so effective visible width threshold is one character lower than it may appear.

Test signals: run on files with no long lines, long non-define lines, and long define lines.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/count_80_col.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/creategroup -->
# sources/user-network-fs/samba/source3/script/creategroup

Purpose: example shell script for Samba's `add group command`, designed to create groups for difficult NT group names.

Important APIs, types, and functions: calls `/usr/sbin/groupadd`, `dd`, `md5sum`, `cut`, `expr`, `getent`, and `grep`.

Control flow: attempt to create the requested group name. On failure, generate a random `nt-xxxxx` group name and retry up to 10 times. Finally print the numeric GID for the created group.

State and persistence: mutates the local system group database through `groupadd`.

Dependencies and integration: depends on system account tools and `/dev/urandom`. Intended for Samba configuration hooks, not as a general safe utility.

Risks: needs privilege, assumes GNU-ish tools, uses grep with an unescaped group name prefix, and can create random local groups if the requested name is invalid or already exists.

Test signals: test normal creation, invalid NT-style names, already-existing groups, exhausted retries, and GID output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/creategroup -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/fix_bool.pl -->
# sources/user-network-fs/samba/source3/script/fix_bool.pl

Purpose: Perl rewrite helper that replaces `True` with `true` and `False` with `false` in a target file.

Important APIs, types, and functions: opens input, writes `$ARGV[0].new`, applies regex substitutions once per line, then renames the temp file over the original.

Control flow: linear read-transform-write-rename.

State and persistence: modifies the target file in place via a sidecar `.new` file.

Dependencies and integration: requires Perl. It is a developer migration helper rather than runtime code.

Risks: substitutions are not global per line, are not token-aware, and can alter strings/comments or partial identifiers. Rename failure handling uses `die @_`, which is not the actual error variable.

Test signals: lines with multiple booleans, strings/comments, missing files, and rename failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/fix_bool.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/format_indent.sh -->
# sources/user-network-fs/samba/source3/script/format_indent.sh

Purpose: shell wrapper around GNU `indent` with Samba C formatting options.

Important APIs, types, and functions: invokes `indent -npro -kr -i8 -ts8 -sob -l80 -ss -ncs "$@"`.

Control flow: no branching; passes all arguments directly to `indent`.

State and persistence: modifies files according to `indent` behavior.

Dependencies and integration: requires an `indent` implementation compatible with these options.

Risks: can create broad formatting churn. Behavior depends on the installed `indent` version.

Test signals: run on a copied C file, check diff shape, and verify unsupported-option behavior on target platforms.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/format_indent.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/makeunicodecasemap.awk -->
# sources/user-network-fs/samba/source3/script/makeunicodecasemap.awk

Purpose: AWK generator for a 65,536-entry Unicode case/character-class map.

Important APIs, types, and functions: `reset_vals` initializes current output state; `print_val` emits a map entry using fields from semicolon-delimited Unicode data; `BEGIN` sets `FS=";"`; `END` fills remaining BMP code points.

Control flow: tracks expected code point `strval`. For each input row, it fills gaps with identity/no-flag entries, emits the current row with upper/lower mappings and flags for upper/lower/digit/xdigit/space, then advances. END fills to 0xffff.

State and persistence: writes generated C initializer lines to stdout; no files are written directly.

Dependencies and integration: expects UnicodeData-like input with category in `$3` and simple uppercase/lowercase mappings in `$13`/`$14`.

Risks: limited to BMP, assumes sorted input, and can loop unexpectedly if input ordering is wrong. Field-number assumptions must match the Unicode data version.

Test signals: feed a small sorted fixture with gaps, letters, digits, spaces, and final fill behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/makeunicodecasemap.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/mknissmbpasswd.sh -->
# sources/user-network-fs/samba/source3/script/mknissmbpasswd.sh

Purpose: imports `smbpasswd` rows from stdin into a NIS+ `smbpasswd` table.

Important APIs, types, and functions: uses shell `read`, `cut`, `nistbladm -a`, and `nisdefaults -d`.

Control flow: read rows until an empty line, skip comments, split colon-separated fields, and add a NIS+ entry with selected password/account fields.

State and persistence: writes records into the NIS+ table `smbpasswd.org_dir.$(nisdefaults -d)`.

Dependencies and integration: depends on NIS+ tooling and legacy smbpasswd format.

Risks: unquoted `echo $row` loses whitespace and glob-like content, empty lines terminate processing, and field extraction is repeated many times. Sensitive password hashes are passed on command lines.

Test signals: comments, blank lines, malformed rows, hashes containing unusual characters, and NIS+ command failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/mknissmbpasswd.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/mknissmbpwdtbl.sh -->
# sources/user-network-fs/samba/source3/script/mknissmbpwdtbl.sh

Purpose: creates the NIS+ `smbpasswd` table and related group/access setup.

Important APIs, types, and functions: calls `nistbladm -D ... -c -s : smbpasswd_tbl`, `nisgrpadm -c`, `nischgrp`, and `nisdefaults -d`.

Control flow: one table creation command defines columns and access rights, then creates a NIS+ group and changes table group ownership.

State and persistence: mutates NIS+ namespace schema and group ownership.

Dependencies and integration: legacy NIS+ admin tools and Samba smbpasswd table schema.

Risks: no error handling between commands; partial setup can remain after failure. It embeds sensitive column access policy and assumes NIS+ is available.

Test signals: run in isolated NIS+ test domain, verify table schema, access rights, group creation, and partial-failure behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/mknissmbpwdtbl.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/mksmbpasswd.sh -->
# sources/user-network-fs/samba/source3/script/mksmbpasswd.sh

Purpose: AWK-based converter from passwd-style colon records to placeholder `smbpasswd` records.

Important APIs, types, and functions: sets `FS=":"`, prints a header, and emits `name:uid:XXXXXXXXXXXXXXXX...` records with disabled-password markers.

Control flow: for each input line, output one smbpasswd-format line using fields 1, 3, and 5.

State and persistence: writes to stdout only.

Dependencies and integration: depends on awk and input compatible with `/etc/passwd` field layout.

Risks: no filtering for system users or malformed records; output contains placeholder hashes and disabled account flags that need downstream handling.

Test signals: passwd fixtures with normal users, empty GECOS, malformed rows, and comments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/mksmbpasswd.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/mksyms.awk -->
# sources/user-network-fs/samba/source3/script/mksyms.awk

Purpose: parses C header files and emits a linker version-script style export list.

Important APIs, types, and functions: AWK state `inheader` tracks multi-line prototypes; it prints `global:` entries for extern variables and function prototypes, then `local: *;`.

Control flow: skip static, typedef, and non-symbol-leading lines; handle simple `extern type name;`; detect one-line function prototypes; enter multiline mode after detecting an opening paren until a closing prototype line is seen.

State and persistence: writes generated version script to stdout. Tracks current filename for comments.

Dependencies and integration: used by `mksyms.sh` with sorted unique header inputs.

Risks: regex-based C parsing can miss complex declarations, macros, attributes, function pointers, or unusual formatting. It may export unintended names if prototypes are nonstandard.

Test signals: headers with extern variables, single-line prototypes, multiline prototypes, static/typedef skips, attributes, and function pointers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/mksyms.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/mksyms.sh -->
# sources/user-network-fs/samba/source3/script/mksyms.sh

Purpose: shell wrapper that runs `mksyms.awk` over header files and updates a symbol export file only when content changes.

Important APIs, types, and functions: sets `LANG`, `LC_ALL`, and `LC_COLLATE` to `C`; validates arguments; sorts and uniquifies header paths; runs awk to a temp file; uses `cmp -s`, `rm`, and `mv`.

Control flow: parse awk executable and output file, build sorted `proto_src`, generate temp output, compare with existing output, then either remove temp or replace the target.

State and persistence: writes or updates the requested symbol file and creates a temporary `.$$.tmp~` file during generation.

Dependencies and integration: depends on shell, awk, sort, uniq, cmp, and `mksyms.awk` in the same directory.

Risks: unquoted paths in `mkdir`, awk invocation, cmp, rm, and mv will break on spaces or shell metacharacters. Temp filename can collide if reused by stale processes.

Test signals: unchanged output path, changed output path, duplicate headers, missing awk, paths with spaces, and interrupted temp-file cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/mksyms.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/samba-log-parser -->
# sources/user-network-fs/samba/source3/script/samba-log-parser

Purpose: Python 3 diagnostic tool for parsing Samba and especially winbind trace logs by traceid, PID, timestamp, and flow lines.

Important APIs, types, and functions: uses `argparse`, `os.walk`, regexes, `defaultdict` import, and record tuples `(date, traceid, lines, filename)`. Main functions are `process_file_no_traceid`, `process_file`, `filter_traceids`, `filter_flow`, `filter_flowcompact`, `print_record_list`, `setup_parser`, and `main`.

Control flow: argument validation requires one of traceid, pid, breakdown, or merge mode. Files or directories are read into memory. `process_file` groups trace records by header and optionally derives traceids from a client PID. Filtering then either prints merged records, writes per-traceid `.full`, `.flow`, and `.flowcompact` files, or prints filtered flow/full output.

State and persistence: normal modes write to stdout. `--breakdown` creates files named `<traceid>.full`, `<traceid>.flow`, and `<traceid>.flowcompact` in the current directory.

Dependencies and integration: expects Samba non-syslog debug logs with high-resolution timestamps and optionally `winbind debug traceid = yes`.

Risks: reads complete files into memory, which is expensive for large logs. Directory processing order can affect intermediate PID-to-traceid decisions, mitigated by delayed filtering. Breakdown filenames are unsanitized traceid strings from logs/options. UnicodeDecodeError skips files.

Test signals: logs with traceid headers, no-traceid timestamp merge, PID-derived traceids, flow and flow-compact filtering, directory mode, Unicode decode failures, and breakdown file creation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/samba-log-parser -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/scancvslog.pl -->
# sources/user-network-fs/samba/source3/script/scancvslog.pl

Purpose: legacy Perl script for extracting CVS log entries after a given date and matching a branch tag.

Important APIs, types, and functions: requires `timelocal.pl`, maps month names to numbers, and defines `make_time`, `get_tag`, and `get_entry`.

Control flow: parse logfile, optional start time, and optional tag; repeatedly collect entries separated by long asterisk lines; normalize the entry date; convert to epoch; compare date and tag; print matching entries.

State and persistence: reads a CVS log and writes matching entries to stdout.

Dependencies and integration: depends on old Perl `timelocal.pl` and historical CVS log formatting.

Risks: uses `@ARGV[n]` scalar oddities, rejects missing tag unless it equals empty extraction result, and has fragile date normalization. The special `19100` year workaround is legacy and suspicious.

Test signals: entries with full and abbreviated month names, missing dates, tag filters, empty start time, and separator edge cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/scancvslog.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/smbaddshare -->
# sources/user-network-fs/samba/source3/script/smbaddshare

Purpose: example Samba selftest helper for the `add share command` configuration hook.

Important APIs, types, and functions: consumes config path, share name, path, comment, and max connections. Uses `$BINDIR/net --configfile=$CONF conf addshare` and `setparm`.

Control flow: add a share with `writeable=no` and `guest_ok=no`; if successful, set `max connections`; exit with the failing return code on error.

State and persistence: mutates Samba registry/configuration through `net conf`.

Dependencies and integration: requires `$BINDIR/net` and a writable Samba config backend. Intended mainly for selftest.

Risks: `$NETCONF` is expanded unquoted as a command prefix, so spaces in `$BINDIR` or config paths can break. Real deployments must review defaults before use.

Test signals: successful add, failed add, failed setparm, max connection value handling, and config paths with special characters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/smbaddshare -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/smbchangeshare -->
# sources/user-network-fs/samba/source3/script/smbchangeshare

Purpose: example Samba selftest helper for the `change share command` hook.

Important APIs, types, and functions: reads config, share name, path, comment, max connections, and CSC policy; calls `net conf setparm` for `path`, `comment`, `max connections`, and `csc policy`.

Control flow: sequentially set each parameter, checking the return code after every command and exiting immediately on failure.

State and persistence: mutates Samba share configuration.

Dependencies and integration: requires `$BINDIR/net` and writable `net conf` backend.

Risks: unquoted `$NETCONF` command prefix has path-splitting risk. Partial updates are possible because earlier parameter changes are not rolled back after a later failure.

Test signals: successful full update, each individual setparm failure, partial update behavior, and CSC policy validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/smbchangeshare -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/smbdeleteshare -->
# sources/user-network-fs/samba/source3/script/smbdeleteshare

Purpose: example Samba selftest helper for the `delete share command` hook.

Important APIs, types, and functions: reads config and share name, builds `$BINDIR/net --configfile=$CONF conf`, and runs `delshare`.

Control flow: execute `net conf delshare`, report and exit with the command return code on failure.

State and persistence: deletes a Samba share from the configured backend.

Dependencies and integration: requires `$BINDIR/net`; intended for selftest or carefully adapted deployments.

Risks: unquoted `$NETCONF` command prefix can break on spaces. It performs irreversible share removal without confirmation.

Test signals: successful deletion, nonexistent share, permission/config failures, and path quoting cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/smbdeleteshare -->
