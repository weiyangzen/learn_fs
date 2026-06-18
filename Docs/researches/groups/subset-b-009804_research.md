# subset-b-009804 Research

Grouped research report for the Samba `source3` client, groupdb, and include files in this work item. Each file section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/client/clitar.c -->
# sources/user-network-fs/samba/source3/client/clitar.c

## Purpose
`clitar.c` implements the `smbclient` tar extension when Samba is built with libarchive. It bridges the interactive and command-line tar commands to SMB client operations so users can create an archive from a remote share or extract a local/archive stream into a remote share. Without libarchive the same public entry points compile as stubs that report tar support is unavailable.

## Important APIs, Types, And Functions
- `struct tar` is the central mutable context. It owns a talloc context, operation and selection modes, block size, hidden/system/incremental/reset/dry/regex/verbose flags, byte counters, archive path, selection path list, libarchive handle, and file/directory counters.
- `tar_ctx` is the global context used by `client.c` interactive commands and exposed through `tar_get_ctx()`.
- `cmd_block()`, `cmd_tarmode()`, and `cmd_tar()` are interactive command handlers. They read `cmd_ptr`, update `tar_ctx`, or parse and immediately execute a tar operation.
- `tar_parse_args()` parses tar flag strings and positional values, configures `struct tar`, reads inclusion files for `F`, updates the global `newer_than` variable for `N`, and marks the context ready with `to_process`.
- `tar_process()` dispatches to `tar_create()` or `tar_extract()`, then clears process state and frees context-owned paths.
- `tar_create()`, `tar_create_from_list()`, `get_file_callback()`, and `tar_get_file()` implement SMB-to-archive traversal and transfer.
- `tar_extract()` and `tar_send_file()` implement archive-to-SMB extraction.
- `tar_create_skip_path()`, `tar_extract_skip_path()`, `tar_path_in_list()`, `is_subpath()`, and path helpers implement inclusion/exclusion and DOS/Unix path normalization.

## Control Flow
The normal create path starts with `tar_parse_args()` choosing `TAR_CREATE`, a selection mode, an archive path, and optional path filters. `tar_process()` calls `tar_create()`, which opens a libarchive writer unless in dry-run mode. Include mode with explicit paths calls `tar_create_from_list()`, temporarily changing the client current directory for nested masks. Otherwise it lists from `client_get_cur_dir()` with `do_list()`. Each `do_list()` item reaches `get_file_callback()`, which builds a clean remote path, skips `.` and `..`, evaluates `tar_create_skip_path()`, and calls `tar_get_file()`. `tar_get_file()` builds a PAX archive entry, optionally clears the archive bit, opens remote regular files with `cli_open()`, reads with `cli_read()`, and writes data to libarchive.

The extract path opens the archive from a filename or stdin, iterates headers with `archive_read_next_header()`, evaluates `tar_extract_skip_path()`, and calls `tar_send_file()`. `tar_send_file()` converts archive paths to DOS-style remote paths, creates parent directories with `make_remote_path()`, opens or truncates the remote file with `cli_open()`, writes each libarchive data block using `cli_writeall()`, closes the file, and applies mode/mtime with `cli_setatr()`.

## State And Persistence
Most per-operation state is stored in `tar_ctx` and its child talloc context, then released after `tar_process()`. The command also mutates process-global Samba client state: it reads and changes the current remote directory during include traversal, writes to the local tar file or stdout, reads from stdin or a local archive, creates remote directories/files, writes file contents, sets remote attributes, and may unset the remote archive bit when reset mode is active. `tar_set_newer_than()` writes the external `newer_than` filter used by smbclient listing logic.

## Dependencies And Integration Points
This file integrates with libarchive, Samba client listing and I/O APIs (`do_list`, `cli_open`, `cli_read`, `cli_writeall`, `cli_close`, `cli_setatr`, `cli_chkpath`, `cli_mkdir`), `client_get_cur_dir()`/`client_set_cur_dir()`, Samba talloc and debug helpers, and DOS attribute constants. It depends on `source3/include/client.h` for `struct file_info` and on generated client prototypes for external command/listing APIs.

## Risks
- `cmd_tarmode()` appears to invert verbose/noverbose table values: `verbose` sets false and `noverbose` sets true, which is likely behavioral drift from intended UI text.
- `tar_create_skip_path()` ignores include-list filtering during create because include mode traversal starts from listed paths. This is intentional for explicit include mode but means include-mode path checks differ from extraction path checks.
- Path handling is security-sensitive. `fix_unix_path()` removes simple leading prefixes, but extraction still depends on `client_clean_name()` and server path semantics for traversal edge cases.
- `tar_send_file()` skips non-regular and non-directory entries, so symlinks, devices, fifos, ACLs, owners, and extended attributes are not restored.
- `cli_setatr()` receives archive mode bits and mtime; mapping POSIX mode to SMB attributes may be lossy or server-dependent.
- The fallback build stubs keep symbols available, but any caller expecting `tar_get_ctx()` to be non-NULL must tolerate the non-libarchive build.

## Test Signals
Useful tests include argument parsing for mutually exclusive operations/selections, `b`, `N`, `F`, dry-run and stdin/stdout paths; create/extract round trips with nested directories, hidden/system/archive attributes, path lists, exclude patterns, case-insensitive subpath matching, and filenames using slash/backslash forms; no-libarchive builds; failed SMB open/read/write/close paths; and extraction attempts containing `../` or absolute paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/client/clitar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/client/clitar_proto.h -->
# sources/user-network-fs/samba/source3/client/clitar_proto.h

## Purpose
`clitar_proto.h` declares the public interface of the smbclient tar extension while keeping `struct tar` opaque to callers. It lets `client.c` and other command-dispatch code configure and invoke tar behavior without depending on the full implementation layout in `clitar.c`.

## Important APIs, Types, And Functions
- Forward declaration `struct tar` hides the mutable tar context fields.
- `cmd_block()`, `cmd_tarmode()`, `cmd_setmode()`, and `cmd_tar()` are command callbacks used by the smbclient command table. `cmd_setmode()` is declared here but not implemented in `clitar.c`, so its definition must come from another compilation unit or generated prototype compatibility.
- `tar_parse_args()` parses tar flags and values into a context.
- `tar_process()` executes a prepared context.
- `tar_to_process()` reports whether parsing produced runnable state.
- `tar_get_ctx()` exposes the global tar context pointer.

## Control Flow
The header supports two call styles: interactive command callbacks invoke parsing and processing from command text, while higher-level command-line startup can call `tar_get_ctx()`, `tar_parse_args()`, check `tar_to_process()`, and later call `tar_process()`.

## State And Persistence
No state is stored in the header. It defines access to implementation-owned global state through an opaque pointer. Callers must respect that the context's lifetime and memory ownership are controlled by `clitar.c`.

## Dependencies And Integration Points
The prototypes depend on `TALLOC_CTX`, `bool`, and Samba's common include environment. They integrate with smbclient's command table and with the libarchive/no-libarchive conditional implementation in `clitar.c`.

## Risks
The declaration of `cmd_setmode()` without a visible implementation in the paired source can hide link-time or stale API issues. Because `struct tar` is opaque, misuse is limited, but callers still share one global context and can race or overwrite state if used outside the intended single-threaded smbclient flow.

## Test Signals
Build tests should cover both `HAVE_LIBARCHIVE` and non-libarchive configurations and verify all declared callbacks resolve. CLI tests should exercise command-line and interactive tar flows through these declarations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/client/clitar_proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/client/dnsbrowse.c -->
# sources/user-network-fs/samba/source3/client/dnsbrowse.c

## Purpose
`dnsbrowse.c` implements DNS-SD/mDNS browsing for SMB services when Samba is built with `WITH_DNSSD_SUPPORT`. It searches for `_smb._tcp` service instances, resolves them, and prints available host/port pairs. Without DNS-SD support it exposes a stub that reports the feature is unavailable.

## Important APIs, Types, And Functions
- `struct mdns_smbsrv_result` stores service name, registration type, domain, interface index, and a linked-list pointer.
- `struct mdns_browse_state` tracks the head of discovered services and whether browse callbacks have completed the current response batch.
- `do_smb_browse()` is the exported entry point.
- `do_smb_browse_reply()` is the `DNSServiceBrowse` callback, collecting add events into the talloc-backed linked list.
- `do_smb_resolve()` calls `DNSServiceResolve()` for each discovered service and waits for its socket to become readable.
- `do_smb_resolve_reply()` prints the resolved host target and port.

## Control Flow
`do_smb_browse()` opens a talloc stack frame, starts `DNSServiceBrowse()` for `_smb._tcp`, obtains the DNS-SD socket, and waits in a `poll_one_fd()` loop. When data arrives it calls `DNSServiceProcessResult()`, which invokes `do_smb_browse_reply()`. Added services are pushed to the result list. After browsing finishes or times out, the code deallocates the browse ref and iterates the result list, resolving each service instance with `do_smb_resolve()`. Resolution also waits on the DNS-SD socket and prints the first resolved endpoint.

## State And Persistence
State is transient and talloc-scoped to the browse call. The only persistent side effect is text output to stdout/stderr through `printf()`/`d_printf()`. No Samba databases or network connections are retained after `DNSServiceRefDeallocate()`.

## Dependencies And Integration Points
The implementation depends on Apple's/Avahi-compatible DNS-SD API (`dns_sd.h`), Samba `poll_one_fd()`, talloc stack frames, and smbclient command plumbing through `client_proto.h`. The fallback stub allows callers to compile regardless of platform DNS-SD availability.

## Risks
- The code contains unused variables and a `TALLOC_FREE(fdset)` call in `do_smb_resolve()` even though no `fdset` variable is declared in the visible source; this is a compile risk unless hidden by platform macros or stale code paths.
- `nextResult` is not explicitly initialized when the list is empty, so the last node may contain uninitialized memory unless talloc allocation happens to be zeroed elsewhere. It uses `talloc_array`, not `talloc_zero`.
- The loops use a fixed 1-second poll and stop after the first result batch, so browsing may miss late responders.
- Resolve errors are silently ignored after the initial error return.

## Test Signals
Build with and without `WITH_DNSSD_SUPPORT`; run under a DNS-SD responder advertising multiple SMB services; test no daemon, timeout, remove events, multiple interfaces, and malformed callback data. Static analysis should flag the `fdset` and uninitialized `nextResult` issues.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/client/dnsbrowse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/client/smbspool.c -->
# sources/user-network-fs/samba/source3/client/smbspool.c

## Purpose
`smbspool.c` is Samba's SMB backend for CUPS. It parses CUPS backend invocations and `smb://` device URIs, obtains credentials from URI or environment, connects to an SMB print share, and streams the print job as a remote spool file.

## Important APIs, Types, And Functions
- `main()` handles CUPS argument forms, `DEVICE_URI`, `AUTH_USERNAME`, `AUTH_PASSWORD`, `AUTH_INFO_REQUIRED`, file/stdin selection, URI parsing, Samba client initialization, retry behavior, and print submission.
- `get_exit_code()` maps selected NTSTATUS authentication failures to CUPS backend exit code `2` and prints `ATTR: auth-info-required=...`.
- `list_devices()` emits the generic SMB network printer backend line for CUPS discovery.
- `smb_connect()` chooses anonymous, username/password, Kerberos, or fallback authentication based on `auth_info_required` and available credential cache.
- `smb_complete_connection()` performs `cli_start_connection()`, `cli_session_creds_init()`, `cli_session_setup_creds()`, and `cli_tree_connect_creds()`.
- `kerberos_ccache_is_valid()` checks the default Kerberos credential cache and logs the principal.
- `smb_print()` sanitizes the job title, opens a spool file on the remote print share, streams data with `cli_writeall()`, and closes it.
- `uri_unescape_alloc()` talloc-duplicates and RFC1738-unescapes URI tokens.

## Control Flow
With no arguments, the backend lists devices and exits successfully. For print jobs, `main()` determines which argv slot contains the device URI and which slots contain CUPS job user/title/copies/file. It opens the input file or uses stdin, prefers `DEVICE_URI` over sanitized argv URIs, validates the `smb://` scheme, and parses optional credentials, workgroup, server, port, and printer. Samba logging, locale, configuration, interfaces, and transports are initialized. The backend retries connection failures up to `MAX_RETRY_CONNECT` except for authentication-required status or printer classes. After connecting, it ignores `SIGTERM` for stdin jobs, calls `smb_print()` once per requested copy, shuts down the CLI, frees global state, and returns the CUPS status.

`smb_connect()` first interprets `AUTH_INFO_REQUIRED`. `negotiate` requires a valid ccache and uses the CUPS job user for Kerberos. `username,password` requires a username and permits fallback after Kerberos. `samba` auto-selects username/password if provided or Kerberos if a ccache exists. On Kerberos failure, it may try passwordless NTLMSSP as the effective user and finally anonymous.

## State And Persistence
The file reads environment variables, local Samba configuration, local passwd data, and optional print input files. It opens a network connection, creates/truncates a remote spool file named from the sanitized job title, writes print data, and closes the remote handle to submit the job. It does not maintain local persistent state beyond normal Samba library caches and output to CUPS stderr/stdout conventions.

## Dependencies And Integration Points
The backend integrates with CUPS backend calling conventions and exit codes, Samba loadparm/client stack, SMB transport selection, Kerberos wrappers, talloc stack frames, and libsmb client functions. It expects `smbspool_krb5_wrapper` or cupsd to supply usable `KRB5CCNAME` for negotiate authentication.

## Risks
- URI parsing is manual and bounded by a 1024-byte local buffer; overlong URIs fail, but edge cases around escaped separators remain important.
- `smb_complete_connection()` passes `true` for `use_kerberos` from the main path even when `smb_connect()` computed `use_kerberos`; fallback flags influence behavior but this deserves regression coverage.
- Title sanitization only allows alnum and whitespace and rejects truncation, but title-to-remote-spool naming still depends on server behavior.
- Rewinding input for multiple copies works for files but stdin is forced to one copy.
- Kerberos cache validation proves a principal exists, not that a service ticket for the target server is usable.
- Authentication error mapping determines whether CUPS holds jobs for credentials; missing status values can produce retry loops instead of auth prompts.

## Test Signals
Run backend invocation permutations for argc 1, 5-8, URI in argv[0]/argv[1]/environment, with and without input files. Exercise `AUTH_INFO_REQUIRED` values `none`, `username,password`, `negotiate`, `samba`, unknown, and absent. Mock or integration-test connection failures, authentication failures, class retry behavior, multiple copies, long URIs, escaped credentials, port parsing, and write/close failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/client/smbspool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/client/smbspool_krb5_wrapper.c -->
# sources/user-network-fs/samba/source3/client/smbspool_krb5_wrapper.c

## Purpose
`smbspool_krb5_wrapper.c` is a privileged CUPS backend helper for Kerberos printing. It decides whether Kerberos negotiation is required, switches from root to the authenticated CUPS user's uid/gid when necessary, preserves or discovers a Kerberos credential cache, sanitizes the environment, and execs the real `smbspool` binary.

## Important APIs, Types, And Functions
- `cups_smb_debug()` emits CUPS-style `DEBUG:` or `ERROR:` messages.
- `kerberos_get_default_ccache()` initializes Kerberos, resolves Samba's forced default ccache name, obtains the full cache name, and copies it into the caller buffer.
- `main()` is the wrapper driver handling `DEVICE_URI`, `AUTH_INFO_REQUIRED`, `AUTH_UID`, privilege changes, `KRB5CCNAME`, environment cleanup, and `execv()`.

## Control Flow
The wrapper saves `DEVICE_URI`, reads `AUTH_INFO_REQUIRED`, and immediately delegates to `smbspool` for absent, `none`, `username,password`, or unrecognized authentication modes. Only `negotiate` activates Kerberos-specific handling. If already non-root, or if `AUTH_UID` maps to root, it delegates directly. Otherwise it validates and converts `AUTH_UID`, looks up the passwd entry, clears supplementary groups, adds the `lp` group so the job file remains accessible, switches gid then uid, chooses `KRB5CCNAME` from the existing environment, the Kerberos default cache, or `FILE:/tmp/krb5cc_<uid>`, clears the environment, restores only needed variables, and execs `${BINDIR}/smbspool` with the original argv.

## State And Persistence
The wrapper mutates process credentials and environment before `execv()`. It does not write files itself, but it may point `KRB5CCNAME` at an existing or conventional file cache path. Failure returns CUPS backend status codes such as `CUPS_BACKEND_AUTH_REQUIRED` or `CUPS_BACKEND_FAILED`.

## Dependencies And Integration Points
It integrates with CUPS backend headers and status codes, Samba dynconfig for `get_dyn_BINDIR()`, Kerberos libraries, system passwd/group APIs, `setgroups()`, `setgid()`, `setuid()`, and the downstream `smbspool` backend.

## Risks
- `CUPS_SMB_ERROR` is defined with `CUPS_SMB_LOG_DEBUG`, so error messages may be labeled `DEBUG` rather than `ERROR`.
- It assumes a local `lp` group is required and present; systems using a different CUPS spool group will fail.
- `strtoul(env, NULL, 10)` does not validate full-string consumption, so partially numeric `AUTH_UID` strings can be accepted.
- `execv()` failure returns its negative value directly without a CUPS-specific diagnostic path.
- The fallback `FILE:/tmp/krb5cc_<uid>` may not exist or may be inaccessible after environment cleanup.

## Test Signals
Test each `AUTH_INFO_REQUIRED` branch, root and non-root execution, missing/invalid/partial `AUTH_UID`, absent `lp` group, uid/gid switch failures, existing `KRB5CCNAME`, default ccache discovery, Heimdal/MIT free paths, environment sanitization, and `execv()` failure. Packaging tests should verify installation permissions and backend symlink layout.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/client/smbspool_krb5_wrapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/groupdb/mapping.c -->
# sources/user-network-fs/samba/source3/groupdb/mapping.c

## Purpose
`mapping.c` is the passdb-facing group mapping facade. It initializes the selected mapping backend, exposes default passdb group/alias mapping methods, handles Unix group management scripts, creates aliases and builtin aliases, and translates backend alias membership data into SAMR/LSA-style results.

## Important APIs, Types, And Functions
- Static `backend` points at the active `struct mapping_backend`, currently initialized via `groupdb_tdb_init()`.
- `add_initial_entry()` creates a `GROUP_MAP` from gid, SID string, SID type, NT name, and comment.
- `get_domain_group_from_sid()` validates that a SID maps to a domain group and that its gid exists in NSS, with a special fallback for domain RID 513.
- `smb_create_group()`, `smb_delete_group()`, `smb_set_primary_group()`, `smb_add_user_group()`, and `smb_delete_user_group()` execute configured administrative scripts and flush NSS/group caches.
- `pdb_default_getgrsid()`, `pdb_default_getgrgid()`, `pdb_default_getgrnam()`, add/update/delete/enum functions, and alias membership methods adapt backend bool/NTSTATUS APIs to passdb method signatures.
- `pdb_default_create_alias()` and `pdb_create_builtin_alias()` allocate or compose SIDs/gids and store alias mappings.
- `pdb_nop_*` functions provide failure-only implementations for passdb backends without group mapping.

## Control Flow
Most passdb calls first call `init_group_mapping()`, which lazily initializes the backend once. Lookup and mutation wrappers then dispatch directly to backend function pointers. Alias creation checks for existing names with `lookup_name()`, allocates a RID with `pdb_new_rid()`, composes the SID, allocates a gid with winbind, populates a `GROUP_MAP`, and stores it. Builtin alias creation composes from `global_sid_Builtin`, resolves a display name with `lookup_sid()`, optionally allocates a gid, and stores the map.

The Unix group helper functions are script-driven. They read loadparm script settings, substitute `%g` and/or `%u`, execute with `smbrun()`, and flush caches on success. `smb_create_group()` additionally reads a gid from script stdout if available, falling back to `getgrnam()`.

## State And Persistence
This file does not persist mappings directly; it delegates to the backend. It does mutate system state indirectly through configured scripts and can allocate RIDs/gids through passdb/winbind infrastructure. It uses talloc-owned `GROUP_MAP` allocations and moves alias info strings into caller-provided structures.

## Dependencies And Integration Points
It integrates with passdb (`pdb_*` method table expectations), groupdb TDB backend, NSS group lookups, winbind gid allocation, SAM/LSA SID helpers, loadparm script configuration, `smbrun()`, cache flushing, and Samba privilege helpers (`become_root()`/`unbecome_root()` around SID lookup).

## Risks
- Script substitution and execution are high-risk administrative surfaces; correctness relies on loadparm quoting/substitution helpers and trusted configuration.
- `pdb_default_create_alias()` can allocate a RID before gid allocation succeeds, wasting RIDs on failure as the debug message notes.
- `get_domain_group_from_sid()` treats RID 513 specially as "None" with gid -1, which callers must not confuse with a valid Unix-mapped group.
- Backend initialization is global and not designed for multiple backend instances.
- NOP function signatures must remain aligned with passdb expectations; drift can produce subtle callback mismatches.

## Test Signals
Test backend initialization failure, add/update/delete/enum wrappers, domain RID 513 behavior, non-domain SID types, missing Unix gids, alias create/delete/info/set/member flows, builtin alias creation with explicit and allocated gids, and each script helper with success/failure/stdout gid parsing/cache flush behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/groupdb/mapping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/groupdb/mapping.h -->
# sources/user-network-fs/samba/source3/groupdb/mapping.h

## Purpose
`mapping.h` defines the storage key constants and backend abstraction for Samba3 group mapping. It is the contract between passdb-facing group mapping code and concrete persistence implementations such as the TDB backend.

## Important APIs, Types, And Functions
- `DATABASE_VERSION_V1` and `DATABASE_VERSION_V2` document historic database versions.
- `GROUP_PREFIX` / `GROUP_PREFIX_LEN` identify records keyed by `UNIXGROUP/<sid>`.
- `MEMBEROF_PREFIX` / `MEMBEROF_PREFIX_LEN` identify reverse alias membership records keyed by `MEMBEROF/<member-sid>`.
- `struct mapping_backend` contains function pointers for initialization, group map add/get/remove/enum, alias membership lookup, add/delete, and member enumeration.

## Control Flow
The header itself has no control flow. Runtime code loads one `mapping_backend` and calls through these function pointers. The reverse-membership design means "which aliases is this SID a member of?" can be answered by one record fetch, while enumerating all members of an alias requires traversal.

## State And Persistence
The constants define on-disk key namespaces used by group mapping stores. Values are backend-defined, but the TDB backend stores packed gid/type/name/comment for group records and space-separated alias SIDs for member-of records.

## Dependencies And Integration Points
The contract depends on `GROUP_MAP`, `dom_sid`, `lsa_SidType`, `gid_t`, `TALLOC_CTX`, and `NTSTATUS` from Samba headers. It is consumed by `mapping.c` and implemented by `mapping_tdb.c`.

## Risks
Changing prefixes or lengths breaks existing databases. Adding function pointers changes backend ABI inside the source tree and requires all implementations to update. Reverse membership optimizes session setup but makes alias member enumeration traversal-heavy.

## Test Signals
Tests should verify exact key prefixes, backend implementations covering every function pointer, and compatibility when reading existing TDB records keyed with these constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/groupdb/mapping.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/groupdb/mapping_tdb.c -->
# sources/user-network-fs/samba/source3/groupdb/mapping_tdb.c

## Purpose
`mapping_tdb.c` implements the `mapping_backend` contract using Samba's dbwrap/TDB layer. It stores SID-to-group mappings in `group_mapping.tdb`, maintains reverse alias membership records, and converts an older `group_mapping.ldb` store into the TDB format on first initialization.

## Important APIs, Types, And Functions
- Static `db` is the opened `db_context` for `group_mapping.tdb`.
- `init_group_mapping()` opens the TDB database and performs legacy LDB conversion if `group_mapping.ldb` exists.
- `group_mapping_key()` builds `UNIXGROUP/<sid>` keys.
- `add_mapping_entry()`, `get_group_map_from_sid()`, `get_group_map_from_gid()`, `get_group_map_from_ntname()`, `group_map_remove()`, and `enum_group_mapping()` implement mapping CRUD and traversal.
- `dbrec2map()`, `find_map()`, and `collect_map()` unpack dbwrap records into `GROUP_MAP` structures and filter them.
- `one_alias_membership()`, `alias_memberships()`, `is_aliasmem()`, `add_aliasmem()`, `enum_aliasmem()`, and `del_aliasmem()` manage reverse membership records.
- `convert_ldb_record()` and `mapping_switch()` read raw LDB/TDB records, convert attributes into group maps and alias membership, then rename the old database.
- `groupdb_tdb_init()` exposes the static `tdb_backend` function table.

## Control Flow
Initialization opens `state_path("group_mapping.tdb")` with `O_RDWR|O_CREAT`. If `group_mapping.ldb` exists, `mapping_switch()` opens it read-only, traverses every record with `convert_ldb_record()`, writes converted maps and memberships to the new TDB, closes the old database, and renames it to `group_mapping.ldb.replaced`. Otherwise historic version-upgrade code is currently disabled.

Direct SID lookup fetches one key and unpacks `"ddff"` into gid, SID name use, NT name, and comment. Gid and NT-name lookup traverse all records. Enumeration traverses all records and filters by SID type, mapped-only mode, and domain SID. Alias membership stores a member-keyed list of alias SIDs. Adding membership verifies the alias exists and has alias/well-known group type, checks duplicates, locks the member record inside a transaction, appends the alias SID string, stores, and commits. Deleting membership reads current aliases, removes the target, deletes the record if empty or rewrites the space-separated list, then commits.

## State And Persistence
Persistent state lives in `group_mapping.tdb`. Group records are keyed by `GROUP_PREFIX + SID`; alias membership records are keyed by `MEMBEROF_PREFIX + member SID`. Membership values are plain space-separated SID strings. Transactions are used for alias add/delete. Conversion from LDB is persistent and destructive in the sense that the old file is renamed after successful conversion.

## Dependencies And Integration Points
This file depends on dbwrap, TDB, Samba state paths, tdb pack/unpack helpers, SID utilities, passdb `GROUP_MAP`, and the `mapping_backend` interface. Its performance matters during session setup because alias membership checks are called while building tokens.

## Risks
- `add_mapping_entry()` ignores its `flag` argument and always uses `TDB_REPLACE`, so insert-only semantics requested by callers are not enforced.
- Gid and NT-name lookups are full database traversals.
- Alias membership values are string lists; corruption, duplicate whitespace, or partial writes outside transactions can affect parsing.
- `add_aliasmem()` starts a transaction but returns immediately on transaction commit failure without cancel cleanup, which is typical after failed commit but should be understood.
- LDB conversion parses raw packed data and is sensitive to bounds; it sets `errno` and returns failure on malformed input but may have partially written earlier converted records before a later failure.
- Disabled version-upgrade cleanup means old version handling may not run through dbwrap.

## Test Signals
Test database open/create failures, exact key formation, add vs replace behavior, direct SID lookup, traversal lookup by gid/name, enum filters, mapped-only filtering, alias duplicate add, delete missing member, delete last member removing the record, LDB conversion success and malformed records, transaction failure injection, and migration rename behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/groupdb/mapping_tdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/groupdb/mapping_tdb.h -->
# sources/user-network-fs/samba/source3/groupdb/mapping_tdb.h

## Purpose
`mapping_tdb.h` declares the TDB implementation entry point for the group mapping backend.

## Important APIs, Types, And Functions
- `groupdb_tdb_init()` returns a pointer to a static `struct mapping_backend` after ensuring the TDB database is initialized.

## Control Flow
Consumers call `groupdb_tdb_init()` during backend initialization. The implementation opens the database and returns NULL on failure, or the function table on success.

## State And Persistence
The header stores no state. The declared function initializes persistent state in `group_mapping.tdb` through the implementation file.

## Dependencies And Integration Points
It depends on `struct mapping_backend` from `mapping.h`. `mapping.c` uses this declaration to bind the default group mapping backend.

## Risks
The header intentionally exposes only the initializer, so all backend behavior depends on the static function table remaining complete and compatible with `mapping.h`.

## Test Signals
Build tests should verify include ordering with `mapping.h`, and runtime tests should verify NULL return on database initialization failure and non-NULL table on success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/groupdb/mapping_tdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/MacExtensions.h -->
# sources/user-network-fs/samba/source3/include/MacExtensions.h

## Purpose
`MacExtensions.h` defines legacy Macintosh CIFS/AFP extension constants, stream names, AFP info structures, and Trans2 information levels used for Finder metadata, comments, desktop database calls, unique IDs, and HFS-style information over SMB.

## Important APIs, Types, And Functions
- Stream names include `.streams`, `:AFP_AfpInfo:$DATA`, `:AFP_Resource:$DATA`, `:Comments:$DATA`, desktop, and ID index streams.
- `AfpInfo` represents the NT AFP_AfpInfo stream layout with signature, version, backup time, Finder info, ProDOS info, and reserved bytes.
- `SambaAfpInfo` extends `AfpInfo` with a create time.
- `SMB_MAC_QUERY_FS_INFO`, `SMB_MAC_FIND_BOTH_HFS_INFO`, `SMB_MAC_SET_FINDER_INFO`, and desktop database info levels occupy the 0x301-0x309 range.
- Support flags describe access control, comments, desktop DB calls, unique IDs, and no-streams/no-Mac support.
- Enums define Macintosh access bits and `SMB_MAC_SET_FINDER_INFO` field masks.

## Control Flow
This is a declarative protocol header. SMB server/client Trans2 handlers use these constants to encode or decode Mac-specific requests and responses.

## State And Persistence
The header describes persistent metadata streams and database-style desktop/icon data that other modules may store. It does not implement storage itself. Structure sizes and offsets are wire/storage contracts.

## Dependencies And Integration Points
It depends on fixed-width integer types from Samba includes. It integrates with SMB Trans2 query/set path and find operations, alternate data stream handling, and AFP/OS X interoperability code.

## Risks
Wire layout constants cannot change without breaking interoperability. Comments note little-endian fields, so implementations must explicitly marshal rather than rely on host layout. The `SambaAfpInfo` use of `unsigned long` is potentially ABI-width-sensitive if serialized directly.

## Test Signals
Protocol tests should verify exact info levels, support flags, AFP info size/offsets, stream names, Finder info masks, and behavior against clients expecting Mac CIFS extensions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/MacExtensions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/ads.h -->
# sources/user-network-fs/samba/source3/include/ads.h

## Purpose
`ads.h` is the source3 Active Directory Services wrapper header. It centralizes LDAP/Kerberos ADS types, reconnect state, SASL wrap operations, LDAP control OIDs, and generated ADS prototypes.

## Important APIs, Types, And Functions
- `struct ads_saslwrap_ops` defines SASL wrap/unwrap/disconnect callbacks.
- `struct ads_reconnect_state` stores a credential-producing callback and private data for reconnect handling.
- `ADS_STRUCT` aliases `struct ads_struct`.
- `ADS_MODLIST` is `LDAPMod **` when ADS/LDAP support is compiled in, otherwise `void **`.
- LDAP control OIDs cover paging, no referrals, server sort, permissive modify, ASQ, extended DN, and SD flags.
- `ads_extended_dn_flags` and `ads_control` describe control values passed into LDAP operations.
- Includes generated `ads_proto.h`, LDAP prototypes when available, and Kerberos prototypes.

## Control Flow
The header has no executable flow, but ADS callers include it to access generated functions and to choose compile-time LDAP-capable or stub-compatible types.

## State And Persistence
No state is stored here. The declared types support LDAP connections, reconnect credential callbacks, and SASL wrapping state owned by implementation modules.

## Dependencies And Integration Points
It integrates source3 with libads, LDAP, Kerberos, generated NDR ADS definitions, and Samba credential handling. Conditional typedefs keep non-ADS builds compiling.

## Risks
Conditional `ADS_MODLIST` typing can hide code paths that compile without LDAP but fail at runtime if not guarded. OID string constants are protocol contracts. Reconnect callbacks must manage talloc ownership of returned credentials correctly.

## Test Signals
Build with and without `HAVE_ADS`/`HAVE_LDAP`, test LDAP controls in ADS searches/modifies, SASL wrap/unwrap flows, reconnect callback behavior, and ownership cleanup through `ADS_TALLOC_CONST_FREE`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/ads.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/adt_tree.h -->
# sources/user-network-fs/samba/source3/include/adt_tree.h

## Purpose
`adt_tree.h` declares a small sorted path tree abstraction used by Samba utilities that need to add, search, and debug-print path-keyed data.

## Important APIs, Types, And Functions
- Opaque `struct sorted_tree`.
- `pathtree_init()` creates a tree with caller data and is freed via talloc.
- `pathtree_add()` adds a path component and associated data.
- `pathtree_find()` searches for a key.
- `pathtree_print_keys()` prints/debugs stored keys.

## Control Flow
Callers initialize a tree, add paths, perform lookups, and optionally print keys. Implementation details are hidden.

## State And Persistence
State is in the talloc-owned tree. There is no disk persistence.

## Dependencies And Integration Points
The header depends on Samba bool/talloc environment and is consumed by modules needing path-indexed in-memory lookup.

## Risks
Opaque semantics leave questions of normalization, case sensitivity, and ownership to the implementation. Callers must ensure key strings remain valid or are copied by the implementation.

## Test Signals
Test insertion/search with nested paths, duplicate paths, case variants, slash variants, and talloc cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/adt_tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/async_smb.h -->
# sources/user-network-fs/samba/source3/include/async_smb.h

## Purpose
`async_smb.h` declares tevent-based helpers for constructing, sending, and receiving asynchronous SMB1 client requests.

## Important APIs, Types, And Functions
- `cli_smb_req_create()` creates a `tevent_req` from SMB command metadata, word parameters, and byte iovecs.
- `cli_smb_send()` sends a request using a contiguous byte buffer.
- `cli_smb_recv()` receives and validates a response, returning the input buffer, word count/vector, byte count, and bytes.

## Control Flow
Callers create or send a request on a `cli_state` with a `tevent_context`, then later call `cli_smb_recv()` when the tevent request completes. The receive API enforces a minimum word count.

## State And Persistence
No persistent state is defined. Requests are talloc/tevent-owned and operate over the live SMB client connection.

## Dependencies And Integration Points
It depends on `struct cli_state`, `tevent_req`, `tevent_context`, `iovec`, `TALLOC_CTX`, and `NTSTATUS`. It integrates low-level SMB client code with Samba's async event model.

## Risks
Callers must keep parameter and byte buffers valid according to request ownership rules. Incorrect `min_wct` or iovec lengths can cause protocol parsing failures. These APIs are SMB1-oriented and should be guarded from SMB2-only assumptions.

## Test Signals
Async tests should cover simple request/response, malformed short responses, multi-iovec byte payloads, timeout/cancel behavior, and memory ownership after receive.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/async_smb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/auth.h -->
# sources/user-network-fs/samba/source3/include/auth.h

## Purpose
`auth.h` defines source3 authentication server-side structures and module interfaces. It standardizes how authentication methods receive user-supplied info, return server-supplied session data, prepare GENSEC/auth4 contexts, and register auth modules.

## Important APIs, Types, And Functions
- `struct extra_auth_info` holds non-normal user and primary group SIDs.
- `struct auth_serversupplied_info` carries guest status, Unix security token, optional cached session info, session keys, Netlogon info3, extra SID info, NSS token flag, and Unix name.
- `prepare_gensec_fn` and `make_auth4_context_fn` callbacks bridge source3 auth to GENSEC and auth4.
- `struct auth_context` holds challenge data, start time, challenge origin, ordered auth method list, Netlogon mode, and context-preparation callbacks.
- `struct auth_methods` is a linked-list module entry with `auth()` callback, optional GENSEC/auth4 callbacks, private data, and flags.
- `auth_init_function` and `auth_init_function_entry` define module initialization.
- `AUTH_INTERFACE_VERSION` is `5`.
- `enum session_key_use_intent` distinguishes full vs 16-byte session key use.

## Control Flow
An auth subsystem builds an `auth_context`, loads `auth_methods`, and invokes each method's `auth()` callback until a result is accepted or all fail. Optional callbacks produce GENSEC or auth4 contexts for higher-level negotiation.

## State And Persistence
Structures are request/session state and talloc-owned by callers. No storage is implemented, but returned tokens and session keys feed persisted sessions and authorization decisions elsewhere.

## Dependencies And Integration Points
It depends on common auth definitions, Unix security tokens, Netlogon generated types, GENSEC, auth4, DATA_BLOB, and generated `auth/proto.h`. Authentication modules must match `AUTH_INTERFACE_VERSION`.

## Risks
Session key handling is security-critical. The cached session-info shortcut is documented as atypical and should remain tightly controlled. Module ABI/version drift can break dynamically loaded auth modules.

## Test Signals
Test module registration/version checks, ordered method fallback, guest/system cached session handling, Netlogon info3-derived tokens, extra SID edge cases, session key intent truncation, and GENSEC/auth4 preparation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/auth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/auth_generic.h -->
# sources/user-network-fs/samba/source3/include/auth_generic.h

## Purpose
`auth_generic.h` declares client-side generic authentication helpers wrapping credentials and GENSEC security negotiation.

## Important APIs, Types, And Functions
- `struct auth_generic_state` owns client credentials and a `gensec_security` context.
- Setters update username, domain, password, or whole credential object.
- `auth_generic_client_prepare()` allocates/prepares state.
- Start functions begin authentication by OID, mechanism name, DCE/RPC auth type/level, or SASL mechanism list.

## Control Flow
Callers prepare a state, set credentials, choose a start method matching the protocol, and then continue negotiation through the underlying GENSEC context.

## State And Persistence
State is in talloc-owned credentials and GENSEC objects. No disk persistence is defined.

## Dependencies And Integration Points
It integrates source3 clients with Samba credential objects, GENSEC, SASL selection, and DCE/RPC authentication type negotiation.

## Risks
Credential ownership and lifetime must be clear when passing a `cli_credentials` pointer. Starting by SASL list depends on mechanism ordering and server capabilities. Password setters handle sensitive data and must avoid logging/copy leaks in implementations.

## Test Signals
Test username/domain/password setters, external credential injection, NTLM/Kerberos/SPNEGO/SASL mechanism selection, invalid OIDs/names, and memory cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/auth_generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/client.h -->
# sources/user-network-fs/samba/source3/include/client.h

## Purpose
`client.h` defines central source3 SMB client structures, print job metadata, directory/file info records, client timeout/buffer constants, and full-connection option flags.

## Important APIs, Types, And Functions
- `CLI_BUFFER_SIZE` aliases maximum SMB buffer size; `CLIENT_TIMEOUT` defaults to 20 seconds.
- `struct print_job_info` stores print job id, priority, size, user, name, and time.
- `struct cli_state` represents an SMB client connection, including DFS linked-list pointers, error mapping, server strings, share/device, timeout, POSIX capabilities, pipe list, oplock preference, low-level connection pointer, and SMB1/SMB2 session/tree state.
- `struct file_info` is a directory listing/stat result with size, allocation, attributes, inode, timestamps, name/short name, reparse tag, POSIX stat fields, owner/group SIDs, and POSIX flag.
- `CLI_FULL_CONNECTION_*` flags control SPNEGO, anonymous fallback, oplocks, DOS errors, ASCII, SMB1 forcing/disabling, IPC, and POSIX requests.

## Control Flow
This is a data contract header. Client connection functions populate and mutate `cli_state`; listing/stat functions populate `file_info`; higher-level tools such as `clitar.c` consume these fields to transfer files.

## State And Persistence
`cli_state` is live connection state and owns active sessions/tree connects/open handles indirectly. It is not persistent, but it gates network resources. `file_info` is snapshot metadata returned from remote servers.

## Dependencies And Integration Points
It integrates source3 client code with SMBXCLI, RPC pipe clients, IDR open handle tracking, Samba fixed string types, SID types, and DOS/SMB constants.

## Risks
Fields span SMB1 and SMB2 and must be interpreted according to negotiated dialect. Direct field access by many modules makes refactoring risky. Timeout and flag defaults influence many command-line tools.

## Test Signals
Test full connection options across SMB1/SMB2, DFS subsidiary connections, POSIX capability negotiation, file_info population for normal and POSIX listings, reparse tags, owner/group SIDs, and print job metadata.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/ctdb_srvids.h -->
# sources/user-network-fs/samba/source3/include/ctdb_srvids.h

## Purpose
`ctdb_srvids.h` defines Samba's static CTDB service IDs in the reserved `0xFE...` range for clustered messaging.

## Important APIs, Types, And Functions
- `CTDB_SRVID_SAMBA_NOTIFY_PROXY` identifies the process receiving clustered file change notifications and multicasting them locally.
- `CTDB_SRVID_SAMBA_PROCESS` identifies Samba processes for broadcast-style messaging.
- A disabled block documents `CTDB_SRVID_SAMBA_NOTIFY`, already provided by CTDB protocol headers for global lock death notifications.

## Control Flow
No executable flow. CTDB messaging code uses these constants when registering and sending messages.

## State And Persistence
No local state. The constants are distributed protocol identifiers and must remain globally unique.

## Dependencies And Integration Points
It integrates notify, messaging, and global lock subsystems with CTDB's service registration namespace.

## Risks
Changing or reusing IDs breaks clustered deployments. The disabled duplicate constant documents dependency on CTDB headers and should remain consistent.

## Test Signals
Cluster tests should verify notify proxy registration, message_send_all behavior, and no service ID collisions with CTDB protocol definitions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/ctdb_srvids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/ctdbd_conn.h -->
# sources/user-network-fs/samba/source3/include/ctdbd_conn.h

## Purpose
`ctdbd_conn.h` declares the Samba3 client interface to the CTDB daemon. It covers connection setup, messaging, database attach/migrate/parse/traverse, IP registration/enumeration, controls, service registration, request framing, and async parse operations.

## Important APIs, Types, And Functions
- Connection lifecycle: `ctdbd_init_connection()`, `ctdbd_init_async_connection()`, `ctdbd_reinit_connection()`, `ctdbd_probe()`.
- Connection state access: `ctdbd_vnn()`, `ctdbd_conn_get_fd()`, `ctdbd_socket_readable()`.
- Messaging: `ctdbd_messaging_send_iov()`, `register_with_ctdbd()`, `deregister_from_ctdbd()`.
- Process/IP helpers: `ctdbd_process_exists()`, register/unregister/passed IP callbacks, public/all IP foreach APIs.
- Database operations: `ctdbd_dbpath()`, `ctdbd_db_attach()`, `ctdbd_migrate()`, `ctdbd_parse()`, `ctdbd_traverse()`, async `ctdbd_parse_send/recv()`.
- Control and request framing: `ctdbd_control_local()`, `ctdb_watch_us()`, `ctdb_unwatch()`, `ctdbd_prep_hdr_next_reqid()`, `ctdbd_req_send/recv()`.

## Control Flow
Callers establish a CTDB daemon connection, optionally integrate its fd with tevent using `ctdbd_socket_readable()`, attach databases, migrate keys, parse/traverse records, register message service IDs, and send/receive framed CTDB requests. Async APIs return `tevent_req` objects completed by the event loop.

## State And Persistence
The header declares operations against clustered CTDB state: database locations, record migration, public IP registrations, process liveness, and service registrations. Actual state is held by ctdbd and database backends, not the header.

## Dependencies And Integration Points
It depends on dbwrap, TDB data types, tevent, networking structures, messaging callbacks, and CTDB protocol headers. It is a key integration layer for clustered Samba file serving and databases.

## Risks
Callback signatures must remain stable across CTDB protocol changes. Request iovecs must start with an initialized CTDB header. Database migration and parse operations can affect cluster correctness and require careful error propagation. IP registration callbacks run in event contexts and must not block unexpectedly.

## Test Signals
Cluster integration tests should cover connect/reconnect/probe, message registration and delivery, database attach/migrate/parse/traverse, async request cancellation, public IP enumeration, process liveness, and control error codes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/ctdbd_conn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/fake_file.h -->
# sources/user-network-fs/samba/source3/include/fake_file.h

## Purpose
`fake_file.h` declares support for synthetic server-side files that Windows clients expect but that are not normal filesystem objects, such as quota metadata or named pipe proxies.

## Important APIs, Types, And Functions
- `enum FAKE_FILE_TYPE` distinguishes none, quota, and named pipe proxy fake files.
- Quota fake file path constants define Win32 and Unix spellings for `$Extend/$Quota:$Q:$INDEX_ALLOCATION`.
- `struct fake_file_handle` stores fake file type and private data.
- `is_fake_file_path()` and `is_fake_file()` classify paths.
- `open_fake_file()` opens a fake file as a Samba `files_struct`.
- `close_fake_file()` closes fake file state.
- `dosmode_from_fake_filehandle()` exposes DOS attributes for fake handles.

## Control Flow
SMB open paths classify a requested path, call `open_fake_file()` instead of normal VFS open for supported synthetic objects, and later call `close_fake_file()` during handle teardown.

## State And Persistence
Fake handles carry private in-memory state. Backing data may come from quota or pipe subsystems, but this header does not define persistent storage.

## Dependencies And Integration Points
It integrates SMB request handling, connection state, `smb_filename`, `files_struct`, quota support, and named pipe proxy logic.

## Risks
Fake file paths must be recognized consistently across slash styles. Access mask enforcement and DOS mode reporting are security-sensitive because these objects bypass normal filesystem lookup.

## Test Signals
Test fake path detection with Win32/Unix spellings, open/close lifecycle, quota read semantics, named pipe proxy routing, access-denied cases, and DOS mode output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/fake_file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/fstring.h -->
# sources/user-network-fs/samba/source3/include/fstring.h

## Purpose
`fstring.h` defines Samba's fixed-size short string type used widely in older source3 structures.

## Important APIs, Types, And Functions
- `FSTRING_LEN` defaults to `256` unless already defined.
- `typedef char fstring[FSTRING_LEN]` defines the storage type.

## Control Flow
No executable flow. Including modules allocate `fstring` fields on stack or inside structs.

## State And Persistence
`fstring` is inline fixed storage. It may be serialized indirectly when embedded in protocol or database structures elsewhere.

## Dependencies And Integration Points
This header is included by `includes.h` and therefore reaches many source3 files. `client.h` uses `fstring` in `print_job_info`.

## Risks
Fixed-size buffers require careful bounded formatting/copying. Redefining `FSTRING_LEN` before inclusion changes ABI for structures containing `fstring`.

## Test Signals
Static analysis and tests should verify bounded writes into `fstring`, truncation behavior, and ABI consistency across modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/fstring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/g_lock.h -->
# sources/user-network-fs/samba/source3/include/g_lock.h

## Purpose
`g_lock.h` declares a global lock abstraction built on dbwrap and Samba messaging. It supports read/write/upgrade/downgrade locks, async locking, lock callbacks, data associated with locks, dumps, sequence numbers, and watcher wakeups.

## Important APIs, Types, And Functions
- Opaque `g_lock_ctx` and `g_lock_lock_cb_state` represent lock manager and active callback state.
- `enum g_lock_type` defines read, write, upgrade, and downgrade requests.
- Context creation: `g_lock_ctx_init_backend()` and `g_lock_ctx_init()`, plus `g_lock_set_lock_order()`.
- Lock operations: async `g_lock_lock_send/recv()`, sync `g_lock_lock()`, and `g_lock_unlock()`.
- Callback helpers dump, write data, unlock, watch blocker death, and wake watchers from inside callback state.
- Data helpers: `g_lock_writev_data()`, `g_lock_write_data()`.
- Introspection: `g_lock_locks_read()`, `g_lock_locks()`, `g_lock_dump_send/recv()`, `g_lock_dump()`, `g_lock_seqnum()`.
- Watch APIs: `g_lock_watch_data_send/recv()` and `g_lock_wake_watchers()`.

## Control Flow
Callers initialize a context with messaging and backend dbwrap state, request a lock on a `TDB_DATA` key, receive a callback when the lock can be acted on, optionally write lock-associated data, and unlock. Async variants integrate with tevent; sync wrappers wait with a timeout.

## State And Persistence
Lock state and optional data are stored in the dbwrap backend and coordinated via messaging. Watchers observe blocker death or explicit wakeups. Sequence numbers expose state changes.

## Dependencies And Integration Points
It depends on server IDs, dbwrap, messaging, TDB data buffers, tevent, and CTDB/Samba messaging infrastructure. It is used by clustered or multi-process subsystems needing cross-process synchronization.

## Risks
Lock ordering is critical to avoid deadlocks. Callback code must unlock correctly and avoid blocking. Watcher semantics depend on accurate process liveness. Data writes under locks must fit backend atomicity guarantees.

## Test Signals
Test read/write compatibility, upgrades/downgrades, timeout behavior, dead owner detection, watcher wakeups, lock dump data, sequence increments, backend lock order, and multi-process contention.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/g_lock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/idmap.h -->
# sources/user-network-fs/samba/source3/include/idmap.h

## Purpose
`idmap.h` defines the winbind idmap module interface for mapping Unix IDs to SIDs and SIDs to Unix IDs.

## Important APIs, Types, And Functions
- `SMB_IDMAP_INTERFACE_VERSION` is `6`, indicating init callbacks take `TALLOC_CTX` through the current module loading convention.
- `struct idmap_domain` describes a configured domain with name, optional SID, methods, user query callback, low/high id range, read-only flag, and private backend data.
- `struct idmap_methods` defines backend callbacks: `init`, `unixids_to_sids`, `sids_to_unixids`, and `allocate_id`.
- Includes generated `winbindd/idmap_proto.h`.

## Control Flow
Winbind loads an idmap backend, initializes an `idmap_domain`, and calls mapping methods for batches of `id_map` entries. Allocation requests call `allocate_id()` unless the domain is read-only or backend policy rejects it.

## State And Persistence
The header defines runtime domain state; actual persistent mappings live in backend databases or external directory services. The `private_data` pointer is backend-owned.

## Dependencies And Integration Points
It depends on generated idmap NDR types, winbind user info, SID types, and NTSTATUS. Backends must match the interface version.

## Risks
`dom_sid` may not be initialized in all request paths, as the comment warns. Range checks and read-only enforcement are backend-critical. Module ABI drift requires version checks.

## Test Signals
Test backend version compatibility, domain range enforcement, batch mapping partial success/failure, read-only allocation rejection, missing `dom_sid` behavior, and private data cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/idmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/idmap_autorid_tdb.h -->
# sources/user-network-fs/samba/source3/include/idmap_autorid_tdb.h

## Purpose
`idmap_autorid_tdb.h` declares common TDB-backed helpers for the autorid idmap backend and related administration tools. Autorid assigns deterministic ranges to domain SID plus domain-range-index pairs and tracks allocation high-water marks.

## Important APIs, Types, And Functions
- Database keys include `NEXT RANGE`, `NEXT ALLOC UID`, `NEXT ALLOC GID`, `ALLOC`, and `CONFIG`.
- `struct autorid_global_config` stores minimum id value, range size, and max range count.
- `struct autorid_range_config` stores domain SID string, range number, domain range index, and low/high Unix IDs.
- Range APIs get, set, acquire, and delete domain/index-to-range mappings by SID or range number.
- HWM and database APIs initialize/open autorid databases and high-water marks.
- Config APIs load/save/parse/render global configuration.
- Iteration APIs traverse or delete all ranges for a domain in read-write or read-only modes.

## Control Flow
Callers open or initialize a dbwrap database, load config, resolve a domain range with `idmap_autorid_get_domainrange()`, and when not read-only, acquire a new range by incrementing the range HWM. Administration paths can set/delete ranges, initialize allocation HWMs, and iterate per-domain mappings.

## State And Persistence
Persistent state lives in the autorid TDB: config string, next range, next uid/gid allocation HWMs, and range mapping records. The header declares operations that must preserve consistency between SID-index and range-number lookup records.

## Dependencies And Integration Points
It integrates with source3 includes, dbwrap/dbwrap_open, util_tdb, idmap_tdb_common, winbind idmap backends, and `net idmap autorid` utilities.

## Risks
Range acquisition is concurrency-sensitive and must be transactional in implementations. Deleting with `force` can remove invalid records but risks losing forensic data. Config parsing must reject malformed values that could overlap id ranges.

## Test Signals
Test database init/open, HWM initialization and incrementing, get existing range vs acquire new, read-only behavior, duplicate setrange conflicts, delete by SID/range with force true/false, config parse/save/load, and iteration counts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/idmap_autorid_tdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/includes.h -->
# sources/user-network-fs/samba/source3/include/includes.h

## Purpose
`includes.h` is the umbrella source3 include header. It validates Samba configuration headers, normalizes platform feature availability, defines core portability types/macros, includes common Samba utility/protocol headers, and declares a few widely used source3 functions.

## Important APIs, Types, And Functions
- Config guard checks that included `config.h` is from Samba unless `NO_CONFIG_H` is set.
- Developer-only C++ reserved-word macros catch accidental use of reserved identifiers in C code.
- Platform normalization covers Kerberos/LDAP availability, `ENOATTR`, Valgrind headers, `SIG_ATOMIC_T`, `uchar`, device/inode/off_t marshalling macros, and signal aliases.
- `struct stat_ex` and `SMB_STRUCT_STAT` define Samba's extended stat representation with birth time, cached DOS attributes, block info, and flags.
- `enum timestamp_set_resolution` defines timestamp precision categories.
- Includes foundational headers for debug, util, talloc, tevent, DATA_BLOB, time, NTSTATUS/errors, charset, dynconfig, locking, SMB protocol, byte order, modules, talloc stack, setid, loadparm, generated prototypes, and safe string helpers.
- Declares `d_printf()`, `d_fprintf()`, `fstr_sprintf()`, `talloc_asprintf_strupper_m()`, `dump_core()`, `exit_server()`, and `exit_server_cleanly()`.
- Redefines `TRUE`/`FALSE` to compile errors, pushing code toward `true`/`false`.

## Control Flow
Most behavior is compile-time include ordering and macro selection. Runtime code relies on declarations and included utilities rather than executable logic here.

## State And Persistence
No runtime state is stored. `stat_ex` is a data carrier for filesystem metadata and may be used in VFS and protocol responses.

## Dependencies And Integration Points
This header is included by many source3 files and anchors integration with replace/system wrappers, Samba utility libraries, generated prototypes, loadparm, SMB protocol definitions, and platform abstraction.

## Risks
Because it is an umbrella header, changes can have repository-wide build impact. Device/inode serialization macros depend on compile-time type sizes. Reserved-word and TRUE/FALSE poison macros can expose legacy code unexpectedly. Include cycles or config guard failures break standalone builds.

## Test Signals
Build matrix coverage across Linux/BSD/Solaris-like platforms, large and small dev_t/ino_t sizes, developer builds, no-config tests, Valgrind header availability, Kerberos/LDAP absent builds, and compile tests for generated prototype inclusion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/includes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/intl.h -->
# sources/user-network-fs/samba/source3/include/intl.h

## Purpose
`intl.h` defines the `N_()` marker macro for translatable strings that should be extracted but not translated immediately.

## Important APIs, Types, And Functions
- `N_(x)` expands to `x`.

## Control Flow
No runtime flow. Code wraps static strings with `N_()` so translation tooling can find them while runtime receives the original literal.

## State And Persistence
No state.

## Dependencies And Integration Points
It integrates source strings with Samba's internationalization tooling and dynamic loading constraints.

## Risks
Using `N_()` where immediate translation is required leaves strings untranslated until later code calls the actual gettext function. Since it is a macro, it provides no type checking beyond expression use.

## Test Signals
Translation extraction tests should ensure `N_()` markers are picked up, and UI tests should verify marked strings are later translated at display time.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/intl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/libsmb_internal.h -->
# sources/user-network-fs/samba/source3/include/libsmb_internal.h

## Purpose
`libsmb_internal.h` is the private internal contract for `libsmbclient`. It defines internal server/file/context structures, DOS attribute descriptors, xattr mode constants, and prototypes for cache, directory, file, path, print job, server, stat, and xattr helpers.

## Important APIs, Types, And Functions
- `SMBC_MAX_NAME` bounds internal names.
- `struct DOS_ATTR_DESC` carries DOS attribute metadata including mode, size, times, and inode.
- `SMB_CTX_FLAG_USE_NT_HASH` extends public context flags.
- `SMBC_XATTR_MODE_*` constants describe internal xattr update operations.
- `struct _SMBCSRV` caches a server connection, device id, pathinfo capability flags, policy handle, echo time, and list links.
- `struct _SMBCFILE` tracks open files/directories, target cli, filename, offset, server, directory entry lists, errors, and list links.
- `struct SMBC_internal_data` stores initialization state, dirent buffer, cached servers, open files, time-name mode, POSIX extension preference, share mode, auth callback, user data, encryption level, case sensitivity, DFS credentials, server cache, POSIX emulation callbacks, high-level SMB callbacks, port, loadparm context, and memory context.
- Prototypes cover `SMBC_add/get/remove/purge_cached_server`, directory functions, file read/write/splice/close/attr functions, path parsing, print job helpers, server lookup/connect/cache cleanup, stat/statvfs helpers, and xattr operations.

## Control Flow
Public `libsmbclient` APIs operate on `SMBCCTX`, whose internal data points at these structures. Path parsing resolves workgroup/server/share/path/user/password/options, server lookup reuses or opens cached `SMBCSRV` connections, file/dir operations allocate `SMBCFILE`, and xattr/stat/print helpers dispatch to SMB protocol functions through cached `cli_state` connections.

## State And Persistence
The main state is process-local client library cache: server connections, open file/dir handles, directory listing buffers, authentication callbacks, DFS credentials, and loadparm context. Persistent effects occur through operations declared here: remote file changes, xattr updates, print jobs, and server/session cache reuse.

## Dependencies And Integration Points
It includes public `libsmbclient.h`, clirap helpers, source3 `includes.h`, `cli_state`, loadparm, POSIX emulation callbacks, and internal libsmb modules. It is private and should not be consumed by external applications.

## Risks
Internal structures are broad and shared across many modules, so field changes can ripple through the library. The fixed `_dirent_name` buffer must be large enough for URL-encoded names and comments. Server/file linked lists require consistent insertion/removal to avoid stale handles. DFS target connections mean `SMBCFILE.targetcli` can differ from `srv->cli`.

## Test Signals
Test server cache reuse/purge, open file and directory lifecycle, DFS referral target handling, auth callback selection, POSIX extension fallback, encryption level behavior, stat/xattr naming modes, print job helpers, and memory cleanup of linked lists.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/libsmb_internal.h -->
