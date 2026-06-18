# Research: subset-b-009889

Grouped code research for Samba `source3/utils` net utility files. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_rpc_trust.c -->
# sources/user-network-fs/samba/source3/utils/net_rpc_trust.c

## Purpose
Implements `net rpc trust create` and `net rpc trust delete`, managing LSA trusted-domain objects over RPC. It can operate against one local/selected domain controller only, using explicit metadata for the other domain, or against both sides when `otherserver=` is provided. Creation supports AD-style up-level trusts and NT4 down-level trusts depending on whether a DNS domain name is supplied.

## Important APIs, Types, and Functions
Key local structures are `enum trust_op`, `struct other_dom_data`, and `struct dom_data`. `parse_trust_args()` parses `otherserver=`, `otheruser=`, `otherdomainsid=`, `otherdomain=`, `other_netbios_domain=`, and `trustpw=`. `connect_and_get_info()` uses `net_make_ipc_connection_ex()`, `cli_rpc_pipe_open_noauth()`, `dcerpc_lsa_open_policy_fallback()`, `get_domain_info()`, and `dcerpc_binding_handle_transport_session_key()` to get an LSA policy handle plus the session key needed for trust-password encryption. `create_trust()` wraps `dcerpc_lsa_CreateTrustedDomainEx2_r()`, while `delete_trust()` wraps `dcerpc_lsa_DeleteTrustedDomain_r()`.

## Control Flow
`net_rpc_trust()` dispatches through `net_run_function()` to `rpc_trust_create()` or `rpc_trust_delete()`, both entering `rpc_trust_common()`. Argument parsing either constructs an alternate `net_context` for the other server or fills the peer domain data from command-line SID/name values. The selected domain is always connected first; the peer domain is connected only when an `otherserver` was supplied. Create builds a `trustDomainPasswords` blob from the supplied or generated trust password, encrypts a copy with each target LSA session key using ARCFOUR, and calls `CreateTrustedDomainEx2` on one or both policy handles. Delete calls `DeleteTrustedDomain` with the peer SID on one or both handles. Handles and CLI connections are shut down on exit.

## State and Persistence
This command mutates domain controller LSA policy state: trusted-domain objects, trust direction, type, attributes, SID, names, and authentication material. It does not write local files directly, but it handles sensitive trust passwords and session keys in memory and clears the `DATA_BLOB` session keys at cleanup.

## Dependencies and Integration Points
It depends on Samba RPC client plumbing, generated LSA and DRS blob NDR code, domain SID helpers, `net_util.c` IPC connection helpers, credentials in `net_context`, and GnuTLS cipher helpers. It integrates with the broader `net rpc` command tree via `NET_TRANSPORT_RPC`.

## Risks
Incorrect SID/domain-name arguments can create or delete the wrong trust relationship. The dual-side mode can partially succeed if the first controller mutation succeeds and the second fails. Trust password material is accepted on the command line, which is visible in process lists on many systems. ARCFOUR here follows the LSA trust auth protocol, but tests should guard against regressions in session-key selection, blob sizing, and memory cleanup.

## Test Signals
Useful checks include usage output for invalid/missing args; one-sided create/delete with explicit peer SID/name metadata; two-sided create/delete with `otherserver`; generated-password path when `trustpw` is omitted; NT4 path when `otherdomain` is omitted; and failure injection around LSA open, auth blob creation, cipher init/encrypt, and second-domain mutation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_rpc_trust.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_sam.c -->
# sources/user-network-fs/samba/source3/utils/net_sam.c

## Purpose
Provides local SAM/passdb administration behind `net sam`: user metadata updates, account flags, account policies, local/domain/builtin group creation and deletion, group membership management, Unix group mapping, privilege grants/revocations, listing/show commands, and optional LDAP provisioning for an `ldapsam` backend.

## Important APIs, Types, and Functions
Most behavior is organized as `net_sam_*` subcommands in `functable` dispatch trees. User mutations use `struct samu`, `lookup_name()`, `pdb_getsampwsid()`, setter callbacks such as `pdb_set_fullname()`, and `pdb_update_sam_account()`. Group mapping uses `GROUP_MAP`, `pdb_getgrgid()`, `pdb_new_rid()`, `sid_compose()`, and `pdb_add_group_mapping_entry()`. Membership paths use `pdb_add_aliasmem()`, `pdb_add_groupmem()`, `pdb_del_aliasmem()`, `pdb_del_groupmem()`, `pdb_enum_aliasmem()`, and `pdb_enum_group_members()`. Privilege paths use `sec_privilege_id()`, `privilege_enum_sids()`, `grant_privilege_by_name()`, and `revoke_privilege_by_name()`. LDAP provisioning, when compiled with `HAVE_LDAP`, uses `smbldap_init()`, `fetch_ldap_pw()`, LDAP modification helpers, and passdb/Winbind allocation helpers.

## Control Flow
`net_sam()` warns when not root, then dispatches to subcommands. `net_sam_set()` dispatches per-field updates, with a shared `net_sam_userset()` for string fields and `net_sam_set_userflag()` for boolean account-control bits. `net_sam_policy()` handles list/show/set for account policies. Rights commands resolve a name to a local SID, validate privilege names, then enumerate, grant, or revoke. Group commands validate SID type before passdb writes. Listing wraps passdb search iterators and optionally prints RID/description. LDAP provisioning validates backend/options, binds with the secret from `secrets.tdb`, checks or creates Domain Users/Admins/Guests and Administrator/Guest entries, and allocates IDs through winbind except for IPA special cases.

## State and Persistence
This file writes persistent Samba identity state through passdb backends and privilege databases. It may alter user attributes, account-control flags, password-last-set time, account policy values, group mappings, aliases, domain groups, membership records, and LDAP directory entries. It also reads `secrets.tdb` for LDAP bind credentials and depends on NSS/Winbind for Unix users/groups and ID allocation.

## Dependencies and Integration Points
It integrates with Samba passdb, LDAP schema utilities, Winbind, ID mapping, SAMR SID constants, privilege APIs, local name/SID lookup, loadparm configuration, and command dispatch in `net_util.c`. It is explicitly local transport, not remote RPC/ADS management.

## Risks
Most subcommands are destructive administrative operations. Type checks prevent some misuse, but name resolution ambiguity, backend capability differences, missing winbind, non-root execution, and partial LDAP provisioning can leave inconsistent identity state. `net_sam_policy_list()` returns `-1` even after listing, which may be intentional legacy behavior but is a test signal. LDAP provisioning creates several entries sequentially without a single transaction.

## Test Signals
Tests should cover usage and SID-type rejection; user field updates; yes/no flag parsing; password-change time toggling; policy set/show/list including invalid values; privilege grant/revoke/list; Unix group map/unmap with existing-name collisions; alias/domain group membership add/delete/list; root warning; passdb backend failures; and LDAP provisioning dry fixtures for existing, missing, and partially present default entries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_sam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_serverid.c -->
# sources/user-network-fs/samba/source3/utils/net_serverid.c

## Purpose
Implements `net serverid` commands, especially `wipedbs`, which cleans stale SMB runtime database records associated with dead/disconnected server IDs. It also provides `exists` for checking whether a parsed server ID is live.

## Important APIs, Types, and Functions
The cleanup model is built around `struct wipedbs_state`, `struct wipedbs_server_data`, and `struct wipedbs_record_marker`. Traversal callbacks collect session records (`wipedbs_traverse_sessions()`), tree-connect records (`wipedbs_traverse_tcon()`), open records and replay references (`wipedbs_traverse_open()` / `wipedbs_traverse_open_replay()`). Temporary in-memory RBT databases index server IDs, open records, and replay records. Deletion uses `dbwrap_do_locked()` with `wipedbs_delete_fn()` and removes related replay state via `smbXsrv_replay_cleanup()`.

## Control Flow
`net_serverid()` dispatches to `wipedbs` or `exists`. `net_serverid_wipedbs()` opens temporary RBT databases, traverses global smbXsrv session/tcon/open databases, records candidate entries by owning `server_id`, then calls `wipedbs_check_server_exists()` to batch-check liveness through `serverid_exists()`. It traverses collected server data and deletes records only for non-existing server IDs. Open records for disconnected servers are additionally gated by durable-open timeout. A replay cleanup pass deletes replay records whose open record is no longer present or no longer marked as live.

## State and Persistence
The command reads and may delete records from Samba smbXsrv runtime TDBs: session, tcon, open, and replay-related databases. It is careful to copy record keys/values before deletion and then re-lock each key and compare the current value with the recorded value to avoid deleting records that changed after scanning. `--test` maps to dry-run behavior through `c->opt_testmode`.

## Dependencies and Integration Points
It depends on `dbwrap`, `dbwrap_rbt`, server ID helpers, session traversal, smbXsrv session/tcon/open APIs, NDR decoders for open records, and durable replay cleanup. `net_tdb.c` reuses `net_serverid_wipedbs()` under `net tdb smbXsrv wipedbs`.

## Risks
The command is intentionally destructive. Bugs in liveness checks, durable timeout calculation, record-value comparison, or replay cleanup can remove active state or leave stale state behind. The code assumes stable traverse order in the temporary RBT database when mapping liveness results back to server data. Open replay handling requires correct NDR decoding and version checks.

## Test Signals
Test fixtures should include live and dead server IDs, disconnected durable opens below and above timeout, records that change between scan and locked delete, replay records with and without associated open records, `--test` dry-run counts, verbose output, malformed open blobs, and `exists` parsing for present and absent server IDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_serverid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_share.c -->
# sources/user-network-fs/samba/source3/utils/net_share.c

## Purpose
Provides the top-level `net share` command router and user-facing usage for listing, adding, deleting, allowed-users inspection, and migration of shares.

## Important APIs, Types, and Functions
`net_share_usage()` prints supported syntax and common method/flag help. `net_share()` handles `HELP`, chooses the RPC implementation with `net_rpc_check(c, 0)`, and falls back to RAP with `net_rap_share()`.

## Control Flow
The file does not implement share operations directly. It validates the explicit help case, then delegates to `net_rpc_share()` when RPC is available for the current context; otherwise it delegates to `net_rap_share()`.

## State and Persistence
No direct persistence occurs in this file. Actual share enumeration/mutation/migration state is handled by the RPC and RAP backends. The command-line options it advertises can affect remote share definitions, ACL copying, file migration attributes, timestamps, and destination host selection through those backends.

## Dependencies and Integration Points
It depends on `utils/net.h`, common method/flag usage helpers, `net_rpc_check()`, `net_rpc_share()`, and `net_rap_share()`. It is an integration shim between the generic `net` command tree and transport-specific share implementations.

## Risks
Risk is primarily dispatch correctness and user confusion: differences between RPC and RAP backend capabilities can produce different behavior for the same command. Usage text must stay aligned with backend-supported options.

## Test Signals
Check `net share HELP`, normal dispatch when RPC check succeeds, fallback dispatch when RPC is unavailable, and usage text coverage for migration and ACL-related options.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_share.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_status.c -->
# sources/user-network-fs/samba/source3/utils/net_status.c

## Purpose
Implements `net status sessions` and `net status shares`, a local status viewer for active Samba sessions and tree connections, including parseable output modes.

## Important APIs, Types, and Functions
Session display uses `sessionid_traverse_read()` with `show_session()` and filters dead processes through `process_exists()`. Share display uses `connections_forall_read()` with `show_share()` or `show_share_parseable()`. `struct sessionids` and `collect_pids()` cache live session records so parseable share output can include user, group, and hostname for matching connection PIDs.

## Control Flow
`net_status()` dispatches `sessions` and `shares`. `net_status_sessions()` parses the optional `parseable` argument, prints headers for human output, and traverses session records. `net_status_shares()` either prints a human table from connection records or, for parseable mode, first collects live sessions and then joins connection records by server ID/PID.

## State and Persistence
This file is read-only. It reads session and connection TDB-backed runtime state and ignores entries whose owning process no longer exists. It allocates a temporary array for session records in parseable share mode and frees it after traversal.

## Dependencies and Integration Points
It depends on Samba session database APIs, connection TDB helpers from `conn_tdb.h`, server ID formatting, UID/GID name conversion, and `net_run_function()` dispatch.

## Risks
The parseable share join assumes matching live session records; guest or unmatched sessions produce empty user/group/hostname fields. Dynamic runtime databases can change during traversal. `SMB_REALLOC_ARRAY()` failure resets the collected list and silently degrades output.

## Test Signals
Cover human and parseable outputs for sessions and shares; dead process filtering; guest/unmatched connection rows; invalid arguments; empty databases; allocation failure behavior if injectable; and stable delimiters for parseable output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_status.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_tdb.c -->
# sources/user-network-fs/samba/source3/utils/net_tdb.c

## Purpose
Implements `net tdb` diagnostic/maintenance subcommands for selected Samba TDB-backed runtime records. It can inspect `locking.tdb` share-mode records by key and exposes smbXsrv cleanup via the serverid wipe implementation.

## Important APIs, Types, and Functions
`net_tdb_locking()` parses a hex key into `struct file_id`, initializes locking in read-only mode, fetches a `share_mode_lock`, optionally dumps full share-mode data with `share_mode_data_dump()`, or prints service path, filename, and share-mode count via `share_mode_count_entries()`. `net_tdb_smbXsrv()` dispatches `wipedbs` directly to `net_serverid_wipedbs()`.

## Control Flow
`net_tdb()` dispatches `locking` and `smbXsrv`. The locking path validates at least one argument, converts hex to a binary `file_id`, fetches the share-mode record, and chooses summary or dump output based on an optional `dump` argument. The smbXsrv path is a nested dispatch table with only `wipedbs`.

## State and Persistence
The locking inspection path is read-only. The smbXsrv `wipedbs` path can delete stale runtime records through `net_serverid_wipedbs()` and honors that function's dry-run behavior.

## Dependencies and Integration Points
It depends on locking/share-mode APIs, generated open-file NDR headers, `net_serverid_wipedbs()` from `net_serverid.c`, and `net_run_function()`.

## Risks
The key must be the exact hex encoding of `struct file_id`; incorrect length is rejected. There is a minor diagnostic bug risk in the not-found message referencing `argv[1]` even when only one argument was supplied. Maintenance behavior is delegated to the higher-risk serverid cleanup code.

## Test Signals
Test invalid/missing keys, malformed hex length, not-found records, summary output, dump output, read-only locking initialization failure, and `net tdb smbXsrv wipedbs` dispatch including dry-run behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_tdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_time.c -->
# sources/user-network-fs/samba/source3/utils/net_time.c

## Purpose
Implements `net time`, a client-side utility for querying a remote SMB server's time, printing it in human or `/bin/date`-ready format, displaying server timezone offset, or setting the local system clock to match the remote server.

## Important APIs, Types, and Functions
`cli_servertime()` performs unauthenticated NetBIOS/SMB connection setup with `cli_connect_nb()`, negotiates protocol with `smbXcli_negprot()`, reads `cli_state_server_time()`, and optionally returns `smb1cli_conn_server_time_zone()`. `nettime()` wraps it for `net_context`. `systime()` formats a `time_t` as `MMDDhhmmYYYY.ss`. Subcommands are `net_time_system()`, `net_time_set()`, and `net_time_zone()`.

## Control Flow
`net_time()` dispatches subcommands when arguments are present. With no subcommand, it locates a target via `-S`, explicit IP, or `find_master_ip()` for the target workgroup, then prints `ctime()` output. `system` prints formatted remote time. `set` calls `settimeofday()` using the remote time. `zone` converts the SMB server timezone field into a signed HHMM offset string.

## State and Persistence
Read-only paths open temporary network connections and do not persist state. `net time set` mutates local system time through `settimeofday()` and requires sufficient privilege. The command may update `net_context` target IP state when it discovers a master browser/time server.

## Dependencies and Integration Points
It depends on libsmb client connection APIs, NetBIOS name lookup, loadparm SMB protocol bounds, SMB transport parsing, and the generic `net` command context/usage helpers.

## Risks
Time-setting is privileged and can disrupt Kerberos, logs, and clustered services if pointed at the wrong host. The code treats returned time `0` as failure, so epoch values cannot be represented. Timezone sign handling follows SMB convention and can be confusing. NetBIOS-disabled environments produce `NT_STATUS_NOT_SUPPORTED`.

## Test Signals
Cover target discovery failure, explicit host/IP, negotiation failure, `system` formatting, `zone` sign/offset conversion, `settimeofday()` failure, NetBIOS-disabled error text, and no-argument usage behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_user.c -->
# sources/user-network-fs/samba/source3/utils/net_user.c

## Purpose
Provides the top-level `net user` command router for user listing, add, delete, rename, and info operations across ADS, RPC, or RAP backends.

## Important APIs, Types, and Functions
`net_user_usage()` prints backend-agnostic user command syntax and common options. `net_user()` handles argument validation, explicit `HELP`, then selects `net_ads_user()`, `net_rpc_user()`, or `net_rap_user()` depending on `net_ads_check()` and `net_rpc_check(c, NET_FLAGS_PDC)`.

## Control Flow
The command requires at least one argument unless showing usage. ADS is preferred when available. If ADS is not selected, RPC against the PDC is preferred. RAP is the final fallback.

## State and Persistence
This file itself does not mutate state. Backend user implementations may mutate Active Directory, SAMR/passdb, or RAP-accessible server user databases. Options such as LDAP container and comments are forwarded through the selected backend.

## Dependencies and Integration Points
It integrates the generic `net` command with ADS/RPC/RAP user backends and common usage/flag helpers from `utils/net.h`.

## Risks
Backend selection changes semantics and supported options. A server not specified by the user may default to the PDC in the RPC path. Usage must remain aligned with all backend implementations.

## Test Signals
Check no-arg usage, `HELP`, ADS-preferred dispatch, RPC-PDC fallback, RAP fallback, and preservation of add/delete/info/rename arguments through dispatch.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_usershare.c -->
# sources/user-network-fs/samba/source3/utils/net_usershare.c

## Purpose
Implements `net usershare` local management for user-defined share definition files: add/modify, delete, info, and list. It validates share names, paths, ownership policy, ACL syntax, guest policy, and persists share definitions as files in the configured usershare directory.

## Important APIs, Types, and Functions
`get_basepath()` resolves `lp_usershare_path()`. `get_share_list()` scans usershare files, filters by wildcard and ownership, and builds `struct file_list`. `info_fn()` opens each file with `O_NOFOLLOW` when available, validates regular-file status, loads lines, calls `parse_usershare_file()`, and renders info/list output. `net_usershare_add()` performs all validation and writes a version-2 usershare file through `mkstemp()`, `write()`, `fchmod()`, and atomic `rename()`. ACL name/SID conversion uses `net_lookup_sid_from_name()` and `net_lookup_name_from_sid()`.

## Control Flow
`net_usershare()` first rejects disabled usershares (`usershare max shares = 0`) and verifies the usershare directory is openable. Subcommands are dispatched via `net_run_function()`. Add parses positional arguments, applies defaults (`Everyone:R` as `S-1-1-0:R`), enforces maximum share count, validates share name and absolute directory path, checks owner-only policy for non-root users, converts ACL entries to canonical SID permissions, verifies guest allowance, creates a protected temp file, writes the usershare image, and renames it over the final lowercase share filename. Info/list build a filtered file list and reuse `info_fn()` for parsed output. Delete lowercases and validates the share name before unlinking its file.

## State and Persistence
Persistent state is one regular file per usershare under `lp_usershare_path()`. Add/modify replaces files atomically; delete unlinks files. Info/list are read-only. The code consults local filesystem metadata, effective UID, Samba loadparm usershare settings, and local smbd/LSA name lookup for ACL conversion.

## Dependencies and Integration Points
It depends on Samba usershare parsing, security descriptor handling, local name/SID lookup from `netlookup.c`, loadparm configuration, filesystem wrappers, and generic `net` command options such as `--long`, `--continue`, and common flags.

## Risks
This is security-sensitive because it lets non-root users publish shares when configured. The code mitigates symlink and race risks with `lstat`/`fstat`, `O_NOFOLLOW` for reads, temp files, and atomic rename, but directory permissions remain critical. Maximum-share counting is advisory and races with concurrent adds. ACL parsing is strict but depends on local smbd/lookup availability for names.

## Test Signals
Cover disabled usershares, missing/unreadable directory, invalid share names, share name colliding with Unix user, relative or non-directory paths, owner-only rejection, guest disallowed rejection, ACL syntax/name conversion failures, SID ACL input, atomic replace, delete failure, list/info with wildcard and `--long`, malformed usershare files, non-regular files, and O_NOFOLLOW behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_usershare.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_util.c -->
# sources/user-network-fs/samba/source3/utils/net_util.c

## Purpose
Contains shared helper routines for the `net` utility: RPC name lookup, SMB IPC/service connection setup, server discovery, command dispatch, usage display, machine-account credential setup, share type formatting, and domain-controller scanning.

## Important APIs, Types, and Functions
`net_rpc_lookup_name()` opens an LSA pipe over an existing `cli_state` and calls `rpccli_lsa_lookup_names()`. `connect_to_service()`, `connect_to_ipc()`, and `connect_to_ipc_anonymous()` wrap `cli_full_connection_creds()`. `connect_dst_pipe()` connects to the destination host and opens a named RPC pipe. `net_use_krb_machine_account()` loads `secrets.tdb` and configures credentials from the machine account. `net_find_server()` and `net_make_ipc_connection_ex()` resolve the target server by explicit host/IP, PDC, DMB, master browser, or localhost default. `net_run_function()` implements subcommand dispatch. `net_scan_dc()` uses DSSETUP with LSA fallback to fill `struct net_dc_info`.

## Control Flow
Callers typically discover/connect through `net_make_ipc_connection_ex()`: it calls `net_find_server()`, then connects to IPC anonymously or with credentials, stores PDC affinity on success, and applies request timeout. Command modules provide `functable` arrays to `net_run_function()`, which case-insensitively matches the first argument and shifts argv for the selected function. DC scanning first attempts `DsRoleGetPrimaryDomainInformation`; if DSSETUP is unavailable, it falls back to LSA account-domain query.

## State and Persistence
Most helpers are transient network operations. `net_use_krb_machine_account()` reads the secrets database and mutates the in-memory credential state in `net_context`. `net_make_ipc_connection_ex()` may update the server affinity cache with `saf_store()` for PDC connections.

## Dependencies and Integration Points
This file is central glue for many `net_*` modules. It depends on libsmb client transport, NetBIOS name queries, RPC pipe clients, generated LSA/DSSETUP stubs, Samba credentials/gensec, loadparm, secrets, netlogon credential warning helpers, and server affinity.

## Risks
Server discovery has many fallback paths and can connect to localhost unless disabled by flags, so callers must pass flags carefully. Error reporting includes credential-specific messages but may hide lower-level resolution details. LSA policy handles are closed best-effort. Machine-account setup exits the process on secrets initialization failure.

## Test Signals
Cover subcommand dispatch and usage behavior; explicit host/IP/PDC/master/localhost discovery; anonymous vs authenticated IPC; request timeout propagation; PDC affinity storage; LSA and DSSETUP scanning success/fallback/failure; machine-account credentials; and connection errors for logon failure, locked-out, and disabled accounts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_vfs.c -->
# sources/user-network-fs/samba/source3/utils/net_vfs.c

## Purpose
Implements `net vfs` local administrative operations that run through Samba VFS semantics rather than raw POSIX calls: displaying NT ACLs for a share path and converting named streams to AppleDouble files for macOS/fruit compatibility.

## Important APIs, Types, and Functions
Global `struct net_vfs_state` holds the command context, session info, connection wrapper, and `connection_struct`. `net_vfs_init()` initializes Samba process state, loads config/registry shares, initializes locking, builds system or non-root session info, resolves the share, creates a connection with `create_conn_struct_chdir()`, grants share access, initializes file handling, and becomes the session user. `net_vfs_get_ntacl()` uses `filename_convert_dirfsp()`, `SMB_VFS_CREATE_FILE()`, and `SMB_VFS_FGET_NT_ACL()`. `net_vfs_stream_to_appledouble()` uses `ad_unconvert()` directly or through `nftw()`.

## Control Flow
`net_vfs()` dispatches `getntacl` and `stream2adouble`. Both require a share argument and call `net_vfs_init()`. `getntacl` converts the supplied path in share context, opens it internally with read-control access, retrieves owner/group/DACL security information, closes handles, and prints the descriptor. `stream2adouble` rejects absolute paths, then either converts each path once or recursively walks with `nftw()`, skipping symlinks unless follow mode is requested; `--continue` controls whether errors abort.

## State and Persistence
`getntacl` is read-only. `stream2adouble` may create/modify AppleDouble sidecar files and remove/convert stream state through the active VFS stack. The command changes process umask to zero, initializes locking, and uses Samba connection/session state to ensure VFS modules see an smbd-like context.

## Dependencies and Integration Points
It depends on Samba loadparm, registry shares, auth/session setup, smbd connection helpers, locking, filename conversion, file open/close paths, security descriptor printing, AppleDouble conversion, string replacement maps, and global messaging context.

## Risks
Running VFS operations outside smbd requires careful initialization; missing root privileges or wrong share context causes failures. `stream2adouble` is destructive/transformative and recursive traversal can touch many files. Symlink following changes traversal risk. The global static state makes concurrent in-process use unsafe.

## Test Signals
Cover root and uid-wrapper checks, unknown share, config load failure, session creation failure, ACL retrieval for files/directories, close failure paths, absolute path rejection, non-recursive conversion, recursive traversal, symlink skip/follow behavior, `--continue`, verbose output, and VFS/adouble conversion failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_vfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_witness.c -->
# sources/user-network-fs/samba/source3/utils/net_witness.c

## Purpose
Implements `net witness` cluster-only diagnostics and control operations for SMB Witness registrations. It can list registrations, send client/share move notifications, force unregister selected registrations, and force synthetic AsyncNotify responses for testing.

## Important APIs, Types, and Functions
`net_witness_open_registration_db()` opens `rpcd_witness_registration.tdb` read-only. The scanning framework uses `struct net_witness_scan_registrations_state`, regex filters, and `struct net_witness_scan_registrations_action_state` callbacks. `net_witness_scan_registrations_parser()` NDR-decodes `rpcd_witness_registration`, skips dead server IDs, applies filters, runs action callbacks, and dumps text/JSON. Update commands build `rpcd_witness_registration_updateB` messages and send them with `messaging_send()` using `MSG_RPCD_WITNESS_REGISTRATION_UPDATE`. Optional JSON support uses Jansson helpers.

## Control Flow
`net_witness()` dispatches `list`, `client-move`, `share-move`, `force-unregister`, and `force-response`. All commands require `clustering=yes`. The scanner initializes optional JSON output and regex filters for registration UUID, net name, share name, IP address, and client computer name. It either does a direct DB lookup for `--witness-registration` or traverses all records. List uses no-op action callbacks. Move commands validate that either an explicit selection or `--witness-apply-to-all` was supplied, validate mutually exclusive `--witness-new-ip`/`--witness-new-node`, choose IPv4/IPv6/node update types, then send update blobs to each matching registration server. Share move additionally ignores registrations without a share name. Force-unregister sends a removal update. Force-response parses optional JSON into a `witness_notifyResponse` payload and sends it.

## State and Persistence
The registration DB is read-only in this tool. Control operations do not edit the DB directly; they send internal messages to the owning witness registration servers, which are expected to mutate registration or notification state. JSON output includes filters, optional message metadata, and registration details.

## Dependencies and Integration Points
It depends on clustered Samba operation, messaging, server ID liveness, dbwrap/TDB parsing, generated Witness/RPCD NDR types, POSIX regex, loadparm clustering, and optional Jansson/audit JSON helpers. It uses the common `net_context` witness options.

## Risks
The update commands can disrupt connected SMB clients by forcing movement, unregister, or notify responses. Selection safeguards require filters or explicit apply-all, but broad regexes can still affect many clients. Forced response JSON is developer-facing and heavily validated, yet malformed or semantically odd responses can exercise unusual client paths. Without Jansson, JSON input/output paths are unavailable.

## Test Signals
Cover clustering-disabled rejection, direct lookup and traversal, invalid regex, AND filter behavior, dead server ID skipping, text and JSON listing, missing selection rejection, `--witness-apply-to-all` mutual exclusion, IPv4/IPv6/node/all-node move variants, share-name filtering, messaging failure, JSON forced-response parsing for resource change and IP list response types, invalid JSON schemas, and no-Jansson builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net_witness.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/netlookup.c -->
# sources/user-network-fs/samba/source3/utils/netlookup.c

## Purpose
Provides helper functions for converting between SIDs and names through a cached anonymous LSA connection to the local smbd. `net_usershare.c` uses these helpers to canonicalize and display usershare ACL entries.

## Important APIs, Types, and Functions
`struct con_struct` caches connection failure state, `cli_state`, LSA pipe, and policy handle. `create_cs()` connects anonymously to local `IPC$` on `127.0.0.1`, opens the LSA pipe, and opens a policy handle. `net_lookup_name_from_sid()` wraps `rpccli_lsa_lookup_sids()`. `net_lookup_sid_from_name()` wraps `rpccli_lsa_lookup_names()`. `cs_destructor()` shuts down the cached CLI connection when the owning talloc context is destroyed.

## Control Flow
Both exported lookup functions call `create_cs()`. If a previous connect failed, the cached error is returned without retry. If no cache exists, `create_cs()` initializes anonymous credentials, connects to local IPC, opens LSA, and stores the cache in the supplied context. Lookups then make a single-name or single-SID LSA RPC and return the first result.

## State and Persistence
The only state is process-local static cache `cs`. No files are written. The cache holds network/RPC resources and remembers failed connection status until the talloc context destructor clears it.

## Dependencies and Integration Points
It depends on libsmb client connection, anonymous credentials, local loadparm NetBIOS name, LSA RPC client helpers, generated LSA NDR tables, and Samba's local smbd/winbind resolution behavior.

## Risks
The global static cache is not thread-safe and failure caching prevents recovery in the same context after smbd starts or recovers. Anonymous IPC/LSA access must be available. `cs_destructor()` references global `cs` rather than its parameter for shutdown. Name lookup returns the input full name as `ret_name` in some remote helper code, but this file returns LSA-provided arrays.

## Test Signals
Cover successful SID-to-name and name-to-SID lookups, local smbd unavailable, LSA pipe open failure, policy open failure, cached failure behavior, destructor cleanup, anonymous credential allocation failure, and use from usershare ACL conversion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/netlookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/nmblookup.c -->
# sources/user-network-fs/samba/source3/utils/nmblookup.c

## Purpose
Standalone NetBIOS Name Service lookup client. It sends broadcast or unicast NBT name queries, can request node status, print returned query flags, translate result addresses to DNS names, bind to root port 137, search for master browsers, and perform status lookup by IP.

## Important APIs, Types, and Functions
Global option state controls query behavior (`give_flags`, `use_bcast`, `got_bcast`, `recursion_desired`, `translate_addresses`, `RootPort`, `find_status`). `open_sockets()` binds a UDP socket using `open_socket_in()` and enables broadcast. `query_one()` calls `name_query()` for explicit broadcast/unicast targets or `name_resolve_bcast()` otherwise. `do_node_status()` calls `node_status_query()` and prints returned names, flags from `node_status_flags()`, and MAC address. `main()` uses Samba popt/cmdline initialization.

## Control Flow
The program initializes Samba client command-line state, parses options, requires at least one node argument, opens the UDP socket, then processes each lookup. `-A` treats the argument as an IP and runs node status for wildcard `*`. `-M` changes lookup type to master browser names. Names may include `#HEXTYPE` suffixes to override the NetBIOS type. Overlong names are skipped. Query failures set a nonzero exit status but processing continues for remaining names.

## State and Persistence
No persistent state is written. Runtime state includes a UDP socket, global option flags, and temporary address/status arrays. Network side effects are NBNS queries and optional reverse DNS lookups.

## Dependencies and Integration Points
It depends on Samba command-line/popt helpers, loadparm client settings, NetBIOS name query/status APIs, socket helpers, address parsing/printing, and common Samba string wrappers.

## Risks
Binding to root port 137 requires privileges and can fail. Broadcast behavior depends on local network configuration and may be noisy. Reverse lookup mode drops addresses without PTR results. Static buffers in flag-format helpers are fine for immediate printing but not reentrant. `sscanf()` parsing of `#` type has minimal validation.

## Test Signals
Cover usage with no nodes, invalid options, broadcast and unicast modes, recursion flag, query flag output, master-browser lookup, `name#type` parsing, overlong name rejection, status lookup by returned address, `-A` IP status mode, root-port failure, reverse translation with and without PTR records, and multiple-node exit status aggregation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/nmblookup.c -->
