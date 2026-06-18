# subset-b-009822 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/errormap.c -->
# sources/user-network-fs/samba/source3/libsmb/errormap.c

Purpose: this file is a compact translation layer between legacy SMB/DOS error tuples, winbind `wbcErr` values, and Samba `NTSTATUS`. It is used where older protocol responses or winbind APIs must be normalized before the higher libsmbclient layers convert status to Unix `errno`.

Important APIs and state: `dos_to_ntstatus(uint8_t eclass, uint32_t ecode)` linearly searches the static `dos_to_ntstatus_map[]`, returning `NT_STATUS_OK` for DOS class zero and `NT_STATUS_UNSUCCESSFUL` for unknown mappings. `map_nt_error_from_wbcErr(wbcErr wbc_err)` similarly searches `wbcErr_ntstatus_map[]`. Both tables are process-static immutable data and have no persistence or allocation behavior.

Control flow and dependencies: callers supply protocol-originated error class/code pairs or winbind return codes; the file depends on `includes.h` for `ERRDOS`, `ERRSRV`, `ERRHRD`, `NT_STATUS_*`, `STATUS_*`, `ARRAY_SIZE`, and `wbcErr`. There is no dynamic dispatch; correctness is entirely table coverage and exact equality.

Integration points: directory listing callbacks use `map_nt_error_from_unix()` elsewhere, while this file gives the reverse side for DOS and winbind sources. It feeds the common Samba status/errno conversion path used by libsmbclient operations.

Risks: unmapped DOS codes collapse to `NT_STATUS_UNSUCCESSFUL`, which can lose useful user-facing detail. The table includes raw literal status values, so future protocol changes need careful review. Test signals should include known DOS class/code pairs, unknown pairs, class zero, every `wbcErr_ntstatus_map[]` entry, and one unmapped winbind value.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/errormap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_cache.c -->
# sources/user-network-fs/samba/source3/libsmb/libsmb_cache.c

Purpose: implements the default in-process libsmbclient server cache used when applications do not provide external cache callbacks. It stores `SMBCSRV *` connections by server, share, workgroup, and username so repeated URL operations can reuse SMB sessions/tree connects.

Important APIs/types: private `struct smbc_server_cache` holds duplicated key strings, an `SMBCSRV *server`, and DLIST links. `SMBC_add_cached_server()` allocates and links a cache record. `SMBC_get_cached_server()` searches by server/workgroup/user and share semantics. `SMBC_remove_cached_server()` unlinks and frees only the cache node, not the `SMBCSRV`. `SMBC_purge_cached_servers()` iterates cache entries and asks `SMBC_remove_unused_server()` to close unused servers.

Control flow and state: cache records live at `context->internal->server_cache`. Lookup treats exact share matches as strongest. Empty share and `*IPC$` are special attribute/browse connections and are never returned for a non-exact data-share request. If `one_share_per_server` is enabled and an existing data share differs, the code issues `cli_tdis()`, updates the cached share name, and returns the same connection for a later tree connect.

Dependencies and integration: relies on Samba allocation macros, `DLIST_ADD/REMOVE`, `cli_tdis()`, `cli_shutdown()`, and context option/callback accessors. It is wired as the default cache implementation by `smbc_new_context()` and consumed by `SMBC_find_server()` / `SMBC_server()`.

Risks: cache identity excludes password and port; callers rely on workgroup/user/share/server partitioning and surrounding connection setup to avoid credential mixups. One-share-per-server mutates cache state and can drop broken connections on failed disconnect or strdup. Tests should exercise exact share reuse, `*IPC$` isolation, one-share-per-server retargeting, purge refusal while files are open, and ENOMEM cleanup paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_compat.c -->
# sources/user-network-fs/samba/source3/libsmb/libsmb_compat.c

Purpose: provides the old global libsmbclient API (`smbc_open`, `smbc_read`, `smbc_opendir`, etc.) on top of the newer context/callback based `SMBCCTX` API. It keeps source compatibility for applications that use integer handles instead of `SMBCFILE *`.

Important APIs/types: `struct smbc_compat_fdlist` maps synthetic integer descriptors to `SMBCFILE *`. Static globals include `statcont` for the active context, initialization flag, deterministic descriptor counter, and in-use/available descriptor lists. `smbc_init()` creates and initializes the default context; `smbc_set_context()` swaps in a caller-owned initialized context. `find_fd()`, `add_fd()`, and `del_fd()` manage descriptor indirection.

Control flow and state: most exported functions look up an `SMBCFILE *` from the synthetic fd and call the corresponding function pointer retrieved from `statcont`. Open/creat/opendir allocate a descriptor after the underlying context operation succeeds; close/closedir remove the descriptor before delegating close. Extended attribute `f*` calls validate the fd and often operate on `file->fname`.

Dependencies and integration: this file depends heavily on getters in `libsmb_setget.c` and implementations installed by `smbc_new_context()`. It exposes legacy ABI while sharing all real network behavior with `libsmb_file.c`, `libsmb_dir.c`, `libsmb_stat.c`, and printjob code.

Risks: all compatibility state is process-global and not protected here by per-call locks; callers needing thread isolation should use explicit contexts. `smbc_close()` deletes the fd before closing, so close failure still invalidates the compatibility descriptor. `smbc_open_print_job()` returns `file->cli_fd` directly instead of a compatibility fd, which is legacy behavior but easy to misuse. Test signals: init idempotence, fd reuse from the available list, `FD_SETSIZE` exhaustion, bad fd xattr behavior, and wrappers calling overridden context callbacks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_context.c -->
# sources/user-network-fs/samba/source3/libsmb/libsmb_context.c

Purpose: owns libsmbclient module initialization, context allocation, default option/callback installation, context initialization, teardown, deprecated option compatibility, version reporting, and credential refresh for DFS-aware operations.

Important APIs/state: static `SMBC_initialized`, `initialized_ctx_count`, and `initialized_ctx_count_mutex` protect module lifetime. `SMBC_module_init()` configures logging, loads `$HOME/.smb/smb.conf`, global config, optional append config, interfaces, SIGPIPE blocking, and the context-count mutex. `smbc_new_context()` allocates `SMBCCTX`, `SMBC_internal_data`, talloc/loadparm context, then installs defaults for options and all major operation callbacks. `smbc_init_context()` fills user/netbios/workgroup defaults and marks a context initialized. `smbc_free_context()` performs polite or aggressive cleanup. `smbc_set_credentials_with_fallback()` builds `cli_credentials` using Kerberos, fallback, ccache, and password settings.

Control flow and persistence: module init runs through `SMB_THREAD_ONCE`. Each initialized context increments a global count under the mutex; free decrements and calls `SMBC_module_terminate()` when it reaches zero. Context persistent state includes open file list, server list/cache, options, callback table, loadparm context, and current credentials. Aggressive free closes files and forcibly shuts down cached servers; polite free refuses with `EBUSY` if files or servers remain.

Dependencies and integration: includes Samba client, socket, secrets, credentials, gensec, loadparm, and thread helper APIs. It is the composition root for default implementations in the other libsmb files.

Risks: global logging/stderr and config are process-wide despite per-context APIs. The `LIBSMBCLIENT_NO_CCACHE` option logic is subtle and should be tested for default ccache behavior. Test signals: missing auth callback rejected, timeout clamped, user/netbios/workgroup defaulting, polite `EBUSY`, aggressive shutdown, module termination after last context, deprecated option set/get, and Kerberos/fallback credential fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_dir.c -->
# sources/user-network-fs/samba/source3/libsmb/libsmb_dir.c

Purpose: implements directory and browse-oriented libsmbclient operations: workgroup/server/share enumeration, directory listing, readdir variants, directory creation/removal, chmod/utimes/unlink/rename, directory seek/tell, fstatdir placeholder, and change notification.

Important APIs/types: private list helpers maintain `SMBCFILE.dir_list` of `struct smbc_dirent` and `dirplus_list` of `struct libsmb_file_info`. Main exported entry points include `SMBC_opendir_ctx`, `SMBC_closedir_ctx`, `SMBC_readdir_ctx`, `SMBC_readdirplus_ctx`, `SMBC_readdirplus2_ctx`, `SMBC_getdents_ctx`, `SMBC_mkdir_ctx`, `SMBC_rmdir_ctx`, `SMBC_telldir_ctx`, `SMBC_lseekdir_ctx`, `SMBC_chmod_ctx`, `SMBC_utimes_ctx`, `SMBC_unlink_ctx`, `SMBC_rename_ctx`, and `SMBC_notify_ctx`.

Control flow: `SMBC_opendir_ctx()` parses the URL and chooses one of several modes. Empty server lists workgroups by querying master browsers. Server with no share resolves workgroup/server identity and lists servers or shares via srvsvc RPC with SMB1 fallback. Server+share resolves DFS paths and uses `cli_list()` to build file entries and plus metadata. Read calls consume cached lists; `readdir`, `getdents`, and `readdirplus` keep their cursors synchronized. Mutating APIs parse paths, get `SMBCSRV`, resolve DFS targets, call `cli_*`, and translate status to `errno`.

State and dependencies: directory contents are snapshot-cached in the `SMBCFILE` object until closed. The file depends on name resolution, RPC srvsvc, SMB client listing and path resolution, tevent notification, stat helpers, and server/cache functions.

Risks: browsing behavior is SMB1/NetBIOS-dependent in several paths and returns errors when only SMB2+ is available for old enumeration calls. `telldir` exposes an internal pointer as offset, valid only while the directory object/list lives. URL encoding affects returned `dirent` layout and buffer sizing. `rename` blocks cross-server/share/user and DFS target mismatch, then may unlink destination on `EEXIST`. Tests should cover root browse, share list RPC/fallback, file listing metadata, cursor sync between read APIs, ENOTDIR correction, rmdir non-empty mapping, rename overwrite, and notify timeout/change callbacks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_file.c -->
# sources/user-network-fs/samba/source3/libsmb/libsmb_file.c

Purpose: implements regular-file operations for libsmbclient, plus shared attribute get/set helpers used by stat, chmod, utimes, and other file/directory APIs.

Important APIs: `SMBC_open_ctx()` parses an SMB URL, obtains `SMBCSRV`, resolves DFS path, opens a file with `cli_open()` or `cli_ntcreate()` for `O_PATH`, records `targetcli`, and adds an `SMBCFILE` to `context->internal->files`. `SMBC_creat_ctx()` wraps open. `SMBC_read_ctx()`, `SMBC_write_ctx()`, `SMBC_splice_ctx()`, `SMBC_lseek_ctx()`, `SMBC_ftruncate_ctx()`, and `SMBC_close_ctx()` validate the open-file list and delegate to `cli_*`. `SMBC_getatr()` and `SMBC_setatr()` implement attribute/stat translation and fallback paths.

Control flow and state: each open file tracks `cli_fd`, original URL, owning `SMBCSRV`, current offset, file/dir flag, and DFS-resolved `targetcli`. Reads/writes update `file->offset`; append mode seeks to EOF once after open. `SMBC_getatr()` tries `cli_qpathinfo2`, then `cli_qpathinfo3`, then old `cli_getatr()` if NT SMBs are unavailable, caching unsupported pathinfo levels in `SMBCSRV`. `SMBC_setatr()` prefers `cli_setpathinfo_ext()` and falls back to open plus `cli_setattrE()`/`cli_setatr()`.

Dependencies and integration: depends on `SMBC_parse_path`, `SMBC_server`, DFS `cli_resolve_path`, `setup_stat`, context options such as share mode and POSIX extensions, and `SMBC_dlist_contains` for handle validation.

Risks: `O_APPEND` is approximated by one seek at open, so concurrent appends may not be strict. Pathinfo capability flags are per server and reset on complete failure. Error conversion differs between read/write paths (`cli_status_to_errno` vs `map_errno_from_nt_status`). Tests should cover invalid context/file handles, DFS target persistence across read/write/close, POSIX SMB3.11 open flag toggling, append seek failure cleanup, fallback stat/setattr behavior, and failed close purging.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_misc.c -->
# sources/user-network-fs/samba/source3/libsmb/libsmb_misc.c

Purpose: provides one small shared utility for validating whether an `SMBCFILE *` belongs to a context-owned doubly linked list.

Important API: `SMBC_dlist_contains(SMBCFILE *list, SMBCFILE *p)` returns false for null list or target and otherwise walks `next` pointers until it finds pointer identity equality.

Control flow/state: there is no allocation, persistence, or mutation. The function is intentionally pointer-based: it does not compare file names, descriptors, or server fields. It is used as a guard in file, directory, stat, and compatibility operations before dereferencing handles supplied by callers.

Dependencies and integration: depends on `libsmbclient.h` / `libsmb_internal.h` for `SMBCFILE`. It integrates with all APIs that maintain `context->internal->files`, including open, close, read/write, directory reads, and fstat.

Risks: this only validates membership in the current in-memory list; it does not protect against concurrent mutation by another thread unless higher-level synchronization is active. A stale pointer that has been freed and reallocated into the list could theoretically pass pointer identity checks. Test signals: null list, null element, first/middle/last match, non-member pointer, and calls after close returning `EBADF` through higher-level APIs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_path.c -->
# sources/user-network-fs/samba/source3/libsmb/libsmb_path.c

Purpose: implements URL encoding/decoding and parsing for libsmbclient `smb://` URLs. It turns user-facing SMB URLs into workgroup, server, port, share, path, user, password, and option components used by every file, directory, stat, and print operation.

Important APIs: internal `urldecode_talloc()` decodes `%xx` sequences into talloc output, stops at `%00`, and counts invalid escapes. `smbc_urldecode()` copies decoded output into a caller buffer. `smbc_urlencode()` percent-encodes characters outside the accepted unreserved set. `SMBC_parse_path()` parses `smb://[[[domain;]user[:password]@]server[:port][/share[/path]]][?options]`.

Control flow/state: parse initializes all output strings to safe defaults, inherits context port and workgroup, strips `?options`, handles empty root browsing, parses optional auth before the first slash, extracts numeric port, share, and backslash-normalized path, then URL-decodes path/server/share/user/password. It calls `smbc_set_credentials_with_fallback()` so DFS referral resolution has fresh credentials.

Dependencies and integration: relies on Samba string/token helpers, talloc, `hex_byte`, `nybble_to_hex_upper`, context getters, and credential update code in `libsmb_context.c`. Every URL-based operation depends on its output and error behavior.

Risks: malformed ports and non-`smb://` prefixes fail with `EINVAL` in callers. `%00` truncation can surprise callers but prevents embedded NUL propagation. Options are parsed but currently rejected by directory code if non-empty. IPv6 literal hosts with colons may be ambiguous because `:` is interpreted as port in server. Tests should cover root URLs, workgroup fallback, auth with domain/user/password, percent decoding including invalid and `%00`, port parse failures, slash-to-backslash conversion, and option extraction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_printjob.c -->
# sources/user-network-fs/samba/source3/libsmb/libsmb_printjob.c

Purpose: implements printer-share helpers for opening print jobs, copying a remote file to a printer queue, listing jobs, and deleting jobs.

Important APIs: `SMBC_open_print_job_ctx()` validates context/path and delegates to the normal open function with `O_WRONLY`. `SMBC_print_file_ctx()` opens a source file from one context and a print job from another, copies 4096-byte chunks via configured read/write callbacks, closes both handles, and returns total bytes copied. `SMBC_list_print_jobs_ctx()` connects to the target share and calls `cli_print_queue()`. `SMBC_unlink_print_job_ctx()` connects and calls `cli_printjob_del()`.

Control flow/state: these operations do not keep extra persistent state beyond normal open `SMBCFILE` and server cache state. URL parsing and default-user fallback mirror file/directory operations. Error handling preserves `errno` around cleanup when opening or writing fails.

Dependencies and integration: depends on `SMBC_parse_path`, `SMBC_server`, context callback getters, and lower-level print `cli_*` calls. The compatibility API in `libsmb_compat.c` delegates to these through function pointers installed by `smbc_new_context()`.

Risks: `SMBC_open_print_job_ctx()` parses but does not otherwise use parsed path components before delegating to normal open; printer semantics rely on server/share behavior. `SMBC_print_file_ctx()` requires both contexts initialized and can leave the caller with only byte count, not detailed partial-write metadata. The condition `if (!fname && !printq)` rejects only both-null, so a single null may reach callback code. Test signals: source open failure, print job open failure with source close, write failure cleanup, byte count for multi-chunk copy, list callback invocation, delete status mapping, and null-argument validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_printjob.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_server.c -->
# sources/user-network-fs/samba/source3/libsmb/libsmb_server.c

Purpose: owns server connection discovery, health checking, session setup, tree connects, DFS proxy handling, IPC attribute connections, and cache insertion/removal for libsmbclient.

Important APIs: `SMBC_check_server()` verifies `cli_state` connectivity and throttles `cli_echo()` by `last_echo_time`. `SMBC_remove_unused_server()` closes and frees an `SMBCSRV` only when no open `SMBCFILE` references it. `SMBC_find_server()` searches the cache, calls auth callbacks when credentials are missing, and purges stale cache entries. `SMBC_server()` wraps `SMBC_server_internal()` and inserts new connections into the cache and server list. `SMBC_attr_server()` creates or reuses a special `*IPC$` connection and opens an LSA policy for attribute operations.

Control flow/state: connection setup splits transports into NetBIOS and other transports, handles one-share-per-server retree-connects, starts SMB connection, applies timeout/signing/POSIX flags, creates credentials from context options, performs session setup with optional anonymous fallback, follows DFS proxy referrals recursively, tree-connects, records case-sensitivity/fs attributes, allocates `SMBCSRV`, and updates context credentials for DFS. Persistent state lives in `context->internal->servers`, cache callbacks, `SMBCSRV.cli`, dev id, pathinfo capability flags, policy handle, and echo timestamp.

Dependencies and integration: depends on cli connection/session APIs, credentials, RPC LSA, srv cache callbacks, smb transport selection, and `smbXcli` protocol helpers. It is the central dependency of file, dir, stat, print, and xattr paths.

Risks: credential fallback and anonymous login behavior are security-sensitive. Cache keys are delegated to callbacks and must remain consistent with connection semantics. SMB2 echo quirks are explicitly tolerated for some statuses. Failure after cache add or tree connect must not leak `cli_state`. Tests should cover cache reuse, stale echo removal, one-share retarget, Kerberos required blocking anonymous fallback, DFS proxy recursion, transport/port selection, encryption-required signing, IPC attr cache, and open-file removal refusal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_setget.c -->
# sources/user-network-fs/samba/source3/libsmb/libsmb_setget.c

Purpose: provides the public getter/setter surface for `SMBCCTX` options, global-ish logging/config hooks, server cache callbacks/data, and all operation function pointers. It is the customization layer that lets callers replace libsmbclient behavior per context.

Important APIs: simple string setters/getters manage NetBIOS name, workgroup, and user. Option APIs cover debug, timeout, port, stderr logging, full time names, share mode, user data, encryption level, case sensitivity, browse LMB count, readdir URL encoding, one-share-per-server, Kerberos/fallback/anonymous/ccache/NT-hash flags, protocol min/max, and POSIX extensions. Function pointer APIs get/set auth, server cache, file, directory, xattr, statvfs, truncate, notify, and print callbacks.

Control flow/state: most setters directly mutate `SMBCCTX` or `SMBC_internal_data`; string setters free and duplicate. `smbc_setDebug()` also updates loadparm command-line log level. `smbc_setOptionDebugToStderr()` switches process logging to stderr and is intentionally sticky. `smbc_setConfiguration()` loads a config file without full reinit. Protocol setters write loadparm settings in the context loadparm object.

Dependencies and integration: includes `libsmbclient.h`, `libsmb_internal.h`, and loadparm APIs. `smbc_new_context()` calls these setters to install defaults, and compatibility wrappers call the getters for dispatch.

Risks: few functions validate null context pointers or allocation failure, so callers must pass initialized contexts. Some options are process-wide in effect despite context-scoped names. Callback replacement can break invariants if custom implementations do not maintain `context->internal->files` or cache contracts. Test signals: each flag bit toggles independently, string setters handle NULL, debug updates loadparm, stderr stickiness, protocol invalid values return false, callback overrides are invoked, server cache data round-trips, and default callbacks match context initialization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_setget.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_stat.c -->
# sources/user-network-fs/samba/source3/libsmb/libsmb_stat.c

Purpose: implements `stat`, `fstat`, `statvfs`, and `fstatvfs` behavior for libsmbclient, translating SMB file attributes and filesystem information into POSIX-like structures.

Important APIs: `setup_stat()` maps SMB attributes, size, inode, dev, and timestamps into `struct stat`, using execute bits as archive/system/hidden markers and write bit for non-readonly. `SMBC_stat_ctx()` parses a URL, connects, and calls `SMBC_getatr()`. `SMBC_fstat_ctx()` validates an open handle, resolves the stored URL through DFS, calls `cli_qfileinfo_basic()`, and fills stat. `SMBC_statvfs_ctx()` opens the path as directory or file and delegates to `SMBC_fstatvfs_ctx()`. `SMBC_fstatvfs_ctx()` fills block/free-node fields from Unix CIFS or full-size info and sets feature flags.

Control flow/state: no independent persistent state is added. It consumes server dev ids, current file handles, and context options. Inode fallback uses `str_checksum(name)` when the server does not provide one.

Dependencies and integration: depends on `SMBC_parse_path`, `SMBC_server`, `SMBC_getatr`, file/dir open/close implementations, DFS `cli_resolve_path`, `smbXcli` tcon helpers, and time helpers. It is called directly by compatibility wrappers and indirectly by statvfs path probing.

Risks: POSIX mode mapping is an approximation, not ACL-aware. Generated inode values can collide or change with path spelling. `SMBC_statvfs_ctx()` has open/close side effects and can fail if opening a readable path is not permitted. Tests should cover directory/file mode mapping, readonly and archive/system/hidden bits, server-provided vs generated inode, fstat on directories delegating to fstatdir, Unix CIFS vs non-Unix filesystem info, DFS flag, case-insensitive flag, and close cleanup after statvfs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_thread_impl.c -->
# sources/user-network-fs/samba/source3/libsmb/libsmb_thread_impl.c

Purpose: exposes a generic hook for applications to install arbitrary mutex and thread-local-storage primitives for Samba's thread abstraction used by libsmbclient.

Important API: `smbc_thread_impl()` accepts seven function pointers: create/destroy/lock mutex and create/destroy/set/get TLS. It stores them in a static `struct smb_thread_functions tf` and passes that table to `smb_thread_set_functions()`.

Control flow/state: the function performs no validation despite the comment saying all pointers are required. The static table persists after the call, so Samba's thread layer references stable storage. Repeated calls overwrite the same static function table.

Dependencies and integration: depends on `../lib/util/smb_threads_internal.h` for `smb_thread_set_functions` and the table shape. `libsmb_context.c` relies on the installed thread functions for `SMB_THREAD_ONCE`, mutex creation, and locking around global context counts.

Risks: null or incompatible callbacks can break later context initialization or global locking. Calling this after contexts are already active may change synchronization semantics mid-process. Tests should install mock functions before `smbc_new_context()`, assert once/mutex/TLS calls route through the mock layer, exercise repeated replacement, and check behavior when callbacks report failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_thread_impl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_thread_posix.c -->
# sources/user-network-fs/samba/source3/libsmb/libsmb_thread_posix.c

Purpose: installs Samba's built-in POSIX pthread implementation for the libsmbclient thread abstraction.

Important API/state: `SMB_THREADS_DEF_PTHREAD_IMPLEMENTATION(tf)` defines a static pthread-backed `struct smb_thread_functions` table. `smbc_thread_posix()` passes that table to `smb_thread_set_functions()`. The file undefines a possible malloc macro before the pthread implementation macro to avoid malloc checker interference.

Control flow and dependencies: if pthread headers are available they are included; the implementation macro supplies the actual mutex/TLS functions. There is no allocation or runtime branching in `smbc_thread_posix()` itself. It integrates with the same global Samba thread function registry used by `smbc_thread_impl()`.

Risks: this is a process-level installation choice and should be called before concurrent context use. Build coverage depends on pthread availability and macro expansion in Samba headers. Test signals: call `smbc_thread_posix()` before `smbc_new_context()`, create/free contexts from multiple threads, verify `SMB_THREAD_ONCE` initializes the module once, and run under thread sanitizers for context-count mutex use.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/libsmb_thread_posix.c -->
