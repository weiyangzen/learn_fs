# subset-b-009834 research

Grouped research for Samba VFS virusfilter, selected filesystem VFS modules, module build declarations, and nmbd daemon files. Each section preserves its source path for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_virusfilter.c -->
# sources/user-network-fs/samba/source3/modules/vfs_virusfilter.c

## Purpose
`vfs_virusfilter.c` is the front-end Samba VFS module for on-access antivirus scanning. It owns share-level configuration, selects one scanner backend (`clamav`, `dummy`, `fsav`, or `sophos`), hooks file open/close/delete/rename operations, evaluates scan results, optionally caches results, and applies configured infected-file actions such as quarantine, rename, delete, or command execution.

## Important APIs, Types, and Functions
The module registers `vfs_virusfilter_fns` via `vfs_virusfilter_init()`, with handlers for connect, disconnect, openat, close, unlinkat, and renameat. `virusfilter_vfs_connect()` reads `virusfilter:*` smb.conf parameters into `struct virusfilter_config`, builds include/exclude name arrays, prepares the socket I/O handle and optional memcache-backed result cache, creates the quarantine directory when needed, and initializes the selected backend. `virusfilter_scan()` is the central scanner wrapper. It checks the cache, invokes backend `scan_init`, `scan`, and `scan_end`, interprets `VIRUSFILTER_RESULT_*`, and dispatches remediation. `infected_file_action_quarantine()`, `infected_file_action_rename()`, and `infected_file_action_delete()` perform root-mediated VFS moves or unlink operations. `virusfilter_treat_infected_file()` and `virusfilter_treat_scan_error()` prepare environment variables and run configured shell commands.

## Control Flow
On connect, the module calls the next VFS connect first, allocates config, loads all options, creates helper objects, then initializes the backend. On open, it skips directories, named streams, disabled scan-on-open, truncating opens, non-regular files, files outside size limits, excluded paths, quarantine/rename trap names, then calls `virusfilter_scan()`. Infected scans fail open with the configured errno; scanner errors fail only when `block access on error` is enabled. On close, the next close runs before optional scan-on-close, and only modified regular files are scanned. Modified files invalidate cache entries when scan-on-close is disabled. Rename and unlink update or remove cache entries after successful filesystem changes.

## State and Persistence
Per-share state is talloc-owned `struct virusfilter_config` on the VFS handle. Persistent filesystem effects include quarantine directories/files, renamed files, deleted files, and optional external command side effects. The scan cache is process memory only, keyed by current directory plus file name and bounded by entry/time limits. Backend socket connections may persist across scans until `scan request limit` triggers `scan_end`.

## Dependencies and Integration Points
This file depends on Samba VFS, loadparm, talloc, SMB filename helpers, root privilege transitions, name matching, and the backend interface in `vfs_virusfilter_common.h`. It uses socket/cache/shell helpers from `vfs_virusfilter_utils.c`. It integrates with smbd file lifecycle semantics and must remain stackable by calling `SMB_VFS_NEXT_*` where appropriate.

## Risks
The module runs privileged filesystem operations and optional shell commands, so configuration validation and environment sanitization are security critical. Quarantine/rename checks are string based and depend on current path handling. Cache keys based on directory/name can become stale if file contents change without observed modified flags, though rename/unlink and modified close paths mitigate common cases. Scanning after close cannot prevent the completed write, only subsequent access or remediation. External scanner latency and socket failures directly affect file open/close behavior.

## Test Signals
Useful tests include backend selection failure without `virusfilter:scanner`, skip cases for directories/streams/truncating opens/size limits/exclude paths, cache add/get/rename/remove behavior, open/close errno behavior for infected and scanner-error results, quarantine tree creation with prefix/suffix validation, and command environment variables for infected and scan-error hooks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_virusfilter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_virusfilter_clamav.c -->
# sources/user-network-fs/samba/source3/modules/vfs_virusfilter_clamav.c

## Purpose
This file implements the ClamAV `clamd` backend for `vfs_virusfilter`. It translates Samba file scan requests into ClamAV `zSCAN` commands over a Unix-domain socket and maps clamd replies into `virusfilter_result` values.

## Important APIs, Types, and Functions
`virusfilter_clamav_init()` sets the default socket path, allocates `struct virusfilter_backend`, names it `clamav`, and installs `virusfilter_backend_clamav`. `virusfilter_clamav_connect()` configures NUL-terminated read/write lines for clamd z-commands. `virusfilter_clamav_scan_init()` connects to `config->socket_path` as root through the shared I/O helper. `virusfilter_clamav_scan()` sends `zSCAN <cwd>/<fname>`, parses `<FILEPATH>: <REPORT> <TOKEN>`, and returns clean, infected, or error. `virusfilter_clamav_scan_end()` disconnects.

## Control Flow
The core module calls backend connect once during VFS connect to configure EOL behavior. For each scan, `scan_init` opens the socket, `scan` sends one command and reads one response, and `scan_end` closes the stream unless the core request-limit logic keeps it alive. Reply validation checks the filepath prefix separator, finds the last space-delimited token, and handles `OK`, `FOUND`, and `ERROR`.

## State and Persistence
The backend stores no private state beyond the shared `config->io_h` stream and `config->socket_path`. It defaults to `/var/run/clamav/clamd.ctl` unless a build-time macro or smb.conf value overrides it. Scan reports are talloc strings returned to the core.

## Dependencies and Integration Points
It depends on `vfs_virusfilter_common.h` for the backend contract and on `vfs_virusfilter_utils.h` for socket line I/O. It integrates with clamd's local socket protocol and the core's cache/remediation policy.

## Risks
The parser assumes clamd echoes exactly the path length formed from `cwd_fname/fname`; path encoding or unusual names could make validation fail. The code indexes `reply[filepath_len + 1]` after receiving arbitrary scanner output, so malformed short replies rely on surrounding memory safety assumptions. Scanning uses filesystem paths visible to clamd, so permissions and chroot/container layout must match smbd's view.

## Test Signals
Mock clamd replies for `OK`, `FOUND`, `ERROR`, malformed missing colon, missing final token, short replies, socket connect failure, and NUL EOL behavior. Integration tests should confirm default and configured socket paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_virusfilter_clamav.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_virusfilter_common.h -->
# sources/user-network-fs/samba/source3/modules/vfs_virusfilter_common.h

## Purpose
This header defines the shared data model and backend ABI for the Samba virusfilter VFS module family. It is the contract between the core VFS frontend, scanner backends, and utility layer.

## Important APIs, Types, and Functions
`virusfilter_action` describes remediation choices: do nothing, quarantine, rename, and delete. `virusfilter_result` describes scan outcomes: OK/init success, clean, error, infected, and suspected. `struct virusfilter_config` carries all share configuration and runtime state, including scan policy, archive/mime options, size limits, exclude/infected name lists, result cache, remediation commands and errnos, quarantine/rename strings, socket path, I/O handle, and selected backend. `struct virusfilter_backend_fns` declares optional `connect`, `disconnect`, `scan_init`, `scan`, and `scan_end` callbacks. `struct virusfilter_backend` names a backend, carries optional version/private data, and points to the callback table. The header declares init functions for Sophos, F-Secure, ClamAV, and dummy backends.

## Control Flow
The core module fills `virusfilter_config`, calls exactly one backend init function, then drives backend callbacks through the function table. Backends may allocate private state under `backend_private` during connect and may use the shared `io_h`.

## State and Persistence
The header itself has no persistence, but its structures define all in-memory virusfilter state. `virusfilter_config` is per VFS handle/share connection. `cache`, `io_h`, and `backend` are owned by talloc hierarchy. External persistence is delegated to core actions and scanners.

## Dependencies and Integration Points
It includes Samba smbd, globals, filesystem, auth, passdb, netlogon, and tsocket headers, making it a Samba-internal header rather than a standalone library ABI. It also defines and exports `virusfilter_debug_class`.

## Risks
Because backend callbacks receive the full mutable config, backends can change frontend behavior unintentionally. The `scan_init` result enum reuses scan outcomes where `VIRUSFILTER_RESULT_OK` has a special initialization meaning distinct from `CLEAN`. Any ABI change must update all backend files.

## Test Signals
Compile coverage for all backends is the main signal. API tests should verify each backend initializes `config->backend`, names itself, and supplies a valid `scan` callback.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_virusfilter_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_virusfilter_dummy.c -->
# sources/user-network-fs/samba/source3/modules/vfs_virusfilter_dummy.c

## Purpose
The dummy backend provides a scanner implementation for tests and controlled deployments. It marks files infected when their path matches the configured `virusfilter:infected files` list and clean otherwise.

## Important APIs, Types, and Functions
`virusfilter_dummy_scan()` logs the file being scanned and calls `is_in_path(fsp->fsp_name->base_name, config->infected_files, false)`. It returns `VIRUSFILTER_RESULT_INFECTED` on match and `VIRUSFILTER_RESULT_CLEAN` otherwise. `virusfilter_dummy_init()` allocates a backend named `dummy` with only the `scan` callback set.

## Control Flow
The core calls this backend exactly like a real scanner. There is no connection setup, no scan initialization, and no scan teardown. Result handling, cache insertion, blocking behavior, and remediation all stay in `vfs_virusfilter.c`.

## State and Persistence
The backend stores no private state and does not set a report string. It depends on the config's `infected_files` pattern list, which is built from smb.conf at connect time. Persistence occurs only through the core's normal infected-file action.

## Dependencies and Integration Points
It includes `vfs_virusfilter_utils.h`, which brings in common types and Samba path matching. It is built into the `vfs_virusfilter` module with the other backends.

## Risks
Because `reportp` is not populated, downstream infected reporting can see a null report and must tolerate it. The backend is intentionally not a real scanner; enabling it outside test scenarios would only enforce administrator-provided path patterns.

## Test Signals
Tests should configure `virusfilter:scanner = dummy` with matching and non-matching `infected files` patterns, then assert open/close behavior, remediation paths, cache handling, and null-report tolerance.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_virusfilter_dummy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_virusfilter_fsav.c -->
# sources/user-network-fs/samba/source3/modules/vfs_virusfilter_fsav.c

## Purpose
This file implements the F-Secure Anti-Virus `fsavd` backend for `vfs_virusfilter`. It configures fsavd protocol options, scans files through the daemon socket, and translates tab-delimited scanner events into virusfilter results.

## Important APIs, Types, and Functions
`struct virusfilter_fsav_config` stores backend options: protocol version, riskware scanning, stop-on-first behavior, and filename filtering. `virusfilter_fsav_connect()` reads backend-specific smb.conf values and sets `config->block_suspected_file`. `virusfilter_fsav_scan_init()` reuses or opens the Unix socket, validates the `DBVERSION` greeting, and sends `PROTOCOL` plus multiple `CONFIGURE` commands. `virusfilter_fsav_scan()` sends `SCAN\t<cwd>/<fname>`, reads replies until `OK`, and maps `CLEAN`, infection/riskware tokens, suspected tokens, `SCAN_FAILURE`, and unknown replies. `virusfilter_fsav_scan_end()` disconnects.

## Control Flow
On VFS connect, the backend config object is allocated under `config->backend` and given a destructor that closes the scanner connection. Each scan initializes the protocol if needed, sends the scan command, loops over scanner events, updates the result/report as significant records arrive, then returns when an `OK` terminator is read or an I/O/protocol error occurs.

## State and Persistence
Backend state is in `backend_private`. The socket stream can persist between scans and is health-checked with a best-effort `PING`. It defaults to `/tmp/.fsav-0` unless overridden. No data is persisted by the backend itself.

## Dependencies and Integration Points
It depends on the shared virusfilter I/O line protocol helpers and F-Secure fsavd's tab-delimited local socket protocol. It integrates suspected-file policy through the core `block_suspected_file` field.

## Risks
The comments note uncertainty around the correct `PING` command; false connection reuse or false reconnects are possible. Reply parsing assumes `strtok_r()` returns non-null tokens before `strcmp()`, so malformed empty replies are risky. Riskware is mapped to infected when emitted by fsavd, which is policy-sensitive.

## Test Signals
Mock fsavd sessions should cover greeting/configure success and failure, connection reuse, clean/infected/riskware/suspected/scan-failure tokens, malformed empty lines, and `block suspected file` true versus false.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_virusfilter_fsav.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_virusfilter_sophos.c -->
# sources/user-network-fs/samba/source3/modules/vfs_virusfilter_sophos.c

## Purpose
This file implements the Sophos SAVDI SSSP/1.0 backend for `vfs_virusfilter`. It connects to the SAVDI socket, configures SSSP options, URL-quotes file paths, sends `SCANFILE`, and converts SSSP replies into core scan results.

## Important APIs, Types, and Functions
`virusfilter_url_quote()` percent-encodes path characters for SSSP. `virusfilter_sophos_connect()` sets CRLF read EOL handling. `virusfilter_sophos_scan_ping()` sends an `OPTIONS` request to validate an existing connection. `virusfilter_sophos_scan_init()` connects to the default `/var/run/savdi/sssp.sock` or configured socket, validates `OK SSSP/1.0`, and configures `output:brief` plus archive scanning. `virusfilter_sophos_scan()` sends `SSSP/1.0 SCANFILE <encoded path>`, expects `ACC`, then reads records until a blank line. `VIRUS` marks infected; `DONE` codes other than known clean/infected codes mark scanner error.

## Control Flow
The core invokes scan init before scanning. If a stream exists, Sophos ping is attempted and a good stream is reused; otherwise the stream is closed and recreated. The scan path builds one encoded URL from current directory plus filename, writes the command without an explicit line helper, validates acceptance, then iterates response lines.

## State and Persistence
The backend stores no custom private state. The shared I/O stream and socket path are the only runtime state. Reports are allocated transiently for the core.

## Dependencies and Integration Points
It depends on Sophos SAVDI's SSSP/1.0 protocol and shared virusfilter socket helpers. It uses Samba's `nybble_to_hex_upper()` for encoding and the core's archive-scan flag.

## Risks
The URL quoting routine treats `char` bytes directly; signed-char high-bit handling can produce surprising encodings on non-ASCII filenames. The command write length is fixed and must match the literal prefix. Reply parsing assumes non-empty tokens. The backend reports only a single token after `VIRUS`, so multi-word scanner reports may be truncated.

## Test Signals
Protocol tests should cover greeting validation, options accepted/done/blank-line sequencing, connection reuse, long path failure, clean `DONE OK 0000`, infected `VIRUS` plus `DONE OK 0203`, scanner error codes, and malformed/empty replies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_virusfilter_sophos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_virusfilter_utils.c -->
# sources/user-network-fs/samba/source3/modules/vfs_virusfilter_utils.c

## Purpose
This file supplies shared utilities for virusfilter backends and the core: Samba substitution expansion, stackable file moves, line-oriented Unix socket I/O with timeouts, in-memory scan result caching, and shell command environment construction/execution.

## Important APIs, Types, and Functions
`virusfilter_string_sub()` wraps Samba substitution for service/user/path variables. `virusfilter_vfs_next_move()` renames through the next VFS module and deliberately refuses cross-device `EXDEV`. I/O helpers include `virusfilter_io_new()`, EOL/timeout setters, `virusfilter_io_connect_path()`, `virusfilter_io_disconnect()`, `write_data_iov_timeout()`, `virusfilter_io_write*()`, `virusfilter_io_readl()`, and `virusfilter_io_writefl_readl()`. Cache helpers create a `memcache`, add/get/rename/remove/purge entries keyed by directory plus filename, and duplicate/free cache entries safely. Shell helpers include `virusfilter_env_set()`, `virusfilter_shell_set_conn_env()`, and `virusfilter_shell_run()`.

## Control Flow
Socket connect builds an AF_UNIX address, opens a nonblocking close-on-exec socket, and wraps it as a tstream. Write/read operations create short-lived tevent contexts and poll send/receive requests with deadlines. `virusfilter_io_readl()` first drains any existing complete line from the buffer, otherwise reads more data until the configured EOL appears. Cache insertion steals the scan report into a talloc cache entry, while lookups copy entries out so callers can free them independently.

## State and Persistence
Runtime state lives in `struct virusfilter_io_handle` and `struct virusfilter_cache`. The cache is per-process memory only and has time-based expiry. Shell execution may produce external side effects through administrator-configured commands.

## Dependencies and Integration Points
The file depends on Samba tsocket/tstream/tevent, memcache, strv, loadparm substitution, and `smbrun`. It is built as `VFS_VIRUSFILTER_UTILS` only when `vfs_virusfilter` is enabled.

## Risks
`virusfilter_io_readl()` appears to calculate `read_size` with `MIN(pending, 1)` followed by `MAX(..., remaining)`, which can request the full remaining buffer rather than the smaller pending amount; this deserves focused review under nonblocking tstream behavior. Formatted writes do not guard against `vsnprintf()` output equal to or larger than the fixed buffer before appending EOL. Cache expiry removal passes an already combined `directory/fname` as `fname` back into `virusfilter_cache_remove()`, which may build a mismatched key. Shell command execution is sanitized but still administrator-controlled and security-sensitive.

## Test Signals
Unit tests should cover partial-line buffering, multiple lines in one read, timeout/error paths, overlong scanner lines, cache add/get/expiry/rename/remove key behavior, cross-device rename refusal, environment variable population, and sanitized versus unsanitized shell execution.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_virusfilter_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_virusfilter_utils.h -->
# sources/user-network-fs/samba/source3/modules/vfs_virusfilter_utils.h

## Purpose
This header declares the utility API shared by the virusfilter core and scanner backends, including socket I/O handles, result cache types, substitution helpers, cache operations, and shell execution wrappers.

## Important APIs, Types, and Functions
It defines buffer and I/O constants: URL max, line buffer size, EOL size, iovec max, and cache buffer size. `struct virusfilter_io_handle` stores a tstream, connect/I/O timeouts, read/write EOL bytes, and an internal read buffer. `struct virusfilter_cache_entry` stores timestamp, result, and report. `struct virusfilter_cache` stores a memcache handle, talloc context, and time limit. Function declarations cover path substitution, next-module move, line socket connect/read/write variants, cache lifecycle and mutation, and shell environment/command execution.

## Control Flow
The header exposes a layered design: backends use I/O functions to talk to scanner daemons; the core uses cache functions before/after scans and shell helpers when handling infected or error outcomes.

## State and Persistence
The declared structs are in-memory only. The I/O handle can preserve a scanner stream across requests, and the cache stores transient scan decisions. No on-disk format is defined here.

## Dependencies and Integration Points
It includes `vfs_virusfilter_common.h`, Samba memcache, and strv helpers. Any backend including this header receives both the common virusfilter ABI and these utilities.

## Risks
Constants assume PATH_MAX-scaled scanner commands fit in fixed buffers; callers must avoid truncation and overflow. The EOL size is one byte in this header, but the Sophos backend requests a two-byte CRLF read EOL, which the setter rejects because `VIRUSFILTER_IO_EOL_SIZE` is 1. That mismatch can make CRLF protocol handling ineffective.

## Test Signals
Compile-time and runtime tests should validate EOL settings for all backends, maximum path handling, cache entry ownership, and that public declarations match implementation attributes such as printf-style varargs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_virusfilter_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_vxfs.c -->
# sources/user-network-fs/samba/source3/modules/vfs_vxfs.c

## Purpose
`vfs_vxfs.c` adapts Samba VFS xattr, DOS attribute, and optional POSIX ACL behavior for Veritas VxFS. It prefers VxFS-specific xattr APIs and falls back to the next VFS module when unsupported, while protecting Samba NT ACL storage.

## Important APIs, Types, and Functions
ACL helpers sort, compact, and compare ACL entries: `vxfs_sort_acl()`, `vxfs_compact_buf()`, `vxfs_compare_acls()`, and `vxfs_compare()`. With `VXFS_ACL_SHARE`, `vxfs_sys_acl_set_fd()` avoids setting identical ACLs to preserve inherited VxFS ACL inode sharing. Xattr handlers `vxfs_fset_xattr()`, `vxfs_fget_xattr()`, `vxfs_fremove_xattr()`, and `vxfs_flistxattr()` route through fd, `/proc/fd` path, or filename VxFS APIs, then fall back. `vxfs_fset_ea_dos_attributes()` maps Samba readonly DOS attributes into VxFS write-protection xattrs. `vfs_vxfs_connect()` initializes VxFS support.

## Control Flow
On connect the module calls the next VFS connect and `vxfs_init()`. For xattrs, it tries fd-based VxFS calls when possible, path-based calls for pathref/proc-fd cases, then next-module xattr calls if VxFS reports unsupported. Samba's generic `XATTR_NTACL_NAME` is mapped to restricted `system.NTACL` storage on fallback. Clients are denied direct access to the protected NTACL xattr. DOS readonly setting first updates normal Samba DOS attributes, then applies or checks VxFS write xattrs.

## State and Persistence
Persistence is on the VxFS filesystem via xattrs and ACLs. The module itself keeps no per-handle private state. It can remove old-style `user.NTACL` entries after successfully setting the current NTACL.

## Dependencies and Integration Points
It depends on VxFS wrapper functions declared in `vfs_vxfs.h` and implemented elsewhere, Samba ACL/xattr VFS operations, pathref fd helpers, and `system.NTACL` security assumptions. It registers as module `vxfs`.

## Risks
The security warning around `XATTR_USER_NTACL` is central: moving NT ACL storage to `user.*` can let local users modify Samba ACLs. Several code paths preserve and restore errno manually and mix old/new removal behavior, which can mask partial failures. Path-based fallbacks for pathref files depend on proc-fd support and race-resistant VFS semantics. ACL comparison compacts entries and ignores some mask differences by design, so tests must prove it does not skip required ACL updates.

## Test Signals
Tests should cover fd, pathref/proc-fd, and path-only xattr operations; unsupported fallback; denial of direct protected NTACL get/set/list/remove; old `user.NTACL` cleanup; readonly DOS attribute mapping; and ACL-share compare/no-op behavior under `VXFS_ACL_SHARE`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_vxfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_vxfs.h -->
# sources/user-network-fs/samba/source3/modules/vfs_vxfs.h

## Purpose
This header declares the VxFS-specific wrapper functions consumed by `vfs_vxfs.c`. It abstracts platform or library calls for VxFS xattr and write-attribute support.

## Important APIs, Types, and Functions
The declarations include fd and path variants for setting, getting, removing, and listing xattrs: `vxfs_setxattr_fd`, `vxfs_getxattr_path`, `vxfs_getxattr_fd`, `vxfs_removexattr_fd`, and `vxfs_listxattr_fd`. It also declares write-attribute controls `vxfs_setwxattr_path`, `vxfs_setwxattr_fd`, `vxfs_checkwxattr_path`, `vxfs_checkwxattr_fd`, and global initialization `vxfs_init()`.

## Control Flow
`vfs_vxfs.c` calls `vxfs_init()` during VFS connect, then chooses fd/path helper calls based on Samba `files_struct` capabilities. The helpers report unsupported operations through errno values, allowing fallback to generic VFS xattr behavior.

## State and Persistence
The header has no state. Its functions act on persistent filesystem metadata managed by VxFS.

## Dependencies and Integration Points
It is tightly coupled to the VxFS wrapper implementation, likely `lib_vxfs.c`, and to Samba's VFS xattr module. The path functions must honor directory versus file behavior where the C module passes an `is_dir` flag to definitions not shown in this header, so implementation prototypes must remain consistent with compilation context.

## Risks
Prototype drift between this header and wrapper implementation would be a hard compile or ABI risk. Because callers rely on errno categories such as `ENOTSUP`, `ENOSYS`, `ENODATA`, `EOPNOTSUPP`, and `ENOENT`, wrapper implementations must preserve errno precisely.

## Test Signals
Build tests with VxFS support enabled are mandatory. Runtime tests should inject wrapper return codes and errno values to verify fallback and error mapping in `vfs_vxfs.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_vxfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_widelinks.c -->
# sources/user-network-fs/samba/source3/modules/vfs_widelinks.c

## Purpose
`vfs_widelinks.c` reintroduces legacy insecure `wide links = yes` behavior as an explicit VFS module. It hides symlink traversal from upper smbd path checks by preserving the logical share-relative current directory and masking symlink semantics for non-POSIX operations.

## Important APIs, Types, and Functions
`struct widelinks_config` stores whether the module is active, whether the share is a DFS root, and the logical `cwd`. `widelinks_connect()` allocates config and checks `lp_widelinks()` and DFS settings. `widelinks_chdir()` records the requested absolute path after the next chdir succeeds. `widelinks_realpath()` returns a canonicalized path based on the logical cwd rather than the underlying filesystem target. `widelinks_lstat()` maps lstat to stat for non-POSIX paths after chdir. `widelinks_openat()` removes symlink-follow prevention flags and handles DFS symlink ENOENT/ELOOP behavior.

## Control Flow
Before the share chdir or when `wide links` is not active, functions pass through to the next VFS module. Once active and after chdir, realpath combines logical cwd plus input path, lstat hides symlinks, and open clears `O_NOFOLLOW`, optional `O_PATH`, and `VFS_OPEN_HOW_RESOLVE_NO_SYMLINKS`. POSIX path requests still see symlinks where lstat is concerned.

## State and Persistence
The only module state is per-connection logical cwd. No on-disk state is changed beyond normal operations performed by the next VFS layer.

## Dependencies and Integration Points
It depends on Samba VFS path operations and loadparm settings `wide links`, `host msdfs`, and `msdfs root`. It exists to isolate insecure share-escape compatibility from core smbd path enforcement.

## Risks
The module intentionally weakens symlink containment and must be enabled only by explicit administrator choice. Incorrect activation before chdir could hide setup-time symlinks, but the code passes through while `cwd == NULL` to fail safer. `openat()` removes no-symlink resolution flags without checking POSIX path flags, so its semantics must match callers' expectations.

## Test Signals
Tests should verify inactive pass-through, pre-chdir pass-through, logical cwd realpath after symlink traversal, lstat-to-stat masking for normal paths, POSIX-path lstat behavior, open flag stripping, and DFS symlink error shaping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_widelinks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_worm.c -->
# sources/user-network-fs/samba/source3/modules/vfs_worm.c

## Purpose
`vfs_worm.c` implements write-once-read-many behavior by denying write or metadata-changing operations on files older than a configured grace period. It protects both file data and ACL/xattr/attribute mutation once the ctime age crosses the threshold.

## Important APIs, Types, and Functions
`struct worm_config_data` stores `grace_period`. `write_access_flags` combines data, append, attribute, delete, owner, DACL, and EA write bits. `vfs_worm_connect()` reads `worm:grace_period` except for IPC/print shares. `is_readonly()` and `fsp_is_readonly()` compare stat ctime age with the grace period. The module hooks `create_file`, `openat`, `fntimes`, `fchmod`, `fchown`, `renameat`, `fsetxattr`, `fremovexattr`, `unlinkat`, DOS attributes, NT ACLs, POSIX ACL set/delete, and rejects changes when readonly.

## Control Flow
On create/open, readonly files with requested or granted write access are denied. Metadata and ACL/xattr operations check readonly before calling the next VFS method. Rename denies if the source is protected and also checks an existing destination path to prevent overwriting a protected target. Unlink builds a full filename, checks readonly, then delegates.

## State and Persistence
The module stores only per-share grace-period config. Protection state is inferred from filesystem ctime, not stored separately. No persistent marker is written by this module.

## Dependencies and Integration Points
It depends on Samba security access masks, stat timestamps, VFS full-path helpers, and next-module operations. It registers as `worm` and is built as an optional VFS module.

## Risks
Using ctime means administrative metadata changes can reset or affect protection timing depending on filesystem semantics. Operations with invalid stat default to readonly in handle-data failure cases but not when stat is simply invalid inside helper flow. Rename destination protection was explicitly added for a CVE fix, so overwrite and race behavior around destination lookup is high risk.

## Test Signals
Tests should cover files younger/older than grace period, MAXIMUM_ALLOWED access, write and metadata operations, unlink of protected files, rename source and destination protection, xattr/ACL denial, IPC/print share bypass, and ctime boundary conditions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_worm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_xattr_tdb.c -->
# sources/user-network-fs/samba/source3/modules/vfs_xattr_tdb.c

## Purpose
`vfs_xattr_tdb.c` stores POSIX-style extended attributes in a Samba TDB database rather than on the underlying filesystem. It enables EA support on filesystems without native xattrs and can optionally pass `user.*` xattrs through to the backend filesystem.

## Important APIs, Types, and Functions
`struct xattr_tdb_config` stores the db handle and `ignore_user_xattr`. `xattr_tdb_init()` opens the configured TDB path, defaults to `state_path("xattr.tdb")`, and toggles `ea support`. Async getxattr support is implemented by `xattr_tdb_getxattrat_send/recv()` and callback `xattr_tdb_getxattrat_done()`. Synchronous fd hooks include `xattr_tdb_fgetxattr()`, `xattr_tdb_fsetxattr()`, `xattr_tdb_flistxattr()`, and `xattr_tdb_fremovexattr()`. `xattr_tdb_openat()` and `xattr_tdb_mkdirat()` clear stale attrs for newly created objects. `xattr_tdb_unlinkat()` removes all stored attrs when a removed object's final link or directory record goes away.

## Control Flow
Most operations lazily initialize config. If `ignore_user_xattr` is true and the xattr name starts with `user.`, operations delegate to the next VFS module. Otherwise the module obtains a file id from stat information and calls `xattr_tdb_*` library routines. On new file or directory creation, it removes all attrs for the new file id to avoid stale records from id reuse. On unlink, it stats before deletion, delegates unlink, and removes the DB record only when the object is removed or the last hard link is gone.

## State and Persistence
Persistent state is the TDB database containing xattr records keyed by Samba file id. The module stores one db handle per VFS handle. Native backend xattrs may also persist when `ignore_user_xattr` is enabled.

## Dependencies and Integration Points
It depends on dbwrap, `source3/lib/xattr_tdb.h`, Samba async VFS xattr APIs, file-id creation, pathref open helpers, and loadparm. It integrates with `ea support` by enabling it after successful DB init and disabling it on init failure.

## Risks
File-id reuse is mitigated on create/mkdir but remains sensitive to filesystems with unstable IDs. Mixed TDB and backend `user.*` listing can produce concatenated lists whose sizing/duplicates must be correct. In async getxattr passthrough, the local `smb_fname` variable is null in the delegation branch, which should be reviewed against `SMB_VFS_NEXT_GETXATTRAT_SEND` expectations. DB corruption or permission errors disable EA support.

## Test Signals
Tests should cover configured/default DB paths, init failure toggling `ea support`, get size-only/value/ERANGE, set flags, list with and without backend user xattrs, remove, create/mkdir stale cleanup, unlink hard-link semantics, symlink/POSIX path stat behavior, and async passthrough.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_xattr_tdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_zfsacl.c -->
# sources/user-network-fs/samba/source3/modules/vfs_zfsacl.c

## Purpose
`vfs_zfsacl.c` converts between ZFS/Solaris NFSv4 ACLs and Samba NT ACLs. It provides NT ACL get/set support for ZFS or Solaris NFSv4 ACL filesystems and blocks conflicting POSIX draft ACL methods.

## Important APIs, Types, and Functions
`struct zfsacl_config_data` stores NFSv4 ACL conversion parameters and zfsacl options. `zfs_get_nt_acl_common()` converts an array of `ace_t` records to Samba `SMB4ACL_T`, maps special owner/group/everyone IDs, adds synchronize bits for allowed ACEs, handles directory delete-child behavior, optional inherited/protected DACL mapping, and special empty ACE blocking. `zfs_process_smbacl()` converts Samba SMB4 ACEs back to `ace_t` and writes them with `facl(ACE_SETACL)`. `zfsacl_fget_nt_acl()` reads with `facl(ACE_GETACLCNT/ACE_GETACL)`, converts to NT ACL, or falls back to a default protected ACL on unsupported filesystems. `zfsacl_fset_nt_acl()` calls `smb_set_nt_acl_nfs4()`.

## Control Flow
On connect, config reads `zfsacl:map_dacl_protected`, `zfsacl:denymissingspecial`, `zfsacl:block_special`, and common SMB ACL4 params. Get ACL reads native ACEs from a pathref fd, builds SMB4 ACLs, then lets shared NFSv4 conversion produce a security descriptor. Set ACL converts the incoming NT descriptor through shared NFSv4 helpers and a callback that writes the native ACE array.

## State and Persistence
The module stores per-share conversion flags only. Persistent ACL state is on the underlying ZFS/NFSv4 filesystem through `facl()`.

## Dependencies and Integration Points
It depends on `nfs4_acls.h`, `sunacl.h` when available, Solaris/ZFS `acl(2)` style `facl()`, Samba security descriptors, and NFSv4 ACL stat wrappers. It deliberately overrides POSIX ACL VFS methods with fail stubs to avoid incompatible Solaris ACL compatibility wrappers.

## Risks
ACL conversion is security-critical and depends on special ID handling. `zfsacl_denymissingspecial` can reject ACLs without owner/group/everyone mappings, while `zfsacl_block_special` inserts or filters zero-mask inherited everyone ACEs. Unsupported filesystem fallback creates a default protected ACL, which may surprise callers but avoids hard failure. Ordering relative to `vfs_solarisacl` matters.

## Test Signals
Tests should cover get/set of owner/group/everyone special ACEs, inherited DACL protected mapping, block-special filtering/insertion, deny-missing-special behavior, synchronize bit add/remove, directory add-file to delete-child mapping, unsupported `facl` fallback, and POSIX ACL method failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_zfsacl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/wscript_build -->
# sources/user-network-fs/samba/source3/modules/wscript_build

## Purpose
This Waf build script declares Samba source3 module subsystems, VFS modules, related test binaries, generated sources, dependencies, conditional enablement, and static/dynamic module settings.

## Important APIs, Types, and Functions
It uses build helper calls such as `bld.SAMBA3_SUBSYSTEM`, `bld.SAMBA3_MODULE`, `bld.SAMBA3_BINARY`, `bld.SAMBA_GENERATOR`, `bld.SAMBA_SUBSYSTEM`, `bld.CONFIG_SET`, `bld.CONFIG_GET`, `bld.SAMBA3_IS_ENABLED_MODULE`, and `bld.SAMBA3_IS_STATIC_MODULE`. In this subset, key declarations include `VFS_VIRUSFILTER_UTILS`, `vfs_xattr_tdb`, `vfs_zfsacl`, `vfs_worm`, `vfs_virusfilter`, `vfs_vxfs`, and `vfs_widelinks`.

## Control Flow
The script is evaluated by Samba's build system. Subsystems are declared first, followed by a long list of VFS module targets. Conditional blocks generate NFSv4 xattr RPC sources only when `vfs_nfs4acl_xattr` is enabled and RPC headers are available. Module enablement is driven by configuration checks and module selection helpers; some test binaries are marked `for_selftest=True`.

## State and Persistence
The file does not store runtime state. It persists build graph metadata into Waf's configured build outputs. Module static/dynamic choices and generated files affect produced binaries and installed modules.

## Dependencies and Integration Points
It integrates source files with Samba libraries and external dependencies such as `acl`, `attr`, `sunacl`, `dbwrap`, `xattr_tdb`, `cephfs`, `gfapi`, `tevent`, `dbus-1`, `uring`, and `varlink`. The virusfilter module depends on `samba-util` and `VFS_VIRUSFILTER_UTILS`; VxFS is built from `lib_vxfs.c vfs_vxfs.c`; ZFS ACL depends on `NFS4_ACLS sunacl`.

## Risks
Incorrect dependency or enablement expressions can silently omit modules or build them without required helper subsystems. `VFS_VIRUSFILTER_UTILS` is enabled only if `vfs_virusfilter` is enabled, so any other consumer would need a build rule change. Generated RPC source paths are sensitive to out-of-tree build path handling, as reflected by the copy/rpcgen workaround.

## Test Signals
Build matrix tests should toggle the selected modules static/dynamic/enabled/disabled, run selftest binaries declared here, verify generated NFS4 xattr sources in out-of-tree builds, and confirm expected external dependency detection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/asyncdns.c -->
# sources/user-network-fs/samba/source3/nmbd/asyncdns.c

## Purpose
`asyncdns.c` provides DNS lookup support for nmbd WINS DNS proxy behavior. When pipes/fork are available, it offloads blocking hostname resolution to a child process; otherwise it performs synchronous DNS lookup inline.

## Important APIs, Types, and Functions
`add_dns_result()` inserts positive or negative DNS answers into the WINS server subnet name cache with different TTLs and sources (`DNS_NAME` or `DNSFAIL_NAME`). In async mode, global fds, child pid, queue/current packet pointers, and `in_dns` track child communication and recursion. `asyncdns_fd()` exposes the read fd. `start_async_dns()` creates pipes, forks, sets signal handling, reinitializes after fork, and runs `asyncdns_process()` in the child. `queue_dns_query()` writes or queues packet queries. `run_dns_queue()` reads child results, updates cache, responds to the current and queued matching packets, frees packets, and starts the next queued query. `kill_async_dns_child()` terminates the child. Sync mode implements `queue_dns_query()` directly with `interpret_addr()`.

## Control Flow
In async mode, nmbd starts the DNS child when configured as WINS server with DNS proxy. Queries are represented as `struct query_record` containing an `nmb_name` and result address. The parent writes one current query to the child and queues additional packets. When the child returns a result, the parent caches it, sends WINS query responses for the current and any queued matching packet, frees them, then dispatches the next queued packet.

## State and Persistence
The DNS answer is persisted in nmbd's in-memory WINS name cache with TTL: one hour for negative answers, two hours for positive answers. Async child/process state is global and process-local. No on-disk persistence is performed here.

## Dependencies and Integration Points
It depends on nmbd packet structures and name cache APIs, Samba pipe/read/write helpers, process-existence checks, `interpret_addr()`, and WINS response functions. It is compiled with `SYNC_DNS` when `HAVE_PIPE` is missing.

## Risks
Global queue state and packet locking must be correct to avoid leaks or double frees. If the child dies, `run_dns_queue()` closes fds and restarts it, but pending current/queued behavior around restart is delicate. DNS replies are keyed by NetBIOS name equality; queued identical questions all receive the same result. The child exits on pipe errors without cleanup beyond process exit.

## Test Signals
Tests should cover positive and negative cache insertion TTL/source, async queue ordering, duplicate queued query fanout, child death/restart, write/read failure handling, `in_dns` recursion guard, packet lock clearing, sync-mode behavior, and SIGTERM child cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/asyncdns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd.c -->
# sources/user-network-fs/samba/source3/nmbd/nmbd.c

## Purpose
`nmbd.c` is the main program and lifecycle manager for Samba's NetBIOS name service daemon. It initializes configuration, daemonization, messaging, WINS/name/browse state, sockets, subnets, signal handlers, async DNS, and then runs the nmbd periodic packet-processing loop.

## Important APIs, Types, and Functions
Global sockets are `ClientNMB`, `ClientDGRAM`, and `global_nmb_port`; `StartupTime` records daemon start. `nmbd_event_context()` returns the global tevent context. `terminate()` performs orderly shutdown by writing WINS data, releasing names, announcing removals, killing async DNS, unlinking pidfile, and exiting. Signal and stdin handlers route SIGTERM, SIGHUP, and foreground stdin EOF. `reload_interfaces()` reconciles interface additions/removals and waits for IPv4 non-loopback interfaces. `reload_nmbd_services()` and `msg_reload_nmbd_services()` reload smb.conf and refresh names/interfaces. `msg_nmbd_send_packet()` sends packets requested over Samba messaging. `process()` is the main loop. `open_sockets()` opens broadcast UDP sockets. `main()` wires all initialization steps.

## Control Flow
`main()` initializes talloc, command-line parsing, logging, signals, role checks, clustering, messaging, loadparm, NetBIOS names, daemon mode, optional async DNS, lock/pid directories, signal handlers, messaging handlers, sockets, interfaces, subnets, lmhosts, WINS, workgroup/name registration, packet server, daemon readiness, then calls `process()`. The main loop repeatedly checks elections, receives and processes packets, runs announcements, refreshes/flushes names and browse lists, handles WINS and browser synchronization, retransmits/expirs response records, checks child sync completion, syncs DMBs, and reloads interfaces.

## State and Persistence
State includes global sockets, global nmbd flags, workgroup/name/subnet structures, WINS database, browse list, pidfile, lock files, messaging registrations, and optional async DNS child. Persistent outputs include WINS database writes, browse list snapshots, pidfile, and logs.

## Dependencies and Integration Points
The file is the integration point for most nmbd subsystems declared in `nmbd.h` and `nmbd_proto.h`: packets, elections, WINS server/client, browse sync, interface management, lmhosts, messaging, server IDs, gencache, and Samba daemon utilities.

## Risks
The process loop is single-threaded and depends on cooperative periodic functions not blocking for long. Interface reload intentionally leaks removed subnet records rather than freeing possibly referenced memory. Only IPv4 non-loopback interfaces are handled for nmbd sockets. Shutdown order matters to avoid stale WINS registrations. AD DC role check prevents standalone nmbd, but can be inhibited by configuration.

## Test Signals
Tests should cover command-line options, daemon/foreground/stdin behavior, SIGTERM/SIGHUP and smbcontrol messages, AD DC role refusal, socket bind failures, interface add/remove/wait behavior, WINS init failures, registration failures, packet send validation, and main-loop periodic function scheduling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd.h -->
# sources/user-network-fs/samba/source3/nmbd/nmbd.h

## Purpose
`nmbd.h` is the central header for Samba's NetBIOS name service daemon. It defines constants, enums, state structures, callback types, subnet traversal macros, WINS record layout, and includes generated nmbd prototypes.

## Important APIs, Types, and Functions
The header defines database keys (`INFO_*`, `ENTRY_PREFIX`), timing constants, browser/election constants, mailslot paths, name source enum, master/domain/logon states, and subnet types. Core structures include `nmb_data`, `name_record`, `browse_cache_record`, `server_info_struct`, `server_record`, `work_record`, `userdata_struct`, `response_record`, `subnet_record`, and `WINS_RECORD`. It defines callback typedefs for response, timeout, success, and fail handlers, including specific register/release/refresh/query/node-status signatures. It declares external subnet globals and includes `nmbd/nmbd_proto.h`.

## Control Flow
This header shapes nmbd control flow by defining how names live on subnets, how workgroups and servers age and announce, how response records retry/expire, and how callbacks are typed for asynchronous name operations. Macros such as `FIRST_SUBNET`, `NEXT_SUBNET_EXCLUDING_UNICAST`, and `NEXT_SUBNET_INCLUDING_UNICAST` drive subnet iteration.

## State and Persistence
The structures describe in-memory daemon state. `WINS_RECORD` is the packed-ish record used between nmbd and WINS replication logic. TTL/death/refresh fields determine persistence in memory and eventual database writes performed elsewhere.

## Dependencies and Integration Points
It includes `libsmb/nmblib.h` and generated `nmbd_proto.h`. `SYNC_DNS` is defined here when `HAVE_PIPE` is unavailable, affecting `asyncdns.c`. Almost every nmbd source file depends on these common state definitions.

## Risks
Because this is a shared internal header, structure layout changes have broad daemon impact. `userdata_struct` uses a flexible array plus explicit 16-byte alignment workaround for older GCC, so allocation/copy/free functions must respect its layout. `WINS_RECORD` has fixed limits such as 25 IPs and 17-byte names. IPv4-specific helpers and fields reflect nmbd's IPv4 NetBIOS focus.

## Test Signals
Compile-time prototype checking is important for callback typedefs. Behavioral tests should exercise response record lifecycle, subnet iteration including/excluding unicast, WINS record serialization limits, userdata copy/free ownership, and state transitions for browser/domain/logon roles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/nmbd/nmbd.h -->
