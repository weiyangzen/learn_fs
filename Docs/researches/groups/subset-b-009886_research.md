# Research: subset-b-009886

Grouped research for Samba `source3/utils` net command files. Each section is source-tree aligned and bounded by reconciliation markers for per-file extraction.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_idmap.c -->
# sources/user-network-fs/samba/source3/utils/net_idmap.c

## Purpose
This file implements the local `net idmap` command family for inspecting and mutating Samba ID mapping databases. It supports classic `tdb`/`tdb2` idmap databases and selected `autorid` database operations, plus LDAP/rfc2307 idmap secret storage.

## Important APIs, Types, And Control Flow
The command entrypoint is `net_idmap()`, which dispatches `dump`, `restore`, `get`, `set`, `delete`, and `check` through `net_run_function`. `enum idmap_dump_backend` and `struct net_idmap_ctx` track whether the active database is classic TDB or autorid. `net_idmap_dbfile()` chooses a database path from `--db`, `lp_idmap_default_backend()`, `state_path()`, or `lp_private_dir()`. Dump traversal uses `net_idmap_dump_one_tdb_entry()` or `net_idmap_dump_one_autorid_entry()`. Restore parses lines such as `UID n SID`, `GID n SID`, `USER HWM`, and `GROUP HWM` and writes reciprocal mappings with `net_idmap_store_id_mapping()`. Delete paths include bidirectional mapping deletion with optional force and autorid range deletion by range number, SID/index, or all domain ranges. Autorid get/set commands use the `idmap_autorid_*` helper API. `net_idmap_check()` translates global CLI flags into `struct check_options` and calls `net_idmap_check_db()`.

## State And Persistence
The file reads and writes persistent TDB databases: `winbindd_idmap.tdb`, `idmap2.tdb`, or `autorid.tdb`, unless `--db` overrides the path. Restore and delete operations use transactions or `dbwrap_trans_do()` for atomicity. Autorid write operations initialize/open the autorid database through `idmap_autorid_db_init()`. `net_idmap_secret()` writes credentials into Samba secrets storage under an uppercased `IDMAP_<backend>_<domain>` key.

## Dependencies And Integration Points
It depends on Samba configuration, dbwrap/TDB, secrets storage, idmap core types, `idmap_autorid_tdb.h`, SID/security helpers, `net_idmap_check.h`, and `smb_strtox`. It integrates into the broader `net` CLI through `net_proto.h` and shares global option fields on `struct net_context`.

## Risks And Test Signals
Risk centers on destructive local database edits, backend gating, and textual restore parsing. `parse_uint32()` accepts values with possible crop to `uint32_t`. Restore line buffers are fixed size and invalid lines are ignored rather than fatal. Non-TDB backends are mostly rejected, but `--db` still leaves backend context defaulting to TDB. Test with TDB dumps/restores, malformed restore lines, reciprocal mapping deletion with and without `-f`, autorid range get/set/delete/config operations, unsupported backends, and dry/auto idmap check modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_idmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_idmap_check.c -->
# sources/user-network-fs/samba/source3/utils/net_idmap_check.c

## Purpose
This file implements `net idmap check`, a consistency checker and optional repair tool for classic idmap TDB databases. It validates key/value formats, reciprocal SID-to-ID mappings, database version, and high-water marks, then optionally commits a generated diff.

## Important APIs, Types, And Control Flow
The exported API is `net_idmap_check_db()`. Internal `enum DT` classifies records as SID, UID, GID, HWM, version, sequence, or invalid. `struct record` stores parsed key/value data and extracted SID or numeric ID. `struct check_actions` encodes interactive prompts, automatic actions, defaults, and verbose formatting. `struct check_ctx` holds the input db, in-memory diff db, options, counters, and computed UID/GID HWMs. `parse_record()` recognizes NUL-terminated `S-*`, `UID n`, `GID n`, `USER HWM`, `GROUP HWM`, `IDMAP_VERSION`, and `__db_sequence_number__` records. `traverse_check()` validates each record, detects missing or mismatched reverse links, updates HWM targets, and records diff operations through `add_record()`/`del_record()`. `check_version()` and `check_hwm()` add repair diffs for missing/wrong metadata. `check_commit()` lists or commits diffs through `traverse_commit()`.

## State And Persistence
Input data is read from a dbwrap TDB database. Proposed repairs are staged in a private in-memory rbt db as `TDB_DATA_diff` records containing old and new values. With `--lock`, the input database is opened writable and held in a transaction across check and commit. Without lock, checking is read-only first and the database is reopened writable only for commit. `--test` cancels the write transaction after exercising commit logic.

## Dependencies And Integration Points
The checker depends on dbwrap, dbwrap_rbt, TDB utility helpers, SID parsing, command-line interaction helpers, string quoting/parsing helpers (`cbuf`, `srprs`), and `struct check_options` from `net_idmap_check.h`. It is called only from `net_idmap.c`.

## Risks And Test Signals
Interactive mode requires a TTY unless `--auto` is used. Automatic repair deletes invalid records and fixes missing reverse links; with `--force`, it can commit after concurrent-change warnings. `unpack_diff()` asserts exact packed sizes, so corrupt diff records would abort. HWM repair computes max seen ID plus one, which should be verified against allocation semantics. Test corrupt non-NUL keys, one-way mappings, mismatched reverse mappings, missing/wrong version, low/missing HWMs, concurrent modification before commit, `--repair`, `--auto`, `--force`, `--test`, and `--lock`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_idmap_check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_idmap_check.h -->
# sources/user-network-fs/samba/source3/utils/net_idmap_check.h

## Purpose
This header defines the small public contract for the idmap database checker used by `net idmap check`.

## Important APIs, Types, And Control Flow
It forward-declares `struct net_context`, defines `struct check_options`, and declares `int net_idmap_check_db(const char *db, const struct check_options *opts)`. The options control dry-run behavior, verbosity, transaction locking, automatic prompt answers, forced repair/commit behavior, and whether repair mode is enabled.

## State And Persistence
The header itself stores no state. Its option fields control whether `net_idmap_check.c` opens the target TDB read-only or writable, stages and commits repairs, or cancels transactions in test mode.

## Dependencies And Integration Points
It includes only `<stdbool.h>` and is consumed by `net_idmap.c` and implemented by `net_idmap_check.c`. It intentionally exposes no checker internals such as record parsing or diff storage.

## Risks And Test Signals
The type name `struct check_options` is generic and duplicated by the registry checker header, so callers must avoid including both incompatible headers in one translation unit. Test signals are compile coverage for the declaration and option mapping tests from `net_idmap.c` flags into the checker.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_idmap_check.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_join.c -->
# sources/user-network-fs/samba/source3/utils/net_join.c

## Purpose
This file implements the generic `net join` command. It chooses between Active Directory join and RPC join behavior and provides usage text.

## Important APIs, Types, And Control Flow
`net_join_usage()` prints valid methods and common flags. `net_join()` handles `HELP`, warns about member options via `net_warn_member_options()`, probes ADS suitability with `net_ads_check_our_domain()`, tries `net_ads_join()`, and falls back to `net_rpc_join()` when ADS probing or joining fails.

## State And Persistence
This file does not directly persist data, but the delegated ADS or RPC join modifies domain membership state, secrets, and machine-account configuration. It forwards the same arguments and `struct net_context` to the selected implementation.

## Dependencies And Integration Points
It depends on `utils/net.h` and externally implemented ADS/RPC join functions declared in `net_proto.h`. It is the user-facing auto-detection layer for `net ads join` versus `net rpc join`.

## Risks And Test Signals
The fallback path can mask ADS-specific failures by attempting RPC after an ADS join error. Tests should verify `HELP`, ADS-success short-circuit, ADS-failure fallback messaging, RPC-only behavior when ADS domain check fails, and option forwarding to both join backends.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_join.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_lookup.c -->
# sources/user-network-fs/samba/source3/utils/net_lookup.c

## Purpose
This file implements `net lookup`, a resolver-oriented command family for NetBIOS names, LDAP/DC/KDC discovery, master browser lookup, SID/name conversion, and `DsGetDcName` diagnostics.

## Important APIs, Types, And Control Flow
`net_lookup()` dispatches subcommands `HOST`, `LDAP`, `DC`, `PDC`, `MASTER`, `KDC`, `NAME`, `SID`, and `DSGETDCNAME`, defaulting unknown first words to host lookup for compatibility with `name#type` syntax. `net_lookup_host()` parses optional NetBIOS type suffixes and calls `resolve_name()`. LDAP lookup, when ADS is available, queries DNS SRV records with sitename support and falls back through PDC discovery. DC/PDC/master lookup use `get_pdc_ip()`, `get_sorted_dc_list()`, and `find_master_ip()`. KDC lookup initializes a Kerberos context and prints realm KDCs. SID/name commands call `lookup_name()` and `lookup_sid()`. `net_lookup_dsgetdcname()` calls `dsgetdcname()` and NDR-prints the returned `netr_DsRGetDCNameInfo`.

## State And Persistence
This file performs network and cache lookups but does not write persistent state. It may read Samba configuration, site-name cache, DNS, NetBIOS browse state, passdb/name-service data, and message context state for `dsgetdcname`.

## Dependencies And Integration Points
Dependencies include namequery, ADS DNS SRV helpers, site-name cache, Kerberos support, security/SID helpers, passdb lookup, generated Netlogon NDR types, and dsgetdcname. Feature guards return errors when ADS or Kerberos support is not compiled in.

## Risks And Test Signals
`net_lookup_host()` mutates the supplied argument string at `#`, so argv mutability assumptions matter. LDAP fallback recomputes `domain` from PDC DNS name but reuses the original DNS query string, which is worth regression coverage. `dsgetdcname` requires `c->msg_ctx` and reports root/messaging issues. Test IPv4/IPv6 formatting, `name#type`, ADS-disabled and Kerberos-disabled builds, site-specific LDAP lookup, DC de-duplication of PDC address, SID/name failures, and flag parsing for `dsgetdcname`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_notify.c -->
# sources/user-network-fs/samba/source3/utils/net_notify.c

## Purpose
This file implements `net notify`, a local client for Samba notifyd messaging. It can register for change notifications on a path or send synthetic trigger events.

## Important APIs, Types, And Control Flow
`net_notify()` validates that a messaging context exists and dispatches `listen` and `trigger`. `net_notify_listen()` looks up the `notify-daemon` server ID in the messaging names database, registers `net_notify_got_event()` for `MSG_PVFS_NOTIFY`, sends a `MSG_SMB_NOTIFY_REC_CHANGE` request containing filter, subdir filter, and path iovecs, then loops in `tevent_loop_once()`. `net_notify_trigger()` sends a `MSG_SMB_NOTIFY_TRIGGER` message containing action, filter, and path. `net_notify_got_event()` validates minimum blob length and NUL termination before printing action and path.

## State And Persistence
No persistent files are written. Runtime state is entirely in Samba messaging, server-id lookup, and the event loop. `listen` is intentionally long-running until event-loop failure or process termination.

## Dependencies And Integration Points
It depends on Samba messaging, tevent, server ID database APIs, notifyd message structures, and `struct net_context`. It integrates with a running notify daemon and requires privileges/context sufficient to access messaging.

## Risks And Test Signals
Filters and action values are parsed with `atoi()` without validation. `listen` has an infinite loop and no local timeout or signal-aware shutdown path. Message layout safety depends on `offsetof(..., path)` matching notifyd structures. Test no-message-context handling, missing notify daemon, malformed notification blobs, successful listen registration, trigger delivery, and invalid numeric argument behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_notify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_offlinejoin.c -->
# sources/user-network-fs/samba/source3/utils/net_offlinejoin.c

## Purpose
This file implements `net offlinejoin`, covering offline domain join provisioning, applying an ODJ blob, and composing an ODJ blob from supplied domain and machine-account data.

## Important APIs, Types, And Control Flow
`net_offlinejoin()` prints usage, initializes libnetapi, and dispatches textual commands `provision`, `requestodj`, and `composeodj`. `net_offlinejoin_provision()` parses `domain=`, `machine_name=`, optional OU/DC/default-password/reuse/save/print options, calls `NetProvisionComputerAccount()`, and optionally writes UTF-16LE-with-BOM ODJ text. `net_offlinejoin_requestodj()` reads ODJ data from `loadfile=` or stdin (`-i`), strips a trailing newline, and calls `NetRequestOfflineDomainJoin()`. `net_offlinejoin_composeodj()` collects realm, workgroup, credentials, DC name/IP, domain SID/GUID, forest, and AD/NT4 flag, validates them, calls `NetComposeOfflineDomainJoin()`, then saves and/or prints the resulting blob.

## State And Persistence
Provisioning creates or reuses a machine account through NetAPI and may save an ODJ file. Requesting an ODJ applies provisioning data to local machine state through NetAPI. Compose only emits a blob unless saved. File writes use `file_save()` after registry string conversion with `push_reg_sz()`.

## Dependencies And Integration Points
It depends on libnetapi, Samba credentials, command-line helpers, registry string utilities, SID/GUID parsing, file load/save helpers, and `struct net_context` options such as realm, workgroup, host, destination IP, password, and stdin mode.

## Risks And Test Signals
Top-level dispatch uses independent `if` statements and returns success for unknown commands after libnetapi initialization, which is a CLI correctness risk. `requestodj` strips the last byte before checking for zero size if stdin produced an empty buffer. Saved blobs intentionally use UTF-16LE plus BOM for Windows compatibility. Test all required argument validation, unknown command behavior, savefile/printblob combinations, IPv4/IPv6 DC address formatting, stdin and loadfile paths, NetAPI error propagation, and restart-required status handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_offlinejoin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_printing.c -->
# sources/user-network-fs/samba/source3/utils/net_printing.c

## Purpose
This file implements `net printing`, a local and RPC-assisted utility for inspecting old printing TDB databases and migrating their forms, drivers, printers, and security descriptors into registry-backed storage.

## Important APIs, Types, And Control Flow
`struct printing_opts` stores optional input encoding and TDB path. `printing_parse_args()` treats `encoding=<CP>` specially and the remaining argument as the TDB file. `net_printing_dump()` opens the TDB read-only, optionally overrides `dos charset`, traverses keys by prefix (`FORMS/`, `DRIVERS/`, `PRINTERS/`, `SECDESC/`), decodes values through generated NDR pull functions, and prints NDR structures. `printing_migrate_internal()` follows a similar traversal but calls `printing_tdb_migrate_form()`, `printing_tdb_migrate_driver()`, `printing_tdb_migrate_printer()`, and in a second pass `printing_tdb_migrate_secdesc()`. `net_printing_migrate()` runs that internal function through `run_rpc_command()` bound to the winreg interface. `net_printing()` dispatches `dump` and `migrate`.

## State And Persistence
Dump mode is read-only except for temporary charset override restored at exit. Migrate mode reads the legacy TDB and writes through a remote/local winreg RPC pipe into the new printing registry storage. TDB record buffers are manually freed with `SAFE_FREE()`.

## Dependencies And Integration Points
Dependencies include TDB, generated NDR for ntprinting/spoolss/security/winreg, RPC client helpers, Samba charset configuration, and `printing/nt_printing_migrate.h`. The migration command integrates with the broader RPC connection machinery via `run_rpc_command()`.

## Risks And Test Signals
Argument parsing silently lets later non-encoding args replace the TDB path. Charset override must always be restored, including error paths. Prefix-based traversal ignores unknown records. Migration intentionally processes security descriptors after objects, so ordering tests matter. Test dump of each prefix, corrupted NDR blobs, encoding conversion, missing TDB, multiple non-option args, RPC connection failure, and successful migration ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_printing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_proto.h -->
# sources/user-network-fs/samba/source3/utils/net_proto.h

## Purpose
This header is the frozen collected prototype surface for the Samba `net` utility. It lets the many command modules call each other and the common net utility layer without relying on generated prototypes.

## Important APIs, Types, And Control Flow
The file declares entrypoints for ADS, DNS update, cache, conf, domain/file/group/groupmap/help/idmap/join/offlinejoin/lookup/RAP/registry/RPC/share/status/time/user/usershare/eventlog/printing/serverid/notify/tdb/vfs/witness commands. It also declares shared helpers such as `run_rpc_command()`, `net_run_function()`, `net_display_usage_from_functable()`, IPC connection helpers, server discovery helpers, SID/name lookup helpers, file copy helpers, printer migration internals, and RPC shell command providers.

## State And Persistence
The header has no runtime state. It shapes cross-module linkage for functions that may read/write remote servers, local TDBs, registry databases, secrets, and Samba configuration through their implementations.

## Dependencies And Integration Points
It includes ADS status and generated libnet join types and references many structs from other subsystems: `net_context`, `cli_state`, `rpc_pipe_client`, `ndr_interface_table`, `dom_sid`, `copy_clistate`, `net_dc_info`, and RPC shell structures. It is included by net command modules as the central declaration contract.

## Risks And Test Signals
Because it is manually frozen, prototypes can drift from implementations if signatures change. It also exposes broad subsystem coupling from a single header, increasing rebuild and include-order sensitivity. Test signals are full `net` utility builds with warnings-as-errors, compile coverage for optional ADS/Kerberos/RPC features, and link coverage for every declared command entrypoint.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_rap.c -->
# sources/user-network-fs/samba/source3/utils/net_rap.c

## Purpose
This file implements the legacy `net rap` command family over SMB RAP calls. It lists and mutates files, shares, sessions, servers, domains, print queues, users, groups, group memberships, services, and passwords on RAP-capable servers.

## Important APIs, Types, And Control Flow
`net_rap()` dispatches subcommands through `net_run_function()`. Each command opens an IPC connection with `net_make_ipc_connection()`, calls a `cli_Net*`/`cli_RNet*`/print helper, prints callback-formatted output, and shuts down the `cli_state`. File commands enumerate, close, and show open files. Share commands list, add, and delete shares. Session commands list, show details/connections, and delete sessions. Server/domain commands enumerate servers and browse domains. Print queue commands enumerate queues/jobs and delete jobs. User/group commands list/add/delete users and groups and list/add/delete group members. Password changes call `cli_oem_change_password()`. Validate, admin, and service start/stop are explicit not-implemented stubs.

## State And Persistence
The file itself stores no local state. Remote state can be changed through close/delete/add operations for files, shares, sessions, users, groups, memberships, print jobs, and passwords. Formatting callbacks are stateless.

## Dependencies And Integration Points
It depends on RAP-generated types, svcctl generated definitions, SMB client APIs, clirap wrappers, common net helpers, and SMB connection naming helpers. Usage for some commands delegates to non-RAP command usage functions such as `net_file_usage()`, `net_share_usage()`, `net_user_usage()`, and `net_group_usage()`.

## Risks And Test Signals
RAP is legacy and many servers may not support operations; some commands print "not supported" only for specific return values. Input parsing is thin: numeric IDs use `atoi()`, share add splits on the first `=`, and fixed RAP name buffers truncate through `strlcpy()`. Some allocated comments are not explicitly freed before process exit. Test against a RAP-capable fixture for list/add/delete flows, unsupported server responses, long names/comments, share paths containing `=`, password change errors, and not-implemented command behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_rap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_registry.c -->
# sources/user-network-fs/samba/source3/utils/net_registry.c

## Purpose
This file implements the local `net registry` command family for enumerating and editing Samba registry hives, importing/exporting/converting `.reg` files, reading/writing security descriptors, and invoking registry database checks.

## Important APIs, Types, And Control Flow
`open_hive()` splits a path with `split_hive_key()`, creates an admin token, and opens a hive. `open_key()` opens the subkey within that hive. `registry_enumkey()` prints keys and values, optionally recursively. Command functions implement `enumerate`, `enumerate_recursive`, `createkey`, `deletekey`, `deletekey_recursive`, `getvalue`, `getvalueraw`, `getvaluesraw`, `setvalue`, `increment`, `deletevalue`, `getsd`, `getsd_sddl`, `setsd_sddl`, `import`, `export`, `convert`, and `check`. Import uses callback adapters for precheck and actual mutation, wrapped in a regdb transaction. Export recursively emits registry format output through `reg_format`. `net_registry_check()` maps CLI flags into `struct check_options` for `net_registry_check_db()`. `net_registry()` initializes the local registry backend for most commands and dispatches the function table.

## State And Persistence
Most commands directly mutate the local registry database/hives through registry APIs. Import opens regdb, starts a transaction, optionally runs precheck, and commits unless test mode is set. Export and convert write `.reg` files. `increment` serializes DWORD updates with a global `g_lock` key named `registry_increment_lock`.

## Dependencies And Integration Points
Dependencies include registry APIs/backends, registry import/format utilities, admin-token creation, global locks, security descriptor display and SDDL conversion, machine SID lookup, TDB utilities, string conversion, and `net_registry_check.h`/`net_registry_util.h`.

## Risks And Test Signals
The `multi_sz` branch in `net_registry_setvalue()` appears to populate from `argv[count+i]` after `count = argc - 3`, which can include the type string and skip later values; expected indexing is likely from the first value argument. `increment` unlocks only on the success path before cleanup, so error paths rely on context teardown rather than explicit unlock. Local registry edits are destructive, especially recursive delete and import. Test path splitting, recursive enumeration, value set/get for DWORD/SZ/MULTI_SZ, raw output, locked increment failures, SDDL round trips, import precheck/testmode/commit/cancel, export recursion, convert options, registry initialization bypass for `convert` and `check`, and force-delete missing keys.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_registry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_registry_check.c -->
# sources/user-network-fs/samba/source3/utils/net_registry_check.c

## Purpose
This file implements `net registry check`, a parser, validator, repairer, and rewriter for Samba registry TDB databases. It reconstructs a key tree from raw TDB records, detects malformed paths and tree metadata, and can repair in place or write a clean output database.

## Important APIs, Types, And Control Flow
The exported API is `net_registry_check_db()`. `struct regval` and `struct regkey` model decoded values, subkeys, security descriptors, and repair flags. `struct check_ctx` holds input/output db handles, in-memory key registry and deletion lists, database version, separator, options, and interaction defaults. Low-level readers parse uint32, C strings, blobs, and serialized registry values. `check_tdb_action()` classifies raw records as `INFO/version`, subkey lists, value lists, security descriptors, sorted subkeys, sequence records, or invalid keys. Paths are normalized for separator and uppercase form, with interactive/automatic skip/delete/edit/retry decisions. `read_subkeys()`, `read_values()`, and `read_sd()` populate the reconstructed tree. `get_version()` selects registry format version and path separator. Repair/write paths use `write_subkeylist()`, `write_sorted()`, `write_values()`, and `write_sd()`. Final actions either check tree warnings, repair in place, delete invalid keys, or wipe/write a new database.

## State And Persistence
Input opens read-only. Output opens when repair/output/write behavior is requested; automatic mode without output repairs the input file. Output writes are transactional and cancelled in test mode. In-memory dbwrap_rbt databases store the reconstructed key tree and invalid raw keys pending deletion.

## Dependencies And Integration Points
It depends on dbwrap/TDB, dbwrap_rbt, registry DB constants and prefixes, security descriptor marshal/unmarshal, registry parser internals, interactive prompting/editing, string parsing helpers, cbuf serialization, and `struct check_options` from `net_registry_check.h`. It is called from `net_registry.c`.

## Risks And Test Signals
Path normalization notes that it is not generally correct for multibyte characters. Some repairs are best-effort and several comments mark incomplete interaction behavior. Automatic mode can delete invalid records or rewrite the same database. `talloc_array_append()` frees the old array on realloc failure, which can lose existing state. Test version 1/2/3 separators, missing/invalid `INFO/version`, malformed non-NUL keys, duplicate subkey lists, mismatched subkey counts, trailing value data, missing parent references, invalid sorted subkeys, security descriptor decode failures, output `--wipe`, in-place repair, `--test`, `--lock`, `--auto`, `--force`, and explicit `--reg-version`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_registry_check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_registry_check.h -->
# sources/user-network-fs/samba/source3/utils/net_registry_check.h

## Purpose
This header defines the public option contract and entrypoint for the registry database checker used by `net registry check`.

## Important APIs, Types, And Control Flow
It forward-declares `struct net_context`, defines `struct check_options`, and declares `int net_registry_check_db(const char *db, const struct check_options *opts)`. Options cover dry-run, verbosity, locking, automatic actions, force, repair, assumed registry format version, output database path, wipe/rewrite mode, and whether the database path was implicit.

## State And Persistence
The header has no state. Its fields directly control whether the checker writes the input database, writes a separate output database, wipes output first, cancels changes in test mode, or treats absent version data as the current default for implicit local registry databases.

## Dependencies And Integration Points
It includes `<stdbool.h>`, is implemented by `net_registry_check.c`, and is consumed by `net_registry.c`. It intentionally does not expose reconstructed tree internals or serialized registry record helpers.

## Risks And Test Signals
Like the idmap checker header, it uses the generic name `struct check_options`; including both checker headers in one C file would create a conflicting tag definition. Test signals are compile coverage and option mapping from `net_registry_check()` CLI flags into this structure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_registry_check.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_registry_util.c -->
# sources/user-network-fs/samba/source3/utils/net_registry_util.c

## Purpose
This file provides shared output and path utility functions for local registry commands.

## Important APIs, Types, And Control Flow
`print_registry_key()` prints a key name and modification time, formatting NTTIME through Unix/http time helpers. `print_registry_value()` prints registry values in human or raw form for DWORD, SZ, EXPAND_SZ, MULTI_SZ, BINARY, and fallback unprintable types. It decodes strings with `pull_reg_sz()` and `pull_reg_multi_sz()`. `print_registry_value_with_name()` adds the value name and delegates formatting. `split_hive_key()` validates a path, converts legacy slash-only paths to backslashes, strips trailing backslashes, splits the hive name at the first backslash, and returns the hive/subkey strings.

## State And Persistence
The utilities do not persist data. They allocate temporary strings under caller/talloc contexts or `talloc_tos()` and print to the net command output stream.

## Dependencies And Integration Points
Dependencies include registry type definitions, `utils/net_registry_util.h`, `utils/net.h`, registry string conversion helpers, time conversion, and Samba talloc conventions. `net_registry.c` uses these functions for path opening and value/key display.

## Risks And Test Signals
Raw value mode suppresses labels but still prints one line per decoded MULTI_SZ element. Invalid string data simply stops printing that value payload. `split_hive_key()` converts `/` only when no backslash exists, so mixed separators are not normalized. Test hive-only paths, empty paths, trailing separators, slash-only legacy paths, mixed separators, DWORD too-short values, malformed SZ/MULTI_SZ blobs, binary values, and timestamp formatting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_registry_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_registry_util.h -->
# sources/user-network-fs/samba/source3/utils/net_registry_util.h

## Purpose
This header declares registry utility functions used by local `net registry` commands.

## Important APIs, Types, And Control Flow
It declares `print_registry_key()`, `print_registry_value()`, `print_registry_value_with_name()`, and `split_hive_key()`. The declarations depend on registry-facing types such as `NTTIME`, `struct registry_value`, `WERROR`, and `TALLOC_CTX` being available from prior includes.

## State And Persistence
There is no header state. The declared functions only format output or return allocated hive/subkey strings to callers.

## Dependencies And Integration Points
This header is included by `net_registry.c` and implemented by `net_registry_util.c`. It forms the shared contract for path splitting and consistent value/key display.

## Risks And Test Signals
The include guard is local (`__NET_REGISTRY_UTIL_H__`) and the header does not include the type definitions it references, so include order matters. Test signals are compile coverage in translation units that already include registry and talloc definitions, plus behavioral tests through the utility implementation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_registry_util.h -->
