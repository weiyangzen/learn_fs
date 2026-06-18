<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/server_info_sam.c -->
# sources/user-network-fs/samba/source3/auth/server_info_sam.c

## Purpose
Builds `auth_serversupplied_info` from a passdb `struct samu` account for the source3 authentication stack. It bridges Samba's passdb identity data with the local UNIX account database and includes a special domain-controller guard for smbd/winbind recursion when the local machine account logs in.

## APIs, Types, and Functions
The exported entry point is `make_server_info_sam(TALLOC_CTX *mem_ctx, struct samu *sampass, struct auth_serversupplied_info **pserver_info)`. It allocates a base server-info object with `make_server_info()`, looks up the UNIX account with `Get_Pwnam_alloc()`, converts passdb data to a Netlogon `SamInfo3` using `samu_to_SamInfo3()`, fills `unix_name` and the `utok` UID/GID, and returns the result on the caller context. The only local helper, `is_our_machine_account()`, checks whether a username is exactly the configured NetBIOS name plus a trailing `$`.

## Control Flow, State, and Persistence
`make_server_info_sam()` works on a temporary talloc stackframe and moves only the completed `server_info` to the caller context. Failure paths return `NO_MEMORY`, `NO_SUCH_USER`, or the passdb conversion status after freeing temporary allocations. Persistent state is not written, but when running as a DC and authenticating the local machine account it calls `winbind_off()` for the process to avoid recursive smbd-to-winbind calls.

## Dependencies and Integration
The file depends on `auth.h`, `passdb.h`, loadparm helpers such as `lp_netbios_name()`, the passdb `struct samu` accessor set, NSS passwd lookup, and winbind client control. It is used by Kerberos session synthesis and passdb-backed NTLM authentication paths that need a source3 `auth_serversupplied_info`.

## Risks and Test Signals
Risks are mostly identity consistency issues: a passdb user without a local passwd entry fails authentication, `samu_to_SamInfo3()` errors propagate directly, and the machine-account winbind disable is global to the process. Test signals include passdb users with valid and missing UNIX accounts, machine account login on a DC, expected UID/GID in the local token, and correct domain/SID fields in generated `info3`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/server_info_sam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/token_util.c -->
# sources/user-network-fs/samba/source3/auth/token_util.c

## Purpose
Constructs and finalizes source3 NT security tokens from SIDs, usernames, Netlogon `SamInfo3` data, UNIX passwd/group data, passdb memberships, built-in aliases, and local privileges. It is the central source3 helper for turning an authenticated identity into the SID list and privilege mask used for authorization.

## APIs, Types, and Functions
Public helpers include `nt_token_check_sid()`, `nt_token_check_domain_rid()`, `get_root_nt_token()`, `add_aliases()`, `get_user_sid_info3_and_extra()`, `create_local_nt_token_from_info3()`, `create_local_nt_token()`, `finalize_local_nt_token()`, `debug_unix_user_token()`, `create_token_from_username()`, `user_sid_in_group_sid()`, `user_in_group_sid()`, and `user_in_group()`. Important private helpers are `init_local_nt_token()`, `add_builtin_administrators()`, `add_builtin_guests()`, `add_local_groups()`, and `create_token_from_sid()`. The major data types are `struct security_token`, `struct dom_sid`, `struct netr_SamInfo3`, `struct extra_auth_info`, `struct samu`, and UNIX `passwd`, UID, and GID values.

## Control Flow, State, and Persistence
Root token creation first checks `SINGLETON_CACHE_TALLOC` for `root_nt_token`; on a miss it resolves UID 0, creates a token with `BUILTIN\Administrators`, grants `SEC_PRIV_DISK_OPERATOR`, and stores the talloc object in memcache. Info3 token creation initializes a claims-disabled token, inserts user and primary group SIDs first, appends group RIDs and extra SIDs uniquely, merges local `/etc/group` SIDs, sets authenticated/default-group flags, and calls `finalize_local_nt_token()`. SID/username token creation first categorizes the SID as local SAM, UNIX user, or winbind/domain user; passdb users use `pdb_enum_group_memberships()`, UNIX users query NSS and `getgroups_unix_user()`, and winbind users synthesize Domain Users as primary group. Finalization adds World and Network when requested, short-circuits anonymous and SYSTEM, adds Authenticated Users, ensures or emulates BUILTIN Administrators/Users/Guests, expands local and builtin aliases if nested groups are enabled, optionally adds the NTLM authentication SID, and computes privileges from token SIDs unless simple administrator privileges are requested.

## Dependencies and Integration
The implementation integrates passdb, secrets domain SID storage, id mapping (`sid_to_uid`, `sid_to_gid`, `uid_to_sid`, `gid_to_sid`), NSS passwd/group lookup, local group enumeration, builtin group creation, privilege lookup, source3 loadparm settings, and the security token library. It is consumed by authentication, session setup, force-user handling, share access checks, and helper functions that need group-membership decisions from usernames or SIDs.

## Risks and Test Signals
The file contains high-impact authorization logic. Risks include stale root-token cache after configuration changes, implicit success return in `add_aliases()` even after some enumeration failures are logged, domain-member behavior depending on secrets and winbind availability, fallback from passdb to UNIX user lookup changing group sources, direct BUILTIN SID insertion when builtin groups cannot be resolved, and group/privilege changes not taking effect until a new token is built. Test signals should cover root token caching, local SAM users, UNIX-only users, winbind/domain users, guest tokens, anonymous and SYSTEM tokens, nested alias expansion, unavailable winbind/builtin group allocation, idmap default-range filtering, and `valid users = +group` style checks through `user_in_group()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/token_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/user_info.c -->
# sources/user-network-fs/samba/source3/auth/user_info.c

## Purpose
Allocates and fills `auth_usersupplied_info`, the structure that carries client-supplied and mapped identity names, endpoints, service description, password material, and password-state metadata into the source3 authentication pipeline.

## APIs, Types, and Functions
The exported function is `make_user_info()`. It receives SMB-visible and mapped account/domain names, workstation, remote and optional local `tsocket_address` values, service description, LM/NT response blobs, optional interactive password hashes, optional plaintext password, and an `auth_password_state`. Local destructors `clear_samr_Password()` and `clear_string()` zero copied hash/plaintext secrets when talloc frees them.

## Control Flow, State, and Persistence
The function allocates a zeroed `struct auth_usersupplied_info`, duplicates string fields under it, copies socket addresses, deep-copies response blobs and interactive hashes, installs secret-clearing destructors, sets the password state, initializes `logon_parameters` to zero, and returns the object. Any allocation failure frees the partial object and returns `NT_STATUS_NO_MEMORY`. State is memory-only and lifetime-bound to the caller's talloc tree.

## Dependencies and Integration
Depends on `auth.h`, generated SAMR password types, Samba `DATA_BLOB` utilities, talloc, and tsocket address copying. It is the construction boundary between SMB session setup/parsing code and backend authentication modules, so it must preserve both the original client identity and the internally mapped identity.

## Risks and Test Signals
Primary risks are secret lifetime and partial allocation cleanup. LM/NT response blobs are not assigned explicit destructors here, while interactive hashes and plaintext are cleared on talloc free. Callers must pass non-NULL required strings and a valid remote address because the function treats allocation/copy failures as fatal. Test signals include allocation-failure cleanup, destructor zeroing of plaintext and `samr_Password`, correct preservation of client versus mapped names/domains, optional local-address behavior, and each password-state mode used by auth backends.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/user_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/user_krb5.c -->
# sources/user-network-fs/samba/source3/auth/user_krb5.c

## Purpose
Maps a Kerberos principal to a local Samba/UNIX user and creates a source3 session-info object when Kerberos authentication succeeds without enough PAC-derived session state. The file also provides `NOT_IMPLEMENTED` stubs when Samba is built without Kerberos.

## APIs, Types, and Functions
With `HAVE_KRB5`, `get_user_from_kerberos_info()` parses `user@REALM`, decides whether the realm is local or trusted, applies username mapping, resolves a UNIX account through `smb_getpwnam()`, performs PAM account checks, optionally maps bad UIDs to guest, and returns NT user/domain, UNIX username, passwd data, and mapping flags. `make_session_info_krb5()` builds `auth_serversupplied_info` as guest, passdb-backed (`make_server_info_sam()`), or artificial passwd-backed (`make_server_info_pw()`), fixes the logon domain when possible, tags `nss_token` if the username was mapped, and calls `create_local_token()`.

## Control Flow, State, and Persistence
Principal parsing rejects names without `@`. Local-realm principals use the workgroup domain and may retry lookup using the bare user after a failed `DOMAIN\user` lookup; foreign realms require `allow trusted domains` and use the realm as the NT domain. Mapping is applied before UNIX lookup. If no passwd entry exists and `map to guest = Bad Uid`, the guest account is looked up and `mapped_to_guest` is set. Session creation then chooses guest server-info, passdb server-info, or passwd-derived server-info and moves into local token creation. No durable state is written; returned strings and passwd wrappers live on the caller's talloc context or the provided passwd allocation lifetime.

## Dependencies and Integration
Depends on Kerberos build configuration, `auth.h`, generated PAC headers, winbind client headers, passdb, loadparm settings such as realm/workgroup/trusted domains/guest mapping, username mapping from `user_util.c`, PAM account restrictions, and token creation. It integrates Kerberos-authenticated SMB session setup with the same local token and passdb identity paths used by NTLM authentication.

## Risks and Test Signals
Risks include realm case/normalization mismatches, trusted-domain policy rejecting valid foreign principals, username map changes altering `DOMAIN\user` lookup behavior, PAM account checks denying otherwise authenticated Kerberos users, guest fallback hiding missing local accounts when configured, and artificial server-info needing explicit domain correction. Test signals include local realm with and without domain-qualified UNIX accounts, foreign realm allowed/denied, mapped usernames, guest mapping on bad UID, PAM restriction failures, passdb-present versus passdb-absent users, and no-Kerberos builds returning `NT_STATUS_NOT_IMPLEMENTED`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/user_krb5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/user_util.c -->
# sources/user-network-fs/samba/source3/auth/user_util.c

## Purpose
Provides username mapping and membership helpers for source3 authentication. It canonicalizes incoming SMB/DOS usernames into UNIX/Samba names using a configured script, username map file, in-process last-result cache, optional gencache entries, UNIX groups, and netgroups.

## APIs, Types, and Functions
Public functions are `user_in_netgroup()`, `user_in_list()`, and `map_username()`. Static helpers include `get_last_from()`, `get_last_to()`, `set_last_from_to()`, `skip_space()`, `fetch_map_from_gencache()`, and `store_map_in_gencache()`. `map_username()` accepts an input name and returns a talloc-owned output name; its boolean return indicates whether the name changed according to mapping rules.

## Control Flow, State, and Persistence
`map_username()` first copies the input to the output, then checks the process-global `last_from`/`last_to` optimization, then optional gencache using an uppercase `USERNAME_MAP/<user>` key. If `username map script` is configured, it runs the script with the user quoted as an argument, reads returned lines from the command fd, and uses the first line as the mapped name. Otherwise it opens `username map`, parses `unixname = dosnames` lines with `fgets_slash()`, trims whitespace, honors leading `!` for immediate return, builds a DOS user list, and matches either wildcard `*` or `user_in_list()`. A miss stores a self-map in the last-result cache and gencache to avoid repeated scans. Global state is `last_from`/`last_to`; durable-ish cache state is Samba gencache with `lp_username_map_cache_time()`.

## Dependencies and Integration
Depends on loadparm username-map settings, substitution context, `smbrun()`, file loading helpers, list parsing, `gencache`, UNIX group checks via `user_in_group()` from token utilities, optional libc netgroup support, and case-insensitive Samba string helpers. Kerberos and NTLM authentication paths call this once to canonicalize incoming account names before local lookup.

## Risks and Test Signals
Risks include command execution trust for the username map script, expensive or stale mappings when gencache lifetime is long, process-global last-result behavior across users, case-sensitive netgroup lookup with only lowercase retry, map-file parse edge cases, and recursive dependency where user-list group checks build tokens through token utilities. Test signals include script success/failure/no-output, map-file wildcard and `!` rules, comments and whitespace trimming, gencache disabled/enabled behavior, repeated lookup hitting last-result cache, UNIX group and netgroup membership forms (`@`, `+`, `&`, `+&`, `&+`), and unmapped names preserving the original output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/user_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/wscript_build -->
# sources/user-network-fs/samba/source3/auth/wscript_build

## Purpose
Defines the Waf build graph for the source3 authentication subsystem, including utility subsystems, the private `auth` library, and built-in or optional authentication modules.

## APIs, Types, and Functions
The script calls `bld.SAMBA3_SUBSYSTEM()` for `TOKEN_UTIL`, `USER_UTIL`, and `AUTH_COMMON`; `bld.SAMBA3_LIBRARY()` for the private `auth` library; and `bld.SAMBA3_MODULE()` for `auth_sam`, `auth_unix`, `auth_winbind`, `auth_builtin`, and `auth_samba4`. It lists source files and dependency strings rather than runtime APIs.

## Control Flow, State, and Persistence
At configure/build time, Waf evaluates these declarations to decide compilation units, library/module boundaries, dependencies, and enablement. `TOKEN_UTIL` builds from `token_util.c`; `USER_UTIL` builds from `user_util.c` and depends on `TOKEN_UTIL`; `AUTH_COMMON` groups common auth helpers including `server_info_sam.c` and `user_info.c`; the private `auth` library includes `user_krb5.c` and NTLMSSP/generic auth sources. Module enablement is conditional for `auth_unix` and `auth_samba4` based on Samba static-module and AD DC build settings.

## Dependencies and Integration
The declared dependencies connect auth code to `samba-util`, passdb (`pdb`), DC utilities, common auth code, plaintext auth, credential/cache helpers, Netlogon client code, hostconfig, messaging, and Samba4 auth/gensec libraries for the `auth_samba4` module. This file is the build integration point that determines whether the source files researched in this group are linked into subsystems, a private library, or modules.

## Risks and Test Signals
Risks include missing dependency declarations causing link failures, moving functions between files without updating subsystem deps, static/dynamic module condition drift, and AD DC builds excluding or including `auth_samba4` incorrectly. Test signals are clean Waf configure/build for static and shared modules, builds with and without AD DC support, builds with `auth_unix` disabled, and link coverage for `TOKEN_UTIL`, `USER_UTIL`, `AUTH_COMMON`, and the private `auth` library.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/client/client.c -->
# sources/user-network-fs/samba/source3/client/client.c

## Purpose
Implements the interactive and batch `smbclient` command-line client. It owns connection setup, command parsing, remote directory state, path cleanup, file transfer, directory listing, deletion, POSIX/UNIX extension commands, metadata commands, share/server browsing, message and tar modes, readline completion, and process startup option handling.

## APIs, Types, and Functions
Externally visible symbols are the global root `struct cli_state *cli`, `client_get_cur_dir()`, `client_set_cur_dir()`, `client_clean_name()`, `do_list()`, `set_remote_attr()`, `cmd_setmode()`, and `main()`. The command table maps user commands to many static handlers including `cmd_dir`, `cmd_get`, `cmd_put`, `cmd_mget`, `cmd_mput`, `cmd_del`, `cmd_deltree`, `cmd_open`, POSIX commands (`cmd_posix`, `cmd_posix_open`, `cmd_posix_mkdir`, `cmd_posix_unlink`, `cmd_posix_rmdir`, `cmd_mkfifo`, `cmd_lock`, `cmd_unlock`, `cmd_posix_whoami`), metadata commands (`cmd_allinfo`, `cmd_getfacl`, `cmd_geteas`, `cmd_setea`, `cmd_stat`, `cmd_chown`, `cmd_utimes`, `cmd_setmode`), connection commands (`cmd_logon`, `cmd_logoff`, `cmd_tcon`, `cmd_tdis`, `cmd_tid`, `cmd_vuid`), and browsing helpers. Important local structs include `push_state`, `do_list_queue`, `file_list`, `scopy_timing`, and `completion_remote`.

## Control Flow, State, and Persistence
Process startup initializes Samba command-line state, parses popt options, extracts service/password or host/message/tar modes, normalizes service names, burns command-line secrets, then dispatches to tar, host query, message, or normal client processing. Normal processing opens a connection through `cli_cm_open()`, applies the per-operation timeout, optionally changes to a base directory, then runs either semicolon-separated `-c` commands or the readline loop. `process_tok()` supports exact and abbreviated command names; command handlers parse arguments from the global `cmd_ptr`.

Remote path state is held in globals: `cur_dir`, `cwd` for ACL display, `fileselection`, `CLI_DIRSEP_CHAR/STR`, and flags such as `recurse`, `showacls`, `lowercase`, `translation`, `prompt`, `backup_intent`, `archive_level`, and `newer_than`. `client_clean_name()` normalizes separators and removes relative components using POSIX or SMB-style cleanup depending on negotiated POSIX pathname support. Most remote operations build a path from `client_get_cur_dir()`, clean it, resolve DFS/referral targets with `cli_resolve_path()`, and then call a `cli_*` operation against the returned `targetcli` and `targetpath`.

Listing uses a talloc-owned queue to iterate breadth-first-ish over masks. `do_list()` installs global callback state, resolves each queued mask, calls `cli_list()`, and `do_list_helper()` invokes the selected file callback and enqueues recursive directory masks. Transfers use `cli_pull()` into `writefile_sink()` for downloads and `cli_push()` from `push_source()` for uploads, with optional text CR/LF translation and throughput counters. Recursive local upload builds a local `file_list` using `opendir()`/`stat()`, while recursive remote delete first lists targets into `deltree_list_head` and deletes in collected order. POSIX mode changes the directory separator to `/` and sets UNIX extension capabilities or SMB3.11 POSIX state before POSIX-only commands are accepted.

## Dependencies and Integration
The file integrates with libsmb client connection/session APIs, DFS path resolution, SMB1/SMB2 protocol helpers, NetBIOS browsing, srvsvc RPC, readline/history, command-line credential and loadparm infrastructure, tar support from `clitar`, security descriptor display, POSIX ACL/EA/stat/mknod/lock APIs, reparse data parsing, and Samba's debug/output wrappers. It is built as part of the source3 client tools and exposes a small prototype surface via `client_proto.h` for tar and related client modules.

## Risks and Test Signals
Risks include broad global mutable state, command handlers that sometimes use root `cli` after resolving `targetcli`, shell escape via lines beginning `!`, pager execution via `$PAGER`, complex SMB1 versus SMB2/POSIX behavior, recursive operations over remote or local trees, and cleanup/error paths around open file handles. Some command behavior depends on server capability negotiation, port/protocol choices, encryption state, and DFS referrals. Test signals should include interactive and `-c` command dispatch, ambiguous abbreviation handling, DFS path operations, SMB1 and SMB2/3 servers, POSIX extension enablement, recursive `mget`/`mput`/`deltree`, resume transfers (`reget`/`reput`), archive-bit filtering/resetting, `showacls`, ACL/EA/stat commands, `iosize` encrypted and unencrypted bounds, `-L` host listing with SMB1 disabled/enabled, NetBIOS message mode, tar mode, readline remote completion, disconnect detection through `smbXcli_conn_monitor_once()`, and secret scrubbing after option parsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/client/client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/client/client_proto.h -->
# sources/user-network-fs/samba/source3/client/client_proto.h

## Purpose
Frozen collected-prototypes header for source3 client code. It publishes the small subset of `client.c` and DNS browsing symbols needed by other client compilation units.

## APIs, Types, and Functions
The header forward-declares `struct cli_state` and `struct file_info`, defines the `ATTR_UNSET` and `ATTR_SET` enum used by DOS attribute mutation, and declares `client_get_cur_dir()`, `client_set_cur_dir()`, `client_clean_name()`, `do_list()`, `set_remote_attr()`, and `do_smb_browse()`. `do_smb_browse()` is declared twice in this snapshot.

## Control Flow, State, and Persistence
There is no runtime logic or persistence. The header fixes compile-time contracts for command helpers, list callbacks, path cleanup, current-directory access, and remote attribute updates. The attribute enum values must match `client.c`'s expectations for `set_remote_attr()` and `cmd_setmode()`.

## Dependencies and Integration
Includes depend indirectly on Samba core types such as `TALLOC_CTX`, `NTSTATUS`, and `uint32_t` from surrounding include order. `client.c` includes it, and other source3 client files such as tar or browse-related code can call the listed helpers without including the full client implementation.

## Risks and Test Signals
Risks include stale frozen prototypes when `client.c` signatures change, the duplicate `do_smb_browse()` declaration hiding accidental edits, and reliance on external include order for base Samba types. Build coverage of client tools is the key signal, plus compile failures when callback signatures or enum use drift.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/client/client_proto.h -->
